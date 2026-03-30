from lib.browser_engine.browser_types import BrowserType
from utils.logging.log_levels import LogLevel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from __future__ import annotations
from typing import List, Union
from enum import Enum
import os

class Environment(str, Enum):
    """Supported deployment environments."""
    
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class BaseKioskConfig(BaseSettings):
    """Base configuration class with common settings for all environments.
    
    This class defines the core configuration schema and default values that are
    shared across all deployment environments. Environment-specific classes inherit
    from this base and override values as needed.
    
    All configuration values can be overridden via environment variables or .env file.
    Environment variables are case-insensitive and will be automatically loaded.
    
    Attributes:
        environment: Current deployment environment (local/staging/production)
        browser_type: Browser engine to use (chromium/chrome/msedge)
        headless: Whether to run browser without GUI
        kiosk_mode: Enable full-screen kiosk mode
        start_url: Initial URL to load on browser start
        window_width: Browser window width in pixels (minimum 800)
        window_height: Browser window height in pixels (minimum 600)
        enable_rotation: Enable automatic tab rotation through URLs
        rotation_urls: List of URLs to cycle through when rotation is enabled
        rotation_interval: Seconds between automatic tab switches (minimum 5)
        disable_infobars: Hide Chrome information bars
        disable_notifications: Block browser notification prompts
        disable_session_restore: Prevent session restore dialogs
        disable_gpu: Disable GPU acceleration (useful for headless/embedded systems)
        disable_dev_shm: Disable /dev/shm usage (useful for Docker/limited memory)
        page_load_timeout: Maximum time to wait for page load in milliseconds
        navigation_timeout: Maximum time to wait for navigation in milliseconds
        auto_restart_on_crash: Automatically restart browser on crash
        max_restart_attempts: Maximum consecutive restart attempts before giving up
        log_level: Application logging verbosity level
        enable_console_logging: Log browser console messages to application logs
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
    )
    
    # Environment
    environment: Environment = Environment.LOCAL
    
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
    log_level: LogLevel = LogLevel.INFO
    enable_console_logging: bool = True
    
    @field_validator("rotation_urls", mode="before")
    @classmethod
    def parse_rotation_urls(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse rotation URLs from comma-separated string or list.
        
        Args:
            v: Either a comma-separated string of URLs or a list of URL strings
            
        Returns:
            List of URL strings with whitespace stripped
            
        Example:
            >>> parse_rotation_urls("https://a.com, https://b.com")
            ['https://a.com', 'https://b.com']
        """
        if isinstance(v, str):
            return [url.strip() for url in v.split(",") if url.strip()]
        return v
    
    def get_browser_args(self) -> List[str]:
        """Generate Chromium launch arguments based on current configuration.
        
        Constructs a list of command-line arguments for Chromium/Chrome browser
        based on the enabled configuration flags. This includes kiosk mode settings,
        performance optimizations, and security/privacy flags.
        
        Returns:
            List of command-line arguments to pass to browser launch
            
        Example:
            >>> config = BaseKioskConfig(kiosk_mode=True, disable_gpu=True)
            >>> args = config.get_browser_args()
            >>> "--kiosk" in args
            True
            >>> "--disable-gpu" in args
            True
        """
        args: List[str] = []
        
        # Kiosk mode flags
        if self.kiosk_mode:
            args.extend([
                "--kiosk",
                "--start-fullscreen",
            ])
        
        # UI element suppression
        if self.disable_infobars:
            args.append("--disable-infobars")
        
        if self.disable_notifications:
            args.append("--disable-notifications")
        
        if self.disable_session_restore:
            args.extend([
                "--disable-session-crashed-bubble",
                "--disable-restore-session-state",
            ])
        
        # Performance optimizations
        if self.disable_gpu:
            args.extend([
                "--disable-gpu",
                "--disable-software-rasterizer",
            ])
        
        if self.disable_dev_shm:
            args.append("--disable-dev-shm-usage")
        
        # Standard kiosk-friendly arguments for unattended operation
        args.extend([
            "--no-first-run",  # Skip first-run wizards
            "--no-default-browser-check",  # Don't check if default browser
            "--disable-translate",  # Disable translation prompts
            "--disable-features=TranslateUI",
            "--disable-popup-blocking",  # Allow popups (kiosk context)
            "--disable-prompt-on-repost",  # Don't confirm form resubmission
            "--disable-background-timer-throttling",  # Keep background tabs active
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-hang-monitor",  # Don't show "page unresponsive" dialogs
            "--disable-ipc-flooding-protection",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",  # No auto-updates during operation
            "--disable-default-apps",
            "--disable-domain-reliability",
            "--disable-features=AutofillServerCommunication",
            "--disable-sync",  # No Google account sync
            "--metrics-recording-only",  # Minimal telemetry
            "--no-pings",
            "--password-store=basic",  # Simple password storage
            "--use-mock-keychain",
            "--autoplay-policy=no-user-gesture-required",  # Allow autoplay
        ])
        
        return args


