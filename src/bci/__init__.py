"""
🧠 Brain-Computer Interface Module (v4.4.0)

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (simplified DSP)
- NumPy: 50-100x faster, full features, requires numpy

The best available version is automatically selected.

Provides comprehensive BCI capabilities for direct neural control of the document
management system, including EEG signal processing, motor imagery classification,
P300 detection, SSVEP processing, and cognitive state monitoring.

Version: 4.4.0 (FULL IMPLEMENTATION - Dual Version)
"""

__version__ = "4.4.0"

# ALWAYS import Pure Python version (baseline, always available)
from .bci_services import (
    # Enums
    FilterType,
    MotorImageryType,
    P300Paradigm,
    CognitiveState,
    BCICommand,
    FeedbackProtocol,
    
    # Dataclasses
    EEGChannel,
    EEGSignal,
    MotorImageryTrial,
    ClassificationResult,
    P300Stimulus,
    P300Response,
    SSVEPStimulus,
    SSVEPResponse,
    CognitiveMetrics,
    BrainRhythms,
    BCIAction,
    ControlSession,
    FeedbackTarget,
    TrainingSession,
    
    # Classes (Pure Python - simplified)
    EEGProcessor as EEGProcessorPython,
    MotorImageryClassifier as MotorImageryClassifierPython,
    P300Detector as P300DetectorPython,
    SSVEPProcessor as SSVEPProcessorPython,
    CognitiveMonitor as CognitiveMonitorPython,
    BCIControlInterface as BCIControlInterfacePython,
    NeurofeedbackSystem as NeurofeedbackSystemPython,
    
    # Singletons (Pure Python)
    get_eeg_processor as get_eeg_processor_python,
    get_motor_imagery_classifier as get_motor_imagery_classifier_python,
    get_p300_detector as get_p300_detector_python,
    get_ssvep_processor as get_ssvep_processor_python,
    get_cognitive_monitor as get_cognitive_monitor_python,
    get_bci_control as get_bci_control_python,
    get_neurofeedback_system as get_neurofeedback_system_python,
)

# TRY to import NumPy version (optional, faster, full DSP features)
try:
    from .bci_services_numpy import (
        # Classes (NumPy version - full features)
        EEGProcessor as EEGProcessorNumpy,
        MotorImageryClassifier as MotorImageryClassifierNumpy,
        P300Detector as P300DetectorNumpy,
        SSVEPProcessor as SSVEPProcessorNumpy,
        CognitiveMonitor as CognitiveMonitorNumpy,
        BCIControlInterface as BCIControlInterfaceNumpy,
        NeurofeedbackSystem as NeurofeedbackSystemNumpy,
        
        # Singletons (NumPy version)
        get_eeg_processor as get_eeg_processor_numpy,
        get_motor_imagery_classifier as get_motor_imagery_classifier_numpy,
        get_p300_detector as get_p300_detector_numpy,
        get_ssvep_processor as get_ssvep_processor_numpy,
        get_cognitive_monitor as get_cognitive_monitor_numpy,
        get_bci_control as get_bci_control_numpy,
        get_neurofeedback_system as get_neurofeedback_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (50-100x faster, full DSP features)
    EEGProcessor = EEGProcessorNumpy
    MotorImageryClassifier = MotorImageryClassifierNumpy
    P300Detector = P300DetectorNumpy
    SSVEPProcessor = SSVEPProcessorNumpy
    CognitiveMonitor = CognitiveMonitorNumpy
    BCIControlInterface = BCIControlInterfaceNumpy
    NeurofeedbackSystem = NeurofeedbackSystemNumpy
    
    # Use NumPy getters
    get_eeg_processor = get_eeg_processor_numpy
    get_motor_imagery_classifier = get_motor_imagery_classifier_numpy
    get_p300_detector = get_p300_detector_numpy
    get_ssvep_processor = get_ssvep_processor_numpy
    get_cognitive_monitor = get_cognitive_monitor_numpy
    get_bci_control = get_bci_control_numpy
    get_neurofeedback_system = get_neurofeedback_system_numpy
else:
    # NumPy not available - use Pure Python (simplified DSP)
    EEGProcessor = EEGProcessorPython
    MotorImageryClassifier = MotorImageryClassifierPython
    P300Detector = P300DetectorPython
    SSVEPProcessor = SSVEPProcessorPython
    CognitiveMonitor = CognitiveMonitorPython
    BCIControlInterface = BCIControlInterfacePython
    NeurofeedbackSystem = NeurofeedbackSystemPython
    
    # Use Pure Python getters
    get_eeg_processor = get_eeg_processor_python
    get_motor_imagery_classifier = get_motor_imagery_classifier_python
    get_p300_detector = get_p300_detector_python
    get_ssvep_processor = get_ssvep_processor_python
    get_cognitive_monitor = get_cognitive_monitor_python
    get_bci_control = get_bci_control_python
    get_neurofeedback_system = get_neurofeedback_system_python

__all__ = [
    # Enums
    "FilterType",
    "MotorImageryType",
    "P300Paradigm",
    "CognitiveState",
    "BCICommand",
    "FeedbackProtocol",
    
    # Dataclasses
    "EEGChannel",
    "EEGSignal",
    "MotorImageryTrial",
    "ClassificationResult",
    "P300Stimulus",
    "P300Response",
    "SSVEPStimulus",
    "SSVEPResponse",
    "CognitiveMetrics",
    "BrainRhythms",
    "BCIAction",
    "ControlSession",
    "FeedbackTarget",
    "TrainingSession",
    
    # Core classes (auto-select best version)
    "EEGProcessor",
    "MotorImageryClassifier",
    "P300Detector",
    "SSVEPProcessor",
    "CognitiveMonitor",
    "BCIControlInterface",
    "NeurofeedbackSystem",
    
    # Pure Python versions (always available)
    "EEGProcessorPython",
    "MotorImageryClassifierPython",
    "P300DetectorPython",
    "SSVEPProcessorPython",
    "CognitiveMonitorPython",
    "BCIControlInterfacePython",
    "NeurofeedbackSystemPython",
    
    # Singletons
    "get_eeg_processor",
    "get_motor_imagery_classifier",
    "get_p300_detector",
    "get_ssvep_processor",
    "get_cognitive_monitor",
    "get_bci_control",
    "get_neurofeedback_system",
    
    # Pure Python singleton getters
    "get_eeg_processor_python",
    "get_motor_imagery_classifier_python",
    "get_p300_detector_python",
    "get_ssvep_processor_python",
    "get_cognitive_monitor_python",
    "get_bci_control_python",
    "get_neurofeedback_system_python",
    
    # Dual-version flag
    "HAS_NUMPY",
]
