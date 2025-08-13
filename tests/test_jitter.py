"""Tests for backoff jitter functionality."""

from resilient_result import Backoff


def test_jitter_default_enabled():
    backoff = Backoff()
    assert backoff.jitter is True


def test_jitter_disabled():
    backoff = Backoff(jitter=False)
    assert backoff.jitter is False


def test_exponential_jitter_variance():
    backoff = Backoff.exp(delay=1.0, jitter=True)

    # Generate multiple delays for same attempt to test variance
    delays = [backoff.calculate(1) for _ in range(100)]

    # All delays should be between 50-100% of expected base delay (2.0)
    expected_base = 2.0
    min_expected = expected_base * 0.5
    max_expected = expected_base * 1.0

    for delay in delays:
        assert min_expected <= delay <= max_expected

    # Should have variance - not all identical
    unique_delays = set(delays)
    assert len(unique_delays) > 50  # Most should be unique


def test_exponential_no_jitter():
    backoff = Backoff.exp(delay=1.0, jitter=False)

    # Without jitter, delays should be deterministic
    delays = [backoff.calculate(1) for _ in range(10)]

    # All delays should be identical
    assert all(delay == 2.0 for delay in delays)


def test_linear_jitter():
    backoff = Backoff.linear(delay=1.0, jitter=True)

    # Attempt 2 should have base delay of 3.0
    delays = [backoff.calculate(2) for _ in range(50)]

    # All delays should be between 1.5-3.0
    for delay in delays:
        assert 1.5 <= delay <= 3.0


def test_fixed_jitter():
    backoff = Backoff.fixed(delay=2.0, jitter=True)

    # Fixed delay with jitter
    delays = [backoff.calculate(0) for _ in range(50)]

    # All delays should be between 1.0-2.0
    for delay in delays:
        assert 1.0 <= delay <= 2.0


def test_jitter_respects_max_delay():
    backoff = Backoff.exp(delay=10.0, factor=2.0, max_delay=5.0, jitter=True)

    # High attempt should hit max_delay, then apply jitter
    delays = [backoff.calculate(10) for _ in range(50)]

    # Should be 50-100% of max_delay (5.0)
    for delay in delays:
        assert 2.5 <= delay <= 5.0


def test_jitter_classmethod_defaults():
    exp_backoff = Backoff.exp()
    linear_backoff = Backoff.linear()
    fixed_backoff = Backoff.fixed()

    # All should have jitter enabled by default
    assert exp_backoff.jitter is True
    assert linear_backoff.jitter is True
    assert fixed_backoff.jitter is True


def test_jitter_classmethod_override():
    backoff = Backoff.exp(jitter=False)
    assert backoff.jitter is False

    # Should produce deterministic results
    delays = [backoff.calculate(1) for _ in range(5)]
    assert all(delay == delays[0] for delay in delays)
