import logging
import os

from .Config import Config
from .Constants import output_location


def setUpConsoleLogger():
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)


def setUpFileLogger(config: Config):
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(os.path.join(output_location, config.outputDir, "log.log"))
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


def removeFileLogger():
    rootLogger = logging.getLogger()
    fileHandlers = [x for x in rootLogger.handlers if isinstance(x, logging.FileHandler)]
    assert len(fileHandlers) == 1
    rootLogger.removeHandler(fileHandlers[0])
