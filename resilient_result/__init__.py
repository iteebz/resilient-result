"""Resilient Result - Result pattern with resilience decorators for clean error handling."""

from .circuit import circuit
from .errors import NetworkError, ParsingError, TimeoutError
from .network import network
from .parsing import parsing
from .policies import Backoff, Circuit, Retry
from .rate_limit import rate_limit
from .resilient import Resilient, resilient
from .result import Err, Ok, Result, unwrap

__version__ = "0.3.0"
__all__ = [
    "Result",
    "Ok",
    "Err",
    "unwrap",
    "resilient",
    "Resilient",
    "Retry",
    "Circuit",
    "Backoff",
    "network",
    "parsing",
    "circuit",
    "rate_limit",
    "NetworkError",
    "ParsingError",
    "TimeoutError",
]
