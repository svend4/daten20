"""
Universal Deployment Platform (v10.0)

Provides comprehensive deployment orchestration, infrastructure as code, continuous
deployment pipelines, multi-cloud management, edge deployment, canary releases,
and self-healing infrastructure for the entire DATEN20 platform.

Version: 10.0.0 (FULL IMPLEMENTATION)
"""

from .deployment_services import (
    # Enums
    DeploymentEnvironment,
    CloudProvider,
    DeploymentStrategy,
    DeploymentStatus,
    IaCProvider,
    PipelineStageType,
    EdgeDeviceType,
    HealthCheckType,
    FailureType,
    RecoveryAction,

    # Data classes
    DeploymentTarget,
    DeploymentPlan,
    DeploymentExecution,
    InfrastructureTemplate,
    InfrastructureState,
    InfrastructureChange,
    PipelineStage,
    Pipeline,
    PipelineExecution,
    EdgeDevice,
    EdgeDeployment,
    CanaryConfig,
    CanaryMetrics,
    CanaryRollout,
    HealthCheck,
    FailureEvent,
    DeploymentConfig,

    # Subsystems
    UniversalDeploymentOrchestrator,
    InfrastructureAsCodeEngine,
    ContinuousDeploymentPipeline,
    MultiCloudManager,
    EdgeDeploymentSystem,
    CanaryReleaseController,
    SelfHealingInfrastructure,

    # Integrated system
    IntegratedDeploymentSystem,
    get_deployment_system,

    # Convenience accessors
    get_deployment_orchestrator,
    get_iac_engine,
    get_cd_pipeline,
    get_multi_cloud_manager,
    get_edge_deployment_system,
    get_canary_controller,
    get_self_healing_infrastructure
)

__all__ = [
    # Enums
    'DeploymentEnvironment',
    'CloudProvider',
    'DeploymentStrategy',
    'DeploymentStatus',
    'IaCProvider',
    'PipelineStageType',
    'EdgeDeviceType',
    'HealthCheckType',
    'FailureType',
    'RecoveryAction',

    # Data classes
    'DeploymentTarget',
    'DeploymentPlan',
    'DeploymentExecution',
    'InfrastructureTemplate',
    'InfrastructureState',
    'InfrastructureChange',
    'PipelineStage',
    'Pipeline',
    'PipelineExecution',
    'EdgeDevice',
    'EdgeDeployment',
    'CanaryConfig',
    'CanaryMetrics',
    'CanaryRollout',
    'HealthCheck',
    'FailureEvent',
    'DeploymentConfig',

    # Subsystems
    'UniversalDeploymentOrchestrator',
    'InfrastructureAsCodeEngine',
    'ContinuousDeploymentPipeline',
    'MultiCloudManager',
    'EdgeDeploymentSystem',
    'CanaryReleaseController',
    'SelfHealingInfrastructure',

    # Integrated system
    'IntegratedDeploymentSystem',
    'get_deployment_system',

    # Convenience accessors
    'get_deployment_orchestrator',
    'get_iac_engine',
    'get_cd_pipeline',
    'get_multi_cloud_manager',
    'get_edge_deployment_system',
    'get_canary_controller',
    'get_self_healing_infrastructure'
]

__version__ = "10.0.0"
