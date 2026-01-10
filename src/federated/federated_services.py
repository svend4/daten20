"""
Federated Learning Platform Services

This module provides comprehensive privacy-preserving distributed machine learning
capabilities. It implements federated learning orchestration, differential privacy,
secure multi-party computation, Byzantine-resilient aggregation, edge model management,
federated analytics, and privacy-preserving training across all platform modules.

Version: 11.0.0
Author: Daten20 Platform
Date: 2026-01-10
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import asyncio
import threading
import time
import random
import math
import hashlib


# ============================================================================
# Data Classes and Enums
# ============================================================================

class FederationType(Enum):
    """Types of federated learning"""
    CROSS_DEVICE = "cross_device"  # Millions of mobile/IoT devices
    CROSS_SILO = "cross_silo"  # Organizations/hospitals
    VERTICAL = "vertical"  # Different features, same users


class AggregationAlgorithm(Enum):
    """Federated aggregation algorithms"""
    FED_AVG = "fed_avg"  # Federated averaging
    FED_PROX = "fed_prox"  # Federated proximal
    FED_OPT = "fed_opt"  # Federated optimization
    FED_NOVA = "fed_nova"  # Normalized averaging


class PrivacyMechanism(Enum):
    """Differential privacy mechanisms"""
    LAPLACE = "laplace"  # Laplace mechanism
    GAUSSIAN = "gaussian"  # Gaussian mechanism
    EXPONENTIAL = "exponential"  # Exponential mechanism


class ByzantineDefense(Enum):
    """Byzantine defense methods"""
    KRUM = "krum"  # Krum aggregation
    TRIMMED_MEAN = "trimmed_mean"  # Trimmed mean
    MEDIAN = "median"  # Coordinate-wise median
    NORM_CLIP = "norm_clip"  # Norm-based clipping


@dataclass
class FederatedClient:
    """Federated learning client"""
    client_id: str
    client_type: str
    data_size: int
    compute_capacity: float
    network_bandwidth: float
    availability: float
    last_seen: datetime = field(default_factory=datetime.now)
    device_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GlobalModel:
    """Global federated model"""
    model_id: str
    architecture: str
    version: int
    weights: Dict[str, Any]
    performance_metrics: Dict[str, float]
    num_rounds: int
    participating_clients: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrainingRound:
    """Federated training round"""
    round_id: int
    global_model_version: int
    selected_clients: List[str]
    client_updates: Dict[str, Any] = field(default_factory=dict)
    aggregated_update: Optional[Dict[str, Any]] = None
    accuracy: float = 0.0
    loss: float = 0.0
    duration: float = 0.0


@dataclass
class PrivacyBudget:
    """Privacy budget tracking"""
    epsilon: float
    delta: float
    spent_epsilon: float = 0.0
    remaining_epsilon: float = 0.0
    composition_method: str = "advanced"


@dataclass
class ClientUpdate:
    """Client model update"""
    client_id: str
    model_weights: Dict[str, Any]
    num_samples: int
    local_loss: float
    local_accuracy: float
    num_epochs: int
    computation_time: float


@dataclass
class EdgeModel:
    """ML model for edge device"""
    model_id: str
    model_type: str
    architecture: str
    quantization: str
    size_mb: float
    inference_latency_ms: float
    accuracy: float
    power_consumption_mw: float


@dataclass
class SecretShare:
    """Secret share for MPC"""
    share_id: str
    share_value: Any
    threshold: int
    total_shares: int
    polynomial_degree: int


@dataclass
class FederatedQuery:
    """Federated analytics query"""
    query_id: str
    query_type: str
    target_metric: str
    filters: Dict[str, Any]
    privacy_budget: float
    min_participants: int


# ============================================================================
# 1. Federated Learning Orchestrator
# ============================================================================

class FederatedLearningOrchestrator:
    """
    Federated Learning Orchestrator for distributed training coordination.
    
    Implements client selection, model distribution, round management,
    and convergence tracking for cross-device and cross-silo FL.
    
    Based on:
    - FedAvg (McMahan et al. 2017)
    - Communication-Efficient Learning
    - Personalized Federated Learning
    """
    
    def __init__(self):
        self.federations: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, FederatedClient] = {}
        self.global_models: Dict[str, GlobalModel] = {}
        self.training_rounds: List[TrainingRound] = []
        self._lock = threading.Lock()
        
    async def register_client(
        self,
        client: FederatedClient
    ) -> bool:
        """Register federated learning client"""
        
        with self._lock:
            self.clients[client.client_id] = client
        
        return True
    
    async def initialize_federation(
        self,
        model_architecture: str,
        target_clients: List[str],
        federation_type: str = 'cross-device'
    ) -> str:
        """Initialize federated learning federation"""
        
        federation_id = f"fed_{int(time.time())}"
        
        # Initialize global model
        global_model = GlobalModel(
            model_id=f"model_{federation_id}",
            architecture=model_architecture,
            version=0,
            weights={'layer1': [0.1] * 10, 'layer2': [0.2] * 5},  # Simplified
            performance_metrics={'accuracy': 0.0, 'loss': 1.0},
            num_rounds=0,
            participating_clients=[]
        )
        
        federation = {
            'federation_id': federation_id,
            'type': federation_type,
            'global_model': global_model,
            'target_clients': target_clients,
            'active_clients': [],
            'current_round': 0,
            'status': 'initialized',
            'created_at': datetime.now()
        }
        
        with self._lock:
            self.federations[federation_id] = federation
            self.global_models[global_model.model_id] = global_model
        
        return federation_id
    
    async def start_training_round(
        self,
        federation_id: str,
        num_clients: int,
        min_clients: int = 10
    ) -> TrainingRound:
        """Start new federated training round"""
        
        if federation_id not in self.federations:
            raise ValueError(f"Federation not found: {federation_id}")
        
        federation = self.federations[federation_id]
        
        # Client selection (random sampling)
        available_clients = [
            c for c in federation['target_clients']
            if c in self.clients and self.clients[c].availability > 0.5
        ]
        
        selected_clients = random.sample(
            available_clients,
            min(num_clients, len(available_clients))
        )
        
        if len(selected_clients) < min_clients:
            raise ValueError(f"Insufficient clients: {len(selected_clients)} < {min_clients}")
        
        # Create training round
        round_id = federation['current_round'] + 1
        federation['current_round'] = round_id
        
        training_round = TrainingRound(
            round_id=round_id,
            global_model_version=federation['global_model'].version,
            selected_clients=selected_clients
        )
        
        self.training_rounds.append(training_round)
        
        return training_round
    
    async def receive_client_update(
        self,
        round_id: int,
        client_id: str,
        model_update: Dict[str, Any]
    ) -> bool:
        """Receive model update from client"""
        
        # Find training round
        training_round = next((r for r in self.training_rounds if r.round_id == round_id), None)
        
        if not training_round:
            return False
        
        if client_id not in training_round.selected_clients:
            return False
        
        # Store update
        training_round.client_updates[client_id] = model_update
        
        return True
    
    async def aggregate_and_update(
        self,
        round_id: int
    ) -> GlobalModel:
        """Aggregate client updates and update global model"""
        
        training_round = next((r for r in self.training_rounds if r.round_id == round_id), None)
        
        if not training_round:
            raise ValueError(f"Training round not found: {round_id}")
        
        # Simple FedAvg aggregation
        num_updates = len(training_round.client_updates)
        
        if num_updates == 0:
            raise ValueError("No client updates received")
        
        # Average weights
        aggregated_weights = {}
        for layer_name in ['layer1', 'layer2']:
            layer_sum = [0.0] * len(training_round.client_updates[next(iter(training_round.client_updates))]['weights'][layer_name])
            
            for client_id, update in training_round.client_updates.items():
                weights = update['weights'][layer_name]
                for i, w in enumerate(weights):
                    layer_sum[i] += w
            
            aggregated_weights[layer_name] = [w / num_updates for w in layer_sum]
        
        training_round.aggregated_update = {'weights': aggregated_weights}
        
        # Update global model (find corresponding federation)
        for federation in self.federations.values():
            if federation['current_round'] == round_id:
                global_model = federation['global_model']
                global_model.weights = aggregated_weights
                global_model.version += 1
                global_model.num_rounds += 1
                
                # Simulate metrics
                global_model.performance_metrics['accuracy'] = min(0.95, 0.5 + round_id * 0.01)
                global_model.performance_metrics['loss'] = max(0.1, 1.0 - round_id * 0.02)
                
                training_round.accuracy = global_model.performance_metrics['accuracy']
                training_round.loss = global_model.performance_metrics['loss']
                
                return global_model
        
        raise ValueError("Federation not found for round")
    
    async def evaluate_global_model(
        self,
        model_id: str,
        test_data: Optional[Any] = None
    ) -> Dict[str, float]:
        """Evaluate global model performance"""
        
        if model_id not in self.global_models:
            return {'error': 'Model not found'}
        
        model = self.global_models[model_id]
        
        # Simulate evaluation
        await asyncio.sleep(0.1)
        
        return {
            'accuracy': model.performance_metrics.get('accuracy', 0.0),
            'loss': model.performance_metrics.get('loss', 1.0),
            'num_rounds': model.num_rounds
        }


# ============================================================================
# 2. Privacy-Preserving Training
# ============================================================================

class PrivacyPreservingTraining:
    """
    Privacy-Preserving Training with differential privacy and secure aggregation.
    
    Implements local differential privacy, gradient clipping, noise addition,
    and privacy budget tracking.
    
    Based on:
    - Differential Privacy (Dwork 2006)
    - Deep Learning with Differential Privacy (Abadi et al. 2016)
    """
    
    def __init__(self):
        self.privacy_budgets: Dict[str, PrivacyBudget] = {}
        self.noise_history: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
    
    async def apply_differential_privacy(
        self,
        gradients: Dict[str, Any],
        epsilon: float,
        delta: float,
        sensitivity: float
    ) -> Dict[str, Any]:
        """Apply differential privacy to gradients"""
        
        # Clip gradients
        clipped = await self.clip_gradients(
            gradients=gradients,
            clipping_norm=sensitivity
        )
        
        # Add noise
        noisy = await self.add_noise(
            values=clipped,
            noise_scale=sensitivity / epsilon,
            mechanism='gaussian'
        )
        
        # Track privacy budget
        await self.track_privacy_budget(
            epsilon_spent=epsilon,
            delta_spent=delta
        )
        
        return noisy
    
    async def clip_gradients(
        self,
        gradients: Dict[str, Any],
        clipping_norm: float
    ) -> Dict[str, Any]:
        """Clip gradients to bound sensitivity"""
        
        clipped = {}
        
        for layer_name, grad_values in gradients.items():
            # Calculate L2 norm
            norm = math.sqrt(sum(g ** 2 for g in grad_values))
            
            # Clip if necessary
            if norm > clipping_norm:
                scale = clipping_norm / norm
                clipped[layer_name] = [g * scale for g in grad_values]
            else:
                clipped[layer_name] = grad_values
        
        return clipped
    
    async def add_noise(
        self,
        values: Dict[str, Any],
        noise_scale: float,
        mechanism: str = 'gaussian'
    ) -> Dict[str, Any]:
        """Add differential privacy noise"""
        
        noisy = {}
        
        for layer_name, layer_values in values.items():
            if mechanism == 'gaussian':
                # Gaussian mechanism
                sigma = noise_scale
                noise = [random.gauss(0, sigma) for _ in layer_values]
            elif mechanism == 'laplace':
                # Laplace mechanism
                b = noise_scale
                noise = [random.expovariate(1/b) * random.choice([-1, 1]) for _ in layer_values]
            else:
                noise = [0.0] * len(layer_values)
            
            noisy[layer_name] = [v + n for v, n in zip(layer_values, noise)]
        
        self.noise_history.append({
            'mechanism': mechanism,
            'noise_scale': noise_scale,
            'timestamp': datetime.now()
        })
        
        return noisy
    
    async def track_privacy_budget(
        self,
        epsilon_spent: float,
        delta_spent: float
    ) -> PrivacyBudget:
        """Track cumulative privacy budget"""
        
        budget_id = "global_budget"
        
        with self._lock:
            if budget_id not in self.privacy_budgets:
                self.privacy_budgets[budget_id] = PrivacyBudget(
                    epsilon=10.0,  # Total budget
                    delta=1e-5,
                    spent_epsilon=0.0,
                    remaining_epsilon=10.0
                )
            
            budget = self.privacy_budgets[budget_id]
            
            # Advanced composition (simplified)
            budget.spent_epsilon += epsilon_spent
            budget.remaining_epsilon = budget.epsilon - budget.spent_epsilon
        
        return budget
    
    async def secure_aggregate(
        self,
        client_updates: List[Dict[str, Any]],
        threshold: int = 10
    ) -> Dict[str, Any]:
        """Secure aggregation without revealing individual updates"""
        
        if len(client_updates) < threshold:
            raise ValueError(f"Insufficient clients for secure aggregation: {len(client_updates)} < {threshold}")
        
        # Simplified secure aggregation (would use encryption in production)
        # Phase 1: Each client masks their update
        masked_updates = []
        masks = []
        
        for update in client_updates:
            # Generate random mask
            mask = {
                layer: [random.random() for _ in values]
                for layer, values in update.items()
            }
            masks.append(mask)
            
            # Add mask to update
            masked = {
                layer: [u + m for u, m in zip(update[layer], mask[layer])]
                for layer in update.keys()
            }
            masked_updates.append(masked)
        
        # Phase 2: Sum masked updates
        aggregated = {}
        for layer in masked_updates[0].keys():
            layer_sum = [0.0] * len(masked_updates[0][layer])
            for update in masked_updates:
                for i, val in enumerate(update[layer]):
                    layer_sum[i] += val
            aggregated[layer] = layer_sum
        
        # Phase 3: Remove aggregate of masks
        for layer in aggregated.keys():
            mask_sum = [sum(mask[layer][i] for mask in masks) for i in range(len(masks[0][layer]))]
            aggregated[layer] = [v - m for v, m in zip(aggregated[layer], mask_sum)]
        
        return aggregated


# ============================================================================
# 3. Model Aggregation Engine
# ============================================================================

class ModelAggregationEngine:
    """
    Model Aggregation Engine for federated learning.
    
    Implements FedAvg, FedProx, FedOpt, and FedNova aggregation algorithms
    with support for non-IID data and heterogeneous clients.
    
    Based on:
    - FedAvg (McMahan et al. 2017)
    - FedProx (Li et al. 2020)
    - FedOpt (Reddi et al. 2021)
    """
    
    def __init__(self):
        self.aggregation_history: List[Dict[str, Any]] = []
        self.momentum_state: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    async def aggregate_fedavg(
        self,
        client_updates: List[ClientUpdate]
    ) -> Dict[str, Any]:
        """Federated Averaging (FedAvg) aggregation"""
        
        if not client_updates:
            raise ValueError("No client updates to aggregate")
        
        # Calculate total samples
        total_samples = sum(update.num_samples for update in client_updates)
        
        # Weighted average by number of samples
        aggregated = {}
        
        for layer_name in client_updates[0].model_weights.keys():
            layer_size = len(client_updates[0].model_weights[layer_name])
            weighted_sum = [0.0] * layer_size
            
            for update in client_updates:
                weight = update.num_samples / total_samples
                layer_weights = update.model_weights[layer_name]
                
                for i, w in enumerate(layer_weights):
                    weighted_sum[i] += weight * w
            
            aggregated[layer_name] = weighted_sum
        
        # Track aggregation
        self.aggregation_history.append({
            'algorithm': 'fedavg',
            'num_clients': len(client_updates),
            'total_samples': total_samples,
            'timestamp': datetime.now()
        })
        
        return {
            'weights': aggregated,
            'algorithm': 'fedavg',
            'num_clients': len(client_updates)
        }
    
    async def aggregate_fedprox(
        self,
        client_updates: List[ClientUpdate],
        global_model: Dict[str, Any],
        mu: float = 0.1
    ) -> Dict[str, Any]:
        """FedProx aggregation with proximal term"""
        
        # FedProx adds proximal term to local objectives
        # Aggregation is still weighted average, but training includes proximal term
        
        aggregated = await self.aggregate_fedavg(client_updates)
        
        # Apply proximal regularization (simplified)
        for layer_name in aggregated['weights'].keys():
            for i in range(len(aggregated['weights'][layer_name])):
                # Pull towards global model
                global_weight = global_model[layer_name][i]
                aggregated_weight = aggregated['weights'][layer_name][i]
                
                # Proximal update
                aggregated['weights'][layer_name][i] = (
                    aggregated_weight * (1 - mu) + global_weight * mu
                )
        
        aggregated['algorithm'] = 'fedprox'
        aggregated['mu'] = mu
        
        return aggregated
    
    async def aggregate_fedopt(
        self,
        client_updates: List[ClientUpdate],
        optimizer: str = 'adam',
        learning_rate: float = 0.01
    ) -> Dict[str, Any]:
        """FedOpt aggregation with adaptive optimization"""
        
        # Get FedAvg aggregation
        aggregated = await self.aggregate_fedavg(client_updates)
        
        # Apply adaptive optimizer on server side
        if optimizer == 'adam':
            # Adam optimizer (simplified)
            beta1, beta2 = 0.9, 0.999
            epsilon = 1e-8
            
            if 'adam_m' not in self.momentum_state:
                # Initialize momentum
                self.momentum_state['adam_m'] = {
                    layer: [0.0] * len(weights)
                    for layer, weights in aggregated['weights'].items()
                }
                self.momentum_state['adam_v'] = {
                    layer: [0.0] * len(weights)
                    for layer, weights in aggregated['weights'].items()
                }
                self.momentum_state['adam_t'] = 0
            
            m = self.momentum_state['adam_m']
            v = self.momentum_state['adam_v']
            t = self.momentum_state['adam_t'] + 1
            self.momentum_state['adam_t'] = t
            
            # Update with Adam
            optimized = {}
            for layer_name, weights in aggregated['weights'].items():
                opt_weights = []
                for i, w in enumerate(weights):
                    # Update biased first moment estimate
                    m[layer_name][i] = beta1 * m[layer_name][i] + (1 - beta1) * w
                    
                    # Update biased second moment estimate
                    v[layer_name][i] = beta2 * v[layer_name][i] + (1 - beta2) * (w ** 2)
                    
                    # Bias-corrected moments
                    m_hat = m[layer_name][i] / (1 - beta1 ** t)
                    v_hat = v[layer_name][i] / (1 - beta2 ** t)
                    
                    # Update
                    opt_weights.append(learning_rate * m_hat / (math.sqrt(v_hat) + epsilon))
                
                optimized[layer_name] = opt_weights
            
            aggregated['weights'] = optimized
        
        aggregated['algorithm'] = f'fedopt_{optimizer}'
        
        return aggregated
    
    async def detect_anomalous_updates(
        self,
        client_updates: List[ClientUpdate]
    ) -> List[str]:
        """Detect anomalous client updates"""
        
        anomalous_clients = []
        
        # Calculate average loss and accuracy
        avg_loss = sum(u.local_loss for u in client_updates) / len(client_updates)
        avg_acc = sum(u.local_accuracy for u in client_updates) / len(client_updates)
        
        # Detect outliers (simple threshold-based)
        for update in client_updates:
            # Suspiciously high loss
            if update.local_loss > avg_loss * 2.0:
                anomalous_clients.append(update.client_id)
            
            # Suspiciously low accuracy
            elif update.local_accuracy < avg_acc * 0.5:
                anomalous_clients.append(update.client_id)
        
        return anomalous_clients


# ============================================================================
# 4. Secure Multi-Party Computation
# ============================================================================

class SecureMultiPartyComputation:
    """
    Secure Multi-Party Computation for privacy-preserving federated learning.
    
    Implements secret sharing, secure sum, and homomorphic encryption
    for computing on encrypted data.
    
    Based on:
    - Secret Sharing (Shamir 1979)
    - Secure Aggregation (Bonawitz et al. 2017)
    """
    
    def __init__(self):
        self.shares: Dict[str, List[SecretShare]] = {}
        self._lock = threading.Lock()
    
    async def create_secret_shares(
        self,
        secret: float,
        num_shares: int,
        threshold: int
    ) -> List[SecretShare]:
        """Create secret shares using Shamir's Secret Sharing"""
        
        if threshold > num_shares:
            raise ValueError("Threshold cannot exceed number of shares")
        
        # Simplified Shamir's Secret Sharing
        # In production, use proper finite field arithmetic
        
        # Polynomial coefficients (secret is constant term)
        coefficients = [secret] + [random.random() * 100 for _ in range(threshold - 1)]
        
        # Generate shares: (x, P(x)) where P is polynomial
        shares = []
        for x in range(1, num_shares + 1):
            # Evaluate polynomial at x
            y = sum(coef * (x ** i) for i, coef in enumerate(coefficients))
            
            share = SecretShare(
                share_id=f"share_{x}",
                share_value=y,
                threshold=threshold,
                total_shares=num_shares,
                polynomial_degree=threshold - 1
            )
            shares.append(share)
        
        return shares
    
    async def reconstruct_secret(
        self,
        shares: List[SecretShare]
    ) -> float:
        """Reconstruct secret from shares using Lagrange interpolation"""
        
        if not shares:
            raise ValueError("No shares provided")
        
        threshold = shares[0].threshold
        
        if len(shares) < threshold:
            raise ValueError(f"Insufficient shares: {len(shares)} < {threshold}")
        
        # Use first 'threshold' shares
        shares = shares[:threshold]
        
        # Lagrange interpolation to get P(0) = secret
        secret = 0.0
        
        for i, share_i in enumerate(shares):
            x_i = i + 1
            y_i = share_i.share_value
            
            # Lagrange basis polynomial L_i(0)
            numerator = 1.0
            denominator = 1.0
            
            for j, share_j in enumerate(shares):
                if i != j:
                    x_j = j + 1
                    numerator *= (0 - x_j)
                    denominator *= (x_i - x_j)
            
            secret += y_i * (numerator / denominator)
        
        return secret
    
    async def secure_sum(
        self,
        values: List[float],
        parties: List[str]
    ) -> float:
        """Compute sum securely without revealing individual values"""
        
        if len(values) != len(parties):
            raise ValueError("Number of values must match number of parties")
        
        # Simplified secure sum using additive secret sharing
        # Each party splits their value into shares
        
        num_parties = len(parties)
        shares_matrix = []
        
        for value in values:
            # Split value into num_parties shares that sum to value
            shares = [random.random() * value for _ in range(num_parties - 1)]
            last_share = value - sum(shares)
            shares.append(last_share)
            
            shares_matrix.append(shares)
        
        # Each party receives one share from each value
        # Then sums their shares and sends to aggregator
        partial_sums = []
        for party_idx in range(num_parties):
            party_sum = sum(shares_matrix[value_idx][party_idx] for value_idx in range(len(values)))
            partial_sums.append(party_sum)
        
        # Aggregator sums partial sums to get total
        total = sum(partial_sums)
        
        return total
    
    async def homomorphic_aggregate(
        self,
        encrypted_values: List[float],
        encryption_scheme: str = 'paillier'
    ) -> float:
        """Aggregate encrypted values homomorphically"""
        
        # Simplified homomorphic encryption (Paillier-like)
        # In production, use proper cryptographic library
        
        if encryption_scheme == 'paillier':
            # Paillier: E(m1) * E(m2) = E(m1 + m2)
            # Simulate by just summing (encryption omitted for simplicity)
            result = sum(encrypted_values)
        else:
            result = sum(encrypted_values)
        
        return result


