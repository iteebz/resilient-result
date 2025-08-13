"""Universal defaults - single source of truth."""

# Retry defaults
RETRY_ATTEMPTS = 2
RETRY_BACKOFF = 1.0

# Backoff defaults
BACKOFF_JITTER = True  # Prevent thundering herd by default

# Circuit breaker defaults
CIRCUIT_FAILURES = 3
CIRCUIT_WINDOW = 60  # 1 minute

# Timeout default
TIMEOUT_SECONDS = 30.0

# Rate limit default
RATE_LIMIT_RPS = 100.0
