import logging
from time import sleep


def test(config: dict):
    for i in range(3):
        sleep(1)
        logging.info("Hello World!")
    x = config["x"]
    y = config["y"]
    return x * x - (y - 2) * (y - 2) - (x * x * x) / 100
