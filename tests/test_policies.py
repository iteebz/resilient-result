"""Tests for policy-based resilience configuration."""

import asyncio

import pytest

from resilient_result import Backoff, Circuit, Retry, resilient


def test_retry_defaults():
    retry = Retry()
    assert retry.attempts == 3
    assert retry.timeout is None


def test_retry_custom():
    retry = Retry(attempts=5, timeout=30.0)
    assert retry.attempts == 5
    assert retry.timeout == 30.0


def test_retry_api_preset():
    retry = Retry.api()
    assert retry.attempts == 3
    assert retry.timeout == 30.0


def test_retry_db_preset():
    retry = Retry.db()
    assert retry.attempts == 5
    assert retry.timeout == 60.0


def test_retry_ml_preset():
    retry = Retry.ml()
    assert retry.attempts == 2
    assert retry.timeout == 120.0


def test_circuit_defaults():
    circuit = Circuit()
    assert circuit.failures == 5
    assert circuit.window == 300


def test_circuit_custom():
    circuit = Circuit(failures=3, window=60)
    assert circuit.failures == 3
    assert circuit.window == 60


def test_circuit_fast_preset():
    circuit = Circuit.fast()
    assert circuit.failures == 3
    assert circuit.window == 60


def test_circuit_standard_preset():
    circuit = Circuit.standard()
    assert circuit.failures == 5
    assert circuit.window == 300


def test_backoff_defaults():
    backoff = Backoff()
    assert backoff.strategy == "exponential"
    assert backoff.delay == 1.0
    assert backoff.factor == 2.0
    assert backoff.max_delay == 30.0


def test_exponential_backoff():
    backoff = Backoff.exp(delay=0.1, factor=2.0, max_delay=10.0)
    assert backoff.calculate(0) == 0.1
    assert backoff.calculate(1) == 0.2
    assert backoff.calculate(2) == 0.4
    assert backoff.calculate(10) == 10.0  # Capped at max_delay


def test_linear_backoff():
    backoff = Backoff.linear(delay=1.0, max_delay=5.0)
    assert backoff.calculate(0) == 1.0
    assert backoff.calculate(1) == 2.0
    assert backoff.calculate(2) == 3.0
    assert backoff.calculate(10) == 5.0  # Capped at max_delay


def test_fixed_backoff():
    backoff = Backoff.fixed(delay=2.0)
    assert backoff.calculate(0) == 2.0
    assert backoff.calculate(1) == 2.0
    assert backoff.calculate(5) == 2.0


@pytest.mark.asyncio
async def test_basic_policy_usage(call_counter, fast_backoff):
    @resilient(retry=Retry(attempts=2), backoff=fast_backoff)
    async def func():
        if call_counter.increment() < 2:
            raise ValueError("Test error")
        return "success"

    result = await func()
    assert result.success
    assert result.data == "success"
    assert call_counter.count == 2


@pytest.mark.asyncio
async def test_timeout_in_retry_policy(slow_func):
    @resilient(retry=Retry(attempts=1, timeout=0.001))
    async def func():
        await asyncio.sleep(0.1)
        return "too slow"

    result = await func()
    assert result.failure


@pytest.mark.asyncio
async def test_presets(call_counter):
    @resilient(retry=Retry.api(), backoff=Backoff.exp(delay=0.001))
    async def api_call():
        if call_counter.increment() < 3:
            raise ConnectionError("API down")
        return {"data": "success"}

    result = await api_call()
    assert result.success
    assert result.data == {"data": "success"}
    assert call_counter.count == 3


@pytest.mark.asyncio
async def test_default_policies(call_counter):
    @resilient()
    async def func():
        if call_counter.increment() < 2:
            raise RuntimeError("Default test")
        return "default success"

    result = await func()
    assert result.success
    assert result.data == "default success"
    assert call_counter.count == 2


def test_sync_policies(call_counter, fast_backoff):
    @resilient(retry=Retry(attempts=2), backoff=fast_backoff)
    def func():
        if call_counter.increment() < 2:
            raise ValueError("Sync error")
        return "sync success"

    result = func()
    assert result.success
    assert result.data == "sync success"
    assert call_counter.count == 2
