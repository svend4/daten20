"""
Federated Learning & Privacy-Preserving Distributed AI - v11.0 (FUNCTIONAL)

Privacy-preserving federated learning for distributed AI training.
Version: 11.0.0 (FUNCTIONAL - uses REAL FedAvg algorithm!)

This module now uses REAL Federated Averaging (FedAvg) algorithm:
- McMahan et al. 2017: "Communication-Efficient Learning of Deep Networks
  from Decentralized Data"
- Weighted model aggregation based on client dataset sizes
- Client sampling and selection
- Local SGD training on distributed data
- Differential Privacy for privacy protection
- Measurable convergence and loss reduction

Example usage:
    from federated_learning import run_federated_learning

    # Run federated learning with 10 clients
    result = run_federated_learning(
        num_clients=10,
        num_rounds=20,
        client_fraction=0.3,
        local_epochs=1,
        enable_dp=False
    )

    print(f"Initial loss: {result['initial_loss']:.4f}")
    print(f"Final loss: {result['final_loss']:.4f}")
    print(f"Improvement: {result['loss_improvement_percent']:.1f}%")

With Differential Privacy:
    # Enable DP for privacy protection
    result = run_federated_learning(
        num_clients=10,
        num_rounds=20,
        enable_dp=True,
        epsilon=1.0  # Privacy budget
    )

    print(f"Privacy budget ε: {result['privacy_budget_epsilon']}")
    print(f"Final loss: {result['final_loss']:.4f}")
"""

__version__ = '11.0.0'
__status__ = 'FUNCTIONAL'

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

# Import REAL federated learning algorithms
from .federated_algorithms import (
    ModelWeights,
    FederatedClient,
    FederatedAveraging,
    DifferentialPrivacy,
    run_federated_learning,
)

logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """Model aggregation strategies"""
    FEDAVG = "federated_averaging"
    FEDPROX = "federated_proximal"
    FEDADAM = "federated_adam"
    SCAFFOLD = "scaffold"


@dataclass
class FederatedConfig:
    """Federated learning configuration"""
    num_clients: int = 10
    rounds: int = 100
    client_fraction: float = 0.3
    local_epochs: int = 1
    enable_differential_privacy: bool = False
    privacy_epsilon: float = 1.0
    num_features: int = 10


