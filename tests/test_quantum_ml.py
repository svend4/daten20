"""
Tests for Quantum Machine Learning Platform (v15.0)

Tests for Quantum Feature Maps, Quantum Neural Networks, Quantum SVM,
Quantum K-Means, Quantum Classifier, QML Trainer, and Hybrid Quantum-Classical
Optimization.

IMPORTANT: These tests verify quantum ML simulation, not execution on real
quantum hardware.
"""

import pytest
import numpy as np


class TestQuantumFeatureMap:
    """Test Quantum Feature Map (v15.0)"""

    def test_import_feature_map(self):
        """Test importing QuantumFeatureMap"""
        from quantum_ml import (
            QuantumFeatureMap,
            FeatureEncoding
        )
        assert QuantumFeatureMap is not None
        assert FeatureEncoding.AMPLITUDE is not None

    def test_create_feature_map(self):
        """Test creating feature map"""
        from quantum_ml import QuantumFeatureMap, FeatureEncoding

        fm = QuantumFeatureMap(num_qubits=4, encoding=FeatureEncoding.ANGLE)
        assert fm is not None
        assert fm.num_qubits == 4

    def test_amplitude_encoding(self):
        """Test amplitude encoding"""
        from quantum_ml import QuantumFeatureMap

        fm = QuantumFeatureMap(num_qubits=3)
        data = np.array([1.0, 2.0, 3.0, 4.0])

        encoded = fm.encode_amplitude(data)
        assert len(encoded) == 2 ** 3
        assert abs(np.linalg.norm(encoded) - 1.0) < 0.01  # Unit norm

    def test_angle_encoding(self):
        """Test angle encoding"""
        from quantum_ml import QuantumFeatureMap

        fm = QuantumFeatureMap(num_qubits=4)
        data = np.array([0.5, 1.0, 1.5, 2.0])

        gates = fm.encode_angle(data)
        assert len(gates) == 4  # One gate per qubit
        assert all(gate[0] == "ry" for gate in gates)

    def test_basis_encoding(self):
        """Test basis encoding"""
        from quantum_ml import QuantumFeatureMap

        fm = QuantumFeatureMap(num_qubits=3)
        value = 5

        encoded = fm.encode_basis(value)
        assert len(encoded) == 3
        assert encoded == "101"  # Binary representation of 5

    async def test_encode_method(self):
        """Test generic encode method"""
        from quantum_ml import QuantumFeatureMap, FeatureEncoding

        fm = QuantumFeatureMap(num_qubits=4, encoding=FeatureEncoding.ANGLE)
        data = np.array([0.5, 1.0, 1.5, 2.0])

        encoded = await fm.encode(data)
        assert encoded is not None


class TestQuantumNeuralNetwork:
    """Test Quantum Neural Network (v15.0)"""

    def test_import_qnn(self):
        """Test importing QuantumNeuralNetwork"""
        from quantum_ml import (
            QuantumNeuralNetwork,
            QuantumCircuitConfig,
            EntanglementPattern
        )
        assert QuantumNeuralNetwork is not None
        assert EntanglementPattern.FULL is not None

    def test_create_qnn(self):
        """Test creating QNN"""
        from quantum_ml import QuantumNeuralNetwork, QuantumCircuitConfig

        config = QuantumCircuitConfig(num_qubits=4, num_layers=2)
        qnn = QuantumNeuralNetwork(config)

        assert qnn is not None
        assert qnn.num_parameters > 0

    def test_initialize_parameters(self):
        """Test parameter initialization"""
        from quantum_ml import QuantumNeuralNetwork, QuantumCircuitConfig

        config = QuantumCircuitConfig(num_qubits=4, num_layers=2)
        qnn = QuantumNeuralNetwork(config)

        params = qnn.get_parameters()
        assert len(params) == qnn.num_parameters
        assert all(-np.pi <= p <= np.pi for p in params)

    def test_build_circuit(self):
        """Test circuit building"""
        from quantum_ml import QuantumNeuralNetwork, QuantumCircuitConfig

        config = QuantumCircuitConfig(num_qubits=4, num_layers=2)
        qnn = QuantumNeuralNetwork(config)

        data = np.random.randn(4)
        circuit = qnn.build_circuit(data)

        assert len(circuit) > 0

    async def test_forward_pass(self):
        """Test forward pass"""
        from quantum_ml import QuantumNeuralNetwork, QuantumCircuitConfig

        config = QuantumCircuitConfig(num_qubits=4, num_layers=2)
        qnn = QuantumNeuralNetwork(config)

        data = np.random.randn(4)
        output = await qnn.forward(data)

        assert isinstance(output, (int, float))
        assert -1 <= output <= 1

    async def test_predict(self):
        """Test batch prediction"""
        from quantum_ml import QuantumNeuralNetwork, QuantumCircuitConfig

        config = QuantumCircuitConfig(num_qubits=4, num_layers=2)
        qnn = QuantumNeuralNetwork(config)

        X = np.random.randn(5, 4)
        predictions = await qnn.predict(X)

        assert len(predictions) == 5
        assert all(p in [0, 1] for p in predictions)


