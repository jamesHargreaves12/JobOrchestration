import sys
from typing import Callable

from job_orchestration.TaskBase import TaskBase

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


def getTaskByName(pathToModuleCode, name) -> Callable[[dict],TaskBase]:
    Tasks = getTasks(pathToModuleCode)
    return getattr(Tasks, name)
