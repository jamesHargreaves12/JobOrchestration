from typing import List

from job_orchestration.configBase import Dict2Class
from job_orchestration.hyperparameter_optimisation.base import HyperParameterOptimisationBase


class Param(Dict2Class):
    name: int
    type: str  # can be stricter.


class FloatParam(Param):
    min: int
    max: int


class ListParam(Param):
    vals: list


class GridOptimizationConfig(Dict2Class):
    gridLineCount: int
    params: List[Param]

    def __init__(self, input_dict: dict):
        super().__init__(input_dict)
        self.params = [FloatParam(p) if p['type'] == 'float' else ListParam(p) for p in input_dict['params']]


class GridSearch(HyperParameterOptimisationBase):
    def getNextTrial(self, config: GridOptimizationConfig, results: list):
        toTry = {}
        gridLineCount = config.gridLineCount  # per config?
        for param in config.params:
            if param.type == "float":
                param: FloatParam
                start = param.min
                end = param.max
                step = (end - start) / (gridLineCount - 1)
                toTry[param.name] = [start + i * step for i in range(gridLineCount)]
            elif param.type == "list":
                param: ListParam
                toTry[param.name] = param.vals
        paramIndex = 0
        choices = {}
        while paramIndex < len(config.params):
            name = config.params[paramIndex].name
            if name not in choices:
                choices[name] = 0
            else:
                choices[name] += 1

            if choices[name] == len(toTry[name]):  # no more choices at this level, backtrack
                del choices[name]
                paramIndex -= 1
                continue

            if paramIndex + 1 < len(config.params):  # haven't got a value for all params yet
                paramIndex += 1
                continue

            candidate = {}
            for param in config.params:
                candidate[param.name] = toTry[param.name][choices[param.name]]
            inResults = False
            for res in results:
                match = all(candidate[p.name] == res[p.name] for p in config.params)
                if match:
                    inResults = True
                    break
            if not inResults:
                return candidate

            if all(choices[p.name] + 1 == len(toTry[p.name]) for p in config.params):  # at end of possible values
                return


if __name__ == "__main__":
    results1 = [
        {'x': 1, 'y': 'a'},
        {'x': 1, 'y': 'b'},
        {'x': 1, 'y': 'c'},
    ]
    config1 = {
        'gridLineCount': 3,
        'params': [
            {'name': 'x', 'type': 'float', 'min': 1, 'max': 3},
            {'name': 'y', 'type': 'list', 'vals': ['a', 'b', 'c']}
        ]
    }

    grid = GridSearch()
    print(grid.getNextTrial(GridOptimizationConfig(config1), results1))
