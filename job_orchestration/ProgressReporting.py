import math
import os
from collections import defaultdict
from time import sleep

from .Config import Config
from .Constants import config_ready_location
from .StatusTracker import StatusTracker, predRunTimes
from .workerRegistration import getRunningWorkersCount


def progressReport(workerCount: int):
    inProgress = os.listdir(config_ready_location)
    print("Number in progress", inProgress.__len__())
    cumulativeTimeRemaining = 0
    taskNumberCounter = defaultdict(int)
    for filename in sorted(inProgress):
        try:
            config = Config(os.path.join(config_ready_location, filename))
            status = StatusTracker(config)
            taskNumberCounter[status.current_task] += 1
            remaining = config.tasks if status.current_task is None else config.tasks[status.getCurrentTaskIndex() + 1:]
            timeRemaining = 0
            for t in remaining:
                m, s = predRunTimes[t.id]
                if m is math.nan and s is math.nan:
                    m,s = 0,0 # not great but I don't think there is a whole lot better that can be done for the case where we have no data
                timeRemaining += m*60+s
                cumulativeTimeRemaining += m * 60 + s
        except:
            pass  # Can fail if status of file changes while running.

    for k, v in taskNumberCounter.items():
        print(k, v)

    print("Number of running workers:", workerCount)
    remainingTime = cumulativeTimeRemaining / max(workerCount, 1)
    print("Expected time remaining: {}m{}".format(int(remainingTime // 60), int(remainingTime % 60)))


def continualProgressReport():
    workerCount = 1
    while True:
        workerCountPrev = workerCount
        workerCount = getRunningWorkersCount()
        if workerCount == 0 and workerCountPrev == 0:
            break # if we have two 0s 60s appart then we will stop
        progressReport(workerCount)
        print()
        sleep(60)


if __name__ == "__main__":
    workerCount = getRunningWorkersCount()
    progressReport(workerCount)