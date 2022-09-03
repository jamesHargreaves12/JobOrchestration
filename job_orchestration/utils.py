from collections import defaultdict, Callable

from git import Repo

overall_cache = defaultdict(dict)


def cached(caller: str, key: str, resolver: Callable):
    cache = overall_cache[caller]
    if key not in cache:
        cache[key] = resolver()
    return cache[key]


def getRepoCached(pathToModuleCode) -> Repo:
    return cached(getRepoCached.__name__, pathToModuleCode, lambda: Repo(pathToModuleCode, search_parent_directories=True))


def isRepoDirtyCached(pathToModuleCode) -> Repo:
    return cached(isRepoDirtyCached.__name__, pathToModuleCode, lambda: getRepoCached(pathToModuleCode).is_dirty())
