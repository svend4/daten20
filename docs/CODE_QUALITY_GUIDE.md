# 🔍 Code Quality Guide - Document Management System

## Overview

Comprehensive code quality system with automated checks, formatters, and linters.

**Version:** 1.0.0
**Date:** 2026-01-11
**Tools:** Black, isort, Flake8, MyPy, Bandit, Pytest

---

## 🎯 Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# Run all quality checks
make lint

# Run fast checks (skip slow ones)
make lint-fast

# Auto-fix formatting issues
make lint-fix
```

### Option 2: Using Script Directly

```bash
# Run all checks
./scripts/quality_check.sh

# Fast mode
./scripts/quality_check.sh --fast

# Auto-fix
./scripts/quality_check.sh --fix

# Specific check
./scripts/quality_check.sh --check=flake8
```

### Option 3: Using Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Runs automatically on git commit
git commit -m "Your message"
```

---

## 📊 Quality Checks

### 1. Black - Code Formatting

**Purpose:** Ensures consistent code formatting

**Command:**
```bash
# Check
black src/ tests/ --check --line-length 120

# Fix
black src/ tests/ --line-length 120

# Makefile
make black
make black-fix
```

**Configuration:** `pyproject.toml`

**Rules:**
- Line length: 120 characters
- Target Python: 3.9, 3.10, 3.11
- Excludes: data/, backups/, logs/, .venv/

**Example:**
```python
# Before black
def my_function(x,y,z):
    return x+y+z

# After black
def my_function(x, y, z):
    return x + y + z
```

---

### 2. isort - Import Sorting

**Purpose:** Organizes import statements

**Command:**
```bash
# Check
isort src/ tests/ --check-only --profile black

# Fix
isort src/ tests/ --profile black

# Makefile
make isort
make isort-fix
```

**Configuration:** `pyproject.toml`

**Rules:**
- Profile: black (compatible with black formatter)
- Line length: 120
- Multi-line mode: 3 (vertical hanging indent)

**Example:**
```python
# Before isort
from pathlib import Path
import os
from typing import Dict
import sys

# After isort
import os
import sys
from pathlib import Path
from typing import Dict
```

---

### 3. Flake8 - Style Guide Enforcement

**Purpose:** Enforces PEP 8 and catches common errors

**Command:**
```bash
# Check
flake8 src/ tests/ --config=.flake8

# Makefile
make flake8
```

**Configuration:** `.flake8`

**Rules:**
- Max line length: 120
- Max complexity: 15
- Ignores: E203, E501, W503 (black compatible)

**Common Errors:**
- E501: Line too long
- F401: Imported but unused
- E302: Expected 2 blank lines
- W291: Trailing whitespace

**Example:**
```python
# ✗ Flake8 error (E501)
def very_long_function_name_that_exceeds_the_maximum_line_length_limit_and_should_be_split_into_multiple_lines():
    pass

# ✓ Fixed
def very_long_function_name_that_should_be_split(
    param1, param2, param3
):
    pass
```

---

### 4. MyPy - Static Type Checking

**Purpose:** Catches type errors before runtime

**Command:**
```bash
# Check
mypy src/ --config-file=mypy.ini --show-error-codes

# Makefile
make mypy
```

**Configuration:** `mypy.ini`, `pyproject.toml`

**Rules:**
- Python version: 3.9
- Check untyped definitions
- Warn on unused configs
- No implicit optional

**Example:**
```python
# ✗ MyPy error
def add(a, b):  # Missing type annotations
    return a + b

# ✓ Fixed
def add(a: int, b: int) -> int:
    return a + b

# ✗ Type mismatch
result: int = "hello"  # error: Incompatible types

# ✓ Fixed
result: str = "hello"
```

---

### 5. Bandit - Security Linting

**Purpose:** Finds common security issues

**Command:**
```bash
# Check
bandit -c .bandit -r src/ -q

# Makefile
make bandit
```

**Configuration:** `.bandit`

**Checks:**
- SQL injection
- Shell injection
- Hardcoded passwords
- Insecure random
- Assert usage in production

**Example:**
```python
# ✗ Bandit warning (B608)
import subprocess
subprocess.call(shell=True)  # Shell injection risk

# ✓ Fixed
import subprocess
subprocess.call(['ls', '-la'])  # No shell=True

# ✗ Hardcoded password (B105)
PASSWORD = "secret123"

# ✓ Use environment variables
PASSWORD = os.getenv("DB_PASSWORD")
```

---

### 6. Pytest - Testing

**Purpose:** Run automated tests

