from job_orchestration.Config import TaskConfig


def test(taskConfig:TaskConfig):
    requiredFields = ['x','y']
    errors = []
    for field in requiredFields:
        if field not in taskConfig:
            errors.append("The field {} is required but not provided.".format(field))
    return errors
