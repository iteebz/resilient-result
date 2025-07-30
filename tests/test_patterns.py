"""Test mechanism-focused resilience patterns."""

import pytest

from resilient_result import Retry, RetryError, resilient, retry


@pytest.mark.asyncio
async def test_retry_exhausted():
    """Test retry exhaustion returns RetryError."""

    @retry(attempts=2, error_type=RetryError)
    async def always_fails():
        raise ValueError("always fails")

    result = await always_fails()
    assert not result.success
    assert isinstance(result.error, RetryError)


@pytest.mark.asyncio
async def test_composition_patterns():
    """Test composing mechanism-focused decorators."""
    from resilient_result import compose, timeout

    @compose(timeout(1.0), retry(attempts=2))
    async def complex_operation():
        return "composed success"

    result = await complex_operation()
    assert result.success
    assert result.data == "composed success"


@pytest.mark.asyncio
async def test_resilient_presets():
    """Test resilient class presets are mechanism-focused."""

    @resilient.api()  # Composed timeout + retry
    async def api_call():
        return "api success"

    result = await api_call()
    assert result.success
    assert result.data == "api success"


@pytest.mark.asyncio
async def test_policy_based_retry():
    """Test policy-based retry configuration."""

    @resilient(retry=Retry.db())  # Database preset
    async def db_operation():
        return {"data": "from_database"}

    result = await db_operation()
    assert result.success
    assert result.data == {"data": "from_database"}
