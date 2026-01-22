"""
Advanced Federated Aggregation Strategies

Implements state-of-the-art aggregation algorithms:
- FedProx: Federated Proximal (handles heterogeneity)
- FedAdam: Federated Adam optimizer
- SCAFFOLD: Stochastic Controlled Averaging
- Krum: Byzantine-robust aggregation
- Median aggregation: Byzantine-robust
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from enum import Enum

from .federated_algorithms import ModelWeights, FederatedClient


class AggregationMethod(Enum):
    """Aggregation methods"""
    FEDAVG = "federated_averaging"
    FEDPROX = "federated_proximal"
    FEDADAM = "federated_adam"
    SCAFFOLD = "scaffold"
    KRUM = "krum"
    MEDIAN = "median"


@dataclass
class FedProxConfig:
    """Configuration for FedProx"""
    mu: float = 0.01  # Proximal term coefficient
    learning_rate: float = 0.01


@dataclass
class FedAdamConfig:
    """Configuration for FedAdam"""
    learning_rate: float = 0.001
    beta1: float = 0.9  # First moment decay
    beta2: float = 0.999  # Second moment decay
    epsilon: float = 1e-8


@dataclass
class SCAFFOLDConfig:
    """Configuration for SCAFFOLD"""
    learning_rate: float = 0.01
    global_momentum: float = 0.9


class FedProx:
    """
    FedProx: Federated Learning with Proximal Term

    Paper: "Federated Optimization in Heterogeneous Networks" (Li et al., 2020)

    Handles heterogeneity by adding proximal term:
    min F(w) + (μ/2)||w - w_t||²

    Where w_t is the global model from previous round.
    """

    def __init__(self, config: FedProxConfig, num_features: int = 10):
        self.config = config
        self.num_features = num_features
        self.global_model = self._initialize_model()

    def _initialize_model(self) -> ModelWeights:
        """Initialize global model"""
        weights = [random.uniform(-0.1, 0.1) for _ in range(self.num_features)]
        return ModelWeights(weights=weights)

    def aggregate(self,
                 client_models: List[Tuple[str, ModelWeights, int]],
                 global_model: ModelWeights) -> ModelWeights:
        """
        Aggregate with FedProx.

        Similar to FedAvg but clients train with proximal term.
        """
        if not client_models:
            return global_model

        total_data = sum(size for _, _, size in client_models)
        if total_data == 0:
            return global_model

        # Weighted averaging (same as FedAvg)
        num_weights = len(client_models[0][1].weights)
        aggregated = [0.0] * num_weights

        for _, model, data_size in client_models:
            weight = data_size / total_data
            for i in range(num_weights):
                aggregated[i] += weight * model.weights[i]

        # Apply proximal regularization implicitly
        # (happens during local training)

        return ModelWeights(weights=aggregated)


class FedAdam:
    """
    FedAdam: Federated Learning with Adam Optimizer

    Paper: "Adaptive Federated Optimization" (Reddi et al., 2021)

    Uses Adam optimizer on server side:
    - First moment (momentum): m_t
    - Second moment (variance): v_t
    - Bias correction
    """

    def __init__(self, config: FedAdamConfig, num_features: int = 10):
        self.config = config
        self.num_features = num_features
        self.global_model = self._initialize_model()

        # Adam state
        self.m = [0.0] * num_features  # First moment
        self.v = [0.0] * num_features  # Second moment
        self.t = 0  # Time step

    def _initialize_model(self) -> ModelWeights:
        """Initialize global model"""
        weights = [random.uniform(-0.1, 0.1) for _ in range(self.num_features)]
        return ModelWeights(weights=weights)

    def aggregate(self,
                 client_models: List[Tuple[str, ModelWeights, int]],
                 global_model: ModelWeights) -> ModelWeights:
        """
        Aggregate with FedAdam optimizer.

        Steps:
        1. Compute pseudo-gradient (difference from current global model)
        2. Update first moment (m)
        3. Update second moment (v)
        4. Apply bias correction
        5. Update global model with Adam step
        """
        if not client_models:
            return global_model

        self.t += 1

        # Step 1: Weighted average of client models (pseudo-gradient)
        total_data = sum(size for _, _, size in client_models)
        if total_data == 0:
            return global_model

        avg_weights = [0.0] * self.num_features
        for _, model, data_size in client_models:
            weight = data_size / total_data
            for i in range(self.num_features):
                avg_weights[i] += weight * model.weights[i]

        # Pseudo-gradient: difference from current global model
        pseudo_grad = [
            global_model.weights[i] - avg_weights[i]
            for i in range(self.num_features)
        ]

        # Step 2: Update first moment (momentum)
        for i in range(self.num_features):
            self.m[i] = (
                self.config.beta1 * self.m[i] +
                (1 - self.config.beta1) * pseudo_grad[i]
            )

        # Step 3: Update second moment (variance)
        for i in range(self.num_features):
            self.v[i] = (
                self.config.beta2 * self.v[i] +
                (1 - self.config.beta2) * (pseudo_grad[i] ** 2)
            )

        # Step 4: Bias correction
        m_hat = [m / (1 - self.config.beta1 ** self.t) for m in self.m]
        v_hat = [v / (1 - self.config.beta2 ** self.t) for v in self.v]

        # Step 5: Adam update
        new_weights = [
            global_model.weights[i] - self.config.learning_rate * m_hat[i] /
            (math.sqrt(v_hat[i]) + self.config.epsilon)
            for i in range(self.num_features)
        ]

        return ModelWeights(weights=new_weights)


class SCAFFOLD:
    """
    SCAFFOLD: Stochastic Controlled Averaging for Federated Learning

    Paper: "SCAFFOLD: Stochastic Controlled Averaging for Federated Learning"
           (Karimireddy et al., 2020)

    Uses control variates to reduce client drift:
    - Server maintains global control variate
    - Each client maintains local control variate
    - Correction terms reduce variance
    """

    def __init__(self, config: SCAFFOLDConfig, num_features: int = 10):
        self.config = config
        self.num_features = num_features
        self.global_model = self._initialize_model()

        # Control variates
        self.c_global = [0.0] * num_features  # Global control
        self.c_clients = {}  # Client-specific controls

    def _initialize_model(self) -> ModelWeights:
        """Initialize global model"""
        weights = [random.uniform(-0.1, 0.1) for _ in range(self.num_features)]
        return ModelWeights(weights=weights)

    def aggregate(self,
                 client_models: List[Tuple[str, ModelWeights, int, List[float]]],
                 global_model: ModelWeights) -> ModelWeights:
        """
        Aggregate with SCAFFOLD control variates.

        Args:
            client_models: (client_id, model, data_size, control_variate)

        Returns:
            Updated global model
        """
        if not client_models:
            return global_model

        total_data = sum(size for _, _, size, _ in client_models)
        if total_data == 0:
            return global_model

        # Aggregate client models
        new_weights = [0.0] * self.num_features
        delta_c = [0.0] * self.num_features

        for client_id, model, data_size, c_client in client_models:
            weight = data_size / total_data

            for i in range(self.num_features):
                # Model aggregation
                new_weights[i] += weight * model.weights[i]

                # Control variate update
                if client_id in self.c_clients:
                    delta_c[i] += weight * (c_client[i] - self.c_clients[client_id][i])

            # Store client control variate
            self.c_clients[client_id] = c_client

        # Update global control variate
        for i in range(self.num_features):
            self.c_global[i] += delta_c[i] * len(client_models) / len(self.c_clients)

        return ModelWeights(weights=new_weights)


class ByzantineRobustAggregation:
    """
    Byzantine-robust aggregation methods.

    Protects against malicious/faulty clients.
    """

    @staticmethod
    def krum(client_models: List[Tuple[str, ModelWeights, int]],
             f: int = 1) -> ModelWeights:
        """
        Krum aggregation: Byzantine-robust

        Paper: "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent"
               (Blanchard et al., 2017)

        Selects the model closest to its neighbors (measured by distance).
        Tolerates up to f Byzantine clients.

        Args:
            client_models: List of (client_id, model, data_size)
            f: Number of Byzantine clients to tolerate

        Returns:
            Selected model (Krum winner)
        """
        if len(client_models) <= 2 * f + 2:
            # Not enough clients for Krum, fall back to simple average
            return ByzantineRobustAggregation._simple_average(client_models)

        n = len(client_models)
        k = n - f - 2  # Number of neighbors to consider

        # Calculate pairwise distances
        distances = []
        for i, (_, model_i, _) in enumerate(client_models):
            # Sum of distances to k closest neighbors
            neighbor_distances = []

            for j, (_, model_j, _) in enumerate(client_models):
                if i != j:
                    dist = ByzantineRobustAggregation._euclidean_distance(
                        model_i, model_j
                    )
                    neighbor_distances.append(dist)

            # Sort and sum k closest
            neighbor_distances.sort()
            score = sum(neighbor_distances[:k])
            distances.append((i, score))

        # Select model with minimum score (Krum winner)
        winner_idx = min(distances, key=lambda x: x[1])[0]

        return client_models[winner_idx][1]

    @staticmethod
    def coordinate_wise_median(client_models: List[Tuple[str, ModelWeights, int]]) -> ModelWeights:
        """
        Coordinate-wise median aggregation.

        Robust to Byzantine clients by taking median of each weight coordinate.

        Args:
            client_models: List of (client_id, model, data_size)

        Returns:
            Median model
        """
        if not client_models:
            return ModelWeights(weights=[])

        num_features = len(client_models[0][1].weights)
        median_weights = []

        for feature_idx in range(num_features):
            # Collect all values for this feature
            values = [model.weights[feature_idx] for _, model, _ in client_models]

            # Calculate median
            values_sorted = sorted(values)
            n = len(values_sorted)

            if n % 2 == 0:
                median = (values_sorted[n//2 - 1] + values_sorted[n//2]) / 2
            else:
                median = values_sorted[n//2]

            median_weights.append(median)

        return ModelWeights(weights=median_weights)

    @staticmethod
    def _euclidean_distance(model1: ModelWeights, model2: ModelWeights) -> float:
        """Calculate Euclidean distance between two models"""
        return math.sqrt(sum(
            (w1 - w2) ** 2
            for w1, w2 in zip(model1.weights, model2.weights)
        ))

    @staticmethod
    def _simple_average(client_models: List[Tuple[str, ModelWeights, int]]) -> ModelWeights:
        """Simple unweighted average"""
        if not client_models:
            return ModelWeights(weights=[])

        num_features = len(client_models[0][1].weights)
        avg_weights = [0.0] * num_features

        for _, model, _ in client_models:
            for i in range(num_features):
                avg_weights[i] += model.weights[i]

        for i in range(num_features):
            avg_weights[i] /= len(client_models)

        return ModelWeights(weights=avg_weights)
