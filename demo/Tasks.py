import logging
from time import sleep

from job_orchestration.TaskBase import TaskBase


class Test(TaskBase):
    def __init__(self, config: dict):
        self.config = config

    def run(self):
        for i in range(3):
            sleep(1)
            logging.info("Hello World!")
        x = self.config["x"]
        y = self.config["y"]
        return x * x - (y - 2) * (y - 2) - (x * x * x) / 100

    def validate(self: dict):
        requiredFields = ['x', 'y']
        errors = []
        for field in requiredFields:
            if field not in self:
                errors.append("The field {} is required but not provided.".format(field))
        return errors
