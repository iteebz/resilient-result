"""Standard error types for resilient operations."""


class NetworkError(Exception):
    """Network operation errors."""

    pass


class ParsingError(Exception):
    """Parsing and data transformation errors."""

    pass


class TimeoutError(Exception):
    """Operation timeout errors."""

    pass
