# Makefile for Document Management System
# ==========================================
# Convenient commands for development, testing, and deployment
#
# Usage:
#   make help          - Show this help message
#   make install       - Install dependencies
#   make test          - Run tests
#   make lint          - Run all code quality checks
#   make format        - Auto-format code
#   make clean         - Clean generated files
#
# Author: Document Management System
# Version: 1.0.0
# Date: 2026-01-11

.PHONY: help install test lint format clean run docs deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

##@ General

help: ## Show this help message
	@echo "$(BLUE)Document Management System - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt || true
	python -m spacy download en_core_web_sm || true
	python -m spacy download ru_core_news_sm || true
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	pip install black isort flake8 mypy bandit pytest pytest-cov pre-commit
	pre-commit install
	@echo "$(GREEN)✓ Dev dependencies installed$(NC)"

format: ## Auto-format code (black, isort)
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/ tests/ *.py --line-length 120
	isort src/ tests/ --profile black --line-length 120
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run all code quality checks
	@echo "$(BLUE)Running quality checks...$(NC)"
	./scripts/quality_check.sh

lint-fast: ## Run fast quality checks (skip slow ones)
	@echo "$(BLUE)Running fast quality checks...$(NC)"
	./scripts/quality_check.sh --fast

lint-fix: ## Run quality checks and auto-fix issues
	@echo "$(BLUE)Running quality checks with auto-fix...$(NC)"
	./scripts/quality_check.sh --fix

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v --tb=short

test-fast: ## Run fast tests (skip slow ones)
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest tests/ -v -m "not slow" --tb=short

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/ -v -m unit --tb=short

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/ -v -m integration --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch tests/ -v

##@ Code Quality

black: ## Run black formatter check
	black src/ tests/ --check --line-length 120

black-fix: ## Run black formatter with auto-fix
	black src/ tests/ --line-length 120

isort: ## Run isort check
	isort src/ tests/ --check-only --profile black --line-length 120

isort-fix: ## Run isort with auto-fix
	isort src/ tests/ --profile black --line-length 120

flake8: ## Run flake8 linter
	flake8 src/ tests/ --config=.flake8

mypy: ## Run mypy type checker
	mypy src/ --config-file=mypy.ini --show-error-codes

bandit: ## Run bandit security linter
	bandit -c .bandit -r src/ -q

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

##@ Cleaning

clean: ## Clean generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-logs: ## Clean log files
	@echo "$(BLUE)Cleaning log files...$(NC)"
	rm -rf logs/*.log
	@echo "$(GREEN)✓ Logs cleaned$(NC)"

clean-data: ## Clean temporary data files (CAUTION!)
	@echo "$(YELLOW)⚠  This will delete temporary data files!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/temp/*; \
		echo "$(GREEN)✓ Data cleaned$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

clean-all: clean clean-logs ## Clean everything

##@ Running

run-dashboard: ## Run web dashboard
	@echo "$(BLUE)Starting dashboard...$(NC)"
	python doc-dashboard.py

run-api: ## Run API server
	@echo "$(BLUE)Starting API server...$(NC)"
	python doc-api-server.py

run-tests-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch tests/

##@ Documentation

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation serving not yet implemented$(NC)"

##@ Deployment

build: ## Build distribution packages
	@echo "$(BLUE)Building packages...$(NC)"
	python setup.py sdist bdist_wheel
	@echo "$(GREEN)✓ Packages built: dist/$(NC)"

deploy-test: ## Deploy to test PyPI
	@echo "$(BLUE)Deploying to test PyPI...$(NC)"
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

deploy-prod: ## Deploy to production PyPI
	@echo "$(YELLOW)⚠  This will deploy to production PyPI!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload dist/*; \
		echo "$(GREEN)✓ Deployed to PyPI$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

##@ Git

git-status: ## Show git status
	git status

git-log: ## Show git log
	git log --oneline -10

git-diff: ## Show git diff
	git diff

##@ Docker

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t dms:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 5000:5000 dms:latest

docker-compose-up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down

##@ CI/CD

ci-test: ## Run CI/CD tests locally
	@echo "$(BLUE)Running CI/CD tests locally...$(NC)"
	./scripts/quality_check.sh --fast
	pytest tests/ -v --tb=short

ci-full: ## Run full CI/CD pipeline locally
	@echo "$(BLUE)Running full CI/CD pipeline...$(NC)"
	./scripts/quality_check.sh
	pytest tests/ --cov=src --cov-report=html

##@ Utilities

version: ## Show version
	@echo "$(BLUE)Document Management System v4.1$(NC)"
	@python --version
	@pip --version

info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Name:    Document Management System"
	@echo "  Version: 4.1"
	@echo "  Python:  $(shell python --version)"
	@echo "  Files:   $(shell find src -name '*.py' | wc -l) Python files"
	@echo "  Tests:   $(shell find tests -name 'test_*.py' | wc -l) test files"
	@echo "  Lines:   $(shell find src -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}') lines of code"

tree: ## Show project tree structure
	@echo "$(BLUE)Project Structure:$(NC)"
	tree -L 2 -I '__pycache__|*.pyc|.git|.venv|venv|data|backups|logs'

check-tools: ## Check if required tools are installed
	@echo "$(BLUE)Checking required tools...$(NC)"
	@command -v python >/dev/null 2>&1 || { echo "$(YELLOW)✗ python not installed$(NC)"; }
	@command -v pip >/dev/null 2>&1 || { echo "$(YELLOW)✗ pip not installed$(NC)"; }
	@command -v black >/dev/null 2>&1 || { echo "$(YELLOW)✗ black not installed$(NC)"; }
	@command -v isort >/dev/null 2>&1 || { echo "$(YELLOW)✗ isort not installed$(NC)"; }
	@command -v flake8 >/dev/null 2>&1 || { echo "$(YELLOW)✗ flake8 not installed$(NC)"; }
	@command -v mypy >/dev/null 2>&1 || { echo "$(YELLOW)✗ mypy not installed$(NC)"; }
	@command -v bandit >/dev/null 2>&1 || { echo "$(YELLOW)✗ bandit not installed$(NC)"; }
	@command -v pytest >/dev/null 2>&1 || { echo "$(YELLOW)✗ pytest not installed$(NC)"; }
	@echo "$(GREEN)✓ Tool check complete$(NC)"

##@ Examples

example-progress: ## Run progress bar examples
	@echo "$(BLUE)Running progress bar examples...$(NC)"
	python examples/progress_examples.py

example-all: ## Run all examples
	@echo "$(BLUE)Running all examples...$(NC)"
	@echo "$(YELLOW)Running example scripts...$(NC)"
	python examples/progress_examples.py --example 1
