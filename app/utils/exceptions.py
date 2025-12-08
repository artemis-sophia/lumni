"""
Custom Exceptions
Structured exception hierarchy for better error handling
"""


class LumniError(Exception):
    """Base exception for Lumni"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(LumniError):
    """Configuration-related errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ProviderError(LumniError):
    """Provider-related errors"""
    def __init__(self, message: str, provider: str = None, details: dict = None):
        if provider:
            details = details or {}
            details["provider"] = provider
        super().__init__(message, "PROVIDER_ERROR", details)


class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    def __init__(self, provider: str, model: str = None, details: dict = None):
        message = f"Rate limit exceeded for provider {provider}"
        if model:
            message += f" model {model}"
        details = details or {}
        if model:
            details["model"] = model
        super().__init__(message, provider, details)
        self.code = "RATE_LIMIT_ERROR"


class ModelNotFoundError(ProviderError):
    """Model not found"""
    def __init__(self, provider: str, model: str, details: dict = None):
        message = f"Model {model} not found for provider {provider}"
        details = details or {}
        details["model"] = model
        super().__init__(message, provider, details)
        self.code = "MODEL_NOT_FOUND"


class AuthenticationError(LumniError):
    """Authentication errors"""
    def __init__(self, message: str = "Invalid API key", details: dict = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class ValidationError(LumniError):
    """Request validation errors"""
    def __init__(self, message: str, field: str = None, details: dict = None):
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class DatabaseError(LumniError):
    """Database-related errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DATABASE_ERROR", details)


class CacheError(LumniError):
    """Cache-related errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CACHE_ERROR", details)

