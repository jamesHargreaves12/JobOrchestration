import logging
import os

from .Config import Config
from .Loggers import setUpConsoleLogger
from .Constants import config_source_location
from .setupOutput import setupOutput
from .validation import checkGitRepo, validateConfig


# This is not intended to be thread safe do not run in parallel.
def SetConfigFilesReady():
    setUpConsoleLogger()
    for filename in os.listdir(config_source_location):
        filepath = os.path.join(config_source_location, filename)
        logging.info("Processing " + filepath)
        config = Config(filepath)
        logging.info("Loaded Config")

        checkGitRepo(config)

        # Validate
        validateConfig(config)

        setupOutput(config, filename)
        os.remove(filepath)
