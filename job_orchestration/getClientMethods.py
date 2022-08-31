import sys
from typing import Callable, NoReturn

modulesCache = {}


# This is kinda horrible but I don't know a better way round the problem of wanting to be able to pull in functions
# by name from another code base. At least it is isolated to this file.

def cached(key, resolver: Callable):
    if key in modulesCache:
        return modulesCache[key]
    module = resolver()
    modulesCache[key] = module
    return module


def getTasks(pathToModuleCode):
    def getTasksModule():
        sys.path.append(pathToModuleCode)
        import Tasks
        sys.path.remove(pathToModuleCode)
        return Tasks

    return cached("Tasks_" + pathToModuleCode, getTasksModule)


def getValidators(pathToModuleCode) -> Callable[[dict], list]:
    def getValidatorsFromModule():
        sys.path.append(pathToModuleCode)
        import Validators
        sys.path.remove(pathToModuleCode)
        return Validators

    return cached("Validators_" + pathToModuleCode, getValidatorsFromModule)


def getTaskByName(pathToModuleCode, name) -> Callable[[dict], NoReturn]:
    Tasks = getTasks(pathToModuleCode)
    return getattr(Tasks, name)


def getValidatorByName(pathToModuleCode, name):
    Validators = getValidators(pathToModuleCode)
    if not hasattr(Validators, name):
        return None
    return getattr(Validators, name)
