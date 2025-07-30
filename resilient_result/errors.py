"""Mechanism-focused error types for resilience patterns."""


class CircuitError(Exception):
    """Circuit breaker is open."""

    pass


class RateLimitError(Exception):
    """Rate limit exceeded."""

    pass


class RetryError(Exception):
    """Max retry attempts exhausted."""

    pass
