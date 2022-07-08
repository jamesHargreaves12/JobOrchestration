import os
from pathlib import Path

import yaml

requiredFields = ['outputDir', 'tasks', 'githubRepository']
taskRequiredFields = ['id', 'method']


class TaskSpecificConfig:
    def __init__(self, taskConfig, overallConfig):
        self.id = taskConfig.get('id', None)
        self.method = taskConfig.get('method', None)
        self.rawTaskConfig = taskConfig
        self.overallConfig = overallConfig

    def validate(self, taskValidators):
        validationErrors = []
        for field in taskRequiredFields:
            if field not in self.rawTaskConfig:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))
        if self.method is not None:
            if hasattr(taskValidators, self.method):
                validationErrors.extend(getattr(taskValidators, self.method)(self.overallConfig.raw_config, self.rawTaskConfig))
        return validationErrors


class Config:
    def __init__(self, configFilePath):
        with open(configFilePath) as fp:
            self.raw_config = yaml.safe_load(fp)

        self.githubRepository = self.raw_config.get('githubRepository',
                                                    None)  # todo perhaps it make sense for this to be a different config object?
        self.moduleName = self.githubRepository.split('/')[-1].split('.')[0]
        self.pathToModuleCode = "./testModules/" + self.moduleName

        self.outputDir = Path(self.raw_config['outputDir']) if 'outputDir' in self.raw_config else None
        self.tasks = [TaskSpecificConfig(taskConfig, self) for taskConfig in
                     self.raw_config['tasks']] if 'tasks' in self.raw_config else None

    def validate(self, taskValidators):
        validationErrors = []
        for field in requiredFields:
            if field not in self.raw_config:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))

        if self.outputDir is not None:
            if os.path.exists(self.outputDir):
                validationErrors.append("The path {} already exists.".format(self.outputDir))

            if not os.path.exists(self.outputDir.parent):
                validationErrors.append("The parent of {} doesn't exist.".format(self.outputDir))

        if self.tasks is not None:
            for task in self.tasks:
                validationErrors.extend(["Task({}): {}".format(task.id, err) for err in task.validate(taskValidators)])
        return validationErrors
