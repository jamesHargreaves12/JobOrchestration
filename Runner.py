import argparse
import logging
import os
import sys
from shutil import copyfile

from Config import Config
from JobStatusTracker import JobStatusTracker
from Loggers import setupConsoleLogger, setUpFileLogger

parser = argparse.ArgumentParser()
parser.add_argument("-path", help="Path to config file that controls execution", type=str)
args = parser.parse_args()

config = Config(args.path)

# This is kinda horrible but I don't know a better way round the problem of wanting to run sub-packages independently
# some times
sys.path.append(config.pathToModuleCode)
import Tasks
import Validators

setupConsoleLogger()


# Validate
logging.info("Starting Validation")
validationErrors = config.validate(Validators)
if validationErrors:
    logging.error("The config file failed validation.")
    for e in validationErrors:
        logging.error(e)
    sys.exit(1)
logging.info("Finished Validation")


os.mkdir(config.outputDir)
setUpFileLogger(config)


status = JobStatusTracker(config)
copyfile(args.path, os.path.join(config.outputDir, 'config.yaml'))
logging.info("Initialization complete")

# Run - todo make this separate executions?
for job in config.jobs:
    logging.info("Running job with name: " + job.id)
    status.setCurrentJob(job.id)
    getattr(Tasks, job.task)(config, job)
logging.info("Finished")
status.finishJob()
