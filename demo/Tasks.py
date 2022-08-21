import logging
from time import sleep


def test(config):
    for i in range(10):
        sleep(1)
        logging.info("Hello World!")