"""Tests for .unwrap() method."""

import pytest

from resilient_result import Err, Ok


def test_unwrap_success():
    """unwrap() should extract data from successful Result."""
    result = Ok("test_data")
    assert result.unwrap() == "test_data"


def test_unwrap_failure_with_exception():
    """unwrap() should raise the original exception."""
    original_error = ValueError("test error")
    result = Err(original_error)

    with pytest.raises(ValueError, match="test error"):
        result.unwrap()


def test_unwrap_failure_with_string():
    """unwrap() should wrap non-exception errors in ValueError."""
    result = Err("string error")

    with pytest.raises(ValueError, match="Result failed with error: string error"):
        result.unwrap()


def test_unwrap_none_data():
    """unwrap() should handle None data correctly."""
    result = Ok(None)
    assert result.unwrap() is None


def test_unwrap_with_resilient_operations():
    """unwrap() should work with @resilient decorated functions."""
    from resilient_result import resilient

    @resilient
    def simple_operation():
        return "success"

    result = simple_operation()
    data = result.unwrap()
    assert data == "success"
