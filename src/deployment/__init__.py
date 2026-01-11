"""
Universal Deployment Platform Module

This module provides comprehensive deployment orchestration across all environments,
clouds, and edge locations. It implements intelligent deployment strategies,
infrastructure as code, continuous deployment pipelines, multi-cloud management,
edge computing deployment, canary releases, and self-healing infrastructure.

Version: 10.0.0
"""

from .deployment_services import (
    # Enums
    DeploymentStrategyType,
    Environment,
    CloudProvider,
    IaCProvider,
    PipelineStageType,

    # Data Classes
    DeploymentTarget,
    DeploymentStrategy,
    DeploymentPlan,
    DeploymentExecution,
    InfrastructureTemplate,
    InfrastructureState,
    PipelineStage,
    Pipeline,
    EdgeDevice,
    CanaryConfig,
    HealthCheck,
    FailureEvent,

    # Services
    UniversalDeploymentOrchestrator,
    InfrastructureAsCodeEngine,
    ContinuousDeploymentPipeline,
    MultiCloudManager,
    EdgeDeploymentSystem,
    CanaryReleaseController,
    SelfHealingInfrastructure,

    # Singleton Getters
    get_deployment_orchestrator,
    get_iac_engine,
    get_cd_pipeline,
    get_multi_cloud_manager,
    get_edge_deployment_system,
    get_canary_controller,
    get_self_healing_infrastructure,
)

__all__ = [
    # Enums
    'DeploymentStrategyType',
    'Environment',
    'CloudProvider',
    'IaCProvider',
    'PipelineStageType',

    # Data Classes
    'DeploymentTarget',
    'DeploymentStrategy',
    'DeploymentPlan',
    'DeploymentExecution',
    'InfrastructureTemplate',
    'InfrastructureState',
    'PipelineStage',
    'Pipeline',
    'EdgeDevice',
    'CanaryConfig',
    'HealthCheck',
    'FailureEvent',

    # Services
    'UniversalDeploymentOrchestrator',
    'InfrastructureAsCodeEngine',
    'ContinuousDeploymentPipeline',
    'MultiCloudManager',
    'EdgeDeploymentSystem',
    'CanaryReleaseController',
    'SelfHealingInfrastructure',

    # Singleton Getters
    'get_deployment_orchestrator',
    'get_iac_engine',
    'get_cd_pipeline',
    'get_multi_cloud_manager',
    'get_edge_deployment_system',
    'get_canary_controller',
    'get_self_healing_infrastructure',
]

__version__ = '10.0.0'
