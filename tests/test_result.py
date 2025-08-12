"""Test suite for Result pattern."""

import pytest

from resilient_result import Err, Ok, Result


def test_ok_creation():
    """Test successful result creation."""
    result = Result.ok("success")
    assert result.success is True
    assert result.failure is False
    assert result.unwrap() == "success"
    assert bool(result) is True


def test_fail_creation():
    """Test failed result creation."""
    result = Result.fail("error message")
    assert result.success is False
    assert result.failure is True
    with pytest.raises(ValueError, match="Result failed with error: error message"):
        result.unwrap()
    assert bool(result) is False


def test_ok_with_none():
    """Test Ok with None data."""
    result = Result.ok(None)
    assert result.success is True
    assert result.unwrap() is None


def test_ok_with_various_types():
    """Test Ok with different data types."""
    # String
    result = Result.ok("hello")
    assert result.success is True
    assert result.unwrap() == "hello"

    # Number
    result = Result.ok(42)
    assert result.success is True
    assert result.unwrap() == 42

    # Dict
    data = {"key": "value"}
    result = Result.ok(data)
    assert result.success is True
    assert result.unwrap() == data

    # List
    data = [1, 2, 3]
    result = Result.ok(data)
    assert result.success is True
    assert result.unwrap() == data


def test_repr():
    """Test string representation."""
    ok_result = Result.ok("data")
    assert repr(ok_result) == "Result.ok('data')"

    fail_result = Result.fail("error")
    assert repr(fail_result) == "Result.fail('error')"


def test_guard_clause_pattern():
    """Test common guard clause usage pattern."""

    def process_data():
        result = Result.fail("processing failed")
        if not result.success:
            return result
        return Result.ok("processed")

    result = process_data()
    assert result.failure is True
    with pytest.raises(ValueError, match="processing failed"):
        result.unwrap()


def test_success_path_pattern():
    """Test success path usage pattern."""

    def process_data():
        result = Result.ok("raw data")
        if result.success:
            processed = result.unwrap().upper()
            return Result.ok(processed)
        return result

    result = process_data()
    assert result.success is True
    assert result.unwrap() == "RAW DATA"


def test_ok_alias():
    """Test Ok constructor."""
    result = Ok("success")
    assert result.success is True
    assert result.unwrap() == "success"


def test_err_alias():
    """Test Err constructor."""
    result = Err("error message")
    assert result.success is False
    with pytest.raises(ValueError, match="error message"):
        result.unwrap()


def test_ok_none():
    """Test Ok with None."""
    result = Ok()
    assert result.success is True
    assert result.unwrap() is None


def test_mixed_usage():
    """Test mixing Result.ok/fail with Ok/Err."""
    results = [
        Result.ok("method1"),
        Ok("alias1"),
        Result.fail("method2"),
        Err("alias2"),
    ]

    successes = [r for r in results if r.success]
    failures = [r for r in results if r.failure]

    assert len(successes) == 2
    assert len(failures) == 2
    assert successes[0].unwrap() == "method1"
    assert successes[1].unwrap() == "alias1"
    with pytest.raises(ValueError, match="method2"):
        failures[0].unwrap()
    with pytest.raises(ValueError, match="alias2"):
        failures[1].unwrap()


def test_early_return_pattern():
    """Test early return with Results."""

    def multi_step_process(should_fail_at: int = None):
        # Step 1
        if should_fail_at == 1:
            return Result.fail("Step 1 failed")
        step1_result = Result.ok("step1_data")

        if not step1_result.success:
            return step1_result

        # Step 2
        if should_fail_at == 2:
            return Result.fail("Step 2 failed")
        step2_result = Result.ok(step1_result.unwrap() + "_step2")

        if not step2_result.success:
            return step2_result

        # Success
        return Result.ok(step2_result.unwrap() + "_complete")

    # All success
    result = multi_step_process()
    assert result.success is True
    assert result.unwrap() == "step1_data_step2_complete"

    # Fail at step 1
    result = multi_step_process(should_fail_at=1)
    assert result.failure is True
    with pytest.raises(ValueError, match="Step 1 failed"):
        result.unwrap()

    # Fail at step 2
    result = multi_step_process(should_fail_at=2)
    assert result.failure is True
    with pytest.raises(ValueError, match="Step 2 failed"):
        result.unwrap()


def test_result_aggregation():
    """Test aggregating multiple Results."""
    results = [
        Result.ok("data1"),
        Result.ok("data2"),
        Result.fail("error1"),
        Result.ok("data3"),
        Result.fail("error2"),
    ]

    successes = [r.unwrap() for r in results if r.success]
    # Test failures by checking they raise expected errors
    assert successes == ["data1", "data2", "data3"]

    failures = [r for r in results if r.failure]
    assert len(failures) == 2
    with pytest.raises(ValueError, match="error1"):
        failures[0].unwrap()
    with pytest.raises(ValueError, match="error2"):
        failures[1].unwrap()
