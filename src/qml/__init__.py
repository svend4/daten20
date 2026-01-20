"""
Quantum Machine Learning Platform v15.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Works everywhere, no dependencies (mock quantum ops)
- NumPy: Full quantum simulation

Version: 15.0.0 (Dual Version)
"""

__version__ = "15.0.0"

from .qml_services import (
    EncodingType,
    AnsatzType,
    OptimizerType,
    QuantumCircuit,
    OptimizationResult,
    
    QuantumCircuitLearning as QuantumCircuitLearningPython,
    QuantumKernelMethods as QuantumKernelMethodsPython,
    QuantumNeuralNetworks as QuantumNeuralNetworksPython,
    QuantumOptimization as QuantumOptimizationPython,
    QuantumDataEncoder as QuantumDataEncoderPython,
    QuantumMeasurement as QuantumMeasurementPython,
    HybridTrainingSystem as HybridTrainingSystemPython,
    
    get_quantum_circuit_learning as get_quantum_circuit_learning_python,
    get_quantum_kernel_methods as get_quantum_kernel_methods_python,
    get_quantum_neural_networks as get_quantum_neural_networks_python,
    get_quantum_optimization as get_quantum_optimization_python,
    get_quantum_data_encoder as get_quantum_data_encoder_python,
    get_quantum_measurement as get_quantum_measurement_python,
    get_hybrid_training_system as get_hybrid_training_system_python,
)

try:
    from .qml_services_numpy import (
        QuantumCircuitLearning as QuantumCircuitLearningNumpy,
        QuantumKernelMethods as QuantumKernelMethodsNumpy,
        QuantumNeuralNetworks as QuantumNeuralNetworksNumpy,
        QuantumOptimization as QuantumOptimizationNumpy,
        QuantumDataEncoder as QuantumDataEncoderNumpy,
        QuantumMeasurement as QuantumMeasurementNumpy,
        HybridTrainingSystem as HybridTrainingSystemNumpy,
        
        get_quantum_circuit_learning as get_quantum_circuit_learning_numpy,
        get_quantum_kernel_methods as get_quantum_kernel_methods_numpy,
        get_quantum_neural_networks as get_quantum_neural_networks_numpy,
        get_quantum_optimization as get_quantum_optimization_numpy,
        get_quantum_data_encoder as get_quantum_data_encoder_numpy,
        get_quantum_measurement as get_quantum_measurement_numpy,
        get_hybrid_training_system as get_hybrid_training_system_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if HAS_NUMPY:
    QuantumCircuitLearning = QuantumCircuitLearningNumpy
    QuantumKernelMethods = QuantumKernelMethodsNumpy
    QuantumNeuralNetworks = QuantumNeuralNetworksNumpy
    QuantumOptimization = QuantumOptimizationNumpy
    QuantumDataEncoder = QuantumDataEncoderNumpy
    QuantumMeasurement = QuantumMeasurementNumpy
    HybridTrainingSystem = HybridTrainingSystemNumpy
    
    get_quantum_circuit_learning = get_quantum_circuit_learning_numpy
    get_quantum_kernel_methods = get_quantum_kernel_methods_numpy
    get_quantum_neural_networks = get_quantum_neural_networks_numpy
    get_quantum_optimization = get_quantum_optimization_numpy
    get_quantum_data_encoder = get_quantum_data_encoder_numpy
    get_quantum_measurement = get_quantum_measurement_numpy
    get_hybrid_training_system = get_hybrid_training_system_numpy
else:
    QuantumCircuitLearning = QuantumCircuitLearningPython
    QuantumKernelMethods = QuantumKernelMethodsPython
    QuantumNeuralNetworks = QuantumNeuralNetworksPython
    QuantumOptimization = QuantumOptimizationPython
    QuantumDataEncoder = QuantumDataEncoderPython
    QuantumMeasurement = QuantumMeasurementPython
    HybridTrainingSystem = HybridTrainingSystemPython
    
    get_quantum_circuit_learning = get_quantum_circuit_learning_python
    get_quantum_kernel_methods = get_quantum_kernel_methods_python
    get_quantum_neural_networks = get_quantum_neural_networks_python
    get_quantum_optimization = get_quantum_optimization_python
    get_quantum_data_encoder = get_quantum_data_encoder_python
    get_quantum_measurement = get_quantum_measurement_python
    get_hybrid_training_system = get_hybrid_training_system_python

__all__ = [
    "__version__",
    "EncodingType",
    "AnsatzType",
    "OptimizerType",
    "QuantumCircuit",
    "OptimizationResult",
    "QuantumCircuitLearning",
    "QuantumKernelMethods",
    "QuantumNeuralNetworks",
    "QuantumOptimization",
    "QuantumDataEncoder",
    "QuantumMeasurement",
    "HybridTrainingSystem",
    "get_quantum_circuit_learning",
    "get_quantum_kernel_methods",
    "get_quantum_neural_networks",
    "get_quantum_optimization",
    "get_quantum_data_encoder",
    "get_quantum_measurement",
    "get_hybrid_training_system",
    "HAS_NUMPY",
]
