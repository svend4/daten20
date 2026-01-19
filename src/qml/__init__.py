"""
Quantum Machine Learning Platform Module (v15.0)

This module provides comprehensive quantum machine learning capabilities
combining quantum circuits, quantum kernels, quantum neural networks, and
hybrid quantum-classical optimization.

Core Systems:
- Quantum Circuit Learning: Variational quantum circuits (VQC), parameterized circuits
- Quantum Kernel Methods: Quantum feature maps, quantum SVM
- Quantum Neural Networks: Quantum perceptrons, QCNN, QRNN
- Quantum Optimization: VQE, QAOA, quantum annealing
- Quantum Data Encoding: Amplitude, angle, basis, IQP encoding
- Quantum Measurement: State tomography, POVM, readout mitigation
- Hybrid Training System: Parameter shift, SPSA, natural gradient

Example Usage:
    from qml import get_quantum_circuit_learning, get_quantum_kernel_methods

    # Create variational quantum circuit
    qcl = get_quantum_circuit_learning()
    circuit = await qcl.create_variational_circuit(
        circuit_id="vqc_1",
        n_qubits=4,
        ansatz_type=AnsatzType.HARDWARE_EFFICIENT,
        depth=3
    )

    # Create quantum kernel
    qkm = get_quantum_kernel_methods()
    feature_map = await qkm.create_feature_map(
        feature_map_id="fm_1",
        n_features=4,
        encoding_type=EncodingType.PAULI,
        reps=2
    )
"""

from .qml_services import (  # Enums; Data Classes; Service Classes; Singleton Getters
    AnsatzType,
    BackendType,
    EncodingType,
    HybridTrainingSystem,
    MeasurementType,
    OptimizationResult,
    OptimizerType,
    QNNLayer,
    QuantumCircuit,
    QuantumCircuitLearning,
    QuantumDataEncoder,
    QuantumKernel,
    QuantumKernelMethods,
    QuantumMeasurement,
    QuantumMeasurementResult,
    QuantumNeuralNetworks,
    QuantumOptimization,
    TrainingJob,
    VariationalCircuit,
    get_hybrid_training_system,
    get_quantum_circuit_learning,
    get_quantum_data_encoder,
    get_quantum_kernel_methods,
    get_quantum_measurement,
    get_quantum_neural_networks,
    get_quantum_optimization,
)

__version__ = "15.0.0"
__all__ = [
    # Enums
    "EncodingType",
    "AnsatzType",
    "OptimizerType",
    "BackendType",
    "MeasurementType",
    # Data Classes
    "QuantumCircuit",
    "VariationalCircuit",
    "QuantumKernel",
    "QNNLayer",
    "TrainingJob",
    "QuantumMeasurementResult",
    "OptimizationResult",
    # Service Classes
    "QuantumCircuitLearning",
    "QuantumKernelMethods",
    "QuantumNeuralNetworks",
    "QuantumOptimization",
    "QuantumDataEncoder",
    "QuantumMeasurement",
    "HybridTrainingSystem",
    # Singleton Getters
    "get_quantum_circuit_learning",
    "get_quantum_kernel_methods",
    "get_quantum_neural_networks",
    "get_quantum_optimization",
    "get_quantum_data_encoder",
    "get_quantum_measurement",
    "get_hybrid_training_system",
]
