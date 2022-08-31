import logging
import os
import shutil
import sys
from shutil import copyfile

from .Config import Config
from .Loggers import setUpConsoleLogger
from .StatusTracker import StatusTracker, isRepoDirtyCached
from .Constants import config_source_location, config_ready_location, config_yaml
from .getClientMethods import getValidatorByName


def setConfigReady(filename: str, specialCaseValidators: dict):
    filepath = os.path.join(config_source_location, filename)
    logging.info("Processing " + filepath)
    config = Config(filepath)

    logging.info("Loaded Config")
    if "UNSAFE_ignoreDirtyCheck" in config.raw_config and config.raw_config["UNSAFE_ignoreDirtyCheck"]:
        logging.warning("Skiping dirty check - these results might not be repeatable")
    else:
        assert not isRepoDirtyCached(config.pathToModuleCode), \
            "You have uncommitted changes this means that your results will not be easily repeatable."

    # Validate
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
                validationErrors.extend(validator(taskConfig))

    if validationErrors:
        logging.error("The config file failed validation.")
        for e in validationErrors:
            logging.error(e)
        sys.exit(1)
    logging.info("Finished Validation")

    logging.info("Creating output Dir " + str(config.outputDir))
    if config.overwriteOutputFine and os.path.exists(config.outputDir):
        shutil.rmtree(config.outputDir)
    os.makedirs(config.outputDir)
    logging.info("Created Directory")

    # Should catch above and move to a failed location.
    updatedConfigLocation = os.path.join(config_ready_location, filename)
    config.writeToLocation(updatedConfigLocation, updateOutputDir=True)

    logging.info("config written")
    status = StatusTracker(config)
    logging.info("Status setup")
    copyfile(updatedConfigLocation, os.path.join(config.outputDir, config_yaml))
    logging.info("Initialization complete")

    os.remove(filepath)


# This is not intended to be thread safe do not run in parallel.
def SetConfigFilesReady(taskConfig):
    setUpConsoleLogger()
    for filename in os.listdir(config_source_location):
        setConfigReady(filename, taskConfig)
