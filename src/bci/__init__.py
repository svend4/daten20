"""
🧠 Brain-Computer Interface Module

Provides comprehensive BCI capabilities for direct neural control of the document
management system, including EEG signal processing, motor imagery classification,
P300 detection, SSVEP processing, and cognitive state monitoring.

Version: 4.4.0
"""

__version__ = "4.4.0"

from .bci_services import (  # EEG Signal Processor; Motor Imagery Classifier; P300 Detector; SSVEP Processor; Cognitive State Monitor; BCI Control Interface; Neurofeedback System
    BCIAction,
    BCICommand,
    BCIControlInterface,
    BrainRhythms,
    ClassificationResult,
    CognitiveMetrics,
    CognitiveMonitor,
    CognitiveState,
    ControlSession,
    EEGChannel,
    EEGProcessor,
    EEGSignal,
    FeedbackProtocol,
    FeedbackTarget,
    FilterType,
    MotorImageryClassifier,
    MotorImageryTrial,
    MotorImageryType,
    NeurofeedbackSystem,
    P300Detector,
    P300Paradigm,
    P300Response,
    P300Stimulus,
    SSVEPProcessor,
    SSVEPResponse,
    SSVEPStimulus,
    TrainingSession,
    get_bci_control,
    get_cognitive_monitor,
    get_eeg_processor,
    get_motor_imagery_classifier,
    get_neurofeedback_system,
    get_p300_detector,
    get_ssvep_processor,
)

__all__ = [
    # EEG Signal Processor
    "EEGChannel",
    "EEGSignal",
    "FilterType",
    "EEGProcessor",
    "get_eeg_processor",
    # Motor Imagery Classifier
    "MotorImageryType",
    "MotorImageryTrial",
    "ClassificationResult",
    "MotorImageryClassifier",
    "get_motor_imagery_classifier",
    # P300 Detector
    "P300Paradigm",
    "P300Stimulus",
    "P300Response",
    "P300Detector",
    "get_p300_detector",
    # SSVEP Processor
    "SSVEPStimulus",
    "SSVEPResponse",
    "SSVEPProcessor",
    "get_ssvep_processor",
    # Cognitive State Monitor
    "CognitiveState",
    "CognitiveMetrics",
    "BrainRhythms",
    "CognitiveMonitor",
    "get_cognitive_monitor",
    # BCI Control Interface
    "BCICommand",
    "BCIAction",
    "ControlSession",
    "BCIControlInterface",
    "get_bci_control",
    # Neurofeedback System
    "FeedbackProtocol",
    "FeedbackTarget",
    "TrainingSession",
    "NeurofeedbackSystem",
    "get_neurofeedback_system",
]
