"""
Quantum Computing Module - v4.1

Real quantum computing capabilities with hybrid quantum-classical architecture.
Supports quantum circuits, algorithms, hardware access, and quantum ML.

Modules:
- quantum_services: Complete quantum computing implementation

Components:
- Quantum Circuit Engine: Visual circuit design and simulation
- Quantum Algorithms: Grover, Shor, VQE, QAOA, quantum walks
- Quantum Hardware Access: IBM, AWS, Azure, Google quantum computers
- Hybrid Computing: Variational quantum-classical algorithms
- Quantum ML: Quantum neural networks and quantum SVM
- Quantum Optimization: MaxCut, TSP, portfolio optimization

Version: 4.1.0
"""

__version__ = "4.1.0"

from .quantum_services import (  # Quantum Circuit Engine; Quantum Algorithms; Quantum Hardware Access; Hybrid Quantum-Classical Computing; Quantum Machine Learning; Quantum Optimization
    QAOA,
    VQE,
    AlgorithmLibrary,
    AlgorithmType,
    CircuitOptimizer,
    ClassicalOptimizer,
    FeatureMapType,
    GateType,
    GraphOptimizer,
    GroverSearch,
    HardwareCalibration,
    HybridExecutor,
    JobStatus,
    MaxCutSolver,
    NoiseModel,
    OptimizationProblem,
    OptimizerType,
    ParameterizedCircuit,
    PortfolioOptimizer,
    ProblemType,
    QMLTrainer,
    QuantumAlgorithm,
    QuantumBackend,
    QuantumCircuit,
    QuantumClassifier,
    QuantumCloud,
    QuantumFeatureMap,
    QuantumGate,
    QuantumJob,
    QuantumKMeans,
    QuantumNeuralNetwork,
    QuantumOptimizationEngine,
    QuantumProvider,
    QuantumState,
    QuantumSVM,
    QuantumWalk,
    SchedulingSolver,
    ShorFactorization,
    TSPSolver,
    VariationalAlgorithm,
    get_algorithm_library,
    get_circuit_optimizer,
    get_hybrid_executor,
    get_qml_trainer,
    get_quantum_cloud,
    get_quantum_optimizer,
)

__all__ = [
    # Quantum Circuit Engine
    "QuantumGate",
    "GateType",
    "QuantumCircuit",
    "QuantumState",
    "NoiseModel",
    "CircuitOptimizer",
    "get_circuit_optimizer",
    # Quantum Algorithms
    "QuantumAlgorithm",
    "AlgorithmType",
    "GroverSearch",
    "ShorFactorization",
    "VQE",
    "QAOA",
    "QuantumWalk",
    "AlgorithmLibrary",
    "get_algorithm_library",
    # Quantum Hardware Access
    "QuantumProvider",
    "QuantumBackend",
    "QuantumJob",
    "JobStatus",
    "HardwareCalibration",
    "QuantumCloud",
    "get_quantum_cloud",
    # Hybrid Quantum-Classical Computing
    "VariationalAlgorithm",
    "ClassicalOptimizer",
    "OptimizerType",
    "ParameterizedCircuit",
    "HybridExecutor",
    "get_hybrid_executor",
    # Quantum Machine Learning
    "QuantumNeuralNetwork",
    "QuantumSVM",
    "QuantumKMeans",
    "FeatureMapType",
    "QuantumFeatureMap",
    "QuantumClassifier",
    "QMLTrainer",
    "get_qml_trainer",
    # Quantum Optimization
    "OptimizationProblem",
    "ProblemType",
    "MaxCutSolver",
    "TSPSolver",
    "PortfolioOptimizer",
    "SchedulingSolver",
    "GraphOptimizer",
    "QuantumOptimizationEngine",
    "get_quantum_optimizer",
]