# ============================================================================
# 5. Edge Model Manager
# ============================================================================

class EdgeModelManager:
    """
    Edge Model Manager for deploying ML models on resource-constrained devices.
    
    Implements quantization, pruning, knowledge distillation, and efficient
    model architectures for edge deployment.
    
    Based on:
    - Model Compression (Hinton et al. 2015)
    - Quantization techniques
    - TinyML principles
    """
    
    def __init__(self):
        self.edge_models: Dict[str, EdgeModel] = {}
        self.deployed_models: Dict[str, str] = {}  # device_id -> model_id
        self._lock = threading.Lock()
    
    async def optimize_for_edge(
        self,
        model_id: str,
        target_size_mb: float,
        target_latency_ms: float,
        min_accuracy: float = 0.80
    ) -> EdgeModel:
        """Optimize model for edge deployment"""
        
        # Simulate model optimization
        await asyncio.sleep(0.2)
        
        # Apply quantization (default 8-bit)
        quantized = await self.quantize_model(
            model_id=model_id,
            bits=8
        )
        
        # Check if meets targets
        if quantized.size_mb > target_size_mb:
            # Apply more aggressive quantization
            quantized = await self.quantize_model(model_id=model_id, bits=4)
        
        if quantized.size_mb > target_size_mb:
            # Apply pruning
            quantized = await self.prune_model(
                model_id=model_id,
                pruning_ratio=0.5
            )
        
        return quantized
    
    async def quantize_model(
        self,
        model_id: str,
        bits: int = 8
    ) -> EdgeModel:
        """Quantize model to lower precision"""
        
        # Simulate quantization
        base_size = 100.0  # MB
        base_latency = 500.0  # ms
        base_accuracy = 0.92
        
        # Quantization effects
        size_reduction = 32 / bits
        latency_reduction = 1.5 if bits <= 8 else 1.0
        accuracy_loss = 0.01 * (32 - bits) / 4  # ~1% per 4-bit reduction
        
        edge_model = EdgeModel(
            model_id=f"{model_id}_int{bits}",
            model_type="quantized",
            architecture="mobilenet_v2",
            quantization=f"int{bits}",
            size_mb=base_size / size_reduction,
            inference_latency_ms=base_latency / latency_reduction,
            accuracy=base_accuracy - accuracy_loss,
            power_consumption_mw=300.0 / latency_reduction
        )
        
        with self._lock:
            self.edge_models[edge_model.model_id] = edge_model
        
        return edge_model
    
    async def prune_model(
        self,
        model_id: str,
        pruning_ratio: float
    ) -> EdgeModel:
        """Prune model by removing less important weights"""
        
        # Simulate pruning
        base_size = 100.0
        base_latency = 500.0
        base_accuracy = 0.92
        
        # Pruning effects
        size_reduction = 1 / (1 - pruning_ratio)
        latency_improvement = 1.2
        accuracy_loss = pruning_ratio * 0.05  # ~5% loss at 100% pruning
        
        edge_model = EdgeModel(
            model_id=f"{model_id}_pruned_{int(pruning_ratio*100)}",
            model_type="pruned",
            architecture="mobilenet_v2_pruned",
            quantization="fp32",
            size_mb=base_size / size_reduction,
            inference_latency_ms=base_latency / latency_improvement,
            accuracy=base_accuracy - accuracy_loss,
            power_consumption_mw=400.0
        )
        
        with self._lock:
            self.edge_models[edge_model.model_id] = edge_model
        
        return edge_model
    
    async def distill_model(
        self,
        teacher_model_id: str,
        student_architecture: str
    ) -> EdgeModel:
        """Distill large teacher model into small student model"""
        
        # Simulate knowledge distillation
        await asyncio.sleep(0.5)
        
        edge_model = EdgeModel(
            model_id=f"student_{teacher_model_id}",
            model_type="distilled",
            architecture=student_architecture,
            quantization="fp32",
            size_mb=10.0,  # 10x smaller
            inference_latency_ms=50.0,  # 10x faster
            accuracy=0.85,  # 10% accuracy loss typical
            power_consumption_mw=200.0
        )
        
        with self._lock:
            self.edge_models[edge_model.model_id] = edge_model
        
        return edge_model
    
    async def deploy_to_edge(
        self,
        model_id: str,
        device_id: str
    ) -> bool:
        """Deploy model to edge device"""
        
        if model_id not in self.edge_models:
            return False
        
        # Simulate deployment
        await asyncio.sleep(0.3)
        
        with self._lock:
            self.deployed_models[device_id] = model_id
        
        return True


