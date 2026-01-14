"""
# SIMPLE VERSION - Unified Quantum API - v4.1

This is a simplified/minimal API that can be expanded later with:
- Advanced quantum circuit optimization
- More quantum algorithms (HHL, QPE, etc.)
- Direct hardware integrations (IBM, AWS, Azure, Google)
- Quantum error correction
- Advanced hybrid algorithms
- Quantum chemistry applications
- Quantum cryptography protocols

Single interface for all quantum computing operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .quantum_services import (
    get_circuit_optimizer,
    get_algorithm_library,
    AlgorithmType,
    get_quantum_cloud,
    QuantumProvider,
    get_hybrid_executor,
    get_qml_trainer,
    get_quantum_optimizer,
    ProblemType,
)

logger = logging.getLogger(__name__)


class QuantumOperation(Enum):
    """Quantum operation types"""
    BUILD_CIRCUIT = "build_circuit"
    RUN_ALGORITHM = "run_algorithm"
    EXECUTE_ON_HARDWARE = "execute_on_hardware"
    HYBRID_OPTIMIZE = "hybrid_optimize"
    TRAIN_QML = "train_qml"
    SOLVE_OPTIMIZATION = "solve_optimization"


@dataclass
class QuantumConfig:
    """Configuration for Quantum API"""
    default_provider: QuantumProvider = QuantumProvider.IBM
    simulation_shots: int = 1024
    enable_noise_model: bool = False
    optimization_level: int = 2
    enable_error_mitigation: bool = True


class QuantumAPI:
    """
    # SIMPLE VERSION
    Unified Quantum API - Single interface for quantum computing operations

    Can be expanded with:
    - Full quantum circuit library
    - More quantum algorithms
    - Direct quantum hardware access
    - Quantum error correction
    - Advanced variational algorithms
    - Quantum chemistry (VQE for molecules)
    - Quantum cryptography (QKD)
    """

    def __init__(self, config: Optional[QuantumConfig] = None):
        """Initialize Quantum API"""
        self.config = config or QuantumConfig()

        # Initialize services
        self.circuit_optimizer = get_circuit_optimizer()
        self.algorithm_library = get_algorithm_library()
        self.quantum_cloud = get_quantum_cloud()
        self.hybrid_executor = get_hybrid_executor()
        self.qml_trainer = get_qml_trainer()
        self.quantum_optimizer = get_quantum_optimizer()

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in QuantumOperation},
            "circuits_executed": 0,
            "algorithms_run": 0,
            "qml_models_trained": 0,
            "optimization_problems_solved": 0,
        }

        logger.info("Quantum API initialized (SIMPLE VERSION)")

    def build_circuit(self, num_qubits: int, gates: List[Tuple[str, List[int]]], **kwargs) -> Dict[str, Any]:
        """
        Build quantum circuit

        Args:
            num_qubits: Number of qubits
            gates: List of (gate_name, qubit_indices) tuples

        Returns:
            Circuit information
        """
        self._track(QuantumOperation.BUILD_CIRCUIT)
        circuit = self.circuit_optimizer.build_circuit(num_qubits, gates, **kwargs)
        return {
            "circuit_id": circuit.circuit_id,
            "num_qubits": circuit.num_qubits,
            "depth": circuit.depth,
            "gate_count": circuit.gate_count
        }

    def run_algorithm(
        self,
        algorithm_type: AlgorithmType,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run quantum algorithm

        Args:
            algorithm_type: Type of algorithm (Grover, Shor, VQE, QAOA)
            parameters: Algorithm parameters

        Returns:
            Algorithm results
        """
        self._track(QuantumOperation.RUN_ALGORITHM)
        result = self.algorithm_library.run(algorithm_type, parameters, **kwargs)
        self.stats["algorithms_run"] += 1
        return result

    def execute_on_hardware(
        self,
        circuit_id: str,
        provider: Optional[QuantumProvider] = None,
        shots: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Execute circuit on real quantum hardware

        Args:
            circuit_id: Circuit ID
            provider: Quantum provider (IBM, AWS, Azure, Google)
            shots: Number of shots

        Returns:
            Job ID
        """
        self._track(QuantumOperation.EXECUTE_ON_HARDWARE)
        provider = provider or self.config.default_provider
        shots = shots or self.config.simulation_shots

        job_id = self.quantum_cloud.submit_job(
            circuit_id=circuit_id,
            provider=provider,
            shots=shots,
            **kwargs
        )

        self.stats["circuits_executed"] += 1
        return job_id

    def get_job_result(self, job_id: str, **kwargs) -> Dict[str, Any]:
        """Get quantum job result"""
        return self.quantum_cloud.get_result(job_id, **kwargs)

    def hybrid_optimize(
        self,
        objective_function: Any,
        num_parameters: int,
        circuit_template: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run hybrid quantum-classical optimization

        Args:
            objective_function: Classical objective function
            num_parameters: Number of variational parameters
            circuit_template: Parameterized circuit template

        Returns:
            Optimization results
        """
        self._track(QuantumOperation.HYBRID_OPTIMIZE)
        result = self.hybrid_executor.optimize(
            objective_function=objective_function,
            num_parameters=num_parameters,
            circuit_template=circuit_template,
            **kwargs
        )
        return result

    def train_qml_model(
        self,
        X_train: List[List[float]],
        y_train: List[int],
        model_type: str = "qnn",
        **kwargs
    ) -> str:
        """
        Train quantum machine learning model

        Args:
            X_train: Training features
            y_train: Training labels
            model_type: Model type (qnn, qsvm, qkmeans)

        Returns:
            Model ID
        """
        self._track(QuantumOperation.TRAIN_QML)
        model_id = self.qml_trainer.train(
            X_train=X_train,
            y_train=y_train,
            model_type=model_type,
            **kwargs
        )
        self.stats["qml_models_trained"] += 1
        return model_id

    def predict_qml(
        self,
        model_id: str,
        X_test: List[List[float]],
        **kwargs
    ) -> List[int]:
        """Predict using QML model"""
        return self.qml_trainer.predict(model_id, X_test, **kwargs)

    def solve_optimization(
        self,
        problem_type: ProblemType,
        problem_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Solve optimization problem using quantum algorithms

        Args:
            problem_type: Type of problem (MaxCut, TSP, Portfolio, Scheduling)
            problem_data: Problem specification

        Returns:
            Solution
        """
        self._track(QuantumOperation.SOLVE_OPTIMIZATION)
        solution = self.quantum_optimizer.solve(
            problem_type=problem_type,
            problem_data=problem_data,
            **kwargs
        )
        self.stats["optimization_problems_solved"] += 1
        return solution

    def _track(self, operation: QuantumOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self.stats

    def list_available_backends(self, provider: Optional[QuantumProvider] = None) -> List[Dict[str, Any]]:
        """List available quantum backends"""
        return self.quantum_cloud.list_backends(provider=provider)


# Singleton
_quantum_api = None


def get_quantum_api(config: Optional[QuantumConfig] = None) -> QuantumAPI:
    """Get singleton Quantum API instance"""
    global _quantum_api
    if _quantum_api is None:
        _quantum_api = QuantumAPI(config=config)
    return _quantum_api


# Convenience functions

def build_circuit(num_qubits: int, gates: List[Tuple[str, List[int]]], **kwargs) -> Dict[str, Any]:
    """Convenience function for building circuits"""
    api = get_quantum_api()
    return api.build_circuit(num_qubits, gates, **kwargs)


def run_grover_search(target: int, num_qubits: int, **kwargs) -> Dict[str, Any]:
    """Convenience function for Grover's search"""
    api = get_quantum_api()
    return api.run_algorithm(
        AlgorithmType.GROVER,
        {"target": target, "num_qubits": num_qubits},
        **kwargs
    )


def solve_maxcut(graph: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Convenience function for MaxCut problem"""
    api = get_quantum_api()
    return api.solve_optimization(
        ProblemType.MAXCUT,
        {"graph": graph},
        **kwargs
    )
