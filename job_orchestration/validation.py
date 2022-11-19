import logging
import sys

from .Config import Config
from .getClientMethods import getTaskByName
from .specialTasks import specialTasks
from .utils import isRepoDirtyCached


def checkGitRepo(config: Config):
    if "UNSAFE_ignoreDirtyCheck" in config.raw_config and config.raw_config["UNSAFE_ignoreDirtyCheck"]:
        logging.warning("Skiping dirty check - these results might not be repeatable")
    else:
        assert not isRepoDirtyCached(config.pathToTasks), \
            "You have uncommitted changes this means that your results will not be easily repeatable."


def validateConfig(config: Config):
    logging.info("Starting Validation")
    validationErrors = config.validate()
    for taskConfig in config.tasks:
        if taskConfig.method is not None:
            if taskConfig.method in specialTasks:
                taskClass = specialTasks[taskConfig.method]
            else:
                taskClass = getTaskByName(config.pathToTasks, taskConfig.method)

            if taskClass is not None:
                task = taskClass(taskConfig.raw_dict)
                logging.info(f"Validating {taskConfig.method}")
                validationResult = task.validate()
                validationErrors.extend(validationResult)

    if validationErrors:
        logging.error("The config file failed validation.")
        for e in validationErrors:
            logging.error(e)
        sys.exit(1)
    logging.info("Finished Validation")
