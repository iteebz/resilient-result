"""Parsing resilience patterns."""

from typing import Optional

from .resilient import decorator


def parsing(retries: int = 3, error_type: Optional[type] = None):
    """@parsing - JSON parsing with correction, returns Result types."""
    from .errors import ParsingError
    from .policies import Retry

    if error_type is None:
        error_type = ParsingError

    async def handle_parsing(error: Exception) -> Optional[bool]:
        """Handle parsing-specific errors."""
        return None  # Always retry parsing errors

    return decorator(
        handler=handle_parsing, retry=Retry(attempts=retries), error_type=error_type
    )