# ============================================================================
# 6. Federated Analytics System
# ============================================================================

class FederatedAnalyticsSystem:
    """
    Federated Analytics System for privacy-preserving analytics.
    
    Performs aggregate statistics, histograms, and analytics queries
    on distributed data without centralization.
    
    Based on:
    - Federated Analytics (Google 2020)
    - Privacy-Preserving Statistics
    """
    
    def __init__(self):
        self.query_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    async def execute_federated_query(
        self,
        query: FederatedQuery,
        clients: List[str]
    ) -> Dict[str, Any]:
        """Execute federated analytics query"""
        
        if len(clients) < query.min_participants:
            return {
                'error': f'Insufficient participants: {len(clients)} < {query.min_participants}'
            }
        
        # Execute query based on type
        if query.query_type == 'count':
            result = await self._count_query(query, clients)
        elif query.query_type == 'average':
            result = await self._average_query(query, clients)
        elif query.query_type == 'histogram':
            result = await self._histogram_query(query, clients)
        else:
            result = {'error': f'Unknown query type: {query.query_type}'}
        
        # Track query
        self.query_history.append({
            'query_id': query.query_id,
            'query_type': query.query_type,
            'num_clients': len(clients),
            'timestamp': datetime.now()
        })
        
        return result
    
    async def _count_query(
        self,
        query: FederatedQuery,
        clients: List[str]
    ) -> Dict[str, Any]:
        """Execute count query"""
        
        # Each client counts matching records
        # Simulate client responses
        counts = [random.randint(0, 100) for _ in clients]
        
        # Add differential privacy noise
        epsilon = query.privacy_budget
        sensitivity = 1.0
        noise_scale = sensitivity / epsilon
        noise = random.gauss(0, noise_scale)
        
        total_count = sum(counts) + noise
        
        return {
            'query_type': 'count',
            'result': int(max(0, total_count)),
            'num_contributors': len(clients),
            'epsilon_spent': epsilon
        }
    
    async def _average_query(
        self,
        query: FederatedQuery,
        clients: List[str]
    ) -> Dict[str, Any]:
        """Execute average query"""
        
        # Each client computes local average
        # Simulate client responses
        local_avgs = [random.uniform(50, 150) for _ in clients]
        local_counts = [random.randint(10, 100) for _ in clients]
        
        # Weighted average
        total_sum = sum(avg * count for avg, count in zip(local_avgs, local_counts))
        total_count = sum(local_counts)
        
        global_avg = total_sum / total_count if total_count > 0 else 0
        
        # Add DP noise
        epsilon = query.privacy_budget
        sensitivity = 200.0 / total_count  # Assuming values in [0, 200]
        noise = random.gauss(0, sensitivity / epsilon)
        
        return {
            'query_type': 'average',
            'result': global_avg + noise,
            'num_contributors': len(clients),
            'epsilon_spent': epsilon
        }
    
    async def _histogram_query(
        self,
        query: FederatedQuery,
        clients: List[str]
    ) -> Dict[str, Any]:
        """Execute histogram query"""
        
        # Define bins
        bins = [0, 25, 50, 75, 100, 125, 150, 175, 200]
        num_bins = len(bins) - 1
        
        # Each client computes local histogram
        histogram = [0] * num_bins
        
        for client in clients:
            # Simulate client histogram
            client_hist = [random.randint(0, 50) for _ in range(num_bins)]
            histogram = [h + ch for h, ch in zip(histogram, client_hist)]
        
        # Add DP noise to each bin
        epsilon_per_bin = query.privacy_budget / num_bins
        noisy_histogram = []
        
        for count in histogram:
            noise = random.gauss(0, 1.0 / epsilon_per_bin)
            noisy_histogram.append(int(max(0, count + noise)))
        
        return {
            'query_type': 'histogram',
            'bins': bins,
            'counts': noisy_histogram,
            'num_contributors': len(clients),
            'epsilon_spent': query.privacy_budget
        }
    
    async def compute_federated_average(
        self,
        metric: str,
        clients: List[str],
        epsilon: float
    ) -> float:
        """Compute federated average with differential privacy"""
        
        query = FederatedQuery(
            query_id=f"avg_{metric}_{int(time.time())}",
            query_type='average',
            target_metric=metric,
            filters={},
            privacy_budget=epsilon,
            min_participants=10
        )
        
        result = await self.execute_federated_query(query, clients)
        
        return result.get('result', 0.0)


