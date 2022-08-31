from typing import Dict, Callable

from .TaskBase import TaskBase
from .hyperparameter_optimisation.hypeparamaterOptimisationMethods import HyperparameterTrial, \
    StartHyperparameterOptimization, HyperparameterEvaluate

specialTasks: Dict[str, Callable[[dict], TaskBase]] = {
    'StartHyperparameterOptimization': StartHyperparameterOptimization,
    'HyperparameterEvaluate': HyperparameterEvaluate,
    'HyperparameterTrial': HyperparameterTrial
}
