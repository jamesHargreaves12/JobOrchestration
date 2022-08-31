from abc import ABCMeta, abstractmethod
from typing import List


class TaskBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, config: dict):
        pass

    @abstractmethod
    def run(self):
        pass

    # intended to be overridden if appropriate
    def validate(self) -> List[str]:
        return []
