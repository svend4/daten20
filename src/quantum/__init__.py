"""
Quantum Computing Services v4.1.0

**DUAL-VERSION IMPLEMENTATION**:
- Pure Python: Mock quantum operations
- NumPy: Full quantum simulation

Version: 4.1.0
"""

__version__ = "4.1.0"

from .quantum_services import (
    GateType, BackendType,
    QuantumGate, QuantumCircuit, QuantumResult,
    
    QuantumCircuitEngine as QuantumCircuitEnginePython,
    QuantumAlgorithms as QuantumAlgorithmsPython,
    QuantumHardwareManager as QuantumHardwareManagerPython,
    HybridQuantumClassical as HybridQuantumClassicalPython,
    QuantumMachineLearning as QuantumMachineLearningPython,
    QuantumOptimization as QuantumOptimizationPython,
    
    get_quantum_circuit_engine as get_quantum_circuit_engine_python,
    get_quantum_algorithms as get_quantum_algorithms_python,
    get_quantum_hardware_manager as get_quantum_hardware_manager_python,
    get_hybrid_quantum_classical as get_hybrid_quantum_classical_python,
    get_quantum_machine_learning as get_quantum_machine_learning_python,
    get_quantum_optimization as get_quantum_optimization_python,
)

try:
    from .quantum_services_numpy import (
        QuantumCircuitEngine as QuantumCircuitEngineNumpy,
        QuantumAlgorithms as QuantumAlgorithmsNumpy,
        QuantumHardwareManager as QuantumHardwareManagerNumpy,
        HybridQuantumClassical as HybridQuantumClassicalNumpy,
        QuantumMachineLearning as QuantumMachineLearningNumpy,
        QuantumOptimization as QuantumOptimizationNumpy,
        
        get_quantum_circuit_engine as get_quantum_circuit_engine_numpy,
        get_quantum_algorithms as get_quantum_algorithms_numpy,
        get_quantum_hardware_manager as get_quantum_hardware_manager_numpy,
        get_hybrid_quantum_classical as get_hybrid_quantum_classical_numpy,
        get_quantum_machine_learning as get_quantum_machine_learning_numpy,
        get_quantum_optimization as get_quantum_optimization_numpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if HAS_NUMPY:
    QuantumCircuitEngine = QuantumCircuitEngineNumpy
    QuantumAlgorithms = QuantumAlgorithmsNumpy
    QuantumHardwareManager = QuantumHardwareManagerNumpy
    HybridQuantumClassical = HybridQuantumClassicalNumpy
    QuantumMachineLearning = QuantumMachineLearningNumpy
    QuantumOptimization = QuantumOptimizationNumpy
    
    get_quantum_circuit_engine = get_quantum_circuit_engine_numpy
    get_quantum_algorithms = get_quantum_algorithms_numpy
    get_quantum_hardware_manager = get_quantum_hardware_manager_numpy
    get_hybrid_quantum_classical = get_hybrid_quantum_classical_numpy
    get_quantum_machine_learning = get_quantum_machine_learning_numpy
    get_quantum_optimization = get_quantum_optimization_numpy
else:
    QuantumCircuitEngine = QuantumCircuitEnginePython
    QuantumAlgorithms = QuantumAlgorithmsPython
    QuantumHardwareManager = QuantumHardwareManagerPython
    HybridQuantumClassical = HybridQuantumClassicalPython
    QuantumMachineLearning = QuantumMachineLearningPython
    QuantumOptimization = QuantumOptimizationPython
    
    get_quantum_circuit_engine = get_quantum_circuit_engine_python
    get_quantum_algorithms = get_quantum_algorithms_python
    get_quantum_hardware_manager = get_quantum_hardware_manager_python
    get_hybrid_quantum_classical = get_hybrid_quantum_classical_python
    get_quantum_machine_learning = get_quantum_machine_learning_python
    get_quantum_optimization = get_quantum_optimization_python

__all__ = [
    "__version__", "GateType", "BackendType", "QuantumGate", "QuantumCircuit", "QuantumResult",
    "QuantumCircuitEngine", "QuantumAlgorithms", "QuantumHardwareManager",
    "HybridQuantumClassical", "QuantumMachineLearning", "QuantumOptimization",
    "get_quantum_circuit_engine", "get_quantum_algorithms", "get_quantum_hardware_manager",
    "get_hybrid_quantum_classical", "get_quantum_machine_learning", "get_quantum_optimization",
    "HAS_NUMPY",
]
