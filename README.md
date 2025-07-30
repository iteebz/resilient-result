# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Pure resilience mechanisms with beautiful Result types.**

```python
from resilient_result import retry, timeout, Result

@retry(attempts=3)
@timeout(10.0)
async def call_api(url: str) -> str:
    return await http.get(url)

result: Result[str, Exception] = await call_api("https://api.example.com")
if result.success:
    print(result.data)  # Clean success
else:
    print(f"Failed: {result.error}")  # No exceptions thrown
```

**Why resilient-result?** Pure mechanisms over domain patterns, Result types over exceptions, orthogonal composition.

**📖 [Full API Reference](docs/api.md)**

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

### Result Types Over Exceptions
```python
from resilient_result import Result, Ok, Err

# Clean error handling - no try/catch needed
result = await call_api("https://api.example.com")
if result.success:
    process(result.data)
else:
    log_error(result.error)
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
    users = result.data  # All succeeded
else:
    print(f"First failure: {result.error}")
```

### Custom Error Handling
```python
async def smart_handler(error):
    if "rate_limit" in str(error):
        await asyncio.sleep(60)
        return None  # Continue retrying
    return False     # Stop retrying

@retry(attempts=5, handler=smart_handler)
async def api_with_intelligent_backoff():
    return await rate_limited_api()
```

## License

MIT - Build amazing resilient systems! 🚀