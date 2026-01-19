"""
# SIMPLE VERSION - Unified Developer Platform API - v3.9

This is a simplified/minimal API that can be expanded later with:
- Full SDK generation capabilities
- Advanced plugin system
- IDE integration tools
- Developer portal features
- API marketplace
- Webhook management
- Custom extension support

Single interface for all developer platform operations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from .developer_services import (
    DeveloperPlatform,
    SDKLanguage,
    PluginType,
    get_developer_platform
)

logger = logging.getLogger(__name__)


class DeveloperOperation(Enum):
    """Developer operation types"""
    GENERATE_SDK = "generate_sdk"
    REGISTER_PLUGIN = "register_plugin"
    CREATE_WEBHOOK = "create_webhook"
    GENERATE_DOCS = "generate_docs"


@dataclass
class DeveloperConfig:
    """Configuration for Developer Platform API"""
    enable_sdk_generation: bool = True
    enable_plugin_system: bool = True
    enable_webhooks: bool = True
    api_versioning: bool = True


class DeveloperPlatformAPI:
    """
    # SIMPLE VERSION
    Unified Developer Platform API - Single interface for developer operations

    Can be expanded with:
    - Full REST/GraphQL API generation
    - OpenAPI/Swagger documentation
    - SDK templates for more languages
    - Plugin marketplace
    - Developer analytics
    - Sandbox environments
    """

    def __init__(self, config: Optional[DeveloperConfig] = None):
        """Initialize Developer Platform API"""
        self.config = config or DeveloperConfig()

        # Initialize platform
        self.platform = get_developer_platform()

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in DeveloperOperation},
            "sdks_generated": 0,
            "plugins_registered": 0,
            "webhooks_created": 0,
        }

        logger.info("Developer Platform API initialized (SIMPLE VERSION)")

    def generate_sdk(self, language: SDKLanguage, api_spec: Dict[str, Any], **kwargs) -> str:
        """Generate SDK for language"""
        self._track(DeveloperOperation.GENERATE_SDK)
        sdk_path = self.platform.generate_sdk(language, api_spec, **kwargs)
        self.stats["sdks_generated"] += 1
        return sdk_path

    def register_plugin(self, plugin_name: str, plugin_type: PluginType, **kwargs) -> str:
        """Register plugin"""
        self._track(DeveloperOperation.REGISTER_PLUGIN)
        plugin_id = self.platform.register_plugin(plugin_name, plugin_type, **kwargs)
        self.stats["plugins_registered"] += 1
        return plugin_id

    def create_webhook(self, url: str, events: List[str], **kwargs) -> str:
        """Create webhook"""
        self._track(DeveloperOperation.CREATE_WEBHOOK)
        webhook_id = self.platform.create_webhook(url, events, **kwargs)
        self.stats["webhooks_created"] += 1
        return webhook_id

    def generate_api_docs(self, format: str = "openapi", **kwargs) -> str:
        """Generate API documentation"""
        self._track(DeveloperOperation.GENERATE_DOCS)
        return self.platform.generate_docs(format, **kwargs)

    def _track(self, operation: DeveloperOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self.stats


# Singleton
_developer_api = None


def get_developer_api(config: Optional[DeveloperConfig] = None) -> DeveloperPlatformAPI:
    """Get singleton Developer Platform API instance"""
    global _developer_api
    if _developer_api is None:
        _developer_api = DeveloperPlatformAPI(config=config)
    return _developer_api
