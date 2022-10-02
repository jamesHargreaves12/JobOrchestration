import os
import shutil

from job_orchestration.Config import Config
from job_orchestration.Constants import config_failed_location, config_ready_location, output_location


def reReadyFailedConfigs():
    for configFilename in os.listdir(config_failed_location):
        configFilepath = os.path.join(config_failed_location, configFilename)
        config = Config(configFilepath)
        shutil.rmtree(os.path.join(output_location, config.outputDir))
        config_ready_path = os.path.join(config_ready_location, configFilename)
        shutil.move(configFilepath, config_ready_path)
        os.makedirs(os.path.join(output_location, config.outputDir))
        shutil.copyfile(config_ready_path, os.path.join(output_location, config.outputDir, configFilename))
