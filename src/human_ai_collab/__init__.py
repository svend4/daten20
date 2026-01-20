"""
Human-AI Collaboration & Augmentation Platform v20.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Mock collaboration systems
- NumPy: Full collaboration features

Version: 20.0.0
"""

__version__ = "20.0.0"

from .human_ai_collab_services import (
    TaskRole, IntentType, ControlMode,
    Task, Intent,
    
    CollaborativeTaskManager as CollaborativeTaskManagerPython,
    IntentUnderstanding as IntentUnderstandingPython,
    AICapabilityMatcher as AICapabilityMatcherPython,
    SharedMentalModel as SharedMentalModelPython,
    MixedInitiativeController as MixedInitiativeControllerPython,
    PerformanceAugmentation as PerformanceAugmentationPython,
    TrustTransparencySystem as TrustTransparencySystemPython,
    
    get_collaborative_task_manager as get_collaborative_task_manager_python,
    get_intent_understanding as get_intent_understanding_python,
    get_ai_capability_matcher as get_ai_capability_matcher_python,
    get_shared_mental_model as get_shared_mental_model_python,
    get_mixed_initiative_controller as get_mixed_initiative_controller_python,
    get_performance_augmentation as get_performance_augmentation_python,
    get_trust_transparency_system as get_trust_transparency_system_python,
)

try:
    from .human_ai_collab_services_numpy import (
        CollaborativeTaskManager as CollaborativeTaskManagerNumpy,
        IntentUnderstanding as IntentUnderstandingNumpy,
        AICapabilityMatcher as AICapabilityMatcherNumpy,
        SharedMentalModel as SharedMentalModelNumpy,
        MixedInitiativeController as MixedInitiativeControllerNumpy,
        PerformanceAugmentation as PerformanceAugmentationNumpy,
        TrustTransparencySystem as TrustTransparencySystemNumpy,
        
        get_collaborative_task_manager as get_collaborative_task_manager_numpy,
        get_intent_understanding as get_intent_understanding_numpy,
        get_ai_capability_matcher as get_ai_capability_matcher_numpy,
        get_shared_mental_model as get_shared_mental_model_numpy,
        get_mixed_initiative_controller as get_mixed_initiative_controller_numpy,
        get_performance_augmentation as get_performance_augmentation_numpy,
        get_trust_transparency_system as get_trust_transparency_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if HAS_NUMPY:
    CollaborativeTaskManager = CollaborativeTaskManagerNumpy
    IntentUnderstanding = IntentUnderstandingNumpy
    AICapabilityMatcher = AICapabilityMatcherNumpy
    SharedMentalModel = SharedMentalModelNumpy
    MixedInitiativeController = MixedInitiativeControllerNumpy
    PerformanceAugmentation = PerformanceAugmentationNumpy
    TrustTransparencySystem = TrustTransparencySystemNumpy
    
    get_collaborative_task_manager = get_collaborative_task_manager_numpy
    get_intent_understanding = get_intent_understanding_numpy
    get_ai_capability_matcher = get_ai_capability_matcher_numpy
    get_shared_mental_model = get_shared_mental_model_numpy
    get_mixed_initiative_controller = get_mixed_initiative_controller_numpy
    get_performance_augmentation = get_performance_augmentation_numpy
    get_trust_transparency_system = get_trust_transparency_system_numpy
else:
    CollaborativeTaskManager = CollaborativeTaskManagerPython
    IntentUnderstanding = IntentUnderstandingPython
    AICapabilityMatcher = AICapabilityMatcherPython
    SharedMentalModel = SharedMentalModelPython
    MixedInitiativeController = MixedInitiativeControllerPython
    PerformanceAugmentation = PerformanceAugmentationPython
    TrustTransparencySystem = TrustTransparencySystemPython
    
    get_collaborative_task_manager = get_collaborative_task_manager_python
    get_intent_understanding = get_intent_understanding_python
    get_ai_capability_matcher = get_ai_capability_matcher_python
    get_shared_mental_model = get_shared_mental_model_python
    get_mixed_initiative_controller = get_mixed_initiative_controller_python
    get_performance_augmentation = get_performance_augmentation_python
    get_trust_transparency_system = get_trust_transparency_system_python

__all__ = [
    "__version__", "TaskRole", "IntentType", "ControlMode", "Task", "Intent",
    "CollaborativeTaskManager", "IntentUnderstanding", "AICapabilityMatcher",
    "SharedMentalModel", "MixedInitiativeController", "PerformanceAugmentation",
    "TrustTransparencySystem",
    "get_collaborative_task_manager", "get_intent_understanding", "get_ai_capability_matcher",
    "get_shared_mental_model", "get_mixed_initiative_controller", "get_performance_augmentation",
    "get_trust_transparency_system", "HAS_NUMPY",
]
