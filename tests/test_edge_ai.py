"""
Comprehensive Test Suite for Edge AI Platform (v16.0)

Tests all 7 subsystems and integrated system:
1. EdgeDeviceManager - Device registration & monitoring
2. DistributedEdgeTraining - Federated & split learning
3. EdgeInferenceOptimizer - Model optimization
4. ModelCompressionEngine - Model compression
5. EdgeOrchestrationSystem - Workload orchestration
6. EdgeCloudSynchronization - Cloud synchronization
7. EdgeAnalyticsPipeline - Real-time analytics
8. IntegratedEdgeAISystem - Unified integration

Total: 48 tests
"""

import asyncio
import pytest
from datetime import datetime

from src.edge_ai import (
    # Enums
    DeviceTier,
    TrainingMode,
    CompressionType,
    OptimizationTarget,
    PlacementStrategy,
    SyncStrategy,
    # Data Classes
    EdgeDevice,
    EdgeAIConfig,
    # Service Classes
    EdgeDeviceManager,
    DistributedEdgeTraining,
    EdgeInferenceOptimizer,
    ModelCompressionEngine,
    EdgeOrchestrationSystem,
    EdgeCloudSynchronization,
    EdgeAnalyticsPipeline,
    # Integrated System
    IntegratedEdgeAISystem,
    # Singletons
    get_edge_ai_system,
)


# ============================================================================
# 1. EdgeDeviceManager Tests
# ============================================================================


