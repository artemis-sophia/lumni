"""
Thread-safe Configuration Manager
Singleton pattern for loading and caching configuration
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional
from app.config import (
    GatewayConfig,
    resolve_env_vars,
    _resolve_env_var
)
from app.utils.logger import Logger
from app.utils.exceptions import ConfigurationError

logger = Logger("ConfigManager")


def validate_no_secrets_in_config(config_data: dict) -> None:
    """Validate that config file doesn't contain hardcoded secrets
    
    Raises ConfigurationError if secrets are detected in config file.
    Secrets should be provided via environment variables.
    """
    # Patterns that indicate secrets (not environment variable references)
    secret_patterns = [
        r'sk-[a-zA-Z0-9]{20,}',  # OpenAI-style API keys
        r'ghp_[a-zA-Z0-9]{36}',  # GitHub personal access tokens
        r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}',  # GitHub fine-grained tokens
        r'[a-zA-Z0-9]{32,}',  # Long alphanumeric strings (potential API keys)
    ]
    
    import re
    import json
    
    def check_value(value, path=""):
        """Recursively check values for secret patterns"""
        if isinstance(value, str):
            # Skip environment variable references
            if value.startswith("${") and value.endswith("}"):
                return
            
            # Check for secret patterns
            for pattern in secret_patterns:
                if re.search(pattern, value):
                    raise ConfigurationError(
                        f"Potential secret detected in config at path: {path}. "
                        "Secrets should be provided via environment variables using ${ENV_VAR} syntax.",
                        {"path": path, "pattern_matched": pattern}
                    )
        elif isinstance(value, dict):
            for key, val in value.items():
                check_value(val, f"{path}.{key}" if path else key)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                check_value(item, f"{path}[{i}]")
    
    # Check the config data
    check_value(config_data)


class ConfigManager:
    """Thread-safe singleton configuration manager"""
    
    _instance: Optional['ConfigManager'] = None
    _lock = threading.Lock()
    _config: Optional[GatewayConfig] = None
    _config_path: Optional[str] = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize config manager (only called once due to singleton)"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._reload_lock = threading.Lock()
    
    def load(self, config_path: Optional[str] = None, force_reload: bool = False) -> GatewayConfig:
        """Load configuration with thread-safe caching
        
        Args:
            config_path: Optional path to config file. If None, uses default.
            force_reload: If True, reload config even if cached.
            
        Returns:
            GatewayConfig instance
        """
        # Determine config path
        if config_path is None:
            config_path = os.getenv("CONFIG_PATH", "./config.json")
        
        # Check if we can use cached config
        if not force_reload and self._config is not None and self._config_path == config_path:
            return self._config
        
        # Load config with thread-safe lock
        with self._reload_lock:
            # Double-check after acquiring lock
            if not force_reload and self._config is not None and self._config_path == config_path:
                return self._config
            
            # Load configuration
            try:
                # Try to use dynaconf for multi-environment support
                try:
                    from dynaconf import Dynaconf
                    
                    # Determine environment
                    env = os.getenv("ENVIRONMENT", "development").lower()
                    
                    # Initialize dynaconf with environment support
                    settings = Dynaconf(
                        envvar_prefix="LUMNI",
                        settings_files=['config.json', f'config.{env}.json'],
                        environments=True,
                        env=env,
                        load_dotenv=True,
                        dotenv_path=".env",
                    )
                    
                    # Get config as dict, resolving env vars
                    config_data = settings.as_dict()
                    
                    # Resolve additional ${ENV_VAR} patterns that dynaconf might not handle
                    resolved_config = resolve_env_vars(config_data)
                    
                    # Convert to Pydantic model
                    self._config = GatewayConfig(**resolved_config)
                    self._config_path = config_path
                    logger.info("Configuration loaded via dynaconf")
                    return self._config
                except ImportError:
                    # Fallback to original implementation if dynaconf not available
                    pass
                
                # Original implementation (fallback)
                config_file = Path(config_path).resolve()
                if not config_file.exists():
                    raise FileNotFoundError(
                        f"Configuration file not found: {config_file}\n"
                        "Please copy config.example.json to config.json and configure it"
                    )
                
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                # Validate no secrets in config file (before resolving env vars)
                # Only check in production or if explicitly enabled
                if os.getenv("ENVIRONMENT", "development").lower() == "production" or \
                   os.getenv("VALIDATE_CONFIG_SECRETS", "false").lower() == "true":
                    try:
                        validate_no_secrets_in_config(config_data)
                    except ConfigurationError as e:
                        logger.error(f"Config validation failed: {e.message}")
                        raise
                
                # Resolve environment variables
                resolved_config = resolve_env_vars(config_data)
                
                # Convert to Pydantic model
                self._config = GatewayConfig(**resolved_config)
                self._config_path = config_path
                logger.info(f"Configuration loaded from {config_file}")
                return self._config
                
            except Exception as e:
                logger.error(f"Failed to load configuration: {str(e)}")
                # If we have a cached config, return it even if reload failed
                if self._config is not None:
                    logger.warn("Using cached configuration due to load failure")
                    return self._config
                raise
    
    def get(self) -> Optional[GatewayConfig]:
        """Get cached configuration without loading
        
        Returns:
            Cached GatewayConfig or None if not loaded
        """
        return self._config
    
    def reload(self, config_path: Optional[str] = None) -> GatewayConfig:
        """Force reload configuration
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            GatewayConfig instance
        """
        return self.load(config_path, force_reload=True)
    
    def clear_cache(self):
        """Clear cached configuration"""
        with self._reload_lock:
            self._config = None
            self._config_path = None


# Global singleton instance accessor
def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager singleton instance"""
    return ConfigManager()


# Convenience function for backward compatibility
def load_config(config_path: Optional[str] = None) -> GatewayConfig:
    """Load configuration (backward compatibility wrapper)
    
    This function is maintained for backward compatibility.
    New code should use ConfigManager directly.
    """
    return get_config_manager().load(config_path)

