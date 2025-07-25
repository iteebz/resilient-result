"""Perfect Result pattern - concise factories, descriptive properties."""

from typing import Any, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    """Perfect Result pattern - best of both worlds."""

    def __init__(self, data: T = None, error: E = None):
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: T = None) -> "Result[T, E]":
        """Create successful result."""
        return cls(data=data)

    @classmethod
    def fail(cls, error: E) -> "Result[T, E]":
        """Create failed result."""
        return cls(error=error)

    @property
    def success(self) -> bool:
        """Check if successful."""
        return self.error is None

    @property
    def failure(self) -> bool:
        """Check if failed."""
        return self.error is not None

    def __bool__(self) -> bool:
        """Allow if result: checks."""
        return self.success

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok({repr(self.data)})"
        else:
            return f"Result.fail({repr(self.error)})"


# Rust-style aliases for streaming compatibility
def Ok(data: T = None) -> Result[T, str]:
    """Rust-style Ok constructor."""
    return Result.ok(data)


def Err(error: str) -> Result[Any, str]:
    """Rust-style Err constructor."""
    return Result.fail(error)
