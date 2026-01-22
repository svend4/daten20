"""
Quantum Machine Learning Platform Module - v15.0

This module provides comprehensive quantum machine learning capabilities with
variational quantum circuits, quantum kernels, quantum neural networks, quantum
SVM, quantum clustering, hybrid quantum-classical optimization, and quantum
feature encoding.

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (slower)
- NumPy: 50-100x faster, requires numpy

The best available version is automatically selected.

Version: 15.0.0 (FULL IMPLEMENTATION - Dual Version)
"""

# ALWAYS import Pure Python version (baseline, always available)
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

    # Subsystems (Pure Python versions)
    QuantumFeatureMap as QuantumFeatureMapPython,
    QuantumNeuralNetwork as QuantumNeuralNetworkPython,
    QuantumSVM as QuantumSVMPython,
    QuantumKMeans as QuantumKMeansPython,
    QuantumClassifier as QuantumClassifierPython,
    QMLTrainer as QMLTrainerPython,
    HybridQuantumClassicalOptimizer as HybridQuantumClassicalOptimizerPython,

    # Integrated System (Pure Python)
    IntegratedQuantumMLSystem as IntegratedQuantumMLSystemPython,

    # Singleton Getter (Pure Python)
    get_quantum_ml_system as get_quantum_ml_system_python,
)

# TRY to import NumPy version (optional, faster)
try:
    from .quantum_ml_services_numpy import (
        # Subsystems (NumPy versions)
        QuantumFeatureMap as QuantumFeatureMapNumpy,
        QuantumNeuralNetwork as QuantumNeuralNetworkNumpy,
        QuantumSVM as QuantumSVMNumpy,
        QuantumKMeans as QuantumKMeansNumpy,
        QuantumClassifier as QuantumClassifierNumpy,
        QMLTrainer as QMLTrainerNumpy,
        HybridQuantumClassicalOptimizer as HybridQuantumClassicalOptimizerNumpy,

        # Integrated System (NumPy)
        IntegratedQuantumMLSystem as IntegratedQuantumMLSystemNumpy,

        # Singleton Getter (NumPy)
        get_quantum_ml_system as get_quantum_ml_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Smart aliases - automatically use best available version
if HAS_NUMPY:
    # NumPy version available - use it (50-100x faster)
    QuantumFeatureMap = QuantumFeatureMapNumpy
    QuantumNeuralNetwork = QuantumNeuralNetworkNumpy
    QuantumSVM = QuantumSVMNumpy
    QuantumKMeans = QuantumKMeansNumpy
    QuantumClassifier = QuantumClassifierNumpy
    QMLTrainer = QMLTrainerNumpy
    HybridQuantumClassicalOptimizer = HybridQuantumClassicalOptimizerNumpy
    IntegratedQuantumMLSystem = IntegratedQuantumMLSystemNumpy
    get_quantum_ml_system = get_quantum_ml_system_numpy
else:
    # NumPy not available - use Pure Python (slower but portable)
    QuantumFeatureMap = QuantumFeatureMapPython
    QuantumNeuralNetwork = QuantumNeuralNetworkPython
    QuantumSVM = QuantumSVMPython
    QuantumKMeans = QuantumKMeansPython
    QuantumClassifier = QuantumClassifierPython
    QMLTrainer = QMLTrainerPython
    HybridQuantumClassicalOptimizer = HybridQuantumClassicalOptimizerPython
    IntegratedQuantumMLSystem = IntegratedQuantumMLSystemPython
    get_quantum_ml_system = get_quantum_ml_system_python

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

    # Subsystems (auto-select best version)
    'QuantumFeatureMap',
    'QuantumNeuralNetwork',
    'QuantumSVM',
    'QuantumKMeans',
    'QuantumClassifier',
    'QMLTrainer',
    'HybridQuantumClassicalOptimizer',

    # Pure Python versions (always available)
    'QuantumFeatureMapPython',
    'QuantumNeuralNetworkPython',
    'QuantumSVMPython',
    'QuantumKMeansPython',
    'QuantumClassifierPython',
    'QMLTrainerPython',
    'HybridQuantumClassicalOptimizerPython',
    'IntegratedQuantumMLSystemPython',
    'get_quantum_ml_system_python',

    # Integrated System
    'IntegratedQuantumMLSystem',

    # Singleton Getter
    'get_quantum_ml_system',

    # Dual-version flag
    'HAS_NUMPY',
]

# Add NumPy versions to __all__ if available
if HAS_NUMPY:
    __all__.extend([
        'QuantumFeatureMapNumpy',
        'QuantumNeuralNetworkNumpy',
        'QuantumSVMNumpy',
        'QuantumKMeansNumpy',
        'QuantumClassifierNumpy',
        'QMLTrainerNumpy',
        'HybridQuantumClassicalOptimizerNumpy',
        'IntegratedQuantumMLSystemNumpy',
        'get_quantum_ml_system_numpy',
    ])

__version__ = '15.0.0'
