"""Engine module - browser engine abstractions."""

from .base import Engine
from .playwright import PlaywrightEngine

__all__ = ["Engine", "PlaywrightEngine"]