class LocalConfig(BaseKioskConfig):
    """Configuration for local development environment.
    
    Optimized for development with verbose logging and debugging features enabled.
    Uses non-headless mode by default for easier debugging and development.
    """
    
    environment: Environment = Environment.LOCAL
    headless: bool = False  # Show browser for debugging
    log_level: LogLevel = LogLevel.DEBUG  # Verbose logging
    enable_console_logging: bool = True
    kiosk_mode: bool = False  # Easier to interact with during dev


class StagingConfig(BaseKioskConfig):
    """Configuration for staging environment.
    
    Mirrors production settings but with enhanced logging for testing and validation.
    Used for pre-production testing and quality assurance.
    """
    
    environment: Environment = Environment.STAGING
    headless: bool = False  # Can still observe behavior
    log_level: LogLevel = LogLevel.INFO
    enable_console_logging: bool = True
    auto_restart_on_crash: bool = True
    max_restart_attempts: int = Field(default=5, ge=1)  # More lenient for testing


class ProductionConfig(BaseKioskConfig):
    """Configuration for production environment.
    
    Optimized for stability, performance, and unattended operation.
    Uses headless mode and minimal logging for production deployments.
    """
    
    environment: Environment = Environment.PRODUCTION
    headless: bool = True  # Headless for production
    log_level: LogLevel = LogLevel.WARNING  # Minimal logging
    enable_console_logging: bool = False  # Reduce noise
    auto_restart_on_crash: bool = True
    max_restart_attempts: int = Field(default=3, ge=1)
    disable_gpu: bool = True  # Often needed in server environments
    disable_dev_shm: bool = True  # Docker/container friendly


# Environment to config class mapping
_CONFIG_MAP: dict[str, type[BaseKioskConfig]] = {
    Environment.LOCAL: LocalConfig,
    Environment.STAGING: StagingConfig,
    Environment.PRODUCTION: ProductionConfig,
}


def get_config(env: Union[str, Environment, None] = None) -> BaseKioskConfig:
    """Factory function to get environment-specific configuration instance.
    
    Creates and returns the appropriate configuration object based on the specified
    or detected environment. Environment detection follows this priority:
    1. Explicit env parameter
    2. ENVIRONMENT environment variable
    3. Default to LOCAL
    
    Args:
        env: Target environment name (local/staging/production) or None for auto-detect
        
    Returns:
        Configuration instance for the specified environment
        
    Raises:
        ValueError: If specified environment is not supported
        
    Example:
        >>> config = get_config("production")
        >>> config.environment
        <Environment.PRODUCTION: 'production'>
        
        >>> config = get_config()  # Auto-detect from ENVIRONMENT env var
        >>> config.log_level
        <LogLevel.DEBUG: 'DEBUG'>
    """
    # Determine environment from parameter, env var, or default
    if env is None:
        env_str = os.getenv("ENVIRONMENT", Environment.LOCAL.value).lower()
    else:
        env_str = env.value if isinstance(env, Environment) else env.lower()
    
    # Validate environment
    try:
        environment = Environment(env_str)
    except ValueError:
        valid_envs = ", ".join([e.value for e in Environment])
        raise ValueError(
            f"Invalid environment '{env_str}'. Must be one of: {valid_envs}"
        )
    
    # Return appropriate config instance
    config_class = _CONFIG_MAP[environment]
    return config_class()


# Global config instance - auto-detects environment
config: BaseKioskConfig = get_config()


__all__ = [
    "BaseKioskConfig",
    "LocalConfig",
    "StagingConfig",
    "ProductionConfig",
    "Environment",
    "BrowserType",
    "LogLevel",
    "get_config",
    "config",
]