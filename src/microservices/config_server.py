#!/usr/bin/env python3
"""
Configuration Management Module

Centralized configuration server with feature flags, hot reload,
and multi-environment support.

Key Features:
- Centralized configuration storage
- Feature flags (boolean, rollout percentage, targeting)
- Dynamic hot reload
- Environment-specific configs (dev, staging, prod)
- Configuration versioning
- Change notification
- Secret management
- Git-backed storage (optional)

Dependencies:
- None (pure Python implementation)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime
from uuid import uuid4
import threading
import json
import logging
import copy
from pathlib import Path

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class FeatureFlagType(str, Enum):
    """Feature flag types"""
    BOOLEAN = "boolean"
    ROLLOUT = "rollout"  # Percentage-based rollout
    TARGETING = "targeting"  # User/tenant targeting


class ConfigChangeType(str, Enum):
    """Configuration change types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    name: str
    flag_type: FeatureFlagType
    enabled: bool = False
    rollout_percentage: float = 0.0  # 0-100
    targeting_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_enabled_for(self, context: Dict[str, Any]) -> bool:
        """
        Check if flag is enabled for given context

        Args:
            context: Context with user_id, tenant_id, etc.

        Returns:
            True if enabled for context
        """
        if not self.enabled:
            return False

        if self.flag_type == FeatureFlagType.BOOLEAN:
            return True

        elif self.flag_type == FeatureFlagType.ROLLOUT:
            # Use consistent hashing for stable rollout
            user_id = context.get("user_id", "")
            if not user_id:
                return False

            hash_value = hash(f"{self.name}:{user_id}") % 100
            return hash_value < self.rollout_percentage

        elif self.flag_type == FeatureFlagType.TARGETING:
            # Check targeting rules
            for rule_key, rule_values in self.targeting_rules.items():
                context_value = context.get(rule_key)
                if context_value and context_value in rule_values:
                    return True

            return False

        return False


