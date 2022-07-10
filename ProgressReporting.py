import os
from collections import defaultdict

from Config import Config
from Constants import config_ready_location
from StatusTracker import StatusTracker

inProgress = os.listdir(config_ready_location)
print("Number in progress", inProgress.__len__())
taskNumberCounter = defaultdict(int)
for filename in sorted(inProgress):
    try:
        config = Config(os.path.join(config_ready_location, filename))
        status = StatusTracker(config)
        taskNumberCounter[status.current_task] += 1
    except:
        pass  # Can fail if status of file changes while running.

for k, v in taskNumberCounter.items():
    print(k, v)
