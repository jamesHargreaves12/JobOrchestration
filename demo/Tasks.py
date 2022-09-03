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
        result = x * x - (y - 2) * (y - 2) - (x * x * x) / 100
        logging.info("The result is {}".format(result))
        return result

    def validate(self):
        requiredFields = ['x', 'y']
        errors = []
        for field in requiredFields:
            if field not in self.config:
                errors.append("The field {} is required but not provided.".format(field))
        return errors
