# Development Guide

## Prerequisites

Install [uv](https://docs.astral.sh/uv/):

```bash
# macOS (Homebrew)
brew install uv

# Or use the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

```bash
# Create virtual environment and install dev dependencies
uv sync --all-extras

# Or install into a specific Python version
uv sync --all-extras --python 3.12
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pyhj212 --cov-report=term-missing

# Run property-based tests only
uv run pytest tests/property/

# Run a single test
uv run pytest tests/unit/test_parser.py -k test_name
```

## Linting and Formatting

```bash
# Run Ruff linter
uv run ruff check src/pyhj212 tests

# Run Ruff formatter
uv run ruff format src/pyhj212 tests

# Run mypy type checking
uv run mypy src/pyhj212
```

## Quick Check

Run all quality checks in one command:

```bash
uv run ruff check src/pyhj212 tests && \
uv run ruff format --check src/pyhj212 tests && \
uv run mypy src/pyhj212 && \
uv run pytest
```

## Project Structure

See the directory layout for module organization. Key design principles:

- Protocol logic is independent of network transport
- Data models use dataclasses with complete type annotations
- CRC implementation verified against official test vectors
- No runtime third-party dependencies
