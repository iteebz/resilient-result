# Changelog

All notable changes to resilient-result will be documented in this file.

## [0.3.0] - 2025-07-27 - Policy Architecture

**Major Enhancement**: Policy-based configuration replaces primitive parameters.

### ✨ New Policy System
- **`Retry` policy**: `Retry.api()`, `Retry.db()`, `Retry.ml()` factory methods
- **`Circuit` policy**: `Circuit.fast()`, `Circuit.standard()` presets
- **`Backoff` policy**: `Backoff.exp()`, `Backoff.linear()`, `Backoff.fixed()` strategies
- **Beautiful API**: `@resilient(retry=Retry.api(), backoff=Backoff.exp())`

### 🔧 API Changes
- **Timeout moved**: Now part of `Retry` policy, not top-level parameter
- **Configurable backoff**: Replaces hardcoded `2**attempt * 0.1` exponential backoff
- **Policy objects**: All configuration via policy objects, not primitives

### 💥 Breaking Changes
- **No backward compatibility**: Clean break from primitive-based API
- **Import changes**: Must import `Retry`, `Circuit`, `Backoff` policies
- **Parameter changes**: `@resilient(retries=3)` → `@resilient(retry=Retry(attempts=3))`

### 📊 Policy Examples
```python
# API calls - moderate retries, reasonable timeout
@resilient(retry=Retry.api())

# Database operations - more retries, longer timeout  
@resilient(retry=Retry.db(), backoff=Backoff.linear())

# Custom fine-grained control
@resilient(
    retry=Retry(attempts=5, timeout=10),
    backoff=Backoff.exp(delay=0.5, factor=1.5),
    circuit=Circuit(failures=3, window=60)
)
```

## [0.2.2] - 2025-07-27 - Enhanced Developer Experience

### Added
- `unwrap()` function for clean Result extraction
- `Result.collect()` method for parallel async operations
- `@resilient.fallback()` pattern for automatic mode switching
- Enhanced `@resilient` syntax with bare decorator support

## [0.2.1] - 2025-07-26 - Boundary Discipline

**Enhancement Release**: Automatic nested Result flattening for clean boundary discipline.

### ✨ New Features
- **Automatic Result flattening**: Nested `Result.ok(Result.ok(data))` → `Result.ok(data)`
- **Clean boundary discipline**: No more manual Result unwrapping in decorated functions
- **Perfect DX**: Zero ceremony - decorators handle all Result complexity

### 🔧 API Enhancements
- **`Result.flatten()` method**: Recursively flattens nested Result objects
- **Auto-flattening in decorators**: All `@resilient` patterns automatically flatten
- **Preserves error propagation**: `Result.ok(Result.fail(error))` → `Result.fail(error)`

### 📊 Real-World Impact
- **Cogency integration**: Eliminates manual Result handling complexity
- **15 new tests**: Comprehensive nested Result flattening coverage
- **Zero breaking changes**: Backward compatible enhancement

### 🎯 Boundary Discipline Pattern
```python
# Before v0.2.1 - manual Result handling
@resilient.preprocess()
async def process(llm, parse_json):
    llm_result = await llm.run("prompt")
    if not llm_result.success:
        return llm_result
    
    parse_result = parse_json(llm_result.data) 
    if not parse_result.success:
        return parse_result
    
    return parse_result.data

# After v0.2.1 - clean boundary discipline  
@resilient.preprocess()
async def process(llm, parse_json):
    llm_response = await llm.run("prompt")     # Auto-unwrapped
    parsed_data = parse_json(llm_response)     # Auto-unwrapped
    return parsed_data                         # Auto-flattened
```

### 🚀 Performance
- **Zero overhead**: Flattening only when needed
- **Recursive safety**: Handles arbitrary nesting depth
- **Memory efficient**: No additional object creation

## [0.2.0] - 2025-07-26 - Foundation Ready

**Major Release**: Complete architecture overhaul from basic Result type to extensible resilience framework.

### 🏗️ Architecture Revolution
- **Extensible registry system**: Domain-specific patterns via `resilient.register()`
- **Beautiful decorator composition**: Stack multiple patterns seamlessly
- **Unified core decorator**: Single `decorator()` function eliminates DRY violations
- **Plugin architecture**: Built-in + custom patterns with consistent API

### ✨ New Features
- **Built-in resilience patterns**:
  - `@resilient.network()` - Smart retry for connection/timeout errors
  - `@resilient.parsing()` - JSON/data parsing with error recovery  
  - `@resilient.circuit()` - Circuit breaker with failure threshold
  - `@resilient.rate_limit()` - Token bucket rate limiting
- **Core decorator enhancements**:
  - `timeout` parameter with asyncio integration
  - `error_type` for custom Result[T, CustomError] types
  - Smart Result detection (passthrough vs auto-wrap)
  - Exponential backoff with jitter
- **New error types**: `NetworkError`, `ParsingError`, `TimeoutError`
- **Sync function support**: Works with both async and sync functions

### 🔧 API Changes
- **Registry API**: `resilient.register(name, factory)` for custom patterns
- **Import shortcuts**: `from resilient_result import network, parsing` 
- **Decorator stacking**: Multiple decorators compose cleanly
- **Handler functions**: Async error handlers for smart retry logic

### 📊 Real-World Validation
- **Cogency integration**: Proven extensibility with AI-specific patterns
- **46 comprehensive tests**: 2.1s runtime, full coverage
- **Production roadmap**: Clear path to v0.3.0 enterprise features

### 🚨 Breaking Changes
- **MAJOR**: Complete rewrite - migration from v0.1.0 requires code changes
- **Architecture**: Moved from simple Result wrapper to full resilience framework
- **Dependencies**: Now requires asyncio (was zero-dependency)

### 📈 Performance
- **Overhead**: ~0.1ms per decorated call
- **Memory**: ~200 bytes per Result object
- **Concurrency**: Thread-safe, async-first design

## [0.1.0] - 2025-07-25 - Genesis

**Initial Release**: Pure Result[T, E] type implementation

### Core Features
- **Result[T, E] type**: Generic Result class with success/error states
- **Rust-style API**: `Ok()`, `Err()`, `.unwrap()`, `.map()`, `.and_then()`  
- **Type safety**: Full generic type support with proper variance
- **Zero dependencies**: Pure Python implementation
- **Method chaining**: Functional composition with `.map()` and `.and_then()`

### API Surface
```python
from resilient_result import Result, Ok, Err

# Creation
result: Result[str, Exception] = Ok("success")
error_result: Result[str, Exception] = Err(Exception("failed"))

# Usage
if result.success:
    print(result.data)
else:
    print(result.error)
```

### Foundation
- **Inheritance-friendly**: Clean subclassing for domain-specific types
- **Performance**: Zero overhead Result wrapper
- **Testing**: Comprehensive test coverage
- **Documentation**: Complete usage examples and API reference

---

[0.2.0]: https://github.com/iteebz/resilient-result/releases/tag/v0.2.0
[0.1.0]: https://github.com/iteebz/resilient-result/releases/tag/v0.1.0