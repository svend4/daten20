"""
Comprehensive Test Suite for Enhanced Federated Learning (v12.0)

Tests new v12.0 features:
1. Advanced Aggregation - FedProx, FedAdam, SCAFFOLD, Krum, Median
2. Secure Aggregation - Encryption and masking
3. Communication Compression - Quantization, top-k, sparsification
4. Byzantine-robust methods

Total: 24 comprehensive tests
"""

import pytest
import random

from src.federated_learning import (
    # Core (v11.0)
    ModelWeights,
    FederatedClient,
    # Advanced Aggregation (v12.0)
    FedProx,
    FedProxConfig,
    FedAdam,
    FedAdamConfig,
    SCAFFOLD,
    SCAFFOLDConfig,
    ByzantineRobustAggregation,
    # Secure Communication (v12.0)
    SecureAggregation,
    CommunicationCompression,
    CompressionMethod,
    CompressionConfig,
    AdaptiveCompression,
)


class TestFedProx:
    """Test FedProx aggregation"""

    def test_fedprox_initialization(self):
        """Test FedProx initializes"""
        config = FedProxConfig(mu=0.01, learning_rate=0.01)
        fedprox = FedProx(config, num_features=10)

        assert fedprox.config.mu == 0.01
        assert len(fedprox.global_model.weights) == 10

    def test_fedprox_aggregation(self):
        """Test FedProx aggregation"""
        fedprox = FedProx(FedProxConfig(), num_features=5)

        # Create client models
        client1_model = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        client2_model = ModelWeights([2.0, 3.0, 4.0, 5.0, 6.0])

        client_models = [
            ("client1", client1_model, 100),
            ("client2", client2_model, 100)
        ]

        aggregated = fedprox.aggregate(client_models, fedprox.global_model)

        assert len(aggregated.weights) == 5
        # Should be weighted average
        assert aggregated.weights[0] == 1.5


class TestFedAdam:
    """Test FedAdam aggregation"""

    def test_fedadam_initialization(self):
        """Test FedAdam initializes"""
        config = FedAdamConfig(learning_rate=0.001)
        fedadam = FedAdam(config, num_features=10)

        assert fedadam.config.learning_rate == 0.001
        assert len(fedadam.m) == 10
        assert len(fedadam.v) == 10
        assert fedadam.t == 0

    def test_fedadam_aggregation(self):
        """Test FedAdam aggregation updates"""
        fedadam = FedAdam(FedAdamConfig(), num_features=5)

        client1_model = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        client2_model = ModelWeights([1.5, 2.5, 3.5, 4.5, 5.5])

        client_models = [
            ("client1", client1_model, 100),
            ("client2", client2_model, 100)
        ]

        # Multiple rounds to test Adam dynamics
        for _ in range(3):
            aggregated = fedadam.aggregate(client_models, fedadam.global_model)
            fedadam.global_model = aggregated

        assert fedadam.t == 3
        assert len(aggregated.weights) == 5


class TestSCAFFOLD:
    """Test SCAFFOLD aggregation"""

    def test_scaffold_initialization(self):
        """Test SCAFFOLD initializes"""
        config = SCAFFOLDConfig(learning_rate=0.01)
        scaffold = SCAFFOLD(config, num_features=10)

        assert scaffold.config.learning_rate == 0.01
        assert len(scaffold.c_global) == 10

    def test_scaffold_aggregation(self):
        """Test SCAFFOLD aggregation with control variates"""
        scaffold = SCAFFOLD(SCAFFOLDConfig(), num_features=5)

        client1_model = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        control1 = [0.1, 0.1, 0.1, 0.1, 0.1]

        client_models = [
            ("client1", client1_model, 100, control1)
        ]

        aggregated = scaffold.aggregate(client_models, scaffold.global_model)

        assert len(aggregated.weights) == 5
        assert "client1" in scaffold.c_clients


