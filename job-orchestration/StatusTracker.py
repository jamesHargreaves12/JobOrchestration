import logging
import os
from datetime import datetime
from enum import Enum
from random import random

import dateutil.parser
import math

import fasteners
import yaml
from git import Repo
from importlib_metadata import version

from .Config import Config
from .Constants import max_error_count, misc_location


class Status(Enum):
    READY = 0
    RUNNING_TASK = 1
    FINISHED_TASK = 2
    FAILED_TASK = 3
    COMPLETE = 4
    FAILED = 5


class PredRunTimes:
    pred_run_times = {}
    alpha = 0.25
    filepath = os.path.join(misc_location, 'pred_run_times.yaml')

    def __init__(self):
        if not os.path.exists(self.filepath):
            return
        obj = yaml.load(open(self.filepath, 'r'), yaml.CLoader)
        for key in obj.keys():
            self.pred_run_times[key] = obj[key]

    def save(self):
        lock = fasteners.InterProcessLock(os.path.join(misc_location, 'lock.file'))
        lock.acquire(blocking=False)  # missing an update is not the end of the world.
        if lock.acquired:
            toWrite = self.pred_run_times.copy()
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as fp:
                    obj = yaml.load(fp, yaml.CLoader)
                    for k, v in obj.items():
                        if k in toWrite:
                            toWrite[k] = v * (1 - self.alpha) + toWrite[k] * self.alpha
                        else:
                            toWrite[k] = v
            with open(self.filepath, 'w+') as fp:
                yaml.dump(toWrite, fp)
            lock.release()

    def update(self, name, value):
        if name in self.pred_run_times:
            self.pred_run_times[name] = self.pred_run_times[name] * (1 - self.alpha) + value * self.alpha
        else:
            self.pred_run_times[name] = value
        if random() < 0.05:
            self.save()

    def __getitem__(self, item):
        if item in self.pred_run_times:
            val = self.pred_run_times[item]
            return math.floor(val / 60), round(val % 60)
        else:
            return math.nan, math.nan


# just basically want a singleton here - kinda jank but works for now
predRunTimes = PredRunTimes()
class StatusTracker:
    def __init__(self, config: Config):
        self.config = config
        self.outFilePath = os.path.join(config.outputDir, 'status.yaml')
        if os.path.exists(self.outFilePath):
            with open(self.outFilePath) as fp:
                vals = yaml.load(fp, yaml.CLoader)
            self.status = Status[vals['status']]
            self.start_time = dateutil.parser.parse(vals['start_time'])
            self.end_time = dateutil.parser.parse(vals['end_time']) if vals['end_time'] != 'None' else None
            self.orchestrationVersion = vals['orchestration_version']
            self.currentTestSha = vals['current_test_sha']
            self.current_task = vals['current_job']
            self.last_updated = dateutil.parser.parse(vals['last_updated'])
            self.error_count = vals['error_count']
            # TODO check matches current state of play + only what should be null is.
        else:
            self.status = Status.READY
            self.start_time = datetime.now()
            self.current_task = None
            self.end_time = None
            self.last_updated = self.start_time
            self.error_count = 0

            testRepo = Repo(config.pathToModuleCode)
            self.currentTestSha = testRepo.head.object.hexsha

            self.orchestrationVersion = version('job-orchestration')

            self.flush()

    def getCurrentTaskIndex(self):
        currentTaskIndecies = [i for i, t in enumerate(self.config.tasks) if t.id == self.current_task]
        assert (len(currentTaskIndecies) == 1)
        return currentTaskIndecies[0]

    def setCurrentTask(self, task_id):
        logging.info("Running task with id: " + task_id)
        self.status = Status.RUNNING_TASK
        self.current_task = task_id
        self.last_updated = datetime.now()
        self.flush()

    def finishTask(self):
        # hmm this could probably be done in a less fragile way.
        if self.status == Status.RUNNING_TASK:
            totalTime = datetime.now()-self.last_updated
            predRunTimes.update(self.current_task, totalTime.total_seconds())

        logging.info("Finishing task with id: " + self.current_task)
        if self.getCurrentTaskIndex() == len(self.config.tasks) - 1:
            self._finishJob()
            return
        self.error_count = 0
        self.status = Status.FINISHED_TASK
        self.last_updated = datetime.now()
        self.flush()

    def failTask(self):
        logging.warning("Setting Task status as failed: " + self.current_task)
        self.error_count += 1

        if self.error_count >= max_error_count:
            self._failJob()
            return
        self.status = Status.FAILED_TASK
        self.last_updated = datetime.now()
        self.flush()

    def _failJob(self):
        logging.error("Job has Failed!")
        self.status = Status.FAILED
        self.last_updated = datetime.now()
        self.flush()

    def _finishJob(self):
        logging.info("Job is finished!")
        self.status = Status.COMPLETE
        self.last_updated = datetime.now()
        self.end_time = datetime.now()
        self.flush()

    def flush(self):
        logging.info("Flushing status file.")
        with open(self.outFilePath, 'w+') as fp:
            yaml.dump(self.getOutput(), fp)

    def getOutput(self):
        return {
            'status': self.status.name,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'last_updated': str(self.last_updated),
            'orchestration_version': self.orchestrationVersion,
            'current_test_sha': self.currentTestSha,
            'current_job': self.current_task,
            'error_count': self.error_count
        }