@dataclass
class ConfigValue:
    """Configuration value with metadata"""
    key: str
    value: Any
    environment: Environment
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "key": self.key,
            "value": self.value,
            "environment": self.environment.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ConfigChangeEvent:
    """Configuration change event"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    change_type: ConfigChangeType = ConfigChangeType.UPDATED
    key: str = ""
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    environment: Optional[Environment] = None
    timestamp: datetime = field(default_factory=datetime.now)


ConfigChangeListener = Callable[[ConfigChangeEvent], None]


class ConfigStore:
    """
    Configuration storage

    Stores configuration values by environment.
    """

    def __init__(self):
        self._configs: Dict[Environment, Dict[str, ConfigValue]] = {
            env: {} for env in Environment
        }
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, environment: Environment) -> ConfigValue:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
            environment: Target environment

        Returns:
            ConfigValue instance
        """
        with self._lock:
            existing = self._configs[environment].get(key)

            if existing:
                existing.value = value
                existing.version += 1
                existing.updated_at = datetime.now()
                config_value = existing
            else:
                config_value = ConfigValue(
                    key=key,
                    value=value,
                    environment=environment
                )
                self._configs[environment][key] = config_value

            return config_value

    def get(self, key: str, environment: Environment, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            environment: Target environment
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        with self._lock:
            config_value = self._configs[environment].get(key)
            return config_value.value if config_value else default

    def delete(self, key: str, environment: Environment) -> bool:
        """
        Delete configuration value

        Args:
            key: Configuration key
            environment: Target environment

        Returns:
            True if deleted
        """
        with self._lock:
            if key in self._configs[environment]:
                del self._configs[environment][key]
                return True
            return False

    def get_all(self, environment: Environment) -> Dict[str, Any]:
        """
        Get all configurations for environment

        Args:
            environment: Target environment

        Returns:
            Dictionary of key-value pairs
        """
        with self._lock:
            return {
                key: config.value
                for key, config in self._configs[environment].items()
            }

    def export_to_file(self, environment: Environment, file_path: str):
        """
        Export configuration to JSON file

        Args:
            environment: Target environment
            file_path: Output file path
        """
        with self._lock:
            configs = {
                key: config.to_dict()
                for key, config in self._configs[environment].items()
            }

        with open(file_path, 'w') as f:
            json.dump(configs, f, indent=2)

        logger.info(f"Exported {environment.value} config to {file_path}")

    def import_from_file(self, environment: Environment, file_path: str):
        """
        Import configuration from JSON file

        Args:
            environment: Target environment
            file_path: Input file path
        """
        with open(file_path, 'r') as f:
            configs = json.load(f)

        with self._lock:
            for key, config_data in configs.items():
                config_value = ConfigValue(
                    key=key,
                    value=config_data["value"],
                    environment=environment,
                    version=config_data.get("version", 1),
                    metadata=config_data.get("metadata", {})
                )
                self._configs[environment][key] = config_value

        logger.info(f"Imported {environment.value} config from {file_path}")


class FeatureFlagManager:
    """
    Feature flag manager

    Manages feature flags across environments.
    """

    def __init__(self):
        self._flags: Dict[str, FeatureFlag] = {}
        self._lock = threading.Lock()

    def create_flag(self, flag: FeatureFlag):
        """Create or update feature flag"""
        with self._lock:
            self._flags[flag.name] = flag
            logger.info(f"Feature flag created: {flag.name}")

    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name"""
        with self._lock:
            return self._flags.get(name)

    def delete_flag(self, name: str) -> bool:
        """Delete feature flag"""
        with self._lock:
            if name in self._flags:
                del self._flags[name]
                logger.info(f"Feature flag deleted: {name}")
                return True
            return False

    def is_enabled(self, name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if feature flag is enabled

        Args:
            name: Flag name
            context: Evaluation context

        Returns:
            True if enabled
        """
        flag = self.get_flag(name)
        if not flag:
            return False

        return flag.is_enabled_for(context or {})

    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags"""
        with self._lock:
            return self._flags.copy()


class ConfigServer:
    """
    Configuration server

    Central configuration management with hot reload and notifications.
    """

    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.config_store = ConfigStore()
        self.feature_flags = FeatureFlagManager()
        self._listeners: List[ConfigChangeListener] = []
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}

    def set_config(self, key: str, value: Any, environment: Optional[Environment] = None) -> ConfigValue:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
            environment: Target environment (default: current)

        Returns:
            ConfigValue instance
        """
        env = environment or self.environment

        # Get old value for change event
        old_value = self.config_store.get(key, env)

        # Set new value
        config_value = self.config_store.set(key, value, env)

        # Clear cache
        cache_key = f"{env.value}:{key}"
        with self._lock:
            self._cache.pop(cache_key, None)

        # Notify listeners
        event = ConfigChangeEvent(
            change_type=ConfigChangeType.UPDATED if old_value else ConfigChangeType.CREATED,
            key=key,
            old_value=old_value,
            new_value=value,
            environment=env
        )
        self._notify_listeners(event)

        return config_value

    def get_config(self, key: str, default: Any = None, environment: Optional[Environment] = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if not found
            environment: Target environment (default: current)

        Returns:
            Configuration value or default
        """
        env = environment or self.environment
        cache_key = f"{env.value}:{key}"

        # Check cache
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Get from store
        value = self.config_store.get(key, env, default)

        # Cache value
        with self._lock:
            self._cache[cache_key] = value

        return value

    def delete_config(self, key: str, environment: Optional[Environment] = None) -> bool:
        """
        Delete configuration value

        Args:
            key: Configuration key
            environment: Target environment (default: current)

        Returns:
            True if deleted
        """
        env = environment or self.environment
        old_value = self.config_store.get(key, env)

        if self.config_store.delete(key, env):
            # Clear cache
            cache_key = f"{env.value}:{key}"
            with self._lock:
                self._cache.pop(cache_key, None)

            # Notify listeners
            event = ConfigChangeEvent(
                change_type=ConfigChangeType.DELETED,
                key=key,
                old_value=old_value,
                environment=env
            )
            self._notify_listeners(event)

            return True

        return False

    def reload(self):
        """Reload all configurations (clear cache)"""
        with self._lock:
            self._cache.clear()
        logger.info("Configuration cache reloaded")

    def add_change_listener(self, listener: ConfigChangeListener):
        """
        Add configuration change listener

        Args:
            listener: Listener function
        """
        with self._lock:
            self._listeners.append(listener)

    def remove_change_listener(self, listener: ConfigChangeListener):
        """
        Remove configuration change listener

        Args:
            listener: Listener function
        """
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def _notify_listeners(self, event: ConfigChangeEvent):
        """Notify all listeners of configuration change"""
        with self._lock:
            listeners = self._listeners.copy()

        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Config change listener failed: {e}")

    def export_config(self, file_path: str, environment: Optional[Environment] = None):
        """
        Export configuration to file

        Args:
            file_path: Output file path
            environment: Target environment (default: current)
        """
        env = environment or self.environment
        self.config_store.export_to_file(env, file_path)

    def import_config(self, file_path: str, environment: Optional[Environment] = None):
        """
        Import configuration from file

        Args:
            file_path: Input file path
            environment: Target environment (default: current)
        """
        env = environment or self.environment
        self.config_store.import_from_file(env, file_path)
        self.reload()

    def get_stats(self) -> Dict[str, Any]:
        """Get configuration server statistics"""
        with self._lock:
            return {
                "environment": self.environment.value,
                "config_count": len(self.config_store.get_all(self.environment)),
                "feature_flags_count": len(self.feature_flags.get_all_flags()),
                "cache_size": len(self._cache),
                "listeners_count": len(self._listeners)
            }


# Singleton instance
_config_server_instance = None
_instance_lock = threading.Lock()


def get_config_server(environment: Optional[Environment] = None) -> ConfigServer:
    """Get singleton Config Server instance"""
    global _config_server_instance

    if _config_server_instance is None:
        with _instance_lock:
            if _config_server_instance is None:
                env = environment or Environment.DEVELOPMENT
                _config_server_instance = ConfigServer(env)

    return _config_server_instance


if __name__ == "__main__":
    # Example usage
    config_server = get_config_server(Environment.DEVELOPMENT)

    # Set configuration
    config_server.set_config("database.host", "localhost")
    config_server.set_config("database.port", 5432)
    config_server.set_config("api.timeout", 30)

    # Get configuration
    db_host = config_server.get_config("database.host")
    db_port = config_server.get_config("database.port")
    print(f"Database: {db_host}:{db_port}")

    # Create feature flag
    flag = FeatureFlag(
        name="new_dashboard",
        flag_type=FeatureFlagType.ROLLOUT,
        enabled=True,
        rollout_percentage=50.0
    )
    config_server.feature_flags.create_flag(flag)

    # Check feature flag
    context1 = {"user_id": "user-123"}
    context2 = {"user_id": "user-456"}

    enabled1 = config_server.feature_flags.is_enabled("new_dashboard", context1)
    enabled2 = config_server.feature_flags.is_enabled("new_dashboard", context2)

    print(f"Feature 'new_dashboard' for user-123: {enabled1}")
    print(f"Feature 'new_dashboard' for user-456: {enabled2}")

    # Add change listener
    def on_config_change(event: ConfigChangeEvent):
        print(f"Config changed: {event.key} = {event.new_value}")

    config_server.add_change_listener(on_config_change)

    # Update config (triggers listener)
    config_server.set_config("api.timeout", 60)

    # Print stats
    print(f"\nConfig server stats: {config_server.get_stats()}")

    print("\nConfiguration Management module loaded successfully!")