class TestQuantumSVM:
    """Test Quantum SVM (v15.0)"""

    def test_import_qsvm(self):
        """Test importing QuantumSVM"""
        from quantum_ml import (
            QuantumSVM,
            QuantumKernelParams,
            QuantumKernel
        )
        assert QuantumSVM is not None
        assert QuantumKernel.FIDELITY is not None

    def test_create_qsvm(self):
        """Test creating QSVM"""
        from quantum_ml import QuantumSVM, QuantumKernelParams

        params = QuantumKernelParams(num_qubits=4)
        qsvm = QuantumSVM(params)

        assert qsvm is not None

    async def test_quantum_kernel(self):
        """Test quantum kernel computation"""
        from quantum_ml import QuantumSVM, QuantumKernelParams

        params = QuantumKernelParams(num_qubits=4)
        qsvm = QuantumSVM(params)

        x1 = np.random.randn(4)
        x2 = np.random.randn(4)

        kernel_value = await qsvm.quantum_kernel(x1, x2)
        assert 0.0 <= kernel_value <= 1.0

    async def test_kernel_matrix(self):
        """Test kernel matrix computation"""
        from quantum_ml import QuantumSVM, QuantumKernelParams

        params = QuantumKernelParams(num_qubits=4)
        qsvm = QuantumSVM(params)

        X = np.random.randn(5, 4)
        K = await qsvm.compute_kernel_matrix(X)

        assert K.shape == (5, 5)
        # Check symmetry
        assert np.allclose(K, K.T)

    async def test_fit_and_predict(self):
        """Test QSVM training and prediction"""
        from quantum_ml import QuantumSVM, QuantumKernelParams

        params = QuantumKernelParams(num_qubits=4)
        qsvm = QuantumSVM(params)

        X_train = np.random.randn(10, 4)
        y_train = np.random.randint(0, 2, 10)

        await qsvm.fit(X_train, y_train)

        X_test = np.random.randn(3, 4)
        predictions = await qsvm.predict(X_test)

        assert len(predictions) == 3
        assert all(p in [0, 1] for p in predictions)


class TestQuantumKMeans:
    """Test Quantum K-Means (v15.0)"""

    def test_import_qkmeans(self):
        """Test importing QuantumKMeans"""
        from quantum_ml import (
            QuantumKMeans,
            ClusteringResult
        )
        assert QuantumKMeans is not None
        assert ClusteringResult is not None

    def test_create_qkmeans(self):
        """Test creating Quantum K-Means"""
        from quantum_ml import QuantumKMeans

        qkmeans = QuantumKMeans(num_clusters=3, num_qubits=4)
        assert qkmeans is not None
        assert qkmeans.num_clusters == 3

    async def test_quantum_distance(self):
        """Test quantum distance computation"""
        from quantum_ml import QuantumKMeans

        qkmeans = QuantumKMeans(num_clusters=3)

        x1 = np.random.randn(4)
        x2 = np.random.randn(4)

        distance = await qkmeans.quantum_distance(x1, x2)
        assert distance >= 0.0

    async def test_fit_clustering(self):
        """Test clustering fit"""
        from quantum_ml import QuantumKMeans

        qkmeans = QuantumKMeans(num_clusters=3, max_iterations=10)

        X = np.random.randn(20, 4)
        result = await qkmeans.fit(X)

        assert result is not None
        assert len(result.cluster_labels) == 20
        assert result.cluster_centers.shape == (3, 4)
        assert result.inertia >= 0.0

    async def test_predict_clusters(self):
        """Test cluster prediction"""
        from quantum_ml import QuantumKMeans

        qkmeans = QuantumKMeans(num_clusters=3)

        X_train = np.random.randn(20, 4)
        await qkmeans.fit(X_train)

        X_test = np.random.randn(5, 4)
        labels = await qkmeans.predict(X_test)

        assert len(labels) == 5
        assert all(0 <= label < 3 for label in labels)


