import logging
from time import sleep

from job_orchestration.Config import TaskConfig


def test(config: TaskConfig):
    for i in range(3):
        sleep(1)
        logging.info("Hello World!")
    x = config["x"]
    y = config["y"]
    return x * x - (y - 2) * (y - 2) - (x * x * x) / 100