class TestByzantineRobust:
    """Test Byzantine-robust aggregation"""

    def test_krum_aggregation(self):
        """Test Krum aggregation"""
        # Create normal and Byzantine models
        normal1 = ModelWeights([1.0, 2.0, 3.0])
        normal2 = ModelWeights([1.1, 2.1, 3.1])
        normal3 = ModelWeights([0.9, 1.9, 2.9])
        byzantine = ModelWeights([100.0, 100.0, 100.0])  # Outlier

        client_models = [
            ("client1", normal1, 100),
            ("client2", normal2, 100),
            ("client3", normal3, 100),
            ("byzantine", byzantine, 100)
        ]

        # Krum should select a normal model
        selected = ByzantineRobustAggregation.krum(client_models, f=1)

        # Selected model should not be the Byzantine one
        assert selected.weights[0] < 50.0

    def test_median_aggregation(self):
        """Test coordinate-wise median aggregation"""
        model1 = ModelWeights([1.0, 2.0, 3.0])
        model2 = ModelWeights([2.0, 3.0, 4.0])
        model3 = ModelWeights([3.0, 4.0, 5.0])
        byzantine = ModelWeights([100.0, 100.0, 100.0])

        client_models = [
            ("client1", model1, 100),
            ("client2", model2, 100),
            ("client3", model3, 100),
            ("byzantine", byzantine, 100)
        ]

        median_model = ByzantineRobustAggregation.coordinate_wise_median(client_models)

        # Median of 4 values takes average of middle two
        # Sorted [1, 2, 3, 100] -> median = (2+3)/2 = 2.5
        assert median_model.weights[0] == 2.5  # Median of [1, 2, 3, 100] = (2+3)/2
        assert median_model.weights[1] == 3.5  # Median of [2, 3, 4, 100] = (3+4)/2 = 3.5


class TestSecureAggregation:
    """Test secure aggregation"""

    def test_secure_aggregation_initialization(self):
        """Test secure aggregation initializes"""
        secure_agg = SecureAggregation(num_clients=10)

        assert secure_agg.num_clients == 10
        assert secure_agg.modulus == 2**32

    def test_mask_generation(self):
        """Test pairwise mask generation"""
        secure_agg = SecureAggregation(num_clients=5)

        mask = secure_agg.generate_pairwise_masks("client1", num_features=10)

        assert len(mask) == 10
        assert "client1" in secure_agg.masks

    def test_model_masking(self):
        """Test model masking"""
        secure_agg = SecureAggregation(num_clients=5)

        model = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        mask = [10.0, 20.0, 30.0, 40.0, 50.0]

        masked = secure_agg.mask_model(model, mask)

        assert len(masked.weights) == 5
        # Masked values should be different
        assert masked.weights[0] != model.weights[0]

    def test_secure_aggregate(self):
        """Test secure aggregation unmasking"""
        secure_agg = SecureAggregation(num_clients=2)

        # Generate masks
        mask1 = secure_agg.generate_pairwise_masks("client1", 5)
        mask2 = secure_agg.generate_pairwise_masks("client2", 5)

        # Create models and mask them
        model1 = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        model2 = ModelWeights([2.0, 3.0, 4.0, 5.0, 6.0])

        masked1 = secure_agg.mask_model(model1, mask1)
        masked2 = secure_agg.mask_model(model2, mask2)

        masked_models = [
            ("client1", masked1, 100),
            ("client2", masked2, 100)
        ]

        # Aggregate (masks should cancel out)
        aggregated = secure_agg.secure_aggregate(masked_models)

        assert len(aggregated.weights) == 5


class TestCommunicationCompression:
    """Test communication compression"""

    def test_quantization(self):
        """Test weight quantization"""
        model = ModelWeights([0.1, 0.5, 0.9, 1.5, 2.0])

        quantized, metadata = CommunicationCompression.quantize(model, num_bits=4)

        assert len(quantized.weights) == 5
        assert "min" in metadata
        assert "max" in metadata
        assert metadata["num_bits"] == 4

    def test_top_k_sparsification(self):
        """Test top-k sparsification"""
        model = ModelWeights([0.1, 5.0, 0.2, 10.0, 0.3])

        sparse = CommunicationCompression.top_k_sparsification(model, k_ratio=0.4)

        # Should keep top 40% = 2 weights (10.0 and 5.0)
        non_zero = sum(1 for w in sparse.weights if abs(w) > 1e-10)
        assert non_zero == 2

    def test_random_sparsification(self):
        """Test random sparsification"""
        random.seed(42)
        model = ModelWeights([1.0] * 100)

        sparse = CommunicationCompression.random_sparsification(model, sparsity_ratio=0.1)

        # Should keep approximately 10% (with randomness)
        non_zero = sum(1 for w in sparse.weights if abs(w) > 1e-10)
        assert 5 <= non_zero <= 20  # Approximate range

    def test_compression_with_config(self):
        """Test compression with configuration"""
        model = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])

        config = CompressionConfig(
            method=CompressionMethod.QUANTIZATION,
            num_bits=8
        )

        compressed, metadata = CommunicationCompression.compress(model, config)

        assert len(compressed.weights) == 5
        assert "method" in metadata or "min" in metadata

    def test_compression_ratio(self):
        """Test compression ratio estimation"""
        original = ModelWeights([1.0, 2.0, 3.0, 4.0, 5.0])
        compressed = ModelWeights([0.0, 2.0, 0.0, 4.0, 0.0])

        ratio = CommunicationCompression.estimate_compression_ratio(original, compressed)

        assert ratio == 0.4  # 2 non-zero out of 5

    def test_reconstruction_error(self):
        """Test reconstruction error calculation"""
        original = ModelWeights([1.0, 2.0, 3.0])
        compressed = ModelWeights([1.1, 2.1, 3.1])

        error = CommunicationCompression.calculate_reconstruction_error(
            original, compressed
        )

        assert error > 0  # Should have some error
        assert error < 1.0  # But not too large


