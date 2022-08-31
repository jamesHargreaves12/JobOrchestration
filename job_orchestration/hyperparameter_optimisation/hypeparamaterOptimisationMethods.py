# For now this is single threaded but we should change this.
import logging
import os
import time

import yaml

from .base import HyperParameterOptimisationBase
from .grid import GridSearch, GridOptimizationConfig
from job_orchestration.Constants import config_source_location
from job_orchestration.configBase import Dict2Class
from job_orchestration.getClientMethods import getTaskByName
from job_orchestration.Config import Config
from job_orchestration.setupOutput import setupOutput


def hyperParameterOptimisationFactory(optimisationMethod: str) -> (HyperParameterOptimisationBase, Dict2Class):
    if optimisationMethod == "grid":
        return GridSearch(), GridOptimizationConfig
    raise Exception("Unknown optimisationMethod")


def __setupNextConfig(currentConfig: dict, baseOutputDir, candidate):
    uid = str(int(time.time()))
    nextConfig = currentConfig
    nextConfig["tasks"] = [
        {
            'id': 'hyperparameterTrial',
            'method': 'hyperparameterTrial',
            'paramVals': candidate
        },
        {
            'id': 'hyperparameterEvaluate',
            'method': 'hyperparameterEvaluate'
        }
    ]
    nextConfig["outputDir"] = os.path.join(baseOutputDir, uid)
    configFilename = "hyperparameter_{}.yaml".format(uid)
    configFilePath = os.path.join(config_source_location, configFilename)
    yaml.dump(nextConfig, open(configFilePath, "w+"))
    setupOutput(Config(configFilePath), configFilename)  # possibly wasteful but works for now


class StartHyperparameterOptimizationConfig(Dict2Class):
    optimisationMethod: str
    baseOutputDir: str


def __runHyperparameterOptimization(config: StartHyperparameterOptimizationConfig):
    hyperParameterOptimizer, configClass = hyperParameterOptimisationFactory(config.optimisationMethod)
    initialCandidate = hyperParameterOptimizer.getNextTrial(configClass(config.raw_dict), [])

    __setupNextConfig(config.raw_dict, config.baseOutputDir, initialCandidate)


# This has all become kinda awkward due to the need to pull some variables from task level config aswell as top level.
# I should revisit this.
class HyperParameterTrialConfig(Dict2Class):
    pathToModuleCode: str
    testMethod: str
    paramVals: dict
    resultsFilepath: str


def __hyperparameterTrial(config: HyperParameterTrialConfig):
    logging.info("getTaskByName")
    task = getTaskByName(config.pathToModuleCode, config.testMethod)
    logging.info("Running Task")

    fakeTaskConfig = {
        'id': 'hyperparameterOptimisation_{}'.format(task.__name__),
        'method': task.__name__
    }
    for param, val in config.paramVals.items():
        fakeTaskConfig[param] = val
    result = task({**config.raw_dict, **fakeTaskConfig})

    logging.info("Finished Task")
    resultsPath = config.resultsFilepath
    curResults: list = yaml.safe_load(open(resultsPath)) if os.path.exists(resultsPath) else []
    trialResult = config.paramVals.copy()
    trialResult["result"] = result
    curResults.append(trialResult)
    with open(config.resultsFilepath, "w+") as fp:
        yaml.dump(curResults, fp)
    logging.info("finished hyperparameterTrial")


class HyperparameterEvaluateConfig(Dict2Class):
    resultsFilepath: str
    numberTrials: int  # should be optional?
    optimisationMethod: str
    baseOutputDir: str


def __hyperparameterEvaluate(config: HyperparameterEvaluateConfig):
    def logMax(results):
        logging.info(
            "The maximum setting of params found is: {}".format(max(results, key=lambda x: x["result"]))
        )

    resultsPath = config.resultsFilepath
    curResults: list = yaml.safe_load(open(resultsPath)) if os.path.exists(resultsPath) else []

    if config.numberTrials is not None and config.numberTrials == len(curResults):
        logMax(curResults)
        return

    hyperParameterOptimizer, configClass = hyperParameterOptimisationFactory(config.optimisationMethod)
    candidate = hyperParameterOptimizer.getNextTrial(configClass(config.raw_dict), curResults)
    if candidate is None:
        logMax(curResults)
        return
    __setupNextConfig(config.raw_dict, config.baseOutputDir, candidate)
