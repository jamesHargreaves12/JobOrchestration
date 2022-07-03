def train(jobConfig, taskConfig):
    requiredJobConfigFields = ['trainData']
    errors = []
    for field in requiredJobConfigFields:
        if field not in jobConfig:
            errors.append("The field {} is required but not provided.".format(field))
    return errors
