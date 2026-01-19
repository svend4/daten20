"""
Quantum Machine Learning Platform Module - v15.0

This module provides comprehensive quantum machine learning capabilities with
variational quantum circuits, quantum kernels, quantum neural networks, quantum
SVM, quantum clustering, hybrid quantum-classical optimization, and quantum
feature encoding.

Version: 15.0.0 (FULL IMPLEMENTATION)
"""

from .quantum_ml_services import (
    # Enumerations
    FeatureEncoding,
    EntanglementPattern,
    QuantumKernel,
    OptimizerType,
    MeasurementBasis,

    # Dataclasses
    QuantumCircuitConfig,
    TrainingConfig,
    QuantumKernelParams,
    QuantumMLResult,
    ClusteringResult,
    QuantumMLConfig,

    # Subsystems
    QuantumFeatureMap,
    QuantumNeuralNetwork,
    QuantumSVM,
    QuantumKMeans,
    QuantumClassifier,
    QMLTrainer,
    HybridQuantumClassicalOptimizer,

    # Integrated System
    IntegratedQuantumMLSystem,

    # Singleton Getter
    get_quantum_ml_system,
)

__all__ = [
    # Enumerations
    'FeatureEncoding',
    'EntanglementPattern',
    'QuantumKernel',
    'OptimizerType',
    'MeasurementBasis',

    # Dataclasses
    'QuantumCircuitConfig',
    'TrainingConfig',
    'QuantumKernelParams',
    'QuantumMLResult',
    'ClusteringResult',
    'QuantumMLConfig',

    # Subsystems
    'QuantumFeatureMap',
    'QuantumNeuralNetwork',
    'QuantumSVM',
    'QuantumKMeans',
    'QuantumClassifier',
    'QMLTrainer',
    'HybridQuantumClassicalOptimizer',

    # Integrated System
    'IntegratedQuantumMLSystem',

    # Singleton Getter
    'get_quantum_ml_system',
]

__version__ = '15.0.0'