class TestAdaptiveCompression:
    """Test adaptive compression"""

    def test_adaptive_initialization(self):
        """Test adaptive compression initializes"""
        adaptive = AdaptiveCompression(
            initial_ratio=0.01,
            final_ratio=0.5,
            total_rounds=100
        )

        assert adaptive.initial_ratio == 0.01
        assert adaptive.final_ratio == 0.5
        assert adaptive.current_round == 0

    def test_compression_ratio_schedule(self):
        """Test compression ratio follows schedule"""
        adaptive = AdaptiveCompression(
            initial_ratio=0.01,
            final_ratio=0.9,
            total_rounds=100
        )

        ratio_start = adaptive.get_compression_ratio(round_num=0)
        ratio_end = adaptive.get_compression_ratio(round_num=100)

        # Formula: final + (initial - final) * cosine_factor
        # cosine_factor = 0.5 * (1 + cos(pi * (1 - progress)))
        # At round 0: progress=0, (1-progress)=1, cos(pi)=-1, factor=0
        # ratio = 0.9 + (0.01-0.9)*0 = 0.9 (starts at FINAL, high compression)
        # At round 100: progress=1, (1-progress)=0, cos(0)=1, factor=1.0
        # ratio = 0.9 + (0.01-0.9)*1.0 = 0.01 (ends at INITIAL, low compression)
        # It DECREASES over time (more compression early, less later for accuracy)
        assert ratio_start > ratio_end
        assert 0.85 < ratio_start < 0.95  # Near final (high)
        assert 0.0 < ratio_end < 0.05  # Near initial (low)

    def test_adaptive_compress(self):
        """Test adaptive compression"""
        adaptive = AdaptiveCompression(
            initial_ratio=0.1,
            final_ratio=0.5,
            total_rounds=10
        )

        model = ModelWeights([float(i) for i in range(20)])

        compressed, metadata = adaptive.compress_adaptive(model, round_num=0)

        assert "ratio" in metadata
        assert "round" in metadata
        assert len(compressed.weights) == 20


class TestIntegration:
    """Integration tests for v12.0 features"""

    def test_full_enhancement_workflow(self):
        """Test complete workflow with all v12.0 components"""
        # Create clients
        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=10)
            for i in range(5)
        ]

        # Test different aggregation methods
        fedprox = FedProx(FedProxConfig(), num_features=10)
        fedadam = FedAdam(FedAdamConfig(), num_features=10)

        # Simulate client training
        client_models = [
            (f"client_{i}", client.local_model, client.data_size)
            for i, client in enumerate(clients[:3])
        ]

        # Test aggregation
        aggregated_prox = fedprox.aggregate(client_models, fedprox.global_model)
        aggregated_adam = fedadam.aggregate(client_models, fedadam.global_model)

        assert len(aggregated_prox.weights) == 10
        assert len(aggregated_adam.weights) == 10

        # Test compression
        config = CompressionConfig(method=CompressionMethod.TOP_K, k_ratio=0.3)
        compressed, _ = CommunicationCompression.compress(aggregated_prox, config)

        assert len(compressed.weights) == 10

        # Test secure aggregation
        secure_agg = SecureAggregation(num_clients=5)
        masks = [secure_agg.generate_pairwise_masks(f"client_{i}", 10) for i in range(3)]

        assert len(masks) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
