"""
🧠 Brain-Computer Interface Module

Provides comprehensive BCI capabilities for direct neural control of the document
management system, including EEG signal processing, motor imagery classification,
P300 detection, SSVEP processing, and cognitive state monitoring.

Version: 4.4.0
"""

__version__ = '4.4.0'

from .bci_services import (
    # EEG Signal Processor
    EEGChannel,
    EEGSignal,
    FilterType,
    EEGProcessor,
    get_eeg_processor,

    # Motor Imagery Classifier
    MotorImageryType,
    MotorImageryTrial,
    ClassificationResult,
    MotorImageryClassifier,
    get_motor_imagery_classifier,

    # P300 Detector
    P300Paradigm,
    P300Stimulus,
    P300Response,
    P300Detector,
    get_p300_detector,

    # SSVEP Processor
    SSVEPStimulus,
    SSVEPResponse,
    SSVEPProcessor,
    get_ssvep_processor,

    # Cognitive State Monitor
    CognitiveState,
    CognitiveMetrics,
    BrainRhythms,
    CognitiveMonitor,
    get_cognitive_monitor,

    # BCI Control Interface
    BCICommand,
    BCIAction,
    ControlSession,
    BCIControlInterface,
    get_bci_control,

    # Neurofeedback System
    FeedbackProtocol,
    FeedbackTarget,
    TrainingSession,
    NeurofeedbackSystem,
    get_neurofeedback_system,
)

__all__ = [
    # EEG Signal Processor
    'EEGChannel',
    'EEGSignal',
    'FilterType',
    'EEGProcessor',
    'get_eeg_processor',

    # Motor Imagery Classifier
    'MotorImageryType',
    'MotorImageryTrial',
    'ClassificationResult',
    'MotorImageryClassifier',
    'get_motor_imagery_classifier',

    # P300 Detector
    'P300Paradigm',
    'P300Stimulus',
    'P300Response',
    'P300Detector',
    'get_p300_detector',

    # SSVEP Processor
    'SSVEPStimulus',
    'SSVEPResponse',
    'SSVEPProcessor',
    'get_ssvep_processor',

    # Cognitive State Monitor
    'CognitiveState',
    'CognitiveMetrics',
    'BrainRhythms',
    'CognitiveMonitor',
    'get_cognitive_monitor',

    # BCI Control Interface
    'BCICommand',
    'BCIAction',
    'ControlSession',
    'BCIControlInterface',
    'get_bci_control',

    # Neurofeedback System
    'FeedbackProtocol',
    'FeedbackTarget',
    'TrainingSession',
    'NeurofeedbackSystem',
    'get_neurofeedback_system',
]
