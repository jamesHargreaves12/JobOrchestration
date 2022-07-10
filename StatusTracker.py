import logging
import os
from datetime import datetime
from enum import Enum
import dateutil.parser

import yaml
from git import Repo

from Config import Config
from Constants import max_error_count


class Status(Enum):
    READY = 0
    RUNNING_TASK = 1
    FINISHED_TASK = 2
    FAILED_TASK = 3
    COMPLETE = 4
    FAILED = 5


class StatusTracker:
    def __init__(self, config: Config):
        self.config = config
        self.outFilePath = os.path.join(config.outputDir, 'status.yaml')
        if os.path.exists(self.outFilePath):
            vals = yaml.safe_load(open(self.outFilePath))
            self.status = Status[vals['status']]
            self.start_time = dateutil.parser.parse(vals['start_time'])
            self.end_time = dateutil.parser.parse(vals['end_time']) if vals['end_time'] != 'None' else None
            self.orchestrationSha = vals['orchestration_sha']
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
            orchestrationRepo = Repo('.')

            self.orchestrationSha = orchestrationRepo.head.object.hexsha

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
            'orchestration_sha': self.orchestrationSha,
            'current_test_sha': self.currentTestSha,
            'current_job': self.current_task,
            'error_count': self.error_count
        }
