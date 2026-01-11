"""
v25.0: AGI & Universal Reasoning Platform

Artificial General Intelligence capable of human-level performance on any
intellectual task through unified cognitive architecture.
"""

from .agi_services import (
    # Services
    UniversalTaskUnderstandingService,
    CrossDomainTransferService,
    AbstractReasoningService,
    MetaCognitiveControlService,
    CommonSenseReasoningService,
    FlexibleGoalManagementService,
    GeneralProblemSolvingService,

    # Enums
    TaskType,
    ReasoningType,
    GoalType,
    GoalStatus,
    ProblemCategory,

    # Data Structures
    UniversalTask,
    TransferMapping,
    ReasoningTrace,
    MetaCognitiveState,
    CommonSenseKnowledge,
    Goal,
    ProblemSolution,

    # Singleton Getters
    get_task_understanding_service,
    get_transfer_service,
    get_reasoning_service,
    get_metacognition_service,
    get_commonsense_service,
    get_goal_management_service,
    get_problem_solving_service,
)

__version__ = '25.0.0'

__all__ = [
    # Services
    'UniversalTaskUnderstandingService',
    'CrossDomainTransferService',
    'AbstractReasoningService',
    'MetaCognitiveControlService',
    'CommonSenseReasoningService',
    'FlexibleGoalManagementService',
    'GeneralProblemSolvingService',

    # Enums
    'TaskType',
    'ReasoningType',
    'GoalType',
    'GoalStatus',
    'ProblemCategory',

    # Data Structures
    'UniversalTask',
    'TransferMapping',
    'ReasoningTrace',
    'MetaCognitiveState',
    'CommonSenseKnowledge',
    'Goal',
    'ProblemSolution',

    # Singleton Getters
    'get_task_understanding_service',
    'get_transfer_service',
    'get_reasoning_service',
    'get_metacognition_service',
    'get_commonsense_service',
    'get_goal_management_service',
    'get_problem_solving_service',

    # Version
    '__version__',
]
