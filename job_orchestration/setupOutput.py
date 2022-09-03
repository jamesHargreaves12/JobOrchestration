import logging
import os
import shutil
from shutil import copyfile

from .Config import Config
from .StatusTracker import StatusTracker
from .Constants import config_ready_location, config_yaml, output_location


def setupOutput(config: Config, configFilename: str):
    outputPath = os.path.join(output_location, config.outputDir)
    logging.info("Creating output Dir " + str(outputPath))
    if config.overwriteOutputFine and os.path.exists(outputPath):
        shutil.rmtree(outputPath)
    os.makedirs(outputPath)
    logging.info("Created Directory")

    # Should catch above and move to a failed location.
    updatedConfigLocation = os.path.join(config_ready_location, configFilename)
    config.writeToLocation(updatedConfigLocation, updateOutputDir=True)

    logging.info("config written")
    status = StatusTracker(config)
    logging.info("Status setup")
    copyfile(updatedConfigLocation, os.path.join(outputPath, config_yaml))
    logging.info("Initialization complete")
