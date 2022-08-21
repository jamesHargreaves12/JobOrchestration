import os
from collections import defaultdict

from .Config import Config
from .Constants import config_ready_location
from .StatusTracker import StatusTracker, predRunTimes

# Note need to set this to get accurate time remaining - TODO set this automatically
number_of_workers = 3


def progressReport():
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
            for t in remaining:
                m, s = predRunTimes[t.id]
                cumulativeTimeRemaining += m * 60 + s
        except:
            pass  # Can fail if status of file changes while running.

    for k, v in taskNumberCounter.items():
        print(k, v)

    remainingTime = cumulativeTimeRemaining / number_of_workers
    print("Expected time remaining: {}m{}".format(int(remainingTime // 60), int(remainingTime % 60)))
