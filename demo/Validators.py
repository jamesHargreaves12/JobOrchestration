def test(taskConfig: dict):
    requiredFields = ['x', 'y']
    errors = []
    for field in requiredFields:
        if field not in taskConfig:
            errors.append("The field {} is required but not provided.".format(field))
    return errors
