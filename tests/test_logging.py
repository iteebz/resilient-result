"""Tests for retry logging functionality."""

import logging

import pytest

from resilient_result import Backoff, retry


def test_debug_content(caplog):
    """Test DEBUG logging shows correct backoff calculations."""
    call_count = 0

    @retry(attempts=3, backoff=Backoff.fixed(2.5, jitter=False))
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("network timeout")
        return "success"

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = failing_func()

    assert result.success
    assert call_count == 3

    # Should have 2 debug logs (attempts 1→2 and 2→3)
    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug_logs) == 2

    # Verify first retry log content
    assert (
        "Retrying failing_func (attempt 2/3) after ConnectionError: waiting 2.5s"
        in debug_logs[0].message
    )
    # Verify second retry log content
    assert (
        "Retrying failing_func (attempt 3/3) after ConnectionError: waiting 2.5s"
        in debug_logs[1].message
    )


def test_exponential_backoff(caplog):
    """Test DEBUG logging shows exponential backoff."""
    call_count = 0

    @retry(attempts=3, backoff=Backoff.exp(delay=0.1, factor=2.0, jitter=False))
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("test error")
        return "success"

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = failing_func()

    assert result.success
    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug_logs) == 2

    # First retry: 0.1s delay
    assert "waiting 0.1s" in debug_logs[0].message
    # Second retry: 0.2s delay (0.1 * 2^1)
    assert "waiting 0.2s" in debug_logs[1].message


def test_recovery_info(caplog):
    """Test INFO logging on successful recovery."""
    call_count = 0

    @retry(attempts=3)
    def eventually_succeeds():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RuntimeError("temporary failure")
        return "recovered"

    with caplog.at_level(logging.INFO, logger="resilient_result"):
        result = eventually_succeeds()

    assert result.success

    # Should have 1 info log for successful recovery
    info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
    assert len(info_logs) == 1
    assert "eventually_succeeds succeeded after 3 attempts" in info_logs[0].message


def test_first_success_silent(caplog):
    """Test no logging when operation succeeds immediately."""

    @retry(attempts=3)
    def immediate_success():
        return "success"

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = immediate_success()

    assert result.success
    # No logs should be generated for immediate success
    assert len(caplog.records) == 0


def test_final_failure_silent(caplog):
    """Test no retry logging on final failure."""

    @retry(attempts=2)
    def always_fails():
        raise TimeoutError("always fails")

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = always_fails()

    assert result.failure

    # Should have only 1 debug log (for the single retry attempt)
    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug_logs) == 1
    assert "Retrying always_fails (attempt 2/2)" in debug_logs[0].message


@pytest.mark.asyncio
async def test_async_logging(caplog):
    """Test logging works with async functions."""
    call_count = 0

    @retry(attempts=2, backoff=Backoff.fixed(1.0, jitter=False))
    async def async_failing():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("async failure")
        return "async success"

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = await async_failing()

    assert result.success

    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug_logs) == 1
    assert (
        "Retrying async_failing (attempt 2/2) after ConnectionError: waiting 1.0s"
        in debug_logs[0].message
    )

    info_logs = [r for r in caplog.records if r.levelno == logging.INFO]
    assert len(info_logs) == 1
    assert "async_failing succeeded after 2 attempts" in info_logs[0].message


def test_exception_types(caplog):
    """Test different exception types are logged."""
    call_count = 0

    @retry(attempts=3, backoff=Backoff.fixed(0.1))
    def mixed_failures():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("connection failed")
        if call_count == 2:
            raise TimeoutError("request timed out")
        return "success"

    with caplog.at_level(logging.DEBUG, logger="resilient_result"):
        result = mixed_failures()

    assert result.success
    debug_logs = [r for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug_logs) == 2

    # First retry should log ConnectionError
    assert "after ConnectionError" in debug_logs[0].message
    # Second retry should log TimeoutError
    assert "after TimeoutError" in debug_logs[1].message
