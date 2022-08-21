import os
from typing import Callable

import yaml

from .Constants import output_location, config_yaml, config_source_location
from .Config import Config
from .StatusTracker import StatusTracker


# Assumption is that the results will always be a yaml file.
def getResults(
        resultsFilename='results.yaml',
        configFilter: Callable[[Config], bool] = None,
        statusFilter: Callable[[StatusTracker], bool] = None):
    results = []
    for path, subdirs, files in os.walk(output_location):
        for name in files:
            if name == resultsFilename:
                config = Config(os.path.join(path, config_yaml))

                if configFilter is not None:
                    if not configFilter(config):
                        continue

                if statusFilter is not None:
                    status = StatusTracker(config)
                    if not statusFilter(status):
                        continue

                results.append(yaml.safe_load(open(os.path.join(path, name))))
    return results


# Simple method to just save a name -> obj dictionary into a set of config files in the correct location
def saveConfigs(configs: dict):
    for filename, c in configs.items():
        yaml.dump(c, open(os.path.join(config_source_location, filename), 'w+'))
