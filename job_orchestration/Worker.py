import logging
import os
import uuid
from random import choice
from shutil import copyfile
from time import time

import fasteners as fasteners

from .Config import Config
from .Loggers import setUpConsoleLogger, setUpFileLogger, removeFileLogger
from .StatusTracker import StatusTracker, Status, predRunTimes
from .Constants import config_ready_location, config_completed_location, config_failed_location
from .getClientMethods import getTaskByName
from job_orchestration.hypeparameterOptimisation import runHyperparameterOptimization, hyperparameterTrial, \
    hyperparameterEvaluate
from .workerRegistration import registerWorkerStarted, registerWorkerFinished

specialCaseMethods = {
    'runHyperparameterOptimization': runHyperparameterOptimization,
    'hyperparameterTrial': hyperparameterTrial,
    'hyperparameterEvaluate': hyperparameterEvaluate
}


def getNextTask(status: StatusTracker, config: Config):
    assert (status.status in [Status.READY, Status.FINISHED_TASK, Status.FAILED_TASK])
    if status.status == Status.READY:
        return config.tasks[0]

    curIndex = status.getCurrentTaskIndex()

    if status.status == Status.FAILED_TASK:
        return config.tasks[curIndex]

    assert (curIndex < len(config.tasks) - 1)
    return config.tasks[curIndex + 1]


def runWorker():
    setUpConsoleLogger()
    workerId = str(uuid.uuid4())
    registerWorkerStarted(workerId)

    try:
        while True:
            startLoopTime = time()
            candidates = [fn for fn in os.listdir(config_ready_location)]
            if not candidates:
                logging.info("No more Configs to run.")
                break
            filename = choice(candidates)
            filepath = os.path.join(config_ready_location, filename)
            logging.info("Processing: " + filepath)

            config = Config(filepath)

            lock = fasteners.InterProcessLock(os.path.join(config.outputDir, 'lock.file'))
            lock.acquire(blocking=False)
            succeeded = True

            if lock.acquired:
                setUpFileLogger(config)
                status = StatusTracker(config)
                try:
                    # Note that there is a possibility that the config was a candidate but is no longer. However,
                    # the only case that can cause this is if the job has failed / completed in which case it will fail on
                    # next line.
                    taskConfig = getNextTask(status, config)
                    status.setCurrentTask(taskConfig.id)

                    logging.info("getTaskByName " + taskConfig.method)
                    if taskConfig.method in specialCaseMethods:
                        task = specialCaseMethods[taskConfig.method]
                    else:
                        task = getTaskByName(config.pathToModuleCode, taskConfig.method)
                    logging.info("Running Task")
                    taskStartTime = time()
                    task(taskConfig)
                    taskEndTime = time()
                    logging.info("Finished Task")

                    status.finishTask()
                    logging.info("status.finishTask complete")
                except Exception as e:
                    succeeded = False
                    logging.exception(e)
                    if status.status not in [Status.COMPLETE, Status.FAILED]:
                        status.failTask()

                if status.status == Status.COMPLETE:
                    completedFilePath = os.path.join(config_completed_location, filename)
                    logging.info("Moving config from {} to {}".format(filepath, completedFilePath))
                    copyfile(filepath, completedFilePath)
                    os.remove(filepath)
                elif status.status == Status.FAILED:
                    failedFilePath = os.path.join(config_failed_location, filename)
                    logging.info("Moving config from {} to {}".format(filepath, failedFilePath))
                    copyfile(filepath, failedFilePath)
                    os.remove(filepath)

                removeFileLogger()
                lock.release()
                endLoopTime = time()
                if succeeded:
                    logging.info("Loop total time = {:.2f}, task total time = {:.2f} hence library overhead = {:.2f}%"
                                 .format(endLoopTime - startLoopTime, taskEndTime - taskStartTime,
                                         100 - (taskEndTime - taskStartTime) / (endLoopTime - startLoopTime) * 100))
        predRunTimes.save()
    finally:
        registerWorkerFinished(workerId)
