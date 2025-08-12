"""Result type for error handling."""

import asyncio
from typing import Any, Generic, List, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    """Result type for success and failure cases."""

    def __init__(self, data: T = None, error: E = None):
        self._data = data
        self._error = error

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
        """True if result is successful."""
        return self._error is None

    @property
    def failure(self) -> bool:
        """True if result is failed."""
        return self._error is not None

    @property
    def error(self) -> E:
        """Error value for inspection."""
        return self._error

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
        if isinstance(self._data, Result):
            return self._data.flatten()  # Recursively flatten

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
            if isinstance(result, Result):
                if result.failure:
                    return cls.fail(result._error)
                collected_data.append(result._data)
            else:
                collected_data.append(result)

        return cls.ok(collected_data)

    def __eq__(self, other) -> bool:
        """Compare Results by value."""
        if not isinstance(other, Result):
            return False
        return self._data == other._data and self._error == other._error

    def unwrap(self):
        """Extract data, raising exception if failed."""
        if self.success:
            return self._data
        if isinstance(self._error, Exception):
            raise self._error
        raise ValueError(f"Result failed with error: {self._error}")

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok({repr(self._data)})"
        return f"Result.fail({repr(self._error)})"


# Constructor functions
def Ok(data: T = None) -> Result[T, Any]:
    """Create successful result."""
    return Result.ok(data)


def Err(error: E) -> Result[Any, E]:
    """Create failed result."""
    return Result.fail(error)