class FederatedLearningEngine:
    """
    Federated Learning Engine - FUNCTIONAL IMPLEMENTATION

    Features:
    - ✅ Federated Averaging (FedAvg) algorithm
    - ✅ Weighted model aggregation (by dataset size)
    - ✅ Client selection and sampling
    - ✅ Local SGD training simulation
    - ✅ Differential Privacy (DP) for privacy protection
    - ✅ Convergence tracking
    - ✅ Loss history and metrics
    - ✅ REAL algorithms, not placeholders!

    Can be expanded with:
    - Federated Proximal (FedProx) for heterogeneity
    - Personalized federated learning
    - Secure aggregation protocols
    - Homomorphic encryption
    - Vertical federated learning
    - Byzantine-robust aggregation
    - Communication efficiency (compression, quantization)
    """

    def __init__(self, config: Optional[FederatedConfig] = None):
        self.config = config or FederatedConfig()

        # Create federated clients
        self.clients = self._create_clients()

        # Initialize FedAvg algorithm
        self.fed_avg = FederatedAveraging(num_features=self.config.num_features)

        # Differential Privacy
        self.dp_mechanism = None
        if self.config.enable_differential_privacy:
            self.dp_mechanism = DifferentialPrivacy(epsilon=self.config.privacy_epsilon)

        # Statistics
        self.training_history = []
        self.current_round = 0

        logger.info(f"Federated Learning Engine initialized (FUNCTIONAL - FedAvg)")
        logger.info(f"Clients: {self.config.num_clients}, DP: {self.config.enable_differential_privacy}")

    def _create_clients(self) -> List[FederatedClient]:
        """Create federated learning clients with heterogeneous data"""
        import random
        clients = []

        for i in range(self.config.num_clients):
            # Heterogeneous dataset sizes (realistic scenario)
            data_size = random.randint(50, 500)
            client = FederatedClient(
                f"client_{i}",
                data_size,
                self.config.num_features
            )
            clients.append(client)

        return clients

    def register_client(self, client_id: str, data_size: int) -> bool:
        """Register new federated learning client"""
        client = FederatedClient(client_id, data_size, self.config.num_features)
        self.clients.append(client)
        logger.info(f"Registered client {client_id} with {data_size} samples")
        return True

    def train_round(self, round_num: Optional[int] = None) -> Dict[str, Any]:
        """
        Run one federated training round using FedAvg.

        Steps:
        1. Select subset of clients
        2. Clients train locally
        3. Aggregate models with weighted averaging
        4. Apply DP noise if enabled
        5. Update global model

        Returns:
            Round results with metrics
        """
        if round_num is None:
            self.current_round += 1
            round_num = self.current_round

        # Run FedAvg round
        result = self.fed_avg.run_round(
            self.clients,
            self.config.client_fraction,
            self.config.local_epochs
        )

        # Apply differential privacy if enabled
        if self.dp_mechanism:
            self.fed_avg.global_model = self.dp_mechanism.add_noise(
                self.fed_avg.global_model,
                sensitivity=1.0
            )
            result['differential_privacy'] = True
            result['privacy_budget'] = self.config.privacy_epsilon

        # Track history
        self.training_history.append(result)

        return result

    def train(self, num_rounds: Optional[int] = None) -> Dict[str, Any]:
        """
        Train federated learning system for multiple rounds.

        Args:
            num_rounds: Number of training rounds (uses config if None)

        Returns:
            Complete training results
        """
        rounds = num_rounds or self.config.rounds

        logger.info(f"Starting federated training for {rounds} rounds")

        for round_num in range(rounds):
            result = self.train_round(round_num + 1)

            if round_num % 10 == 0:
                logger.info(
                    f"Round {round_num+1}/{rounds}: "
                    f"Loss={result['average_loss']:.4f}, "
                    f"Convergence={result['convergence_indicator']:.2f}"
                )

        # Aggregate results
        return self.get_training_summary()

    def aggregate_models(self, client_models: List[Dict[str, Any]],
                         strategy: AggregationStrategy = AggregationStrategy.FEDAVG) -> Dict[str, Any]:
        """
        Aggregate client models using specified strategy.

        Currently implements FedAvg (weighted averaging).

        Args:
            client_models: List of client model updates
            strategy: Aggregation strategy to use

        Returns:
            Aggregation result
        """
        if strategy != AggregationStrategy.FEDAVG:
            logger.warning(f"Strategy {strategy} not yet implemented, using FedAvg")

        # Convert to format expected by FedAvg
        updates = [
            (model['client_id'], model['weights'], model.get('data_size', 100))
            for model in client_models
        ]

        aggregated = self.fed_avg.aggregate(updates)

        return {
            "aggregation": strategy.value,
            "status": "functional",
            "model_norm": self.fed_avg._model_norm(aggregated),
            "num_clients_aggregated": len(client_models)
        }

    def get_training_summary(self) -> Dict[str, Any]:
        """Get complete training summary with statistics"""
        if not self.training_history:
            return {"status": "no_training_yet"}

        loss_history = [r['average_loss'] for r in self.training_history]
        initial_loss = loss_history[0]
        final_loss = loss_history[-1]
        improvement = ((initial_loss - final_loss) / initial_loss * 100) if initial_loss > 0 else 0.0

        return {
            "total_rounds": len(self.training_history),
            "num_clients": len(self.clients),
            "client_fraction": self.config.client_fraction,
            "differential_privacy_enabled": self.config.enable_differential_privacy,
            "privacy_epsilon": self.config.privacy_epsilon if self.config.enable_differential_privacy else None,
            "initial_loss": initial_loss,
            "final_loss": final_loss,
            "loss_improvement_percent": improvement,
            "convergence_indicator": self.training_history[-1]['convergence_indicator'],
            "loss_history": loss_history,
            "status": "FUNCTIONAL",
            "algorithm": "FedAvg"
        }


# Singleton instance
_engine = None


def get_federated_learning_engine(config: Optional[FederatedConfig] = None) -> FederatedLearningEngine:
    """Get singleton Federated Learning Engine"""
    global _engine
    if _engine is None:
        _engine = FederatedLearningEngine(config)
    return _engine


__all__ = [
    # Main classes
    'FederatedLearningEngine',
    'FederatedConfig',
    'AggregationStrategy',
    # Algorithm components
    'ModelWeights',
    'FederatedClient',
    'FederatedAveraging',
    'DifferentialPrivacy',
    # Utility functions
    'run_federated_learning',
    'get_federated_learning_engine',
    # Metadata
    '__version__',
    '__status__',
]
