# For now this is single threaded but we should change this.
import logging
import os
import time
from abc import ABC

import yaml

from .base import HyperParameterOptimisationBase
from .grid import GridSearch, GridOptimizationConfig
from job_orchestration.Constants import config_source_location
from job_orchestration.configBase import Dict2Class
from job_orchestration.getClientMethods import getTaskByName
from job_orchestration.Config import Config
from job_orchestration.setupOutput import setupOutput
from job_orchestration.TaskBase import TaskBase


def hyperParameterOptimisationFactory(optimisationMethod: str) -> (HyperParameterOptimisationBase, Dict2Class):
    if optimisationMethod == "grid":
        return GridSearch(), GridOptimizationConfig
    raise Exception("Unknown optimisationMethod")


def setupNextConfig(currentConfig: dict, baseOutputDir, candidate):
    uid = str(int(time.time()))
    nextConfig = currentConfig
    nextConfig["tasks"] = [
        {
            'id': 'HyperparameterTrial',
            'method': 'HyperparameterTrial',
            'paramVals': candidate
        },
        {
            'id': 'HyperparameterEvaluate',
            'method': 'HyperparameterEvaluate'
        }
    ]
    nextConfig["outputDir"] = os.path.join(baseOutputDir, uid)
    configFilename = "hyperparameter_{}.yaml".format(uid)
    configFilePath = os.path.join(config_source_location, configFilename)
    yaml.dump(nextConfig, open(configFilePath, "w+"))
    setupOutput(Config(configFilePath), configFilename)  # possibly wasteful but works for now


class TaskWithInitAndValidate(TaskBase, Dict2Class, ABC):
    def __init__(self, config: dict):
        Dict2Class.__init__(self, config)


class StartHyperparameterOptimization(TaskWithInitAndValidate):
    optimisationMethod: str
    baseOutputDir: str

    def run(self):
        hyperParameterOptimizer, configClass = hyperParameterOptimisationFactory(self.optimisationMethod)
        initialCandidate = hyperParameterOptimizer.getNextTrial(configClass(self.raw_dict), [])

        setupNextConfig(self.raw_dict, self.baseOutputDir, initialCandidate)


class HyperparameterTrial(TaskWithInitAndValidate):
    pathToTasks: str
    testMethod: str
    paramVals: dict
    resultsFilepath: str

    def run(self):
        logging.info("getTaskByName")
        task = getTaskByName(self.pathToTasks, self.testMethod)
        logging.info("Running Task")

        fakeTaskConfig = {
            'id': 'hyperparameterOptimisation_{}'.format(task.__name__),
            'method': task.__name__
        }
        for param, val in self.paramVals.items():
            fakeTaskConfig[param] = val
        taskConfig = {**self.raw_dict, **fakeTaskConfig}
        result = task(taskConfig).run()

        logging.info("Finished Task")
        resultsPath = self.resultsFilepath
        curResults: list = yaml.safe_load(open(resultsPath)) if os.path.exists(resultsPath) else []
        trialResult = self.paramVals.copy()
        trialResult["result"] = result
        curResults.append(trialResult)
        with open(self.resultsFilepath, "w+") as fp:
            yaml.dump(curResults, fp)
        logging.info("finished hyperparameterTrial")


class HyperparameterEvaluate(TaskWithInitAndValidate):
    resultsFilepath: str
    numberTrials: int  # should be optional?
    optimisationMethod: str
    baseOutputDir: str

    def run(self):
        def logMax(results):
            logging.info(
                "The maximum setting of params found is: {}".format(max(results, key=lambda x: x["result"]))
            )

        resultsPath = self.resultsFilepath
        curResults: list = yaml.safe_load(open(resultsPath)) if os.path.exists(resultsPath) else []

        if self.numberTrials is not None and self.numberTrials == len(curResults):
            logMax(curResults)
            return

        hyperParameterOptimizer, configClass = hyperParameterOptimisationFactory(self.optimisationMethod)
        candidate = hyperParameterOptimizer.getNextTrial(configClass(self.raw_dict), curResults)
        if candidate is None:
            logMax(curResults)
            return
        setupNextConfig(self.raw_dict, self.baseOutputDir, candidate)
