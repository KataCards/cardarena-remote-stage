from enum import Enum


class LogLevel(str, Enum):
    """RFC 5424 compliant logging levels.
    
    Simple enum for standard syslog severity levels compatible with Python logging.
    """
    
    EMERGENCY = "EMERGENCY"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    NOTICE = "NOTICE"
    INFORMATIONAL = "INFORMATIONAL"
    DEBUG = "DEBUG"


__all__ = ["LogLevel"]