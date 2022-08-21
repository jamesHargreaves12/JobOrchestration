import logging
from time import sleep


def test():
    for i in range(10):
        sleep(1000)
        logging.info("Hello World!")