import os
from time import time
from typing import Callable

import fasteners
import yaml

from job_orchestration.Constants import misc_location

workers_registration_path = os.path.join(misc_location, "workers.yaml")


def updateRegistrationFile(transform: Callable[[dict], dict]):
    lock = fasteners.InterProcessLock(os.path.join(misc_location, 'lock.file'))
    lock.acquire(blocking=True)
    if lock.acquired:
        workersRegistration = {}
        if os.path.exists(workers_registration_path):
            workersRegistration = yaml.safe_load(open(workers_registration_path))
        workersRegistration = transform(workersRegistration)
        yaml.dump(workersRegistration, open(workers_registration_path, "w"))
        lock.release()


def registerWorkerStarted(workerId: str):
    def addWorker(registrationState: dict):
        registrationState[workerId] = time()
        return registrationState

    updateRegistrationFile(addWorker)


def registerWorkerFinished(workerId: str):
    def removeWorker(registrationState: dict):
        del registrationState[workerId]
        return registrationState

    updateRegistrationFile(removeWorker)


def getRunningWorkersCount():
    workerRegistration = {}
    if os.path.exists(workers_registration_path):
        workerRegistration = yaml.safe_load(workers_registration_path)
    return len(workerRegistration)
