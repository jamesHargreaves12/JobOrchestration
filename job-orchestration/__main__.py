import argparse
import os
from .Constants import config_source_location, config_ready_location, config_completed_location, config_failed_location, config_free_parking_location, misc_location


def __setupDirectoryStructure():
    requiredLocations = [config_source_location, config_ready_location, config_completed_location, config_failed_location, config_free_parking_location, misc_location]
    for loc in requiredLocations:
        if not os.path.exists(loc):
            os.makedirs(loc)


def newWorker():
    from .Worker import runWorker
    runWorker()


def readyConfigs():
    from .SetConfigFilesReady import SetConfigFilesReady
    SetConfigFilesReady()


def progressReport():
    from .ProgressReporting import progressReport
    progressReport()


actions = [newWorker, readyConfigs, progressReport]

parser = argparse.ArgumentParser()
parser.add_argument("-action",  type=str, required=True)
args = parser.parse_known_args()[0]
actionId = args.action.lower()
for action in actions:
    if action.__name__.lower() == actionId:
        __setupDirectoryStructure()
        action()
        break
else:
    raise Exception("-action must be in following list " + str([x.__name__ for x in actions]))
