import logging
import os
import shutil
from shutil import copyfile

from .Config import Config
from .StatusTracker import StatusTracker
from .Constants import config_ready_location, config_yaml


def setupOutput(config: Config, configFilename: str):
    logging.info("Creating output Dir " + str(config.outputDir))
    if config.overwriteOutputFine and os.path.exists(config.outputDir):
        shutil.rmtree(config.outputDir)
    os.makedirs(config.outputDir)
    logging.info("Created Directory")

    # Should catch above and move to a failed location.
    updatedConfigLocation = os.path.join(config_ready_location, configFilename)
    config.writeToLocation(updatedConfigLocation, updateOutputDir=True)

    logging.info("config written")
    status = StatusTracker(config)
    logging.info("Status setup")
    copyfile(updatedConfigLocation, os.path.join(config.outputDir, config_yaml))
    logging.info("Initialization complete")
