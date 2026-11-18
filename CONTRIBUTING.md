# Contributing

Thank you for considering contributing to PyHJ212!

## Development Setup

See [DEVELOPMENT.md](DEVELOPMENT.md) for environment setup instructions using `uv`.

## Code Standards

- Follow PEP 8 with 100-character line limit
- Complete type annotations on all public APIs
- Google-style docstrings
- Run `ruff check`, `ruff format`, and `mypy` before submitting

## Testing

- Write tests before or alongside implementation
- Use Hypothesis for property-based testing
- Include both valid and invalid input tests
- Test TCP stream fragmentation and concatenation

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests and implementation
4. Ensure all checks pass: `uv run ruff check`, `uv run ruff format --check`, `uv run mypy`, `uv run pytest`
5. Update documentation as needed
6. Submit a pull request with a clear description

## Commit Messages

Follow conventional commit format:

```
type(scope): subject

Body explaining why.
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
