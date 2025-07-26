# Minimal justfile for resilient-result development

# Run tests
test:
    poetry run pytest

# Run tests with coverage
test-cov:
    poetry run pytest --cov=resilient_result --cov-report=term-missing

# Format code with black and ruff
format:
    poetry run black .
    poetry run ruff format .

# Lint and fix with ruff
lint:
    poetry run ruff check .

# Lint and auto-fix with ruff  
lint-fix:
    poetry run ruff check --fix .

# Format + lint (full cleanup)
clean: format lint-fix

# Install dependencies
install:
    poetry install

# Build package
build:
    poetry build

# Run all checks (test + lint)
check: lint test

# Development setup
dev: install format lint-fix test