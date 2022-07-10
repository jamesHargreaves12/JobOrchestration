import logging
import os
import sys
from random import choice
from shutil import copyfile
import InBuiltUtilityTasks
import fasteners as fasteners

from Config import Config, TaskSpecificConfig
from Loggers import setUpConsoleLogger, setUpFileLogger, removeFileLogger
from StatusTracker import StatusTracker, Status
from Constants import config_ready_location, config_completed_location, config_failed_location


def getNextTask(status: StatusTracker, config: Config):
    assert (status.status in [Status.READY, Status.FINISHED_TASK, Status.FAILED_TASK])
    if status.status == Status.READY:
        return config.tasks[0]

    curIndex = status.getCurrentTaskIndex()

    assert (curIndex < len(config.tasks) - 1)
    return config.tasks[curIndex + 1]


def runTask(config: Config, task:TaskSpecificConfig):
    if task.method == 'createConfigs':
        InBuiltUtilityTasks.createConfigs(config,task)
    sys.path.append(config.pathToModuleCode)
    import Tasks
    sys.path.remove(config.pathToModuleCode)

    getattr(Tasks, task.method)(config.raw_config, task.rawTaskConfig)


setUpConsoleLogger()
candidates = [fn for fn in os.listdir(config_ready_location)]

while True:
    candidates = [fn for fn in os.listdir(config_ready_location)]
    if not candidates:
        break
    filename = choice(candidates)
    filepath = os.path.join(config_ready_location, filename)
    logging.info("Processing: " + filepath)

    config = Config(filepath)

    lock = fasteners.InterProcessLock(os.path.join(config.outputDir, 'lock.file'))
    lock.acquire(blocking=False)

    if lock.acquired:
        setUpFileLogger(config)
        status = StatusTracker(config)
        try:
            # Note that there is a possibility that the config was a candidate but is no longer. However,
            # the only case that can cause this is if the job has failed / completed in which case it will fail on
            # next line.
            task = getNextTask(status, config)
            status.setCurrentTask(task.id)
            runTask(config, task)
            status.finishTask()
        except Exception as e:
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

