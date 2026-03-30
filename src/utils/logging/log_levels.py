"""Logging level definitions following RFC 5424 Syslog Protocol.

This module defines logging severity levels according to RFC 5424 (The Syslog Protocol).
RFC 5424 defines 8 severity levels (0-7), which we map to Python's logging levels.

Reference: https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1

The severity levels are:
    0 - Emergency: System is unusable
    1 - Alert: Action must be taken immediately
    2 - Critical: Critical conditions
    3 - Error: Error conditions
    4 - Warning: Warning conditions
    5 - Notice: Normal but significant condition
    6 - Informational: Informational messages
    7 - Debug: Debug-level messages
"""

from enum import IntEnum
import logging


class RFC5424Level(IntEnum):
    """RFC 5424 Syslog severity levels.
    
    These numeric severity levels follow the RFC 5424 standard for syslog messages.
    Lower numbers indicate higher severity.
    
    Attributes:
        EMERGENCY: System is unusable (severity 0)
        ALERT: Action must be taken immediately (severity 1)
        CRITICAL: Critical conditions (severity 2)
        ERROR: Error conditions (severity 3)
        WARNING: Warning conditions (severity 4)
        NOTICE: Normal but significant condition (severity 5)
        INFO: Informational messages (severity 6)
        DEBUG: Debug-level messages (severity 7)
    """
    
    EMERGENCY = 0  # System is unusable
    ALERT = 1      # Action must be taken immediately
    CRITICAL = 2   # Critical conditions
    ERROR = 3      # Error conditions
    WARNING = 4    # Warning conditions
    NOTICE = 5     # Normal but significant condition
    INFO = 6       # Informational messages
    DEBUG = 7      # Debug-level messages


class LogLevel(str, IntEnum):
    """Application logging levels mapped to RFC 5424 and Python logging.
    
    This enum provides a bridge between RFC 5424 syslog severity levels and
    Python's standard logging levels. Each level includes both the string name
    (for configuration) and numeric value (for comparison).
    
    Attributes:
        EMERGENCY: System is unusable - maps to CRITICAL (50)
        ALERT: Immediate action required - maps to CRITICAL (50)
        CRITICAL: Critical conditions - maps to CRITICAL (50)
        ERROR: Error conditions - maps to ERROR (40)
        WARNING: Warning conditions - maps to WARNING (30)
        NOTICE: Significant normal condition - maps to INFO (20)
        INFO: Informational messages - maps to INFO (20)
        DEBUG: Debug-level messages - maps to DEBUG (10)
    """
    
    # RFC 5424 Level 0 - Emergency: system is unusable
    EMERGENCY = "EMERGENCY"
    
    # RFC 5424 Level 1 - Alert: action must be taken immediately
    ALERT = "ALERT"
    
    # RFC 5424 Level 2 - Critical: critical conditions
    CRITICAL = "CRITICAL"
    
    # RFC 5424 Level 3 - Error: error conditions
    ERROR = "ERROR"
    
    # RFC 5424 Level 4 - Warning: warning conditions
    WARNING = "WARNING"
    
    # RFC 5424 Level 5 - Notice: normal but significant condition
    NOTICE = "NOTICE"
    
    # RFC 5424 Level 6 - Informational: informational messages
    INFO = "INFO"
    
    # RFC 5424 Level 7 - Debug: debug-level messages
    DEBUG = "DEBUG"
    
    def to_python_level(self) -> int:
        """Convert RFC 5424 level to Python logging level.
        
        Maps the RFC 5424 severity levels to Python's standard logging levels:
        - EMERGENCY, ALERT, CRITICAL -> logging.CRITICAL (50)
        - ERROR -> logging.ERROR (40)
        - WARNING -> logging.WARNING (30)
        - NOTICE, INFO -> logging.INFO (20)
        - DEBUG -> logging.DEBUG (10)
        
        Returns:
            Python logging level constant (10-50)
            
        Example:
            >>> LogLevel.ERROR.to_python_level()
            40
            >>> LogLevel.DEBUG.to_python_level()
            10
        """
        mapping = {
            LogLevel.EMERGENCY: logging.CRITICAL,  # 50
            LogLevel.ALERT: logging.CRITICAL,      # 50
            LogLevel.CRITICAL: logging.CRITICAL,   # 50
            LogLevel.ERROR: logging.ERROR,         # 40
            LogLevel.WARNING: logging.WARNING,     # 30
            LogLevel.NOTICE: logging.INFO,         # 20
            LogLevel.INFO: logging.INFO,           # 20
            LogLevel.DEBUG: logging.DEBUG,         # 10
        }
        return mapping[self]
    
    def to_rfc5424_severity(self) -> int:
        """Convert to RFC 5424 numeric severity level.
        
        Returns:
            RFC 5424 severity number (0-7)
            
        Example:
            >>> LogLevel.ERROR.to_rfc5424_severity()
            3
            >>> LogLevel.DEBUG.to_rfc5424_severity()
            7
        """
        mapping = {
            LogLevel.EMERGENCY: RFC5424Level.EMERGENCY,  # 0
            LogLevel.ALERT: RFC5424Level.ALERT,          # 1
            LogLevel.CRITICAL: RFC5424Level.CRITICAL,    # 2
            LogLevel.ERROR: RFC5424Level.ERROR,          # 3
            LogLevel.WARNING: RFC5424Level.WARNING,      # 4
            LogLevel.NOTICE: RFC5424Level.NOTICE,        # 5
            LogLevel.INFO: RFC5424Level.INFO,            # 6
            LogLevel.DEBUG: RFC5424Level.DEBUG,          # 7
        }
        return mapping[self]
    
    @classmethod
    def from_string(cls, level: str) -> "LogLevel":
        """Parse log level from string (case-insensitive).
        
        Args:
            level: String representation of log level
            
        Returns:
            Corresponding LogLevel enum value
            
        Raises:
            ValueError: If level string is not recognized
            
        Example:
            >>> LogLevel.from_string("error")
            <LogLevel.ERROR: 'ERROR'>
            >>> LogLevel.from_string("INFO")
            <LogLevel.INFO: 'INFO'>
        """
        level_upper = level.upper()
        try:
            return cls[level_upper]
        except KeyError:
            valid_levels = ", ".join([lv.value for lv in cls])
            raise ValueError(
                f"Invalid log level '{level}'. Must be one of: {valid_levels}"
            )
    
    @classmethod
    def get_default(cls) -> "LogLevel":
        """Get the default log level.
        
        Returns:
            Default log level (INFO)
        """
        return cls.INFO


__all__ = ["LogLevel", "RFC5424Level"]