"""Resilient Result - Result pattern with resilience decorators for clean error handling."""

from .circuit import circuit
from .errors import CircuitError, RateLimitError, RetryError
from .policies import Backoff, Circuit, Retry, Timeout
from .rate_limit import rate_limit
from .resilient import Resilient, compose, resilient, retry
from .result import Err, Ok, Result, unwrap
from .timeout import timeout

__version__ = "0.3.1"
__all__ = [
    "Result",
    "Ok",
    "Err",
    "unwrap",
    "resilient",
    "Resilient",
    "retry",
    "compose",
    "timeout",
    "circuit",
    "rate_limit",
    "Retry",
    "Circuit",
    "Backoff",
    "Timeout",
    "CircuitError",
    "RateLimitError",
    "RetryError",
]
