# Resilience Decorators

## Core Decorators

```python
@retry()                    # 2 attempts, 1s fixed backoff
@retry(attempts=5)          # Custom attempts
@timeout()                  # 30 second timeout
@timeout(seconds=10)        # Custom timeout  
@circuit()                  # 3 failures, 60s window
@circuit(failures=5)        # Custom threshold
@rate_limit()               # 100 rps rate limiting
@rate_limit(rps=500)        # Custom rate
```

## Composition

**Order matters - decorators execute right-to-left:**

```python
@rate_limit()    # 4. Controls call frequency  
@circuit()       # 3. Stops calling if broken
@timeout()       # 2. Kills slow calls
@retry()         # 1. Retries failures
async def api_call():
    return await http.get(url)
```

**Execution flow:**
1. Retry wrapper attempts the call
2. Timeout wrapper kills if > 30s  
3. Circuit wrapper blocks if service is broken
4. Rate limit wrapper controls frequency

## Policies

```python
from resilient_result import Retry, Backoff

# Jitter enabled by default to prevent thundering herd
@retry(attempts=5, backoff=Backoff.linear(delay=1.0))
@retry(attempts=3, backoff=Backoff.exp(delay=0.1))
@retry(attempts=3, backoff=Backoff.fixed(delay=1.0))

# Disable jitter for deterministic timing (testing)
@retry(backoff=Backoff.exp(delay=1.0, jitter=False))
```

## Presets

```python
from resilient_result import resilient

@resilient.api()       # timeout(30) + retry(3)
@resilient.db()        # timeout(60) + retry(5) 
@resilient.protected() # circuit + retry
```

## Manual Composition

```python
from resilient_result import compose

@compose(
    circuit(failures=3),
    timeout(10.0),
    retry(attempts=3)
)
async def robust_operation():
    return await external_service()
```

## Error Handlers

```python
async def smart_handler(error):
    if "rate_limit" in str(error):
        await asyncio.sleep(60)
        return None  # Continue retrying
    return False     # Stop retrying

@retry(attempts=5, handler=smart_handler)
async def api_with_backoff():
    return await rate_limited_api()
```

## Parallel Operations

```python
from resilient_result import Result

operations = [fetch_user(1), fetch_user(2), fetch_user(3)]
result = await Result.collect(operations)
```