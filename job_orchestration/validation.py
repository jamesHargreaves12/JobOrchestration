import logging
import sys

from .Config import Config
from .StatusTracker import isRepoDirtyCached
from .getClientMethods import getValidatorByName
from .hypeparameterOptimisation import specialCaseValidators


def checkGitRepo(config: Config):
    if "UNSAFE_ignoreDirtyCheck" in config.raw_config and config.raw_config["UNSAFE_ignoreDirtyCheck"]:
        logging.warning("Skiping dirty check - these results might not be repeatable")
    else:
        assert not isRepoDirtyCached(config.pathToModuleCode), \
            "You have uncommitted changes this means that your results will not be easily repeatable."


def validateConfig(config: Config):
    logging.info("Starting Validation")
    validationErrors = config.validate()
    for taskConfig in config.tasks:
        validationErrors = []
        if taskConfig.method is not None:
            if taskConfig.method in specialCaseValidators:
                validator = specialCaseValidators[taskConfig.method]
            else:
                validator = getValidatorByName(taskConfig.overallConfig.pathToModuleCode, taskConfig.method)
            if validator is not None:
                validationErrors.extend(validator({**config.raw_config, **taskConfig.rawTaskConfig}))

    if validationErrors:
        logging.error("The config file failed validation.")
        for e in validationErrors:
            logging.error(e)
        sys.exit(1)
    logging.info("Finished Validation")
