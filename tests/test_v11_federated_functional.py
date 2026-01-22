"""
Functional Test Suite for Federated Learning (v11.0)

Tests REAL federated learning implementation:
1. ModelWeights - Weight representation and operations
2. FederatedClient - Client creation and local training
3. FederatedAveraging - FedAvg aggregation algorithm
4. DifferentialPrivacy - Privacy mechanisms
5. FederatedLearningEngine - Complete system integration
6. Measurable results - Loss reduction, convergence

Total: 15+ comprehensive functional tests
"""

import pytest
from src.federated_learning import (
    ModelWeights,
    FederatedClient,
    FederatedAveraging,
    DifferentialPrivacy,
    FederatedLearningEngine,
    FederatedConfig,
    AggregationStrategy,
    run_federated_learning,
    get_federated_learning_engine,
)


class TestModelWeights:
    """Test model weight representation"""

    def test_model_weights_creation(self):
        """Test creating model weights"""
        weights = ModelWeights(weights=[0.1, 0.2, 0.3])

        assert weights is not None
        assert len(weights) == 3
        assert weights.weights == [0.1, 0.2, 0.3]

    def test_model_weights_copy(self):
        """Test copying model weights"""
        original = ModelWeights(weights=[1.0, 2.0, 3.0])
        copy = original.copy()

        assert copy.weights == original.weights
        # Modify copy shouldn't affect original
        copy.weights[0] = 999.0
        assert original.weights[0] == 1.0


class TestFederatedClient:
    """Test federated client"""

    def test_client_initialization(self):
        """Test client initializes correctly"""
        client = FederatedClient("client_1", data_size=100, num_features=5)

        assert client is not None
        assert client.client_id == "client_1"
        assert client.data_size == 100
        assert client.num_features == 5
        assert len(client.local_model) == 5

    def test_client_local_training(self):
        """Test client can train locally"""
        client = FederatedClient("client_1", data_size=100, num_features=10)

        # Global model
        global_model = ModelWeights(weights=[0.0] * 10)

        # Train locally
        updated_model, loss = client.train_local(global_model, num_epochs=1)

        assert updated_model is not None
        assert len(updated_model) == 10
        assert loss >= 0.0  # Loss should be non-negative
        assert loss < float('inf')

    def test_client_training_reduces_loss(self):
        """Test that training reduces loss over rounds"""
        client = FederatedClient("client_1", data_size=100, num_features=10)
        global_model = ModelWeights(weights=[0.0] * 10)

        # First training
        _, loss1 = client.train_local(global_model, num_epochs=1)

        # Second training (loss should decrease)
        _, loss2 = client.train_local(global_model, num_epochs=1)

        # Loss should decrease over training rounds
        assert loss2 < loss1


class TestFederatedAveraging:
    """Test FedAvg algorithm"""

    def test_fedavg_initialization(self):
        """Test FedAvg initializes correctly"""
        fed_avg = FederatedAveraging(num_features=10)

        assert fed_avg is not None
        assert fed_avg.num_features == 10
        assert len(fed_avg.global_model) == 10
        assert fed_avg.round_number == 0

    def test_fedavg_aggregation_single_client(self):
        """Test aggregation with single client"""
        fed_avg = FederatedAveraging(num_features=5)

        client_model = ModelWeights(weights=[1.0, 2.0, 3.0, 4.0, 5.0])
        client_updates = [("client_1", client_model, 100)]

        aggregated = fed_avg.aggregate(client_updates)

        # With single client, result should equal client model
        assert aggregated.weights == client_model.weights

    def test_fedavg_aggregation_weighted(self):
        """Test weighted aggregation with multiple clients"""
        fed_avg = FederatedAveraging(num_features=3)

        # Two clients with different data sizes
        model1 = ModelWeights(weights=[1.0, 2.0, 3.0])
        model2 = ModelWeights(weights=[3.0, 4.0, 5.0])

        client_updates = [
            ("client_1", model1, 100),  # 100 samples
            ("client_2", model2, 100),  # 100 samples
        ]

        aggregated = fed_avg.aggregate(client_updates)

        # Equal weights (50/50): average of [1,2,3] and [3,4,5] = [2,3,4]
        assert abs(aggregated.weights[0] - 2.0) < 0.01
        assert abs(aggregated.weights[1] - 3.0) < 0.01
        assert abs(aggregated.weights[2] - 4.0) < 0.01

    def test_fedavg_client_selection(self):
        """Test client selection mechanism"""
        fed_avg = FederatedAveraging(num_features=5)

        # Create 10 clients
        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=5)
            for i in range(10)
        ]

        # Select 30% of clients
        selected = fed_avg.select_clients(clients, fraction=0.3)

        # Should select 3 clients (30% of 10)
        assert len(selected) == 3
        # Selected should be subset of all clients
        assert all(c in clients for c in selected)

    def test_fedavg_run_round(self):
        """Test running complete federated round"""
        fed_avg = FederatedAveraging(num_features=10)

        # Create clients
        clients = [
            FederatedClient(f"client_{i}", data_size=100, num_features=10)
            for i in range(5)
        ]

        # Run one round
        result = fed_avg.run_round(clients, client_fraction=0.4, local_epochs=1)

        assert result is not None
        assert result['round'] == 1
        assert result['participating_clients'] == 2  # 40% of 5 = 2
        assert result['total_clients'] == 5
        assert 'average_loss' in result
        assert result['average_loss'] >= 0.0