# ============================================================================
# 7. Byzantine-Resilient Aggregator
# ============================================================================

class ByzantineResilientAggregator:
    """
    Byzantine-Resilient Aggregator for defending against malicious clients.
    
    Implements Krum, Trimmed Mean, Median, and norm-based clipping
    to tolerate Byzantine (malicious) clients.
    
    Based on:
    - Krum (Blanchard et al. 2017)
    - Byzantine-Robust FL (Yin et al. 2018)
    """
    
    def __init__(self):
        self.suspicious_updates: List[Dict[str, Any]] = []
        self.defense_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    async def detect_byzantine_updates(
        self,
        updates: List[ClientUpdate],
        byzantine_ratio: float = 0.1
    ) -> List[str]:
        """Detect Byzantine (malicious) client updates"""
        
        suspicious_clients = []
        
        # Calculate statistics
        losses = [u.local_loss for u in updates]
        accuracies = [u.local_accuracy for u in updates]
        
        avg_loss = sum(losses) / len(losses)
        avg_acc = sum(accuracies) / len(accuracies)
        
        std_loss = math.sqrt(sum((l - avg_loss) ** 2 for l in losses) / len(losses))
        std_acc = math.sqrt(sum((a - avg_acc) ** 2 for a in accuracies) / len(accuracies))
        
        # Detect outliers (beyond 3 standard deviations)
        for update in updates:
            if abs(update.local_loss - avg_loss) > 3 * std_loss:
                suspicious_clients.append(update.client_id)
            elif abs(update.local_accuracy - avg_acc) > 3 * std_acc:
                suspicious_clients.append(update.client_id)
        
        # Track suspicious updates
        with self._lock:
            for client_id in suspicious_clients:
                self.suspicious_updates.append({
                    'client_id': client_id,
                    'reason': 'statistical_outlier',
                    'timestamp': datetime.now()
                })
        
        return suspicious_clients
    
    async def aggregate_krum(
        self,
        updates: List[ClientUpdate],
        num_byzantine: int
    ) -> Dict[str, Any]:
        """Krum aggregation (select update closest to majority)"""
        
        n = len(updates)
        f = num_byzantine
        
        if n <= 2 * f + 2:
            raise ValueError(f"Insufficient honest clients: need n > 2f+2, have n={n}, f={f}")
        
        # Calculate pairwise distances
        def distance(u1: ClientUpdate, u2: ClientUpdate) -> float:
            # Simplified Euclidean distance
            dist = 0.0
            for layer in u1.model_weights.keys():
                for w1, w2 in zip(u1.model_weights[layer], u2.model_weights[layer]):
                    dist += (w1 - w2) ** 2
            return math.sqrt(dist)
        
        # For each update, sum distances to n-f-2 closest updates
        scores = []
        for i, update_i in enumerate(updates):
            distances = []
            for j, update_j in enumerate(updates):
                if i != j:
                    distances.append(distance(update_i, update_j))
            
            # Sort and sum n-f-2 smallest distances
            distances.sort()
            score = sum(distances[:n - f - 2])
            scores.append((score, i))
        
        # Select update with smallest score (closest to majority)
        scores.sort()
        selected_idx = scores[0][1]
        selected_update = updates[selected_idx]
        
        # Track defense
        self.defense_history.append({
            'method': 'krum',
            'num_updates': n,
            'num_byzantine': f,
            'selected_client': selected_update.client_id,
            'timestamp': datetime.now()
        })
        
        return {
            'weights': selected_update.model_weights,
            'defense_method': 'krum',
            'num_updates_used': 1,
            'num_updates_rejected': n - 1
        }
    
    async def aggregate_trimmed_mean(
        self,
        updates: List[ClientUpdate],
        trim_ratio: float = 0.1
    ) -> Dict[str, Any]:
        """Trimmed mean aggregation (remove outliers, then average)"""
        
        n = len(updates)
        trim_count = int(n * trim_ratio)
        
        # For each coordinate, sort values and trim top/bottom
        aggregated = {}
        
        for layer_name in updates[0].model_weights.keys():
            layer_size = len(updates[0].model_weights[layer_name])
            trimmed_weights = []
            
            for coord_idx in range(layer_size):
                # Collect all values for this coordinate
                values = [u.model_weights[layer_name][coord_idx] for u in updates]
                
                # Sort and trim
                values.sort()
                trimmed = values[trim_count:n - trim_count]
                
                # Average remaining
                avg = sum(trimmed) / len(trimmed) if trimmed else 0.0
                trimmed_weights.append(avg)
            
            aggregated[layer_name] = trimmed_weights
        
        return {
            'weights': aggregated,
            'defense_method': 'trimmed_mean',
            'trim_ratio': trim_ratio,
            'num_updates_used': n - 2 * trim_count,
            'num_updates_rejected': 2 * trim_count
        }
    
    async def aggregate_median(
        self,
        updates: List[ClientUpdate]
    ) -> Dict[str, Any]:
        """Coordinate-wise median aggregation"""
        
        aggregated = {}
        
        for layer_name in updates[0].model_weights.keys():
            layer_size = len(updates[0].model_weights[layer_name])
            median_weights = []
            
            for coord_idx in range(layer_size):
                # Collect all values for this coordinate
                values = [u.model_weights[layer_name][coord_idx] for u in updates]
                
                # Calculate median
                values.sort()
                n = len(values)
                if n % 2 == 1:
                    median = values[n // 2]
                else:
                    median = (values[n // 2 - 1] + values[n // 2]) / 2
                
                median_weights.append(median)
            
            aggregated[layer_name] = median_weights
        
        return {
            'weights': aggregated,
            'defense_method': 'median',
            'num_updates_used': len(updates),
            'num_updates_rejected': 0
        }
    
    async def clip_by_norm(
        self,
        updates: List[ClientUpdate],
        threshold: float
    ) -> List[ClientUpdate]:
        """Clip updates with large norms"""
        
        clipped_updates = []
        
        for update in updates:
            # Calculate L2 norm of update
            norm = 0.0
            for layer in update.model_weights.values():
                norm += sum(w ** 2 for w in layer)
            norm = math.sqrt(norm)
            
            # Clip if necessary
            if norm > threshold:
                scale = threshold / norm
                clipped_weights = {
                    layer: [w * scale for w in weights]
                    for layer, weights in update.model_weights.items()
                }
                
                clipped_update = ClientUpdate(
                    client_id=update.client_id,
                    model_weights=clipped_weights,
                    num_samples=update.num_samples,
                    local_loss=update.local_loss,
                    local_accuracy=update.local_accuracy,
                    num_epochs=update.num_epochs,
                    computation_time=update.computation_time
                )
                clipped_updates.append(clipped_update)
            else:
                clipped_updates.append(update)
        
        return clipped_updates


# ============================================================================
# Singleton Instances
# ============================================================================

_fl_orchestrator: Optional[FederatedLearningOrchestrator] = None
_privacy_trainer: Optional[PrivacyPreservingTraining] = None
_model_aggregator: Optional[ModelAggregationEngine] = None
_secure_mpc: Optional[SecureMultiPartyComputation] = None
_edge_manager: Optional[EdgeModelManager] = None
_federated_analytics: Optional[FederatedAnalyticsSystem] = None
_byzantine_aggregator: Optional[ByzantineResilientAggregator] = None

_lock = threading.Lock()


def get_fl_orchestrator() -> FederatedLearningOrchestrator:
    """Get singleton instance of FederatedLearningOrchestrator"""
    global _fl_orchestrator
    if _fl_orchestrator is None:
        with _lock:
            if _fl_orchestrator is None:
                _fl_orchestrator = FederatedLearningOrchestrator()
    return _fl_orchestrator


def get_privacy_trainer() -> PrivacyPreservingTraining:
    """Get singleton instance of PrivacyPreservingTraining"""
    global _privacy_trainer
    if _privacy_trainer is None:
        with _lock:
            if _privacy_trainer is None:
                _privacy_trainer = PrivacyPreservingTraining()
    return _privacy_trainer


def get_model_aggregator() -> ModelAggregationEngine:
    """Get singleton instance of ModelAggregationEngine"""
    global _model_aggregator
    if _model_aggregator is None:
        with _lock:
            if _model_aggregator is None:
                _model_aggregator = ModelAggregationEngine()
    return _model_aggregator


def get_secure_mpc() -> SecureMultiPartyComputation:
    """Get singleton instance of SecureMultiPartyComputation"""
    global _secure_mpc
    if _secure_mpc is None:
        with _lock:
            if _secure_mpc is None:
                _secure_mpc = SecureMultiPartyComputation()
    return _secure_mpc


def get_edge_model_manager() -> EdgeModelManager:
    """Get singleton instance of EdgeModelManager"""
    global _edge_manager
    if _edge_manager is None:
        with _lock:
            if _edge_manager is None:
                _edge_manager = EdgeModelManager()
    return _edge_manager


def get_federated_analytics() -> FederatedAnalyticsSystem:
    """Get singleton instance of FederatedAnalyticsSystem"""
    global _federated_analytics
    if _federated_analytics is None:
        with _lock:
            if _federated_analytics is None:
                _federated_analytics = FederatedAnalyticsSystem()
    return _federated_analytics


def get_byzantine_aggregator() -> ByzantineResilientAggregator:
    """Get singleton instance of ByzantineResilientAggregator"""
    global _byzantine_aggregator
    if _byzantine_aggregator is None:
        with _lock:
            if _byzantine_aggregator is None:
                _byzantine_aggregator = ByzantineResilientAggregator()
    return _byzantine_aggregator
