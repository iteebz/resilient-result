"""Resilient Result - Result pattern with @resilient decorators for clean error handling."""

from .decorators import resilient
from .result import Err, Ok, Result

__version__ = "0.1.0"
__all__ = ["Result", "Ok", "Err", "resilient"]
