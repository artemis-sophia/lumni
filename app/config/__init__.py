"""
Configuration Management with Pydantic Settings
Supports JSON config file with environment variable substitution
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import Field, BaseModel


class ServerConfig(BaseModel):
    """Server configuration"""
    port: int = 3000
    host: str = "0.0.0.0"


class AuthConfig(BaseModel):
    """Authentication configuration"""
    unified_api_key: str = Field(..., alias="unifiedApiKey")
    key_rotation_enabled: bool = Field(False, alias="keyRotationEnabled")

    class Config:
        populate_by_name = True


class ProviderRateLimit(BaseModel):
    """Provider rate limit configuration"""
    requests_per_minute: int = Field(..., alias="requestsPerMinute")
    requests_per_day: int = Field(..., alias="requestsPerDay")

    class Config:
        populate_by_name = True


class ProviderConfig(BaseModel):
    """Provider configuration"""
    enabled: bool = True
    api_key: str = Field(..., alias="apiKey")
    base_url: Optional[str] = Field(None, alias="baseUrl")
    priority: int = 1
    rate_limit: ProviderRateLimit = Field(..., alias="rateLimit")

    class Config:
        populate_by_name = True


class FallbackConfig(BaseModel):
    """Fallback configuration"""
    enabled: bool = True
    strategy: str = "priority"  # priority, round-robin, least-used
    health_check_interval: int = Field(30000, alias="healthCheckInterval")
    retry_attempts: int = Field(3, alias="retryAttempts")
    retry_delay: int = Field(1000, alias="retryDelay")

    class Config:
        populate_by_name = True


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    enabled: bool = True
    track_usage: bool = Field(True, alias="trackUsage")
    alert_threshold: float = Field(0.8, alias="alertThreshold")
    persist_metrics: bool = Field(True, alias="persistMetrics")

    class Config:
        populate_by_name = True


class StorageConfig(BaseModel):
    """Storage configuration"""
    type: str = "sqlite"  # sqlite, postgresql
    path: str = "./data/gateway.db"
    connection_string: Optional[str] = Field(None, alias="connectionString")

    class Config:
        populate_by_name = True


class LiteLLMConfig(BaseModel):
    """LiteLLM configuration"""
    config_path: str = Field("./litellm_config.yaml", alias="configPath")
    proxy: Dict[str, Any] = {}

    class Config:
        populate_by_name = True


class PortkeyConfig(BaseModel):
    """Portkey AI configuration"""
    enabled: bool = False
    api_key: Optional[str] = Field(None, alias="apiKey")
    environment: str = "development"
    virtual_key: Optional[str] = Field(None, alias="virtualKey")
    config: Dict[str, Any] = {}

    class Config:
        populate_by_name = True


class AcademicConfig(BaseModel):
    """Academic task classification configuration"""
    task_classification: Dict[str, Any] = Field(..., alias="taskClassification")
    benchmark_selection: Dict[str, Any] = Field(..., alias="benchmarkSelection")

    class Config:
        populate_by_name = True


class CacheConfig(BaseModel):
    """Cache configuration"""
    type: str = "memory"  # memory, redis
    connection_string: Optional[str] = Field(None, alias="connectionString")
    ttl: int = 3600

    class Config:
        populate_by_name = True


class GatewayConfig(BaseModel):
    """Main gateway configuration"""
    server: ServerConfig
    auth: AuthConfig
    providers: Dict[str, ProviderConfig]
    fallback: FallbackConfig
    monitoring: MonitoringConfig
    storage: StorageConfig
    litellm: LiteLLMConfig
    portkey: PortkeyConfig
    academic: AcademicConfig
    cache: CacheConfig

    class Config:
        populate_by_name = True


def resolve_env_vars(obj: Any) -> Any:
    """Resolve environment variables in config object"""
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        env_var = obj[2:-1]
        value = os.getenv(env_var)
        
        # Special handling: Codestral can fallback to MISTRAL_API_KEY
        if env_var == "CODESTRAL_API_KEY" and not value:
            value = os.getenv("MISTRAL_API_KEY")
        
        return value or obj
    
    if isinstance(obj, list):
        return [resolve_env_vars(item) for item in obj]
    
    if isinstance(obj, dict):
        return {key: resolve_env_vars(value) for key, value in obj.items()}
    
    return obj


def load_config(config_path: Optional[str] = None) -> GatewayConfig:
    """Load configuration from JSON file with environment variable substitution"""
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "./config.json")
    
    # Resolve path for cross-platform compatibility
    config_file = Path(config_path).resolve()
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            "Please copy config.example.json to config.json and configure it"
        )
    
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    # Resolve environment variables
    resolved_config = resolve_env_vars(config_data)
    
    # Convert to Pydantic model
    return GatewayConfig(**resolved_config)

