import logging
import os
import shutil
import sys
from shutil import copyfile

from git import Repo

from .Config import Config
from .Loggers import setUpConsoleLogger
from .StatusTracker import StatusTracker
from .Constants import config_source_location, config_ready_location, config_yaml


# This is not intended to be thread safe do not run in parallel.


def SetConfigFilesReady():
    setUpConsoleLogger()
    for filename in os.listdir(config_source_location):
        filepath = os.path.join(config_source_location, filename)
        logging.info("Processing " + filepath)
        config = Config(filepath)

        assert not Repo(config.pathToModuleCode).is_dirty(), \
            "You have uncommitted changes this means that your results will not be easily repeatable."

        # Validate
        logging.info("Starting Validation")
        validationErrors = config.validate()
        if validationErrors:
            logging.error("The config file failed validation.")
            for e in validationErrors:
                logging.error(e)
            sys.exit(1)
        logging.info("Finished Validation")

        logging.info("Creating output Dir " + str(config.outputDir))
        if os.path.exists(config.outputDir) and config.overwriteOutputFine:
            shutil.rmtree(config.outputDir)
        os.makedirs(config.outputDir)

        # Should catch above and move to a failed location.
        updatedConfigLocation = os.path.join(config_ready_location, filename)
        config.writeToLocation(updatedConfigLocation, updateOutputDir=True)

        status = StatusTracker(config)
        copyfile(updatedConfigLocation, os.path.join(config.outputDir, config_yaml))
        logging.info("Initialization complete")

        os.remove(filepath)