**Command:**
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Makefile
make test
make test-coverage
```

**Configuration:** `pyproject.toml`

**Markers:**
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

---

## 🛠️ Configuration Files

### pyproject.toml

Main configuration for Black, isort, pytest, coverage, and MyPy:

```toml
[tool.black]
line-length = 120
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--cov=src"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
```

### .flake8

Flake8 configuration:

```ini
[flake8]
max-line-length = 120
max-complexity = 15
extend-ignore = E203,E501,W503
exclude = .git,__pycache__,.venv,venv
```

### .pre-commit-config.yaml

Pre-commit hooks configuration with 12+ checks:
- Black, isort, Flake8, MyPy, Bandit
- Trailing whitespace, end-of-file fixer
- YAML/JSON syntax checks
- Large file detection
- Security checks

---

## 📋 Makefile Commands

### Development

```bash
make install          # Install dependencies
make install-dev      # Install dev dependencies
make format           # Auto-format code
make lint             # Run all checks
make lint-fast        # Fast checks
make lint-fix         # Auto-fix issues
```

### Testing

```bash
make test             # Run all tests
make test-fast        # Fast tests
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-coverage    # With coverage report
```

### Code Quality

```bash
make black            # Check formatting
make black-fix        # Fix formatting
make isort            # Check imports
make isort-fix        # Fix imports
make flake8           # Style check
make mypy             # Type check
make bandit           # Security check
make pre-commit       # Run all pre-commit hooks
```

### Cleaning

```bash
make clean            # Clean generated files
make clean-logs       # Clean log files
make clean-all        # Clean everything
```

### Running

```bash
make run-dashboard    # Run dashboard
make run-api          # Run API server
```

### Utilities

```bash
make help             # Show help
make version          # Show version
make info             # Project info
make check-tools      # Check installed tools
```

---

## 🚀 Usage Workflows

### Workflow 1: Before Committing

```bash
# 1. Format code
make format

# 2. Run fast checks
make lint-fast

# 3. Run tests
make test-fast

# 4. Commit
git add .
git commit -m "Your message"
# Pre-commit hooks run automatically
```

### Workflow 2: Full Quality Check

```bash
# Run everything
make lint
make test-coverage

# Or use script
./scripts/quality_check.sh
pytest tests/ --cov=src --cov-report=html
```

### Workflow 3: Fixing Issues

```bash
# Auto-fix formatting
make lint-fix

# Or manually
make black-fix
make isort-fix

# Then check remaining issues
make lint
```

### Workflow 4: CI/CD Pipeline

```bash
# Simulate CI/CD locally
make ci-full

# Fast CI check
make ci-test
```

---

## 🔧 Troubleshooting

### Issue: "black not found"

**Solution:**
```bash
pip install black isort flake8 mypy bandit pytest pytest-cov
# Or
make install-dev
```

### Issue: "Too many flake8 errors"

**Solution:**
```bash
# Auto-fix formatting first
make format

# Then check remaining
make flake8
```

### Issue: "MyPy type errors"

**Solution:**
```python
# Add type annotations
def func(x: int, y: str) -> bool:
    return True

# Or use type: ignore for third-party code
import some_untyped_lib  # type: ignore
```

### Issue: "Pre-commit hooks failing"

**Solution:**
```bash
# Run manually to see errors
pre-commit run --all-files

# Auto-fix
make lint-fix

# Bypass (NOT recommended)
git commit --no-verify
```

---

## ✅ Quality Standards

### Code Must Pass:

1. ✅ **Black** - Formatted correctly
2. ✅ **isort** - Imports organized
3. ✅ **Flake8** - Style guide compliant
4. ⚠️ **MyPy** - Type safe (warnings acceptable)
5. ⚠️ **Bandit** - No critical security issues
6. ✅ **Pytest** - All tests passing
7. ⚠️ **Coverage** - >70% (target: 80%)

### Legend:
- ✅ = Blocking (must pass)
- ⚠️ = Non-blocking (warnings ok)

---

## 📊 Quality Metrics

### Current Status:

```bash
# Check metrics
make info

# Output:
# Files:   213 Python files
# Tests:   172 test files
# Lines:   131,000+ lines of code
# Coverage: 70%+ (target: 80%)
```

### Quality Goals:

- **Code Coverage:** 80%+
- **Complexity:** < 15 (per function)
- **Line Length:** ≤ 120 characters
- **Test Pass Rate:** 100%
- **Security Issues:** 0 critical

---

## 🎓 Best Practices

### 1. Run Checks Frequently

```bash
# Before committing
make lint-fast

# Before pushing
make lint
make test
```

### 2. Use Auto-Formatters

```bash
# Save time - let tools fix formatting
make format
```

### 3. Write Type Annotations

```python
# Good
def process(doc: str, max_len: int = 100) -> Dict[str, Any]:
    ...

# Bad (no types)
def process(doc, max_len=100):
    ...
```

### 4. Keep Functions Simple

```python
# Good (low complexity)
def validate_email(email: str) -> bool:
    return '@' in email and '.' in email

# Bad (high complexity - multiple nested ifs)
def complex_function(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                ...
```

### 5. Write Tests

```python
# Every function should have tests
def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid") == False
```

---

## 🔗 Integration with IDEs

### VS Code

`.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "120"],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

Settings → Tools → External Tools:
- Add Black, isort, Flake8 as external tools
- Configure File Watchers for auto-formatting

---

## 📚 Resources

### Documentation

- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [Flake8](https://flake8.pycqa.org/)
- [MyPy](https://mypy.readthedocs.io/)
- [Bandit](https://bandit.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)

### Internal Docs

- Progress Bars: `docs/PROGRESS_BARS_GUIDE.md`
- Testing: `docs/TESTING_INFRASTRUCTURE_COMPLETE.md`
- Deployment: `docs/DEPLOYMENT_GUIDE_V4.0.md`

---

## ✅ Checklist

Before pushing code:

- [ ] Run `make format` (auto-format)
- [ ] Run `make lint-fast` (quick checks)
- [ ] Run `make test-fast` (quick tests)
- [ ] All checks pass ✓
- [ ] Tests pass ✓
- [ ] Commit with descriptive message
- [ ] Push to feature branch
- [ ] Create PR

---

**Author:** Document Management System
**Date:** 2026-01-11
**Version:** 1.0.0
