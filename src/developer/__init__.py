"""
Developer Platform & SDK Ecosystem - v3.9

Developer tools, SDK generation, plugin system, and developer portal.

Modules:
- developer_services: Unified developer platform services

Components:
- SDK Generator: Multi-language SDK generation
- Plugin System: Extensible plugin architecture
- GraphQL v2: Federation and subscriptions
- Workflow Designer: Visual workflow builder
- Developer Portal: Documentation and API playground
- API Gateway v2: Advanced routing and transformation

Version: 3.9.0
"""

__version__ = '3.9.0'

from .developer_services import (
    # SDK Generator
    SupportedLanguage,
    SDKConfig,
    SDKGenerator,
    get_sdk_generator,
    # Plugin System
    Plugin,
    PluginManifest,
    PluginManager,
    get_plugin_manager,
    # GraphQL v2
    GraphQLSchema,
    GraphQLServer,
    get_graphql_server,
    # Workflow Designer
    WorkflowNode,
    WorkflowNodeType,
    Workflow,
    WorkflowEngine,
    get_workflow_engine,
    # Developer Portal
    DeveloperPortal,
    get_developer_portal,
    # API Gateway v2
    APIGateway,
    Route,
    get_api_gateway,
)

__all__ = [
    # SDK Generator
    'SupportedLanguage',
    'SDKConfig',
    'SDKGenerator',
    'get_sdk_generator',
    # Plugin System
    'Plugin',
    'PluginManifest',
    'PluginManager',
    'get_plugin_manager',
    # GraphQL v2
    'GraphQLSchema',
    'GraphQLServer',
    'get_graphql_server',
    # Workflow Designer
    'WorkflowNode',
    'WorkflowNodeType',
    'Workflow',
    'WorkflowEngine',
    'get_workflow_engine',
    # Developer Portal
    'DeveloperPortal',
    'get_developer_portal',
    # API Gateway v2
    'APIGateway',
    'Route',
    'get_api_gateway',
]