class TestDifferentialPrivacy:
    """Test differential privacy mechanisms"""

    def test_dp_initialization(self):
        """Test DP mechanism initializes correctly"""
        dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5)

        assert dp is not None
        assert dp.epsilon == 1.0
        assert dp.delta == 1e-5
        assert dp.noise_scale > 0.0

    def test_dp_add_noise(self):
        """Test adding noise to model"""
        dp = DifferentialPrivacy(epsilon=1.0)

        model = ModelWeights(weights=[1.0, 2.0, 3.0])
        noised_model = dp.add_noise(model, sensitivity=1.0)

        assert noised_model is not None
        assert len(noised_model) == len(model)
        # Noised model should be different from original
        # (with very high probability)
        differences = sum(
            1 for i in range(len(model))
            if abs(noised_model.weights[i] - model.weights[i]) > 0.01
        )
        assert differences > 0  # At least some weights should be different

    def test_dp_clip_gradient(self):
        """Test gradient clipping"""
        dp = DifferentialPrivacy(epsilon=1.0)

        # Model with large norm
        model = ModelWeights(weights=[10.0, 10.0, 10.0])
        # Norm = sqrt(100+100+100) = sqrt(300) ≈ 17.3

        # Clip to norm of 5.0
        clipped = dp.clip_gradient(model, clip_norm=5.0)

        # Calculate clipped norm
        import math
        clipped_norm = math.sqrt(sum(w**2 for w in clipped.weights))

        # Should be clipped to 5.0
        assert abs(clipped_norm - 5.0) < 0.1

    def test_dp_privacy_budget(self):
        """Test different privacy budgets"""
        # High privacy (low epsilon) = more noise
        dp_high_privacy = DifferentialPrivacy(epsilon=0.1)

        # Low privacy (high epsilon) = less noise
        dp_low_privacy = DifferentialPrivacy(epsilon=10.0)

        # High privacy should have larger noise scale
        assert dp_high_privacy.noise_scale > dp_low_privacy.noise_scale


class TestFederatedLearningEngine:
    """Test complete federated learning engine"""

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        config = FederatedConfig(num_clients=5, rounds=10)
        engine = FederatedLearningEngine(config)

        assert engine is not None
        assert len(engine.clients) == 5
        assert engine.config.rounds == 10
        assert engine.fed_avg is not None

    def test_engine_register_client(self):
        """Test registering new client"""
        config = FederatedConfig(num_clients=3)
        engine = FederatedLearningEngine(config)

        initial_count = len(engine.clients)

        # Register new client
        success = engine.register_client("new_client", data_size=200)

        assert success is True
        assert len(engine.clients) == initial_count + 1

    def test_engine_train_round(self):
        """Test running single training round"""
        config = FederatedConfig(num_clients=5, client_fraction=0.4)
        engine = FederatedLearningEngine(config)

        result = engine.train_round(round_num=1)

        assert result is not None
        assert result['round'] == 1
        assert 'average_loss' in result
        assert 'participating_clients' in result
        assert result['participating_clients'] > 0

    def test_engine_complete_training(self):
        """Test complete training workflow"""
        config = FederatedConfig(
            num_clients=5,
            rounds=10,
            client_fraction=0.4,
            local_epochs=1
        )
        engine = FederatedLearningEngine(config)

        # Run complete training
        summary = engine.train(num_rounds=10)

        assert summary is not None
        assert summary['status'] == 'FUNCTIONAL'
        assert summary['total_rounds'] == 10
        assert summary['initial_loss'] > 0.0
        assert summary['final_loss'] > 0.0
        # Loss should improve (decrease)
        assert summary['final_loss'] < summary['initial_loss']
        assert summary['loss_improvement_percent'] > 0.0

    def test_engine_with_differential_privacy(self):
        """Test training with differential privacy enabled"""
        config = FederatedConfig(
            num_clients=5,
            rounds=5,
            enable_differential_privacy=True,
            privacy_epsilon=1.0
        )
        engine = FederatedLearningEngine(config)

        assert engine.dp_mechanism is not None

        result = engine.train_round()

        assert 'differential_privacy' in result
        assert result['differential_privacy'] is True
        assert 'privacy_budget' in result


class TestIntegration:
    """Integration tests"""

    def test_run_federated_learning_basic(self):
        """Test basic federated learning run"""
        result = run_federated_learning(
            num_clients=5,
            num_rounds=10,
            client_fraction=0.4,
            local_epochs=1,
            enable_dp=False
        )

        assert result is not None
        assert result['status'] == 'FUNCTIONAL'
        assert result['num_clients'] == 5
        assert result['num_rounds'] == 10
        assert result['final_loss'] > 0.0
        assert result['loss_improvement_percent'] >= 0.0

    def test_run_federated_learning_with_dp(self):
        """Test federated learning with differential privacy"""
        result = run_federated_learning(
            num_clients=5,
            num_rounds=10,
            enable_dp=True,
            epsilon=1.0
        )

        assert result is not None
        assert result['differential_privacy_enabled'] is True
        assert result['privacy_budget_epsilon'] == 1.0
        assert result['status'] == 'FUNCTIONAL'

    def test_convergence_over_rounds(self):
        """Test that loss converges over training rounds"""
        result = run_federated_learning(
            num_clients=10,
            num_rounds=20,
            client_fraction=0.3,
            local_epochs=1
        )

        loss_history = result['loss_history']

        # Loss should generally decrease
        assert loss_history[0] > loss_history[-1]

        # Convergence indicator should be positive
        assert result['convergence_indicator'] >= 0.0

    def test_singleton_accessor(self):
        """Test singleton pattern works"""
        engine1 = get_federated_learning_engine()
        engine2 = get_federated_learning_engine()

        assert engine1 is engine2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
