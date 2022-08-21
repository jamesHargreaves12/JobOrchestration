import argparse
import os
from .Constants import config_source_location, config_ready_location, config_completed_location, config_failed_location, \
    misc_location


def __setupDirectoryStructure():
    requiredLocations = [config_source_location, config_ready_location, config_completed_location,
                         config_failed_location, misc_location]
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


def rereadyFailed():
    from .rereadyFailedConfigs import reReadyFailedConfigs
    reReadyFailedConfigs()


actions = [newWorker, readyConfigs, progressReport,rereadyFailed]

parser = argparse.ArgumentParser()
parser.add_argument("-action", type=str)
args = parser.parse_known_args()[0]
if "action" in args and args.action is not None:
    actionId = args.action.lower()
else:
    print("Which action would you like to perform?")
    for i,act in enumerate(actions):
        print("    {}: {}".format(i,act.__name__))
    userInput = input()
    if str.isdigit(userInput):
        actionId = actions[int(userInput)].__name__.lower()
    else:
        actionId = userInput.lower()


for action in actions:
    if action.__name__.lower() == actionId:
        __setupDirectoryStructure()
        action()
        break
else:
    raise Exception("-action must be in following list " + str([x.__name__ for x in actions]))
