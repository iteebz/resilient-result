# resilient-result

[![PyPI version](https://badge.fury.io/py/resilient-result.svg)](https://badge.fury.io/py/resilient-result)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)

**Policy-based resilience with beautiful Result types.**

```python
from resilient_result import resilient, Retry, Backoff

@resilient(retry=Retry.api(), backoff=Backoff.exp())
async def call_api(url: str) -> str:
    return await http.get(url)

result = await call_api("https://api.example.com")
if result.success:
    print(result.data)  # Clean success
else:
    print(f"Failed: {result.error}")  # No exceptions thrown
```

**Why resilient-result?** Policy objects over primitives, Result types over exceptions, zero ceremony.

**📖 [Full API Reference](docs/api.md)**

## Installation

```bash
pip install resilient-result
```

## Core Features

### Policy-Based Configuration
```python
from resilient_result import resilient, Retry, Circuit, Backoff

# Beautiful presets
@resilient(retry=Retry.api())                    # API defaults  
@resilient(retry=Retry.db(), backoff=Backoff.linear())  # Database operations

# Custom configuration
@resilient(retry=Retry(attempts=5, timeout=10), circuit=Circuit.fast())
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

### Built-in Patterns
```python
@resilient.network()         # Smart retry for network errors
@resilient.parsing()         # JSON parsing with recovery  
@resilient.circuit()         # Circuit breaker protection
@resilient.rate_limit()      # Token bucket rate limiting
```

## License

MIT - Build amazing resilient systems! 🚀