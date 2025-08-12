# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Resilience mechanisms with Result types.**

```python
from resilient_result import retry, timeout, Result

@retry(attempts=3)
@timeout(10.0)
async def call_api(url: str) -> str:
    return await http.get(url)

result: Result[str, Exception] = await call_api("https://api.example.com")
if result.success:
    data = result.unwrap()  # Extract data safely
    print(data)
else:
    print(f"Failed: {result.error}")  # Inspect error directly
```

**Why resilient-result?** Pure mechanisms over domain patterns, Result types over exceptions, orthogonal composition.

**📖 [Result API](docs/result.md) | 🔧 [Resilience Patterns](docs/resilient.md)**

## Installation

```bash
pip install resilient-result
```

## Core Features

### Pure Mechanism Composition
```python
from resilient_result import retry, timeout, circuit, rate_limit

# Orthogonal composition - each decorator handles one concern
@retry(attempts=3)           # Retry mechanism
@timeout(10.0)               # Time-based protection  
@circuit(failures=5)         # Circuit breaker protection
@rate_limit(rps=100)         # Rate limiting mechanism
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

### Advanced Composition
```python
from resilient_result import compose, resilient

# Manual composition - right to left
@compose(
    circuit(failures=3),
    timeout(10.0), 
    retry(attempts=3)
)
async def robust_operation():
    return await external_service()

# Pre-built patterns
@resilient.api()       # timeout(30) + retry(3)
@resilient.db()        # timeout(60) + retry(5)
@resilient.protected() # circuit + retry
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