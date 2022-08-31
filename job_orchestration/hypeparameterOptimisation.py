# For now this is single threaded but we should change this.
from .Config import TaskConfig

from .hyperparameter_optimisation.hypeparamaterOptimisationMethods import HyperParameterTrialConfig, \
    __hyperparameterTrial, RunHyperparameterOptimizationConfig, __runHyperparameterOptimization, \
    HyperparameterEvaluateConfig, __hyperparameterEvaluate


def runHyperparameterOptimization(config: TaskConfig):
    __runHyperparameterOptimization(RunHyperparameterOptimizationConfig(config.overallConfig.raw_config),specialCaseValidators)


def validate_runHyperparameterOptimization(config: TaskConfig):
    RunHyperparameterOptimizationConfig(config.overallConfig.raw_config).validate()
    return []


def hyperparameterTrial(config: TaskConfig):
    __hyperparameterTrial(HyperParameterTrialConfig(config))


def validate_hyperparameterTrial(config: TaskConfig):
    HyperParameterTrialConfig(config).validate()
    return []


def hyperparameterEvaluate(config: TaskConfig):
    __hyperparameterEvaluate(HyperparameterEvaluateConfig(config.overallConfig.raw_config),specialCaseValidators)


def validate_hyperparameterEvaluate(config: TaskConfig):
    HyperparameterEvaluateConfig(config.overallConfig.raw_config).validate()
    return []


specialCaseValidators = {
    'runHyperparameterOptimization': validate_runHyperparameterOptimization,
    'hyperparameterTrial': validate_hyperparameterTrial,
    'hyperparameterEvaluate': validate_hyperparameterEvaluate
}
