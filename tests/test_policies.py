"""Tests for policy-based resilience configuration."""

import asyncio

import pytest

from resilient_result import Backoff, Circuit, Retry, resilient


class TestRetryPolicy:
    """Test Retry policy functionality."""

    def test_retry_defaults(self):
        retry = Retry()
        assert retry.attempts == 3
        assert retry.timeout is None

    def test_retry_custom(self):
        retry = Retry(attempts=5, timeout=30.0)
        assert retry.attempts == 5
        assert retry.timeout == 30.0

    def test_retry_api_preset(self):
        retry = Retry.api()
        assert retry.attempts == 3
        assert retry.timeout == 30.0

    def test_retry_db_preset(self):
        retry = Retry.db()
        assert retry.attempts == 5
        assert retry.timeout == 60.0

    def test_retry_ml_preset(self):
        retry = Retry.ml()
        assert retry.attempts == 2
        assert retry.timeout == 120.0


class TestCircuitPolicy:
    """Test Circuit breaker policy functionality."""

    def test_circuit_defaults(self):
        circuit = Circuit()
        assert circuit.failures == 5
        assert circuit.window == 300

    def test_circuit_custom(self):
        circuit = Circuit(failures=3, window=60)
        assert circuit.failures == 3
        assert circuit.window == 60

    def test_circuit_fast_preset(self):
        circuit = Circuit.fast()
        assert circuit.failures == 3
        assert circuit.window == 60

    def test_circuit_standard_preset(self):
        circuit = Circuit.standard()
        assert circuit.failures == 5
        assert circuit.window == 300


class TestBackoffPolicy:
    """Test Backoff strategy functionality."""

    def test_backoff_defaults(self):
        backoff = Backoff()
        assert backoff.strategy == "exponential"
        assert backoff.delay == 1.0
        assert backoff.factor == 2.0
        assert backoff.max_delay == 30.0

    def test_exponential_backoff(self):
        backoff = Backoff.exp(delay=0.1, factor=2.0, max_delay=10.0)
        assert backoff.calculate(0) == 0.1
        assert backoff.calculate(1) == 0.2
        assert backoff.calculate(2) == 0.4
        assert backoff.calculate(10) == 10.0  # Capped at max_delay

    def test_linear_backoff(self):
        backoff = Backoff.linear(delay=1.0, max_delay=5.0)
        assert backoff.calculate(0) == 1.0
        assert backoff.calculate(1) == 2.0
        assert backoff.calculate(2) == 3.0
        assert backoff.calculate(10) == 5.0  # Capped at max_delay

    def test_fixed_backoff(self):
        backoff = Backoff.fixed(delay=2.0)
        assert backoff.calculate(0) == 2.0
        assert backoff.calculate(1) == 2.0
        assert backoff.calculate(5) == 2.0


class TestPolicyIntegration:
    """Test policy integration with @resilient decorator."""

    @pytest.mark.asyncio
    async def test_basic_policy_usage(self):
        """Test basic policy-based decorator usage."""
        call_count = 0

        @resilient(retry=Retry(attempts=2), backoff=Backoff.fixed(delay=0.001))
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"

        result = await failing_func()
        assert result.success
        assert result.data == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_in_retry_policy(self):
        """Test timeout specified in retry policy."""

        @resilient(retry=Retry(attempts=1, timeout=0.001))
        async def slow_func():
            await asyncio.sleep(0.1)
            return "too slow"

        result = await slow_func()
        assert result.failure

    @pytest.mark.asyncio
    async def test_beautiful_preset_combinations(self):
        """Test beautiful preset method combinations."""
        call_count = 0

        @resilient(retry=Retry.api(), backoff=Backoff.exp(delay=0.001))
        async def api_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("API down")
            return {"data": "success"}

        result = await api_call()
        assert result.success
        assert result.data == {"data": "success"}
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_default_policies(self):
        """Test that @resilient() still works with sensible defaults."""
        call_count = 0

        @resilient()
        async def default_behavior():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Default test")
            return "default success"

        result = await default_behavior()
        assert result.success
        assert result.data == "default success"
        assert call_count == 2

    def test_sync_function_with_policies(self):
        """Test sync functions work with new policy system."""
        call_count = 0

        @resilient(retry=Retry(attempts=2), backoff=Backoff.fixed(delay=0.001))
        def sync_failing():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Sync error")
            return "sync success"

        result = sync_failing()
        assert result.success
        assert result.data == "sync success"
        assert call_count == 2


class TestBackwardCompatibility:
    """Ensure old usage patterns still work during transition."""

    @pytest.mark.asyncio
    async def test_bare_resilient_decorator(self):
        """Test @resilient with no arguments still works."""

        @resilient
        async def simple_func():
            return "simple"

        result = await simple_func()
        assert result.success
        assert result.data == "simple"

    @pytest.mark.asyncio
    async def test_old_syntax_compatibility(self):
        """Test that old Resilient class methods still work."""
        from resilient_result import Resilient

        @Resilient().network(retries=2)
        async def network_call():
            return "network success"

        result = await network_call()
        assert result.success
        assert result.data == "network success"
