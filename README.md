# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Resilience mechanisms with Result types.**

```python
from resilient_result import resilient, Result

# Simple: perfect defaults for most cases
@resilient()
async def call_api(url: str) -> str:
    return await http.get(url)

# Advanced: compose individual mechanisms
@timeout(seconds=10)
@retry(attempts=5)  
async def robust_call(url: str) -> str:
    return await http.get(url)

result: Result[str, Exception] = await call_api("https://api.example.com")
if result.success:
    data = result.unwrap()  # Extract data safely
    print(data)
else:
    print(f"Failed: {result.error}")  # Inspect error directly
```

**Why resilient-result?** Network calls fail. Databases timeout. APIs rate limit. Handle it cleanly without exception soup.

**Observability built-in:** Enable `logging.getLogger('resilient_result').setLevel(logging.DEBUG)` to see retry attempts and recovery.

**📖 [Result API](docs/result.md) | 🔧 [Resilience Patterns](docs/resilient.md)**

## Installation

```bash
pip install resilient-result
```

## Core Features

### Progressive Disclosure

```python
from resilient_result import resilient, retry, timeout, circuit, rate_limit

# Simple: Just works with reasonable defaults
@resilient()  # 2 attempts, 1s backoff, 30s timeout
async def simple_operation():
    return await external_service()

# Advanced: Compose individual mechanisms
@rate_limit(rps=100)         # Rate limiting (100 rps default)
@circuit(failures=3)         # Circuit breaker (1 minute window)
@timeout(seconds=10)         # Time-based protection
@retry(attempts=5)           # Retry mechanism
async def critical_operation():
    return await external_service()
```

### Result Usage
```python
from resilient_result import Result, Ok, Err

# Pattern 1: Check then unwrap
result = await call_api("https://api.example.com")
if result.success:
    data = result.unwrap()
    process(data)

# Pattern 2: Error inspection for conditional logic
result = await call_api("https://api.example.com")
if result.failure and "rate_limit" in result.error:
    await asyncio.sleep(60)  # Backoff on rate limit
    retry()
elif result.failure:
    log_error(result.error)

# Pattern 3: Direct unwrap (raises exception on failure)
try:
    data = result.unwrap()
    process(data)
except ApiError as e:
    log_error(e)
```

### Policy Configuration
```python
from resilient_result import Retry, Backoff, Circuit, resilient

# Explicit policy configuration
@resilient(
    retry=Retry(attempts=5, timeout=60),
    backoff=Backoff.exp(delay=0.1, max_delay=10),  # Jitter enabled by default
    circuit=Circuit(failures=3, window=60)  # 1 minute window
)
async def custom_operation():
    return await external_service()

# Shorthand for common patterns
@resilient(retry=Retry(attempts=5))  # Just more attempts
@resilient(timeout=60)               # Just longer timeout
async def database_operation():
    return await db.query()
```

### Parallel Operations
```python
from resilient_result import Result

# Collect multiple async operations
operations = [fetch_user(1), fetch_user(2), fetch_user(3)]
result = await Result.collect(operations)

if result.success:
    users = result.unwrap()  # All succeeded
else:
    try:
        result.unwrap()  # Raises first failure
    except Exception as e:
        print(f"First failure: {e}")
```

### Error Inspection Patterns
```python
# Canonical API: 3 ways to work with Results
result = await call_api("https://api.example.com")

# 1. Status checking
if result.success:
    print("Success!")
if result.failure:
    print("Failed!")

# 2. Error inspection (without exceptions)
if result.failure:
    error_msg = result.error
    if "network" in str(error_msg):
        retry_with_backoff()
    elif "auth" in str(error_msg):
        refresh_token()

# 3. Value extraction (raises on failure)
try:
    data = result.unwrap()  
    process(data)
except Exception as e:
    handle_error(e)
```

## License

MIT - Build amazing resilient systems! 🚀

---

**🗺️ [Roadmap](docs/dev/roadmap.md)**