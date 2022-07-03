import os
from pathlib import Path

import yaml

requiredFields = ['outputDir', 'jobs','githubRepository']
jobRequiredFields = ['id', 'task']
NOT_GIVEN = 'NOT_GIVEN'


class JobConfig:
    def __init__(self, jobConfig, overallConfig):
        self.id = jobConfig.get('id', None)
        self.task = jobConfig.get('task', None)
        self.jobConfig = jobConfig
        self.overallConfig = overallConfig

    def validate(self, jobValidators):
        validationErrors = []
        for field in jobRequiredFields:
            if field not in self.jobConfig:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))
        if self.task is not None:
            if hasattr(jobValidators, self.task):
                validationErrors.extend(getattr(jobValidators, self.task)(self.jobConfig, self.overallConfig))
        return validationErrors


class Config:
    def __init__(self, configFilePath):
        with open(configFilePath) as fp:
            self.raw_config = yaml.safe_load(fp)

        self.githubRepository = self.raw_config.get('githubRepository', None) # todo perhaps it make sense for this to be a different config object?
        self.moduleName = self.githubRepository.split('/')[-1].split('.')[0]
        self.pathToModuleCode = "./testModules/"+self.moduleName

        self.outputDir = Path(self.raw_config['outputDir']) if 'outputDir' in self.raw_config else None
        self.jobs = [JobConfig(jobConfig, self) for jobConfig in
                     self.raw_config['jobs']] if 'jobs' in self.raw_config else None

    def validate(self, jobValidators):
        validationErrors = []
        for field in requiredFields:
            if field not in self.raw_config:
                validationErrors.append("The '{}' attribute is required but not present.".format(field))

        if self.outputDir is not None:
            if os.path.exists(self.outputDir):
                validationErrors.append("The path {} already exists.".format(self.outputDir))

            if not os.path.exists(self.outputDir.parent):
                validationErrors.append("The parent of {} doesn't exist.".format(self.outputDir))

        if self.jobs is not None:
            for job in self.jobs:
                validationErrors.extend(["Job({}): {}".format(job.id, err) for err in job.validate(jobValidators)])
        return validationErrors
