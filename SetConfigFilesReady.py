import logging
import os
import shutil
import sys
from shutil import copyfile

from Config import Config
from Loggers import setUpConsoleLogger
from SetupTaskRepo import setupGit
from StatusTracker import StatusTracker
from Constants import config_source_location, config_ready_location

setUpConsoleLogger()

# This is not intended to be thread safe do not run in parallel.
for filename in os.listdir(config_source_location):
    filepath = os.path.join(config_source_location, filename)
    logging.info("Processing " + filepath)
    config = Config(filepath)

    setupGit(config)

    # This is kinda horrible but I don't know a better way round the problem of wanting to run sub-packages independently
    # some times
    sys.path.append(config.pathToModuleCode)
    import Validators
    sys.path.remove(config.pathToModuleCode)

    # Validate
    logging.info("Starting Validation")
    validationErrors = config.validate(Validators)
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
    copyfile(updatedConfigLocation, os.path.join(config.outputDir, 'config.yaml'))
    logging.info("Initialization complete")

    os.remove(filepath)
