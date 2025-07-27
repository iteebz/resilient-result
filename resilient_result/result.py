"""Perfect Result pattern - concise factories, descriptive properties."""

import asyncio
from typing import Any, Generic, List, TypeVar

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

    def flatten(self) -> "Result[T, E]":
        """Flatten nested Result objects - enables clean boundary discipline.

        Example:
            Result.ok(Result.ok("data")) -> Result.ok("data")
            Result.ok(Result.fail("error")) -> Result.fail("error")
        """
        if not self.success:
            return self  # Already failed, nothing to flatten

        # If data is a Result, flatten it
        if isinstance(self.data, Result):
            return self.data.flatten()  # Recursively flatten

        return self  # No nesting, return as-is

    @classmethod
    async def collect(cls, operations: List[Any]) -> "Result[List[T], E]":
        """Collect multiple async operations into a single Result.

        All operations must succeed for the result to be successful.
        Returns Result.ok([data1, data2, ...]) if all succeed.
        Returns Result.fail(first_error) if any fails.
        """
        results = await asyncio.gather(*operations, return_exceptions=True)

        collected_data = []
        for result in results:
            if isinstance(result, Exception):
                return cls.fail(result)
            elif isinstance(result, Result):
                if result.failure:
                    return cls.fail(result.error)
                collected_data.append(result.data)
            else:
                collected_data.append(result)

        return cls.ok(collected_data)

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok({repr(self.data)})"
        else:
            return f"Result.fail({repr(self.error)})"


# Rust-style constructors that return proper Result instances
def Ok(data: T = None) -> Result[T, Any]:
    """Rust-style Ok constructor - returns proper Result instance."""
    return Result.ok(data)


def Err(error: E) -> Result[Any, E]:
    """Rust-style Err constructor - returns proper Result instance."""
    return Result.fail(error)


def unwrap(result: Result[T, E]) -> T:
    """Extract data from Result, raising exception if failed.

    Usage:
        data = unwrap(some_operation())  # Raises if failed
    """
    if result.success:
        return result.data
    else:
        # Raise the original error if it's an exception, otherwise wrap it
        if isinstance(result.error, Exception):
            raise result.error
        else:
            raise ValueError(f"Result failed with error: {result.error}")
