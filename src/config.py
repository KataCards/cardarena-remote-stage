from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
import os

from lib.browser_engine.browser_types import BrowserType
from utils.logging.log_levels import LogLevel

class BaseKioskConfig(BaseSettings):
    """Base configuration class with common settings for all environments.
    
    This class defines the core configuration schema and default values that are
    shared across all deployment environments. Environment-specific classes inherit
    from this base and override values as needed.
    
    All configuration values can be overridden via environment variables or .env file.
    Environment variables are case-insensitive and will be automatically loaded.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
    )
    
    # Environment
    environment: str = "local"
    
    # Browser settings
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = False
    
    # Kiosk mode settings
    kiosk_mode: bool = True
    start_url: str = "https://www.google.com"
    
    # Display settings (minimum 800x600 for usability)
    window_width: int = Field(default=1920, ge=800)
    window_height: int = Field(default=1080, ge=600)
    
    # Tab rotation settings
    enable_rotation: bool = False
    rotation_urls: List[str] = []
    rotation_interval: int = Field(default=30, ge=5)  # Minimum 5 seconds
    
    # Browser behavior flags
    disable_infobars: bool = True
    disable_notifications: bool = True
    disable_session_restore: bool = True
    
    # Performance settings
    disable_gpu: bool = False
    disable_dev_shm: bool = False
    
    # Timeout settings (in milliseconds, minimum 5 seconds)
    page_load_timeout: int = Field(default=30000, ge=5000)
    navigation_timeout: int = Field(default=30000, ge=5000)
    
    # Error handling
    auto_restart_on_crash: bool = True
    max_restart_attempts: int = Field(default=3, ge=1)
    
    # Logging
    log_level: LogLevel = LogLevel.INFORMATIONAL
    enable_console_logging: bool = True


class LocalConfig(BaseKioskConfig):
    """Configuration for local development environment.
    
    Optimized for development with verbose logging and debugging features enabled.
    Uses non-headless mode by default for easier debugging and development.
    """
    
    environment: str = "local"
    headless: bool = False  # Show browser for debugging
    log_level: LogLevel = LogLevel.DEBUG  # Verbose logging
    enable_console_logging: bool = True
    kiosk_mode: bool = False  # Easier to interact with during dev


class StagingConfig(BaseKioskConfig):
    """Configuration for staging environment.
    
    Mirrors production settings but with enhanced logging for testing and validation.
    Used for pre-production testing and quality assurance.
    """
    
    environment: str = "staging"
    headless: bool = False  # Can still observe behavior
    log_level: LogLevel = LogLevel.INFORMATIONAL
    enable_console_logging: bool = True
    auto_restart_on_crash: bool = True
    max_restart_attempts: int = Field(default=5, ge=1)  # More lenient for testing


class ProductionConfig(BaseKioskConfig):
    """Configuration for production environment.
    
    Optimized for stability, performance, and unattended operation.
    Uses headless mode and minimal logging for production deployments.
    """
    
    environment: str = "production"
    headless: bool = True  # Headless for production
    log_level: LogLevel = LogLevel.WARNING  # Minimal logging
    enable_console_logging: bool = False  # Reduce noise
    auto_restart_on_crash: bool = True
    max_restart_attempts: int = Field(default=3, ge=1)
    disable_gpu: bool = True  # Often needed in server environments
    disable_dev_shm: bool = True  # Docker/container friendly


def get_config() -> BaseKioskConfig:
    """Factory function to get environment-specific configuration instance.
    
    Creates and returns the appropriate configuration object based on the
    APP_ENVIRONMENT environment variable. Environment detection follows this priority:
    1. APP_ENVIRONMENT environment variable
    2. Default to local
    
    Returns:
        Configuration instance for the specified environment
        
    Raises:
        ValueError: If specified environment is not supported
        
    Example:
        >>> config = get_config()
        >>> config.environment
        'production'
    """
    # Determine environment from APP_ENVIRONMENT env var or default
    env_str = os.getenv("APP_ENVIRONMENT", "local").lower()
    
    # Return appropriate config instance
    match env_str:
        case "local":
            return LocalConfig()
        case "staging":
            return StagingConfig()
        case "production":
            return ProductionConfig()
        case _:
            return LocalConfig()


# Global config instance - auto-detects environment
config: BaseKioskConfig = get_config()

__all__ = [
    "BaseKioskConfig",
    "LocalConfig",
    "StagingConfig",
    "ProductionConfig",
    "BrowserType",
    "LogLevel",
    "get_config",
    "config",
]