import os
import shutil
from shutil import copyfile

from job_orchestration.Config import Config
from job_orchestration.Constants import config_failed_location, config_ready_location


def reReadyFailedConfigs():
    for configFilename in os.listdir(config_failed_location):
        configFilepath = os.path.join(config_failed_location, configFilename)
        config = Config(configFilepath)
        shutil.rmtree(config.outputDir)
        copyfile(configFilepath, os.path.join(config_ready_location, configFilename))