import os.path
import sys

import yaml

from .Config import Config, TaskSpecificConfig
from .Constants import config_free_parking_location


def createConfigs(config: Config, task: TaskSpecificConfig):
    sys.path.append(config.pathToModuleCode)
    import Tasks
    sys.path.remove(config.pathToModuleCode)

    configs: dict = getattr(Tasks, 'createConfigs')(config.raw_config, task.rawTaskConfig)

    for filename, c in configs.items():
        yaml.dump(c, open(os.path.join(config_free_parking_location, filename),'w+'))
