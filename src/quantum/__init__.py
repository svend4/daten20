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

Version: 4.1.0 (Complete)
"""

__version__ = '4.1.0'

# Unified Quantum API (SIMPLE VERSION)
from .quantum_api_simple import (
    QuantumAPI,
    QuantumConfig,
    QuantumOperation,
    get_quantum_api,
    build_circuit,
    run_grover_search,
    solve_maxcut,
)

from .quantum_services import (
    # Quantum Circuit Engine
    QuantumGate,
    GateType,
    QuantumCircuit,
    QuantumState,
    NoiseModel,
    CircuitOptimizer,
    get_circuit_optimizer,

    # Quantum Algorithms
    QuantumAlgorithm,
    AlgorithmType,
    GroverSearch,
    ShorFactorization,
    VQE,
    QAOA,
    QuantumWalk,
    AlgorithmLibrary,
    get_algorithm_library,

    # Quantum Hardware Access
    QuantumProvider,
    QuantumBackend,
    QuantumJob,
    JobStatus,
    HardwareCalibration,
    QuantumCloud,
    get_quantum_cloud,

    # Hybrid Quantum-Classical Computing
    VariationalAlgorithm,
    ClassicalOptimizer,
    OptimizerType,
    ParameterizedCircuit,
    HybridExecutor,
    get_hybrid_executor,

    # Quantum Machine Learning
    QuantumNeuralNetwork,
    QuantumSVM,
    QuantumKMeans,
    FeatureMapType,
    QuantumFeatureMap,
    QuantumClassifier,
    QMLTrainer,
    get_qml_trainer,

    # Quantum Optimization
    OptimizationProblem,
    ProblemType,
    MaxCutSolver,
    TSPSolver,
    PortfolioOptimizer,
    SchedulingSolver,
    GraphOptimizer,
    QuantumOptimizationEngine,
    get_quantum_optimizer,
)

__all__ = [
    # Unified API (SIMPLE VERSION)
    'QuantumAPI',
    'QuantumConfig',
    'QuantumOperation',
    'get_quantum_api',
    'build_circuit',
    'run_grover_search',
    'solve_maxcut',

    # Quantum Circuit Engine
    'QuantumGate',
    'GateType',
    'QuantumCircuit',
    'QuantumState',
    'NoiseModel',
    'CircuitOptimizer',
    'get_circuit_optimizer',

    # Quantum Algorithms
    'QuantumAlgorithm',
    'AlgorithmType',
    'GroverSearch',
    'ShorFactorization',
    'VQE',
    'QAOA',
    'QuantumWalk',
    'AlgorithmLibrary',
    'get_algorithm_library',

    # Quantum Hardware Access
    'QuantumProvider',
    'QuantumBackend',
    'QuantumJob',
    'JobStatus',
    'HardwareCalibration',
    'QuantumCloud',
    'get_quantum_cloud',

    # Hybrid Quantum-Classical Computing
    'VariationalAlgorithm',
    'ClassicalOptimizer',
    'OptimizerType',
    'ParameterizedCircuit',
    'HybridExecutor',
    'get_hybrid_executor',

    # Quantum Machine Learning
    'QuantumNeuralNetwork',
    'QuantumSVM',
    'QuantumKMeans',
    'FeatureMapType',
    'QuantumFeatureMap',
    'QuantumClassifier',
    'QMLTrainer',
    'get_qml_trainer',

    # Quantum Optimization
    'OptimizationProblem',
    'ProblemType',
    'MaxCutSolver',
    'TSPSolver',
    'PortfolioOptimizer',
    'SchedulingSolver',
    'GraphOptimizer',
    'QuantumOptimizationEngine',
    'get_quantum_optimizer',
]
