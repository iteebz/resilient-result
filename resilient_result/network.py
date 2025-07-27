"""Network resilience patterns."""

from typing import Optional

from .resilient import decorator


def network(retries: int = 2, error_type: Optional[type] = None):
    """@network - Network calls with retry, returns Result types."""
    from .errors import NetworkError

    if error_type is None:
        error_type = NetworkError

    async def handle_network(error: Exception) -> Optional[bool]:
        """Handle network-specific errors."""
        error_str = str(error).lower()
        if "timeout" in error_str or "connection" in error_str:
            return None  # Retry
        return False  # Don't retry for other network errors

    from .policies import Retry

    return decorator(
        handler=handle_network, retry=Retry(attempts=retries), error_type=error_type
    )
