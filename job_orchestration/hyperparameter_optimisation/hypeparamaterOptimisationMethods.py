# For now this is single threaded but we should change this.
import logging
import os
import time

import yaml

from .base import HyperParameterOptimisationBase
from .grid import GridSearch, GridOptimizationConfig
from job_orchestration.Config import Config, TaskConfig
from job_orchestration.Constants import config_source_location
from job_orchestration.SetConfigFilesReady import setConfigReady
from job_orchestration.configBase import Dict2Class
from job_orchestration.getClientMethods import getTaskByName


def hyperParameterOptimisationFactory(optimisationMethod: str) -> (HyperParameterOptimisationBase, Dict2Class):
    if optimisationMethod == "grid":
        return GridSearch(), GridOptimizationConfig
    raise Exception("Unknown optimisationMethod")


def __setupNextConfig(currentConfig: dict, baseOutputDir, candidate, specialCaseValidators):
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
    yaml.dump(nextConfig, open(os.path.join(config_source_location, configFilename), "w+"))
    setConfigReady(configFilename, specialCaseValidators) # possibly wasteful but works for now


class RunHyperparameterOptimizationConfig(Dict2Class):
    optimisationMethod: str
    baseOutputDir: str


def __runHyperparameterOptimization(config: RunHyperparameterOptimizationConfig, specialCaseValidators):
    hyperParameterOptimizer, configClass = hyperParameterOptimisationFactory(config.optimisationMethod)
    initialCandidate = hyperParameterOptimizer.getNextTrial(configClass(config.input_dict), [])

    __setupNextConfig(config.input_dict, config.baseOutputDir, initialCandidate, specialCaseValidators)


# This has all become kinda awkward due to the need to pull some variables from task level config aswell as top level.
# I should revisit this.
class HyperParameterTrialConfig(Dict2Class):
    pathToModuleCode: str
    testMethod: str
    paramVals: dict
    resultsFilepath: str
    overallConfig: Config

    def __init__(self, taskConfig: TaskConfig):
        super().__init__(taskConfig.overallConfig.raw_config)
        self.paramVals = taskConfig.rawTaskConfig["paramVals"]
        self.overallConfig = taskConfig.overallConfig


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
    taskConfig = TaskConfig(fakeTaskConfig, config.overallConfig)
    result = task(taskConfig)
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


def __hyperparameterEvaluate(config: HyperparameterEvaluateConfig, specialCaseValidators):
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
    candidate = hyperParameterOptimizer.getNextTrial(configClass(config.input_dict), curResults)
    if candidate is None:
        logMax(curResults)
        return
    __setupNextConfig(config.input_dict, config.baseOutputDir, candidate, specialCaseValidators)
