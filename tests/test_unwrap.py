"""Tests for unwrap() utility function."""

import pytest

from resilient_result import Err, Ok, unwrap


def test_unwrap_success():
    """unwrap() should extract data from successful Result."""
    result = Ok("test_data")
    assert unwrap(result) == "test_data"


def test_unwrap_failure_with_exception():
    """unwrap() should raise the original exception."""
    original_error = ValueError("test error")
    result = Err(original_error)

    with pytest.raises(ValueError, match="test error"):
        unwrap(result)


def test_unwrap_failure_with_string():
    """unwrap() should wrap non-exception errors in ValueError."""
    result = Err("string error")

    with pytest.raises(ValueError, match="Result failed with error: string error"):
        unwrap(result)


def test_unwrap_none_data():
    """unwrap() should handle None data correctly."""
    result = Ok(None)
    assert unwrap(result) is None


def test_unwrap_with_resilient_operations():
    """unwrap() should work with @resilient decorated functions."""
    from resilient_result import resilient

    @resilient
    def simple_operation():
        return "success"

    result = simple_operation()
    data = unwrap(result)
    assert data == "success"
