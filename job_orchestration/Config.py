import os
from datetime import datetime
from pathlib import Path
from typing import List

import yaml

from .Constants import output_location
from .configBase import Dict2Class


class MinimalTaskConfig(Dict2Class):
    id: str
    method: str


class Config:
    githubRepository: str
    pathToTasks: str
    overwriteOutputFine: bool
    moduleName: str
    outputDir: Path
    tasks: List[MinimalTaskConfig]

    def __init__(self, configFilePath):
        with open(configFilePath) as fp:
            self.raw_config = yaml.load(fp,yaml.CLoader)

        self.githubRepository = self.raw_config.get('githubRepository', None)
        self.pathToTasks = self.raw_config.get('pathToTasks', None)
        self.overwriteOutputFine = self.raw_config['overwriteOutputFine'] if 'overwriteOutputFine' in self.raw_config else False

        self.moduleName = self.githubRepository.split('/')[-1].split('.')[0]

        self.outputDir = Path(
            getFullOutputDir(self.raw_config['outputDir'])) if 'outputDir' in self.raw_config else None
        self.tasks = [MinimalTaskConfig({**self.raw_config, **taskConfig}) for taskConfig in
                      self.raw_config['tasks']] if 'tasks' in self.raw_config else None

    def writeToLocation(self, location, updateOutputDir):
        to_write = self.raw_config.copy()
        if updateOutputDir:
            to_write['outputDir'] = str(self.outputDir)
        yaml.dump(to_write, open(location, 'w'))

    def validate(self):
        validationErrors = []
        for field in ['outputDir', 'tasks', 'githubRepository', 'pathToTasks']:
            if field not in self.raw_config:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))

        if self.outputDir is not None:
            if os.path.exists(os.path.join(output_location, self.outputDir)) and not self.overwriteOutputFine:
                validationErrors.append("The path {} already exists.".format(self.outputDir))

        #todo check task id unique

        if self.tasks is not None:
            for task in self.tasks:
                validationErrors.extend(["Task({}): {}".format(task.id, err) for err in task.validate()])
        return validationErrors


def getFullOutputDir(rawOutputDir: str):
    path = rawOutputDir.format(date=datetime.now().strftime('%Y_%m_%d'), time=datetime.now().strftime('%H_%M_%S'))
    return os.path.join(output_location, path)


