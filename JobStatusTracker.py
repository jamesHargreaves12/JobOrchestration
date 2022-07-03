import os
from datetime import datetime
from enum import Enum

import yaml


class Status(Enum):
    RUNNING = 1
    FINISHED = 2
    FAILED = 3


class JobStatusTracker:
    def __init__(self, config):
        self.config = config
        self.status = Status.RUNNING
        self.start_time = datetime.now()
        self.current_job = None
        self.end_time = None
        self.outFilePath = os.path.join(config.outputDir, 'status.yaml')
        self.flush()

    def setCurrentJob(self, jobId):
        self.current_job = jobId

    def finishJob(self):
        self.status = Status.FINISHED
        self.end_time = datetime.now()
        self.flush()

    def flush(self):
        with open(self.outFilePath, 'w+') as fp:
            yaml.dump(self.getOutput(), fp)

    def getOutput(self):
        return {
            'status': self.status.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'current_job': self.current_job
        }