class TestQuantumClassifier:
    """Test Quantum Classifier (v15.0)"""

    def test_import_classifier(self):
        """Test importing QuantumClassifier"""
        from quantum_ml import QuantumClassifier
        assert QuantumClassifier is not None

    def test_create_classifier(self):
        """Test creating classifier"""
        from quantum_ml import QuantumClassifier

        classifier = QuantumClassifier(num_qubits=4, num_classes=2, num_layers=2)
        assert classifier is not None
        assert classifier.num_classes == 2

    async def test_forward(self):
        """Test forward pass"""
        from quantum_ml import QuantumClassifier

        classifier = QuantumClassifier(num_qubits=4, num_classes=2)

        X = np.random.randn(3, 4)
        logits = await classifier.forward(X)

        assert logits.shape == (3, 2)

    async def test_predict_proba(self):
        """Test probability prediction"""
        from quantum_ml import QuantumClassifier

        classifier = QuantumClassifier(num_qubits=4, num_classes=2)

        X = np.random.randn(3, 4)
        proba = await classifier.predict_proba(X)

        assert proba.shape == (3, 2)
        # Check probabilities sum to 1
        assert np.allclose(np.sum(proba, axis=1), 1.0)

    async def test_predict(self):
        """Test label prediction"""
        from quantum_ml import QuantumClassifier

        classifier = QuantumClassifier(num_qubits=4, num_classes=3)

        X = np.random.randn(5, 4)
        predictions = await classifier.predict(X)

        assert len(predictions) == 5
        assert all(0 <= p < 3 for p in predictions)


class TestQMLTrainer:
    """Test QML Trainer (v15.0)"""

    def test_import_trainer(self):
        """Test importing QMLTrainer"""
        from quantum_ml import (
            QMLTrainer,
            TrainingConfig,
            OptimizerType
        )
        assert QMLTrainer is not None
        assert OptimizerType.ADAM is not None

    def test_create_trainer(self):
        """Test creating trainer"""
        from quantum_ml import (
            QMLTrainer,
            QuantumClassifier,
            TrainingConfig
        )

        classifier = QuantumClassifier(num_qubits=4, num_classes=2)
        config = TrainingConfig(num_epochs=10)
        trainer = QMLTrainer(classifier, config)

        assert trainer is not None

    async def test_compute_loss(self):
        """Test loss computation"""
        from quantum_ml import (
            QMLTrainer,
            QuantumClassifier,
            TrainingConfig
        )

        classifier = QuantumClassifier(num_qubits=4, num_classes=2)
        config = TrainingConfig()
        trainer = QMLTrainer(classifier, config)

        X = np.random.randn(5, 4)
        y = np.random.randint(0, 2, 5)

        loss = await trainer.compute_loss(X, y)
        assert loss >= 0.0

    async def test_fit_training(self):
        """Test model training"""
        from quantum_ml import (
            QMLTrainer,
            QuantumClassifier,
            TrainingConfig
        )

        classifier = QuantumClassifier(num_qubits=4, num_classes=2)
        config = TrainingConfig(num_epochs=5, batch_size=5)
        trainer = QMLTrainer(classifier, config)

        X = np.random.randn(20, 4)
        y = np.random.randint(0, 2, 20)

        history = await trainer.fit(X, y)

        assert "loss" in history
        assert "val_loss" in history
        assert len(history["loss"]) <= 5


