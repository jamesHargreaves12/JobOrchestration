from abc import ABCMeta, abstractmethod


class HyperParameterOptimisationBase(metaclass=ABCMeta):
    @abstractmethod
    def getNextTrial(self, config: object, results: list):
        pass
