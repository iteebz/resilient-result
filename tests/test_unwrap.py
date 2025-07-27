"""Tests for unwrap() utility function."""

import pytest

from resilient_result import Err, Ok, unwrap


class TestUnwrap:
    """Test the unwrap() utility function."""

    def test_unwrap_success(self):
        """unwrap() should extract data from successful Result."""
        result = Ok("test_data")
        assert unwrap(result) == "test_data"

    def test_unwrap_failure_with_exception(self):
        """unwrap() should raise the original exception."""
        original_error = ValueError("test error")
        result = Err(original_error)

        with pytest.raises(ValueError, match="test error"):
            unwrap(result)

    def test_unwrap_failure_with_string(self):
        """unwrap() should wrap non-exception errors in ValueError."""
        result = Err("string error")

        with pytest.raises(ValueError, match="Result failed with error: string error"):
            unwrap(result)

    def test_unwrap_none_data(self):
        """unwrap() should handle None data correctly."""
        result = Ok(None)
        assert unwrap(result) is None

    def test_unwrap_with_resilient_operations(self):
        """unwrap() should work with @resilient decorated functions."""
        from resilient_result import resilient

        @resilient
        def simple_operation():
            return "success"

        result = simple_operation()
        data = unwrap(result)
        assert data == "success"
