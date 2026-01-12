# 🚀 CI/CD Guide
## Continuous Integration and Deployment for Daten20

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Workflows](#workflows)
3. [Branch Strategy](#branch-strategy)
4. [Pull Request Process](#pull-request-process)
5. [Release Process](#release-process)
6. [Status Badges](#status-badges)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The daten20 project uses GitHub Actions for comprehensive CI/CD automation. The pipeline includes:

- ✅ **Automated Testing** - Unit, integration, and E2E tests
- ✅ **Code Quality** - Linting, formatting, type checking
- ✅ **Security Scanning** - Dependency checks, code analysis, secret detection
- ✅ **Performance Testing** - Benchmarking and load testing
- ✅ **Automated Releases** - Version management and publishing
- ✅ **Documentation** - Auto-generated docs and reports

---

## 🔧 Workflows

### 1. Main CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Scheduled nightly builds (2 AM UTC)

**Jobs:**
- **test** - Run test suite on Python 3.9, 3.10, 3.11
- **lint** - Code quality checks (Black, isort, flake8, mypy, bandit, safety)
- **build** - Build Python package
- **docker** - Build Docker image (main branch only)
- **docs** - Build documentation

**Example Run:**
```bash
# Trigger on push
git push origin develop

# View results
https://github.com/svend4/daten20/actions/workflows/ci.yml
```

### 2. PR Validation (`pr-validation.yml`)

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**
- **quick-checks** - Fast validation (format, lint, PR title)
- **test-changed-files** - Test only changed modules
- **compatibility-check** - Test on Python 3.9 and 3.11
- **size-check** - Validate PR size
- **documentation-check** - Check for doc updates
- **completion-test** - Validate CLI auto-completion
- **pr-summary** - Generate validation summary

**PR Title Format:**
```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

Examples:
feat: add document encryption
fix: correct PDF parsing bug
docs: update API documentation
test: add unit tests for anonymizer
```

### 3. Security Scans (`security.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`
- Scheduled weekly scans (Monday 9 AM UTC)

**Jobs:**
- **dependency-scan** - Check dependencies (safety, pip-audit)
- **code-scan** - Analyze code (bandit, semgrep)
- **secret-scan** - Detect secrets (gitleaks)
- **license-scan** - Check license compliance

**View Reports:**
```bash
# Download artifacts from GitHub Actions
# Navigate to: Actions → Security Scans → Latest Run → Artifacts
```

### 4. Performance Tests (`performance.yml`)

**Triggers:**
- Push to `main`
- Pull requests to `main`
- Scheduled nightly tests (3 AM UTC)

**Jobs:**
- **benchmark** - Performance benchmarking with pytest-benchmark
- **load-test** - Load testing with Locust
- **memory-profile** - Memory profiling

**Run Locally:**
```bash
# Benchmark tests
pytest tests/performance/ --benchmark-only

# Memory profiling
pytest tests/performance/ -m memory --memprof
```

### 5. Release (`release.yml`)

**Triggers:**
- Push tags matching `v*.*.*` (e.g., v1.2.3)
- Manual workflow dispatch

**Jobs:**
- **validate-release** - Validate version format and changelog
- **build** - Build release packages
- **test-release** - Test installation
- **create-github-release** - Create GitHub release
- **publish-pypi** - Publish to PyPI (if configured)
- **build-docker-release** - Build and push Docker images
- **notify** - Send notifications

**Create Release:**
```bash
# 1. Update version in setup.py or pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add setup.py CHANGELOG.md
git commit -m "chore: prepare release v1.2.3"

# 4. Create and push tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# 5. Monitor release workflow
https://github.com/svend4/daten20/actions/workflows/release.yml
```

---

## 🌿 Branch Strategy

### Branch Types

```
main (protected)
  ↑
develop (integration)
  ↑
feature/* (new features)
fix/* (bug fixes)
claude/* (AI assistant branches)
```

### Branch Rules

**main branch:**
- Protected branch
- Requires PR approval
- All checks must pass
- No direct pushes

**develop branch:**
- Integration branch
- Regular merges from feature branches
- Tested before merging to main

**feature/fix branches:**
- Short-lived branches
- One feature/fix per branch
- Delete after merging

**claude/* branches:**
- AI-assisted development
- Follow same PR process
- Named: `claude/feature-description-XXXXX`

---

## 📝 Pull Request Process

### 1. Create Branch

```bash
# From develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feat/add-document-encryption

# Make changes, commit
git add .
git commit -m "feat: add document encryption support"

# Push branch
git push -u origin feat/add-document-encryption
```

### 2. Open Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select base: `develop`, compare: `feat/add-document-encryption`
4. Fill PR template:

```markdown
## Description
Adds AES-256 encryption support for sensitive documents.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Unit tests added
- [x] Integration tests added
- [x] Manual testing completed

## Checklist
- [x] Code follows style guidelines
- [x] Self-reviewed code
- [x] Commented complex code
- [x] Updated documentation
- [x] No new warnings
- [x] Tests pass locally
```

### 3. Automated Checks

The PR will trigger:
- PR Validation workflow (fast checks)
- Main CI workflow (full test suite)

**Expected checks:**
- ✅ PR title format
- ✅ Code formatting (Black)
- ✅ Import sorting (isort)
- ✅ Linting (flake8)
- ✅ Tests pass
- ✅ Coverage maintained
- ✅ Security scans pass

### 4. Address Feedback

```bash
# Make requested changes
git add .
git commit -m "fix: address review comments"
git push

# Checks run automatically on push
```

### 5. Merge

Once approved:
- **Squash and merge** for feature branches
- **Merge commit** for release branches
- Delete branch after merging

---

## 🎉 Release Process

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backwards compatible)
PATCH: Bug fixes (backwards compatible)
```

### Release Steps

#### 1. Prepare Release

```bash
# Checkout develop
git checkout develop
git pull origin develop

# Update version
# Edit setup.py, pyproject.toml, or __version__ file

# Update CHANGELOG.md
cat >> CHANGELOG.md <<EOF
## [1.2.3] - 2026-01-12

### Added
- Document encryption support
- CLI auto-completion for all tools

### Fixed
- PDF parsing memory leak
- NER entity detection accuracy

### Changed
- Updated dependencies to latest versions
EOF

# Commit changes
git add .
git commit -m "chore: prepare release v1.2.3"
git push origin develop
```

#### 2. Merge to Main

```bash
# Create PR from develop to main
# Wait for all checks to pass
# Get approval and merge
```

#### 3. Create Release Tag

```bash
# Checkout main
git checkout main
git pull origin main

# Create annotated tag
git tag -a v1.2.3 -m "Release v1.2.3

- Document encryption support
- CLI auto-completion
- Bug fixes and improvements"

# Push tag
git push origin v1.2.3
```

#### 4. Monitor Release Workflow

1. Go to Actions → Release workflow
2. Monitor jobs: build, test, publish
3. Verify release on GitHub Releases page
4. Verify package on PyPI (if published)
5. Verify Docker images (if published)

#### 5. Post-Release

```bash
# Merge main back to develop
git checkout develop
git merge main
git push origin develop

# Announce release
# Update documentation
# Notify users
```

---

## 📊 Status Badges

Add these badges to README.md:

```markdown
## Status

![CI](https://github.com/svend4/daten20/actions/workflows/ci.yml/badge.svg)
![Security](https://github.com/svend4/daten20/actions/workflows/security.yml/badge.svg)
![Performance](https://github.com/svend4/daten20/actions/workflows/performance.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)
![Coverage](https://codecov.io/gh/svend4/daten20/branch/main/graph/badge.svg)
```

---

## 🐛 Troubleshooting

### Tests Failing Locally But Passing in CI

```bash
# Ensure you have all dependencies
pip install -r requirements.txt
pip install -e ".[dev,test]"

# Clear cache
pytest --cache-clear

# Run with same settings as CI
pytest tests/ -v --cov=src --cov-report=xml
```

### Lint Errors

```bash
# Auto-fix formatting
black src/ tests/
isort src/ tests/

# Check remaining issues
flake8 src/ tests/
mypy src/
```

### Coverage Dropped

```bash
# Run coverage report
pytest --cov=src --cov-report=html

# Open htmlcov/index.html
# Identify uncovered lines
# Add tests
```

### Docker Build Fails

```bash
# Test build locally
docker build -t daten20:test .

# Check logs
docker build -t daten20:test . --progress=plain
```

### Security Scan Failures

```bash
# Check dependencies
safety check

# Scan code
bandit -r src/

# Update vulnerable dependencies
pip install --upgrade <package>
```

### Release Failed

**Check:**
1. Version format (v1.2.3)
2. CHANGELOG.md updated
3. All CI checks passed
4. PyPI credentials configured (if publishing)
5. Docker credentials configured (if publishing)

```bash
# Manually trigger release
gh workflow run release.yml -f version=1.2.3
```

---

## 🔧 Local Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/svend4/daten20.git
cd daten20

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

### Daily Workflow

```bash
# Update from remote
git pull origin develop

# Create feature branch
git checkout -b feat/my-feature

# Make changes
# ...

# Run tests
pytest tests/

# Check formatting
black --check src/ tests/
isort --check src/ tests/

# Fix formatting
black src/ tests/
isort src/ tests/

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add my feature"

# Push and create PR
git push -u origin feat/my-feature
```

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Formatting](https://black.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)

---

## 🎯 Summary

### CI/CD Features

✅ **Automated Testing** - 94 tests, 91.5% passing
✅ **Code Quality** - Black, isort, flake8, mypy, pylint
✅ **Security** - Safety, bandit, semgrep, gitleaks
✅ **Performance** - Benchmarking, load testing, profiling
✅ **Releases** - Automated versioning, PyPI, Docker
✅ **Documentation** - Auto-generated, always up-to-date
✅ **PR Validation** - Fast feedback on pull requests
✅ **Multi-Python** - Tested on 3.9, 3.10, 3.11
✅ **Nightly Builds** - Catch issues early
✅ **Scheduled Scans** - Regular security audits

### Workflow Summary

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| CI | Push, PR, Schedule | Main testing & building | ~5-10 min |
| PR Validation | PR opened/updated | Fast PR checks | ~2-3 min |
| Security | Push, PR, Schedule | Security scanning | ~3-5 min |
| Performance | Push to main, Schedule | Performance testing | ~5-10 min |
| Release | Tag push | Automated releases | ~10-15 min |

---

**Version:** 1.0
**Date:** 2026-01-12
**Status:** ✅ Production-Ready
**Task:** Task 27 - GitHub Actions CI/CD Setup
