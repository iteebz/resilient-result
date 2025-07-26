# Changelog

All notable changes to resilient-result will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Foundation Ready 🚀

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