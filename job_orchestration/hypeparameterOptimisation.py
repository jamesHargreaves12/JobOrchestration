from .hyperparameter_optimisation.hypeparamaterOptimisationMethods import HyperParameterTrialConfig, \
    __hyperparameterTrial, StartHyperparameterOptimizationConfig, __runHyperparameterOptimization, \
    HyperparameterEvaluateConfig, __hyperparameterEvaluate


def runHyperparameterOptimization(config: dict):
    __runHyperparameterOptimization(StartHyperparameterOptimizationConfig(config))


def validate_runHyperparameterOptimization(config: dict):
    return StartHyperparameterOptimizationConfig(config).validate()


def hyperparameterTrial(config: dict):
    __hyperparameterTrial(HyperParameterTrialConfig(config))


def validate_hyperparameterTrial(config: dict):
    return HyperParameterTrialConfig(config).validate()


def hyperparameterEvaluate(config: dict):
    __hyperparameterEvaluate(HyperparameterEvaluateConfig(config))


def validate_hyperparameterEvaluate(config: dict):
    return HyperparameterEvaluateConfig(config).validate()


specialCaseValidators = {
    'runHyperparameterOptimization': validate_runHyperparameterOptimization,
    'hyperparameterTrial': validate_hyperparameterTrial,
    'hyperparameterEvaluate': validate_hyperparameterEvaluate
}
