# Changelog

All notable changes to resilient-result will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2025-08-13

### Changed
- **BREAKING**: Deleted all preset methods for constitutional compliance
- **BREAKING**: Removed `Retry.api()`, `Retry.db()`, `Retry.ml()` - use `Retry(attempts=N)` 
- **BREAKING**: Removed `Circuit.fast()`, `Circuit.standard()` - use `Circuit(failures=N)`
- **BREAKING**: Removed `Timeout.api()`, `Timeout.db()`, `Timeout.ml()` - use `Timeout(seconds=N)`
- **BREAKING**: Removed `compose()` function - use decorator stacking
- **BREAKING**: Changed defaults to universal reasonable values:
  - Retry: 2 attempts (was 3), 1s fixed backoff (was exponential) 
  - Circuit: 3 failures (was 5), 60s window (was 300s)
  - Timeout: 30s universal default
  - Rate limit: 100 rps (was 10 rps) - more realistic for modern APIs

### Added
- **Single source of truth**: All defaults imported from `defaults.py` module
- **Progressive disclosure**: `@resilient()` for simple cases, individual decorators for power users
- **Simplified API**: Removed choice paralysis - one obvious way for each use case
- **Retry logging**: DEBUG level logging shows retry attempts and backoff delays, INFO level logs successful recovery
- **Constitutional compliance**: Eliminated API multiplication, verbose naming, and dual defaults
- **Jitter support**: Backoff strategies include jitter by default to prevent thundering herd problems

## [0.4.0] - 2025-08-13

### Changed
- **BREAKING**: Simplified Result API to 3 canonical methods following "one clear way" principle
- **BREAKING**: Removed `.is_ok()` and `.is_err()` methods (use `.success`/`.failure` properties) 
- **BREAKING**: Removed `.unwrap_err()` method (`.unwrap()` raises exceptions on failure)
- **BREAKING**: Removed standalone `unwrap()` function (use `result.unwrap()` method)
- **BREAKING**: Removed `.data` property (use `result.unwrap()` for value extraction)
- **BREAKING**: Retained `.error` property for error inspection (common use case)
- **3 canonical ways**: `.success`/`.failure` for status, `.error` for inspection, `.unwrap()` for extraction

## [0.3.1] - 2024-07-30

### Changed
- Pure mechanism architecture: removed domain-specific patterns
- Independent `@timeout(seconds)` decorator (no longer tied to retry)
- Consolidated error types: `CircuitError`, `RateLimitError`, `RetryError`
- Uses Python's built-in `TimeoutError` for timeout operations

### Added
- Orthogonal decorator composition: `@retry` + `@timeout` + `@circuit` + `@rate_limit`
- `compose()` function for explicit decorator composition
- `Resilient` class with pre-built patterns (`.api()`, `.db()`, `.protected()`)
- Result flattening for clean boundary discipline
- `Result.collect()` for parallel async operations

### Removed
- **BREAKING**: Domain patterns (`.network()`, `.parsing()`) - use pure mechanisms instead
- Registry system - replaced with simple decorator composition

### Fixed
- 16% test reduction (98→82 tests) eliminating redundancy
- Consolidated test files for better maintainability

## [0.2.2] - 2024-07-27

### Added
- `unwrap()` standalone function for Result extraction
- `Result.collect()` method for parallel async operations  
- Enhanced `@resilient` syntax with bare decorator support

## [0.2.1] - 2024-07-26

### Added
- Automatic nested Result flattening (`Result.flatten()` method)
- Auto-flattening in all resilient decorators
- 15 new tests for comprehensive flattening coverage

### Fixed
- Clean boundary discipline - no more manual Result unwrapping needed
- Preserves error propagation through nested Results

## [0.2.0] - 2024-07-26

### Added
- Extensible registry system for domain-specific patterns
- Built-in resilience patterns: `@resilient.network()`, `@resilient.parsing()`, `@resilient.circuit()`, `@resilient.rate_limit()`
- Unified core decorator with consistent API
- Policy objects: `Retry`, `Circuit`, `Backoff`, `Timeout`
- Timeout support with asyncio integration
- Custom error types support
- Sync and async function support
- Smart Result detection and auto-wrapping

### Changed
- **BREAKING**: Complete architecture overhaul from simple Result type to resilience framework
- **BREAKING**: Now requires asyncio (was zero-dependency)

### Fixed
- Eliminated DRY violations with unified decorator core
- Thread-safe, async-first design

## [0.1.0] - 2024-07-25

### Added
- Initial `Result[T, E]` type implementation
- Rust-style API: `Ok()`, `Err()`, `.unwrap()`, `.map()`, `.and_then()`
- Generic type support with proper variance
- Method chaining for functional composition
- Zero dependencies - pure Python implementation
- Comprehensive test coverage

[0.4.0]: https://github.com/iteebz/resilient-result/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/iteebz/resilient-result/compare/v0.2.2...v0.3.1
[0.2.2]: https://github.com/iteebz/resilient-result/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/iteebz/resilient-result/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/iteebz/resilient-result/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/iteebz/resilient-result/releases/tag/v0.1.0