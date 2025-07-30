"""Test suite for Result pattern."""

from resilient_result import Err, Ok, Result


def test_ok_creation():
    """Test successful result creation."""
    result = Result.ok("success")
    assert result.success is True
    assert result.failure is False
    assert result.data == "success"
    assert result.error is None
    assert bool(result) is True


def test_fail_creation():
    """Test failed result creation."""
    result = Result.fail("error message")
    assert result.success is False
    assert result.failure is True
    assert result.data is None
    assert result.error == "error message"
    assert bool(result) is False


def test_ok_with_none():
    """Test Ok with None data."""
    result = Result.ok(None)
    assert result.success is True
    assert result.data is None
    assert result.error is None


def test_ok_with_various_types():
    """Test Ok with different data types."""
    # String
    result = Result.ok("hello")
    assert result.success is True
    assert result.data == "hello"

    # Number
    result = Result.ok(42)
    assert result.success is True
    assert result.data == 42

    # Dict
    data = {"key": "value"}
    result = Result.ok(data)
    assert result.success is True
    assert result.data == data

    # List
    data = [1, 2, 3]
    result = Result.ok(data)
    assert result.success is True
    assert result.data == data


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
    assert result.error == "processing failed"


def test_success_path_pattern():
    """Test success path usage pattern."""

    def process_data():
        result = Result.ok("raw data")
        if result.success:
            processed = result.data.upper()
            return Result.ok(processed)
        return result

    result = process_data()
    assert result.success is True
    assert result.data == "RAW DATA"


def test_ok_alias():
    """Test Ok constructor."""
    result = Ok("success")
    assert result.success is True
    assert result.data == "success"
    assert result.error is None


def test_err_alias():
    """Test Err constructor."""
    result = Err("error message")
    assert result.success is False
    assert result.error == "error message"
    assert result.data is None


def test_ok_none():
    """Test Ok with None."""
    result = Ok()
    assert result.success is True
    assert result.data is None


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
    assert successes[0].data == "method1"
    assert successes[1].data == "alias1"
    assert failures[0].error == "method2"
    assert failures[1].error == "alias2"


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
        step2_result = Result.ok(step1_result.data + "_step2")

        if not step2_result.success:
            return step2_result

        # Success
        return Result.ok(step2_result.data + "_complete")

    # All success
    result = multi_step_process()
    assert result.success is True
    assert result.data == "step1_data_step2_complete"

    # Fail at step 1
    result = multi_step_process(should_fail_at=1)
    assert result.failure is True
    assert result.error == "Step 1 failed"

    # Fail at step 2
    result = multi_step_process(should_fail_at=2)
    assert result.failure is True
    assert result.error == "Step 2 failed"


def test_result_aggregation():
    """Test aggregating multiple Results."""
    results = [
        Result.ok("data1"),
        Result.ok("data2"),
        Result.fail("error1"),
        Result.ok("data3"),
        Result.fail("error2"),
    ]

    successes = [r.data for r in results if r.success]
    failures = [r.error for r in results if r.failure]

    assert successes == ["data1", "data2", "data3"]
    assert failures == ["error1", "error2"]
