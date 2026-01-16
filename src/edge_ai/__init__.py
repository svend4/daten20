"""
Distributed Edge AI Platform Module (v16.0)

This module provides comprehensive distributed edge AI capabilities for deploying
and training AI models at the edge with ultra-low latency (<10ms), offline support,
and intelligent orchestration across thousands of edge devices.

Core Systems:
- Edge Device Manager: Registration, monitoring, lifecycle management (10K+ devices)
- Distributed Edge Training: Split learning, federated learning, gossip protocols
- Edge Inference Optimizer: TensorRT, TFLite, ONNX conversion and optimization
- Model Compression Engine: Quantization, pruning, distillation (10-100x compression)
- Edge Orchestration System: Workload placement, scheduling, load balancing
- Edge-Cloud Synchronization: Delta sync, conflict resolution, offline support
- Edge Analytics Pipeline: Real-time stream processing, anomaly detection, CEP

Example Usage:
    from edge_ai import get_edge_device_manager, get_model_compression_engine

    # Register edge device
    device_mgr = get_edge_device_manager()
    device = await device_mgr.register_device(
        device_id="jetson_nano_01",
        device_info={
            'tier': 'tier_3_edge_server',
            'cpu_cores': 4,
            'ram_mb': 4096,
            'storage_gb': 64,
            'has_gpu': True,
            'gpu_memory_mb': 1024
        }
    )

    # Compress model for edge
    compression = get_model_compression_engine()
    compressed = await compression.quantize_model(
        model_id="resnet50",
        quantization_type=CompressionType.QUANTIZATION_INT8
    )
"""

from .edge_ai_services import (  # Enums; Data Classes; Service Classes; Singleton Getters
    CompressedModel,
    CompressionType,
    DeviceMetrics,
    DeviceTier,
    DistributedEdgeTraining,
    EdgeAnalyticsPipeline,
    EdgeCloudSynchronization,
    EdgeDevice,
    EdgeDeviceManager,
    EdgeInferenceOptimizer,
    EdgeOrchestrationSystem,
    ModelCompressionEngine,
    OptimizationTarget,
    PlacementStrategy,
    SyncOperation,
    SyncStrategy,
    TrainingJob,
    TrainingMode,
    WorkloadPlacement,
    get_distributed_edge_training,
    get_edge_analytics_pipeline,
    get_edge_cloud_synchronization,
    get_edge_device_manager,
    get_edge_inference_optimizer,
    get_edge_orchestration_system,
    get_model_compression_engine,
)

__version__ = "16.0.0"
__all__ = [
    # Enums
    "DeviceTier",
    "TrainingMode",
    "CompressionType",
    "OptimizationTarget",
    "PlacementStrategy",
    "SyncStrategy",
    # Data Classes
    "EdgeDevice",
    "DeviceMetrics",
    "TrainingJob",
    "CompressedModel",
    "WorkloadPlacement",
    "SyncOperation",
    # Service Classes
    "EdgeDeviceManager",
    "DistributedEdgeTraining",
    "EdgeInferenceOptimizer",
    "ModelCompressionEngine",
    "EdgeOrchestrationSystem",
    "EdgeCloudSynchronization",
    "EdgeAnalyticsPipeline",
    # Singleton Getters
    "get_edge_device_manager",
    "get_distributed_edge_training",
    "get_edge_inference_optimizer",
    "get_model_compression_engine",
    "get_edge_orchestration_system",
    "get_edge_cloud_synchronization",
    "get_edge_analytics_pipeline",
]
