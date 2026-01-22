"""
Secure Aggregation & Communication Efficiency

Implements:
1. Secure Aggregation with encryption
2. Communication compression (quantization, sparsification)
3. Gradient compression techniques
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

from .federated_algorithms import ModelWeights


class CompressionMethod(Enum):
    """Compression methods"""
    NONE = "none"
    QUANTIZATION = "quantization"
    TOP_K = "top_k"
    RANDOM_SPARSIFICATION = "random_sparsification"


@dataclass
class CompressionConfig:
    """Configuration for compression"""
    method: CompressionMethod = CompressionMethod.NONE
    # Quantization
    num_bits: int = 8  # Bits per value
    # Top-K
    k_ratio: float = 0.1  # Keep top 10%
    # Random sparsification
    sparsity_ratio: float = 0.1  # Keep 10%


class SecureAggregation:
    """
    Secure Aggregation Protocol

    Simplified version inspired by:
    "Practical Secure Aggregation for Privacy-Preserving Machine Learning"
    (Bonawitz et al., 2017)

    Uses secret sharing and masking:
    1. Clients add random masks to their updates
    2. Server aggregates masked updates
    3. Masks cancel out in aggregation
    """

    def __init__(self, num_clients: int, modulus: int = 2**32):
        """
        Initialize secure aggregation.

        Args:
            num_clients: Number of clients
            modulus: Modulus for arithmetic (for masking)
        """
        self.num_clients = num_clients
        self.modulus = modulus

        # Pairwise masks (simplified - in practice uses key agreement)
        self.masks = {}

    def generate_pairwise_masks(self, client_id: str, num_features: int) -> List[float]:
        """
        Generate pairwise masks for a client.

        In practice, clients would generate these using key agreement
        protocols (e.g., Diffie-Hellman).

        Args:
            client_id: Client identifier
            num_features: Number of model features

        Returns:
            Random mask vector
        """
        # Generate random mask
        mask = [random.randint(-1000, 1000) for _ in range(num_features)]

        # Store for later cancellation
        self.masks[client_id] = mask

        return mask

    def mask_model(self, model: ModelWeights, mask: List[float]) -> ModelWeights:
        """
        Add mask to model for secure transmission.

        Args:
            model: Original model weights
            mask: Random mask

        Returns:
            Masked model
        """
        masked_weights = [
            (w + m) % self.modulus
            for w, m in zip(model.weights, mask)
        ]

        return ModelWeights(weights=masked_weights)

    def secure_aggregate(self,
                        masked_models: List[Tuple[str, ModelWeights, int]]) -> ModelWeights:
        """
        Securely aggregate masked models.

        Masks cancel out: Σ(model_i + mask_i) - Σ(mask_i) = Σ(model_i)

        Args:
            masked_models: List of (client_id, masked_model, data_size)

        Returns:
            Aggregated model (unmasked)
        """
        if not masked_models:
            return ModelWeights(weights=[])

        num_features = len(masked_models[0][1].weights)
        total_data = sum(size for _, _, size in masked_models)

        # Sum masked models (weighted)
        aggregated = [0.0] * num_features

        for client_id, model, data_size in masked_models:
            weight = data_size / total_data

            for i in range(num_features):
                aggregated[i] += weight * model.weights[i]

        # In practice, masks would cancel out through protocol
        # Here we explicitly remove them (simplified)
        for client_id, _, data_size in masked_models:
            if client_id in self.masks:
                weight = data_size / total_data
                mask = self.masks[client_id]

                for i in range(num_features):
                    aggregated[i] -= weight * mask[i]

        return ModelWeights(weights=aggregated)


class CommunicationCompression:
    """
    Communication-efficient methods for federated learning.

    Reduces bandwidth by compressing model updates.
    """

    @staticmethod
    def quantize(model: ModelWeights, num_bits: int = 8) -> Tuple[ModelWeights, Dict]:
        """
        Quantize model weights to reduce precision.

        Maps continuous values to discrete bins.

        Args:
            model: Original model
            num_bits: Bits per value (e.g., 8 bits = 256 levels)

        Returns:
            (quantized_model, metadata_for_dequantization)
        """
        # Find min/max for normalization
        min_val = min(model.weights)
        max_val = max(model.weights)

        if min_val == max_val:
            # All values identical
            return model, {"min": min_val, "max": max_val, "num_bits": num_bits}

        # Number of quantization levels
        levels = 2 ** num_bits

        # Quantize
        quantized = []
        for w in model.weights:
            # Normalize to [0, 1]
            normalized = (w - min_val) / (max_val - min_val)

            # Quantize to integer
            quantized_int = int(normalized * (levels - 1))

            # Dequantize back to float (lossy)
            dequantized = quantized_int / (levels - 1) * (max_val - min_val) + min_val

            quantized.append(dequantized)

        metadata = {
            "min": min_val,
            "max": max_val,
            "num_bits": num_bits
        }

        return ModelWeights(weights=quantized), metadata

    @staticmethod
    def top_k_sparsification(model: ModelWeights, k_ratio: float = 0.1) -> ModelWeights:
        """
        Top-K sparsification: Keep only top K% of weights by magnitude.

        Paper: "Deep Gradient Compression" (Lin et al., 2018)

        Args:
            model: Original model
            k_ratio: Ratio of weights to keep (e.g., 0.1 = 10%)

        Returns:
            Sparse model
        """
        k = max(1, int(len(model.weights) * k_ratio))

        # Get indices of top-k by absolute value
        sorted_indices = sorted(
            range(len(model.weights)),
            key=lambda i: abs(model.weights[i]),
            reverse=True
        )
        top_k_indices = set(sorted_indices[:k])

        # Zero out non-top-k weights
        sparse_weights = [
            w if i in top_k_indices else 0.0
            for i, w in enumerate(model.weights)
        ]

        return ModelWeights(weights=sparse_weights)

    @staticmethod
    def random_sparsification(model: ModelWeights,
                            sparsity_ratio: float = 0.1) -> ModelWeights:
        """
        Random sparsification: Randomly keep certain weights.

        Unbiased estimator with reduced variance.

        Args:
            model: Original model
            sparsity_ratio: Ratio of weights to keep

        Returns:
            Sparse model
        """
        sparse_weights = []

        for w in model.weights:
            if random.random() < sparsity_ratio:
                # Keep and scale up (for unbiased estimation)
                sparse_weights.append(w / sparsity_ratio)
            else:
                # Drop
                sparse_weights.append(0.0)

        return ModelWeights(weights=sparse_weights)

    @staticmethod
    def compress(model: ModelWeights, config: CompressionConfig) -> Tuple[ModelWeights, Dict]:
        """
        Compress model using specified method.

        Args:
            model: Original model
            config: Compression configuration

        Returns:
            (compressed_model, metadata)
        """
        if config.method == CompressionMethod.QUANTIZATION:
            return CommunicationCompression.quantize(model, config.num_bits)

        elif config.method == CompressionMethod.TOP_K:
            compressed = CommunicationCompression.top_k_sparsification(
                model, config.k_ratio
            )
            return compressed, {"method": "top_k", "k_ratio": config.k_ratio}

        elif config.method == CompressionMethod.RANDOM_SPARSIFICATION:
            compressed = CommunicationCompression.random_sparsification(
                model, config.sparsity_ratio
            )
            return compressed, {"method": "random_sparse", "sparsity": config.sparsity_ratio}

        else:
            # No compression
            return model, {"method": "none"}

    @staticmethod
    def estimate_compression_ratio(original: ModelWeights,
                                  compressed: ModelWeights) -> float:
        """
        Estimate compression ratio.

        Args:
            original: Original model
            compressed: Compressed model

        Returns:
            Compression ratio (e.g., 0.1 = 10x compression)
        """
        # Count non-zero elements in compressed
        non_zero = sum(1 for w in compressed.weights if abs(w) > 1e-10)
        total = len(compressed.weights)

        return non_zero / total if total > 0 else 1.0

    @staticmethod
    def calculate_reconstruction_error(original: ModelWeights,
                                      compressed: ModelWeights) -> float:
        """
        Calculate Mean Squared Error between original and compressed.

        Args:
            original: Original model
            compressed: Compressed model

        Returns:
            MSE
        """
        if len(original.weights) != len(compressed.weights):
            return float('inf')

        mse = sum(
            (o - c) ** 2
            for o, c in zip(original.weights, compressed.weights)
        ) / len(original.weights)

        return mse


class AdaptiveCompression:
    """
    Adaptive compression that adjusts based on training progress.

    Higher compression early in training, lower compression near convergence.
    """

    def __init__(self,
                 initial_ratio: float = 0.01,
                 final_ratio: float = 0.5,
                 total_rounds: int = 100):
        """
        Initialize adaptive compression.

        Args:
            initial_ratio: Compression ratio at start (e.g., 0.01 = 1%)
            final_ratio: Compression ratio at end (e.g., 0.5 = 50%)
            total_rounds: Total training rounds
        """
        self.initial_ratio = initial_ratio
        self.final_ratio = final_ratio
        self.total_rounds = total_rounds
        self.current_round = 0

    def get_compression_ratio(self, round_num: Optional[int] = None) -> float:
        """
        Get compression ratio for current round.

        Uses cosine annealing schedule.

        Args:
            round_num: Current round number

        Returns:
            Compression ratio for this round
        """
        if round_num is None:
            round_num = self.current_round

        # Cosine annealing from initial to final
        progress = min(round_num / self.total_rounds, 1.0)
        cosine_factor = 0.5 * (1 + math.cos(math.pi * (1 - progress)))

        ratio = self.final_ratio + (self.initial_ratio - self.final_ratio) * cosine_factor

        return ratio

    def compress_adaptive(self, model: ModelWeights, round_num: Optional[int] = None) -> Tuple[ModelWeights, Dict]:
        """
        Compress with adaptive ratio.

        Args:
            model: Model to compress
            round_num: Current round

        Returns:
            (compressed_model, metadata)
        """
        if round_num is not None:
            self.current_round = round_num

        ratio = self.get_compression_ratio()

        # Use top-k sparsification with adaptive ratio
        compressed = CommunicationCompression.top_k_sparsification(model, ratio)

        metadata = {
            "method": "adaptive_top_k",
            "ratio": ratio,
            "round": self.current_round
        }

        self.current_round += 1

        return compressed, metadata
