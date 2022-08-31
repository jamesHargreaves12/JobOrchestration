import os
from datetime import datetime
from pathlib import Path

import yaml

from .Constants import output_location

requiredFields = ['outputDir', 'tasks', 'githubRepository']
taskRequiredFields = ['id', 'method']


class Config:
    def __init__(self, configFilePath):
        with open(configFilePath) as fp:
            self.raw_config = yaml.load(fp,yaml.CLoader)

        self.githubRepository = self.raw_config.get('githubRepository',
                                                    None)  # todo perhaps it make sense for this to be a different config object?
        self.moduleName = self.githubRepository.split('/')[-1].split('.')[0]
        self.pathToModuleCode = self.raw_config.get('pathToModuleCode',None)

        self.outputDir = Path(
            getFullOutputDir(self.raw_config['outputDir'])) if 'outputDir' in self.raw_config else None
        self.overwriteOutputFine = self.raw_config['overwriteOutputFine'] if 'overwriteOutputFine' in self.raw_config else False
        self.tasks = [TaskConfig(taskConfig, self) for taskConfig in
                      self.raw_config['tasks']] if 'tasks' in self.raw_config else None

    def __getitem__(self, item):
        return self.raw_config[item]

    def writeToLocation(self, location, updateOutputDir):
        to_write = self.raw_config.copy()
        if updateOutputDir:
            to_write['outputDir'] = str(self.outputDir)
        yaml.dump(to_write, open(location, 'w'))

    def validate(self):
        validationErrors = []
        for field in requiredFields:
            if field not in self.raw_config:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))

        if self.outputDir is not None:
            if os.path.exists(self.outputDir) and not self.overwriteOutputFine:
                validationErrors.append("The path {} already exists.".format(self.outputDir))

        #todo check task id unique

        if self.tasks is not None:
            for task in self.tasks:
                validationErrors.extend(["Task({}): {}".format(task.id, err) for err in task.validate()])
        return validationErrors


class TaskConfig:
    def __init__(self, taskConfig, overallConfig: Config):
        self.id = taskConfig.get('id', None)
        self.method = taskConfig.get('method', None) # todo rename to name
        self.rawTaskConfig = taskConfig
        self.overallConfig = overallConfig

    def __getitem__(self, item):
        if item in self.rawTaskConfig:
            return self.rawTaskConfig[item]
        return self.overallConfig[item]

    def __contains__(self, item):
        return item in self.rawTaskConfig or item in self.overallConfig.raw_config

    def validate(self):
        validationErrors = []
        for field in taskRequiredFields:
            if field not in self.rawTaskConfig:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))
        return validationErrors


def getFullOutputDir(rawOutputDir: str):
    path = rawOutputDir.format(date=datetime.now().strftime('%Y_%m_%d'), time=datetime.now().strftime('%H_%M_%S'))
    return os.path.join(output_location, path)


