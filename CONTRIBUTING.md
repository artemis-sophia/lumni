# Contributing to Lumni

Thank you for your interest in contributing to Lumni! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- Git

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone git@github.com:YOUR_USERNAME/lumni.git
   cd lumni
   ```

3. **Install dependencies**:
   ```bash
   poetry install --with dev
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   poetry run pre-commit install
   ```

5. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch** from `main` (or `master`)
2. **Make your changes** following the coding standards below
3. **Write or update tests** for your changes
4. **Run tests locally**:
   ```bash
   poetry run pytest
   ```
5. **Run linting**:
   ```bash
   poetry run ruff check app/ tests/
   poetry run black --check app/ tests/
   ```
6. **Run type checking**:
   ```bash
   poetry run mypy app/
   ```

### Coding Standards

- **Style**: Follow PEP 8 guidelines
- **Formatting**: Use Black (line length: 100)
- **Linting**: Use Ruff for linting
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings for public functions and classes
- **Tests**: Aim for >80% code coverage

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add rate limiting middleware

fix(cli): resolve provider list display issue

docs(readme): update installation instructions
```

### Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Add tests** for new features or bug fixes
3. **Ensure all tests pass** and CI checks are green
4. **Update CHANGELOG.md** with your changes (if applicable)
5. **Create a pull request** with a clear description:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Any breaking changes

### Pull Request Template

When creating a PR, please fill out the template completely:
- Description of changes
- Type of change
- Related issues
- Testing performed
- Checklist items

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api/test_chat_endpoint.py

# Run with verbose output
poetry run pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the `app/` directory structure
- Use descriptive test names: `test_function_name_scenario`
- Use fixtures from `conftest.py` when possible
- Mock external API calls

## Documentation

- Update `README.md` for user-facing changes
- Update `ARCHITECTURE.md` for architectural changes
- Add docstrings to new functions and classes
- Update `CHANGELOG.md` for notable changes

## Questions?

- Open an issue for bug reports or feature requests
- Check existing issues and PRs before creating new ones
- Be respectful and constructive in all communications

## Recognition

Contributors will be recognized in:
- Release notes
- CONTRIBUTORS.md (if created)
- Project documentation

Thank you for contributing to Lumni!