class TestEdgeDeviceManager:
    """Test Edge Device Manager subsystem"""

    @pytest.mark.asyncio
    async def test_register_device(self):
        """Test device registration"""
        manager = EdgeDeviceManager()
        device = await manager.register_device(
            device_id="test_device_001",
            device_info={
                "tier": "tier_3_edge_server",
                "cpu_cores": 4,
                "ram_mb": 4096,
                "storage_gb": 64,
                "has_gpu": True,
            },
        )
        assert device is not None
        assert device.device_id == "test_device_001"
        assert device.device_tier == DeviceTier.TIER_3_EDGE_SERVER
        assert device.cpu_cores == 4
        assert device.status == "active"

    @pytest.mark.asyncio
    async def test_get_device(self):
        """Test retrieving device info"""
        manager = EdgeDeviceManager()
        await manager.register_device(
            device_id="test_device_002",
            device_info={"tier": "tier_2_gateway", "cpu_cores": 2, "ram_mb": 2048},
        )

        device = await manager.get_device("test_device_002")
        assert device is not None
        assert device.device_id == "test_device_002"

    @pytest.mark.asyncio
    async def test_list_devices(self):
        """Test listing all devices"""
        manager = EdgeDeviceManager()
        await manager.register_device(
            "dev1", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )
        await manager.register_device(
            "dev2", {"tier": "tier_2_gateway", "cpu_cores": 2}
        )

        devices = await manager.list_devices()
        assert len(devices) >= 2

    @pytest.mark.asyncio
    async def test_update_device_metrics(self):
        """Test updating device metrics"""
        manager = EdgeDeviceManager()
        await manager.register_device(
            "metrics_device", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        await manager.update_device_metrics(
            device_id="metrics_device",
            cpu_utilization=75.0,
            memory_utilization=60.0,
            inference_latency_ms=8.5,
        )

        metrics = await manager.get_device_metrics("metrics_device")
        assert metrics is not None
        assert metrics.cpu_utilization == 75.0

    @pytest.mark.asyncio
    async def test_decommission_device(self):
        """Test device decommissioning"""
        manager = EdgeDeviceManager()
        await manager.register_device(
            "decomm_device", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        result = await manager.decommission_device("decomm_device")
        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_get_device_by_tier(self):
        """Test filtering devices by tier"""
        manager = EdgeDeviceManager()
        await manager.register_device(
            "tier3_dev", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        tier3_devices = await manager.get_devices_by_tier(DeviceTier.TIER_3_EDGE_SERVER)
        assert len(tier3_devices) > 0


# ============================================================================
# 2. DistributedEdgeTraining Tests
# ============================================================================


class TestDistributedEdgeTraining:
    """Test Distributed Edge Training subsystem"""

    @pytest.mark.asyncio
    async def test_start_federated_training(self):
        """Test starting federated training job"""
        training = DistributedEdgeTraining()
        job = await training.start_federated_training(
            model_architecture="resnet18",
            dataset_id="imagenet_subset",
            participating_devices=["device_1", "device_2", "device_3"],
            total_rounds=50,
        )

        assert job is not None
        assert job.training_mode == TrainingMode.FEDERATED
        assert job.total_rounds == 50
        assert len(job.participating_devices) == 3

    @pytest.mark.asyncio
    async def test_start_split_learning(self):
        """Test starting split learning job"""
        training = DistributedEdgeTraining()
        job = await training.start_split_learning(
            model_architecture="mobilenet_v2",
            dataset_id="cifar10",
            edge_device="edge_device_1",
            cloud_server="cloud_server_1",
            split_layer=5,
        )

        assert job is not None
        assert job.training_mode == TrainingMode.SPLIT_LEARNING

    @pytest.mark.asyncio
    async def test_training_round(self):
        """Test executing a training round"""
        training = DistributedEdgeTraining()
        job = await training.start_federated_training(
            "resnet18", "dataset", ["d1", "d2"], total_rounds=10
        )

        result = await training.execute_training_round(job.job_id)
        assert result.get("status") == "success"
        assert "round_loss" in result

    @pytest.mark.asyncio
    async def test_get_training_status(self):
        """Test getting training job status"""
        training = DistributedEdgeTraining()
        job = await training.start_federated_training(
            "resnet18", "dataset", ["d1"], total_rounds=10
        )

        status = await training.get_training_status(job.job_id)
        assert status is not None
        assert "status" in status

    @pytest.mark.asyncio
    async def test_aggregate_models(self):
        """Test model aggregation"""
        training = DistributedEdgeTraining()

        device_models = {
            "device_1": {"weights": [1.0, 2.0, 3.0]},
            "device_2": {"weights": [1.5, 2.5, 3.5]},
        }

        aggregated = await training.aggregate_models(
            device_models, aggregation_method="fedavg"
        )
        assert aggregated is not None
        assert "global_model" in aggregated

    @pytest.mark.asyncio
    async def test_stop_training(self):
        """Test stopping training job"""
        training = DistributedEdgeTraining()
        job = await training.start_federated_training(
            "resnet18", "dataset", ["d1"], total_rounds=10
        )

        result = await training.stop_training(job.job_id)
        assert result.get("status") == "success"


# ============================================================================
# 3. EdgeInferenceOptimizer Tests
# ============================================================================


class TestEdgeInferenceOptimizer:
    """Test Edge Inference Optimizer subsystem"""

    @pytest.mark.asyncio
    async def test_optimize_for_latency(self):
        """Test optimization for latency"""
        optimizer = EdgeInferenceOptimizer()
        result = await optimizer.optimize_model(
            model_id="model_001",
            target_framework="tflite",
            optimization_target=OptimizationTarget.LATENCY,
        )

        assert result.get("status") == "success"
        assert "optimized_model_id" in result

    @pytest.mark.asyncio
    async def test_optimize_for_throughput(self):
        """Test optimization for throughput"""
        optimizer = EdgeInferenceOptimizer()
        result = await optimizer.optimize_model(
            model_id="model_002",
            target_framework="onnx",
            optimization_target=OptimizationTarget.THROUGHPUT,
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_convert_to_tensorrt(self):
        """Test TensorRT conversion"""
        optimizer = EdgeInferenceOptimizer()
        result = await optimizer.convert_to_tensorrt(
            model_id="model_003", precision="fp16"
        )

        assert result is not None
        assert result.get("framework") == "tensorrt"

    @pytest.mark.asyncio
    async def test_convert_to_tflite(self):
        """Test TFLite conversion"""
        optimizer = EdgeInferenceOptimizer()
        result = await optimizer.convert_to_tflite(
            model_id="model_004", quantize=True
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_benchmark_model(self):
        """Test model benchmarking"""
        optimizer = EdgeInferenceOptimizer()
        benchmark = await optimizer.benchmark_model(
            model_id="model_005", num_runs=100
        )

        assert "latency_ms" in benchmark
        assert "throughput_qps" in benchmark

    @pytest.mark.asyncio
    async def test_profile_model(self):
        """Test model profiling"""
        optimizer = EdgeInferenceOptimizer()
        profile = await optimizer.profile_model(model_id="model_006")

        assert profile is not None
        assert "layers" in profile or "operations" in profile


# ============================================================================
# 4. ModelCompressionEngine Tests
# ============================================================================


class TestModelCompressionEngine:
    """Test Model Compression Engine subsystem"""

    @pytest.mark.asyncio
    async def test_quantize_int8(self):
        """Test INT8 quantization"""
        compression = ModelCompressionEngine()
        result = await compression.quantize_model(
            model_id="compress_model_001",
            quantization_type=CompressionType.QUANTIZATION_INT8,
        )

        assert result is not None
        assert result.compression_type == CompressionType.QUANTIZATION_INT8
        assert result.compression_ratio > 1.0

    @pytest.mark.asyncio
    async def test_quantize_fp16(self):
        """Test FP16 quantization"""
        compression = ModelCompressionEngine()
        result = await compression.quantize_model(
            model_id="compress_model_002",
            quantization_type=CompressionType.QUANTIZATION_FP16,
        )

        assert result is not None
        assert result.compression_ratio >= 2.0  # FP32→FP16 is 2x

    @pytest.mark.asyncio
    async def test_prune_model(self):
        """Test model pruning"""
        compression = ModelCompressionEngine()
        result = await compression.prune_model(
            model_id="prune_model_001", pruning_ratio=0.5
        )

        assert result.get("status") == "success"
        assert result.get("pruning_ratio") == 0.5

    @pytest.mark.asyncio
    async def test_distill_model(self):
        """Test knowledge distillation"""
        compression = ModelCompressionEngine()
        result = await compression.distill_model(
            teacher_model_id="teacher_001",
            student_model_id="student_001",
            temperature=2.0,
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_compression_accuracy_loss(self):
        """Test accuracy loss after compression"""
        compression = ModelCompressionEngine()
        result = await compression.quantize_model(
            model_id="accuracy_test_model",
            quantization_type=CompressionType.QUANTIZATION_INT8,
        )

        # Accuracy loss should be reasonable (<5%)
        assert result.accuracy_loss < 0.05

    @pytest.mark.asyncio
    async def test_get_compressed_model(self):
        """Test retrieving compressed model"""
        compression = ModelCompressionEngine()
        await compression.quantize_model(
            "retrieve_model", CompressionType.QUANTIZATION_INT8
        )

        model = await compression.get_compressed_model("retrieve_model")
        assert model is not None


# ============================================================================
# 5. EdgeOrchestrationSystem Tests
# ============================================================================


class TestEdgeOrchestrationSystem:
    """Test Edge Orchestration System subsystem"""

    @pytest.mark.asyncio
    async def test_place_workload(self):
        """Test workload placement"""
        orchestration = EdgeOrchestrationSystem()
        placement = await orchestration.place_workload(
            workload_id="workload_001",
            requirements={"cpu_cores": 2, "ram_mb": 1024},
            strategy=PlacementStrategy.LOAD_BALANCED,
        )

        assert placement is not None
        assert placement.workload_id == "workload_001"

    @pytest.mark.asyncio
    async def test_placement_strategies(self):
        """Test different placement strategies"""
        orchestration = EdgeOrchestrationSystem()

        # Test LOAD_BALANCED
        p1 = await orchestration.place_workload(
            "wl1", {"cpu_cores": 2}, PlacementStrategy.LOAD_BALANCED
        )
        assert p1 is not None

        # Test LATENCY_OPTIMIZED
        p2 = await orchestration.place_workload(
            "wl2", {"cpu_cores": 2}, PlacementStrategy.LATENCY_OPTIMIZED
        )
        assert p2 is not None

    @pytest.mark.asyncio
    async def test_rebalance_workloads(self):
        """Test workload rebalancing"""
        orchestration = EdgeOrchestrationSystem()

        # Place some workloads first
        await orchestration.place_workload(
            "wl_rebalance_1", {"cpu_cores": 2}, PlacementStrategy.LOAD_BALANCED
        )

        result = await orchestration.rebalance_workloads()
        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_get_workload_placement(self):
        """Test getting workload placement info"""
        orchestration = EdgeOrchestrationSystem()
        await orchestration.place_workload(
            "wl_get", {"cpu_cores": 2}, PlacementStrategy.LOAD_BALANCED
        )

        placement = await orchestration.get_workload_placement("wl_get")
        assert placement is not None

    @pytest.mark.asyncio
    async def test_remove_workload(self):
        """Test removing workload"""
        orchestration = EdgeOrchestrationSystem()
        await orchestration.place_workload(
            "wl_remove", {"cpu_cores": 2}, PlacementStrategy.LOAD_BALANCED
        )

        result = await orchestration.remove_workload("wl_remove")
        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_get_cluster_status(self):
        """Test getting cluster status"""
        orchestration = EdgeOrchestrationSystem()
        status = await orchestration.get_cluster_status()

        assert status is not None
        assert "total_devices" in status or "workloads" in status


# ============================================================================
# 6. EdgeCloudSynchronization Tests
# ============================================================================


class TestEdgeCloudSynchronization:
    """Test Edge-Cloud Synchronization subsystem"""

    @pytest.mark.asyncio
    async def test_sync_entity(self):
        """Test entity synchronization"""
        sync = EdgeCloudSynchronization()
        result = await sync.sync_entity(
            entity_id="entity_001",
            entity_type="model",
            data={"version": 1, "weights": "..."},
            device_id="device_1",
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_delta_sync(self):
        """Test delta synchronization"""
        sync = EdgeCloudSynchronization()
        result = await sync.sync_with_strategy(
            entity_id="delta_entity",
            entity_type="data",
            data={"field": "value"},
            strategy=SyncStrategy.DELTA_SYNC,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_resolve_conflict(self):
        """Test conflict resolution"""
        sync = EdgeCloudSynchronization()
        resolved = await sync.resolve_conflict(
            entity_id="conflict_entity",
            local_version={"data": "local"},
            remote_version={"data": "remote"},
            resolution_strategy="last_write_wins",
        )

        assert resolved is not None

    @pytest.mark.asyncio
    async def test_get_sync_status(self):
        """Test getting sync status"""
        sync = EdgeCloudSynchronization()
        await sync.sync_entity(
            "status_entity", "model", {"v": 1}, "device_1"
        )

        status = await sync.get_sync_status("status_entity")
        assert status is not None

    @pytest.mark.asyncio
    async def test_queue_offline_operation(self):
        """Test queueing operations while offline"""
        sync = EdgeCloudSynchronization()
        result = await sync.queue_offline_operation(
            operation_type="UPDATE",
            entity_id="offline_entity",
            data={"offline": True},
            device_id="offline_device",
        )

        assert result.get("status") == "queued"

    @pytest.mark.asyncio
    async def test_sync_offline_queue(self):
        """Test syncing queued offline operations"""
        sync = EdgeCloudSynchronization()

        # Queue some operations
        await sync.queue_offline_operation(
            "CREATE", "entity_1", {"data": 1}, "device_1"
        )

        # Sync queue
        result = await sync.sync_offline_queue(device_id="device_1")
        assert result is not None


# ============================================================================
# 7. EdgeAnalyticsPipeline Tests
# ============================================================================


class TestEdgeAnalyticsPipeline:
    """Test Edge Analytics Pipeline subsystem"""

    @pytest.mark.asyncio
    async def test_create_pipeline(self):
        """Test creating analytics pipeline"""
        analytics = EdgeAnalyticsPipeline()
        result = await analytics.create_pipeline(
            pipeline_id="pipeline_001",
            stream_source="sensor_data",
            processing_functions=["filter", "transform", "aggregate"],
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_process_event(self):
        """Test processing single event"""
        analytics = EdgeAnalyticsPipeline()
        await analytics.create_pipeline(
            "event_pipeline", "events", ["process"]
        )

        result = await analytics.process_event(
            pipeline_id="event_pipeline",
            event={"type": "sensor_reading", "value": 42.5},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch event processing"""
        analytics = EdgeAnalyticsPipeline()
        await analytics.create_pipeline(
            "batch_pipeline", "batch_events", ["aggregate"]
        )

        events = [
            {"type": "reading", "value": i} for i in range(10)
        ]

        result = await analytics.process_batch(
            pipeline_id="batch_pipeline",
            events=events,
        )

        assert result.get("status") == "success"
        assert result.get("processed_count", 0) > 0

    @pytest.mark.asyncio
    async def test_detect_anomaly(self):
        """Test anomaly detection"""
        analytics = EdgeAnalyticsPipeline()
        await analytics.create_pipeline(
            "anomaly_pipeline", "anomaly_events", ["anomaly_detection"]
        )

        result = await analytics.detect_anomaly(
            pipeline_id="anomaly_pipeline",
            event={"value": 999.9},  # Anomalous value
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_pipeline_stats(self):
        """Test getting pipeline statistics"""
        analytics = EdgeAnalyticsPipeline()
        await analytics.create_pipeline(
            "stats_pipeline", "stats_events", ["process"]
        )

        stats = await analytics.get_pipeline_stats("stats_pipeline")
        assert stats is not None
        assert "pipeline_id" in stats

    @pytest.mark.asyncio
    async def test_stop_pipeline(self):
        """Test stopping pipeline"""
        analytics = EdgeAnalyticsPipeline()
        await analytics.create_pipeline(
            "stop_pipeline", "stop_events", ["process"]
        )

        result = await analytics.stop_pipeline("stop_pipeline")
        assert result.get("status") == "success"


# ============================================================================
# 8. IntegratedEdgeAISystem Tests
# ============================================================================


class TestIntegratedEdgeAISystem:
    """Test Integrated Edge AI System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        """Test system initialization with config"""
        config = EdgeAIConfig(
            enable_device_manager=True,
            enable_distributed_training=True,
            enable_compression=True,
        )

        system = IntegratedEdgeAISystem(config)
        assert system.device_manager is not None
        assert system.distributed_training is not None
        assert system.compression_engine is not None

    @pytest.mark.asyncio
    async def test_deploy_model_to_edge(self):
        """Test end-to-end model deployment"""
        system = IntegratedEdgeAISystem()

        result = await system.deploy_model_to_edge(
            model_id="deploy_model_001",
            model_data={"architecture": "resnet18"},
            target_devices=["device_1", "device_2"],
            compress=True,
            optimize=True,
        )

        assert result.get("status") == "success"
        assert "deployed_devices" in result

    @pytest.mark.asyncio
    async def test_train_federated_model(self):
        """Test federated model training"""
        system = IntegratedEdgeAISystem()

        # Register devices first
        await system.device_manager.register_device(
            "train_device_1", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        result = await system.train_federated_model(
            model_architecture="mobilenet_v2",
            dataset_id="cifar10",
            participating_devices=["train_device_1"],
            num_rounds=10,
        )

        assert result is not None
        assert "job_id" in result

    @pytest.mark.asyncio
    async def test_monitor_edge_infrastructure(self):
        """Test infrastructure monitoring"""
        system = IntegratedEdgeAISystem()

        # Register a device
        await system.device_manager.register_device(
            "monitor_device", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        status = await system.monitor_edge_infrastructure(
            include_metrics=True,
            include_analytics=True,
        )

        assert status is not None
        assert "total_devices" in status

    @pytest.mark.asyncio
    async def test_optimize_edge_deployment(self):
        """Test deployment optimization"""
        system = IntegratedEdgeAISystem()

        result = await system.optimize_edge_deployment(
            rebalance=True,
            compress_models=True,
        )

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_handle_edge_offline_mode(self):
        """Test offline mode handling"""
        system = IntegratedEdgeAISystem()

        await system.device_manager.register_device(
            "offline_device", {"tier": "tier_3_edge_server", "cpu_cores": 4}
        )

        result = await system.handle_edge_offline_mode(
            device_id="offline_device",
            duration_sec=3600,
        )

        assert result is not None
        assert result.get("sync_paused") is True

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        """Test getting system status"""
        system = IntegratedEdgeAISystem()
        status = system.get_system_status()

        assert status is not None
        assert "device_manager_enabled" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        """Test system performance benchmarking"""
        system = IntegratedEdgeAISystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        """Test singleton accessor"""
        system1 = get_edge_ai_system()
        system2 = get_edge_ai_system()

        # Should be same instance
        assert system1 is system2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