class TestHybridQuantumClassicalOptimizer:
    """Test Hybrid Quantum-Classical Optimizer (v15.0)"""

    def test_import_hybrid_optimizer(self):
        """Test importing HybridQuantumClassicalOptimizer"""
        from quantum_ml import HybridQuantumClassicalOptimizer
        assert HybridQuantumClassicalOptimizer is not None

    def test_create_hybrid_optimizer(self):
        """Test creating hybrid optimizer"""
        from quantum_ml import HybridQuantumClassicalOptimizer, OptimizerType

        optimizer = HybridQuantumClassicalOptimizer(
            num_qubits=4,
            num_quantum_layers=2,
            classical_optimizer=OptimizerType.ADAM
        )

        assert optimizer is not None

    async def test_quantum_objective(self):
        """Test quantum objective evaluation"""
        from quantum_ml import HybridQuantumClassicalOptimizer

        optimizer = HybridQuantumClassicalOptimizer(num_qubits=4)

        parameters = np.random.uniform(-np.pi, np.pi, optimizer.quantum_circuit.num_parameters)
        problem_data = {"type": "maxcut", "graph": [[0, 1], [1, 2]]}

        cost = await optimizer.quantum_objective(parameters, problem_data)
        assert isinstance(cost, float)

    async def test_optimize(self):
        """Test hybrid optimization"""
        from quantum_ml import HybridQuantumClassicalOptimizer

        optimizer = HybridQuantumClassicalOptimizer(num_qubits=4)

        problem_data = {"type": "maxcut"}
        result = await optimizer.optimize(problem_data, num_iterations=10)

        assert result is not None
        assert "best_parameters" in result
        assert "best_cost" in result
        assert "history" in result


class TestIntegratedSystem:
    """Test Integrated Quantum ML System (v15.0)"""

    def test_import_integrated(self):
        """Test importing integrated system"""
        from quantum_ml import (
            IntegratedQuantumMLSystem,
            QuantumMLConfig,
            get_quantum_ml_system
        )
        assert IntegratedQuantumMLSystem is not None
        assert QuantumMLConfig is not None
        assert get_quantum_ml_system is not None

    def test_create_integrated_system(self):
        """Test creating integrated system"""
        from quantum_ml import IntegratedQuantumMLSystem, QuantumMLConfig

        config = QuantumMLConfig()
        system = IntegratedQuantumMLSystem(config)

        assert system is not None
        assert system.feature_map is not None
        assert system.qnn is not None
        assert system.qsvm is not None

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        from quantum_ml import get_quantum_ml_system

        system1 = get_quantum_ml_system()
        system2 = get_quantum_ml_system()

        assert system1 is system2

    def test_system_status(self):
        """Test system status"""
        from quantum_ml import IntegratedQuantumMLSystem

        system = IntegratedQuantumMLSystem()
        status = system.get_system_status()

        assert "feature_map_enabled" in status
        assert "qnn_enabled" in status
        assert "qsvm_enabled" in status

    async def test_train_classifier_integration(self):
        """Test integrated classifier training"""
        from quantum_ml import IntegratedQuantumMLSystem, TrainingConfig

        system = IntegratedQuantumMLSystem()

        X_train = np.random.randn(20, 4)
        y_train = np.random.randint(0, 2, 20)

        config = TrainingConfig(num_epochs=3, batch_size=5)
        result = await system.train_classifier(X_train, y_train, config)

        assert result is not None
        assert result.predictions is not None
        assert result.accuracy is not None

    async def test_quantum_svm_integration(self):
        """Test integrated QSVM"""
        from quantum_ml import IntegratedQuantumMLSystem

        system = IntegratedQuantumMLSystem()

        X_train = np.random.randn(10, 4)
        y_train = np.random.randint(0, 2, 10)
        X_test = np.random.randn(3, 4)
        y_test = np.random.randint(0, 2, 3)

        result = await system.quantum_svm_classification(X_train, y_train, X_test, y_test)

        assert result is not None
        assert result.predictions is not None

    async def test_quantum_clustering_integration(self):
        """Test integrated quantum clustering"""
        from quantum_ml import IntegratedQuantumMLSystem

        system = IntegratedQuantumMLSystem()

        X = np.random.randn(15, 4)
        result = await system.quantum_clustering(X, num_clusters=3)

        assert result is not None
        assert len(result.cluster_labels) == 15
        assert result.cluster_centers.shape == (3, 4)

    async def test_benchmark_performance(self):
        """Test performance benchmarking"""
        from quantum_ml import IntegratedQuantumMLSystem

        system = IntegratedQuantumMLSystem()
        benchmarks = await system.benchmark_performance()

        assert isinstance(benchmarks, dict)
