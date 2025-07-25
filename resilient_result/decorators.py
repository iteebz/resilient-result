"""@resilient decorator - converts exceptions to Result pattern."""

import functools
import inspect
from typing import Awaitable, Callable, TypeVar, Union

from .result import Result

T = TypeVar("T")


def resilient(
    func: Callable[..., Union[T, Awaitable[T]]]
) -> Callable[..., Union[Result, Awaitable[Result]]]:
    """@resilient - Converts function exceptions to Result.fail(), success to Result.ok().

    Catches all exceptions from the decorated function and converts them to Result.fail().
    Successful executions return Result.ok(data).

    Examples:
        @resilient
        def divide(a: int, b: int) -> int:
            return a // b

        result = divide(10, 2)  # Result.ok(5)
        result = divide(10, 0)  # Result.fail("integer division or modulo by zero")

        @resilient
        async def fetch_data() -> dict:
            return {"data": "value"}

        result = await fetch_data()  # Result.ok({"data": "value"})

    Returns:
        Decorator that converts function to return Result[T, str] instead of raising exceptions
    """

    # Determine if function is async
    is_async = inspect.iscoroutinefunction(func)

    if is_async:

        @functools.wraps(func)
        async def async_result_wrapper(*args, **kwargs) -> Result:
            try:
                result = await func(*args, **kwargs)
                return Result.ok(result)
            except Exception as e:
                return Result.fail(str(e))

        return async_result_wrapper
    else:

        @functools.wraps(func)
        def sync_result_wrapper(*args, **kwargs) -> Result:
            try:
                result = func(*args, **kwargs)
                return Result.ok(result)
            except Exception as e:
                return Result.fail(str(e))

        return sync_result_wrapper
