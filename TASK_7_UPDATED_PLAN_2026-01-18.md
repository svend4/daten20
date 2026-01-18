# TASK 7: Test Coverage Increase Plan - Updated

**Objective:** Increase test coverage from **~21%** to **80%**
**Date:** 2026-01-18
**Priority:** P1 (High Priority)
**Estimated Time:** 20-30 hours

---

## 📊 Current State

### Coverage Analysis Results (Static Analysis)

- **Total modules:** 219
- **Modules with good coverage:** 45 (20.5%)
- **Modules with partial coverage:** 4 (1.8%)
- **Modules without tests:** 170 (77.6%)
- **Current estimated coverage:** ~21%

### Code Statistics

- Total source lines: 132,585
- Total code lines: 97,021
- Total test lines: 26,115
- Test to code ratio: 0.27:1

**Gap to target:** ~59% (need to reach 80%)

---

## 🎯 Strategy

Focus on **critical core modules** that the entire system depends on, NOT experimental AI services.

### Phase 1: Critical Core Modules (Priority 1)

**Target:** Increase coverage to 50% (~30% improvement)
**Time:** 8-10 hours

| Module | Lines | Current Status | Priority | Est. Hours |
|--------|-------|----------------|----------|------------|
| `core/validator.py` | 594 | ❌ No tests | P1 | 3h |
| `core/email_verification.py` | 584 | ❌ No tests | P1 | 2h |
| `core/database_universal.py` | 509 | ❌ No tests | P1 | 3h |
| `core/parser.py` | 213 | ❌ No tests | P1 | 1.5h |
| `core/logger.py` | 215 | ❌ No tests | P1 | 1h |

**Subtotal:** ~10.5 hours, ~2,115 lines

### Phase 2: Complete Partial Coverage (Priority 1)

**Target:** Bring partially covered modules to 80%+
**Time:** 4-5 hours

| Module | Lines | Current | Priority | Est. Hours |
|--------|-------|---------|----------|------------|
| `core/auth.py` | 763 | ⚠️ Partial (233 test lines) | P1 | 2h |
| `core/database.py` | 645 | ⚠️ Partial (231 test lines) | P1 | 2h |
| `analytics/bi_dashboard.py` | 959 | ⚠️ Partial (551 test lines) | P2 | 1.5h |
| `ml/semantic_search.py` | 494 | ⚠️ Partial (216 test lines) | P2 | 1h |

**Subtotal:** ~6.5 hours, ~2,861 lines

### Phase 3: Async/ML Modules (Priority 2)

**Target:** Test async processing (recently completed features)
**Time:** 4-5 hours

| Module | Lines | Current | Priority | Est. Hours |
|--------|-------|---------|----------|------------|
| `core/async_ml.py` | 518 | ❌ No tests | P1 | 2h |
| `core/async_io.py` | 324 | ❌ No tests | P1 | 1.5h |
| `core/celery_app.py` | 483 | ❌ No tests* | P2 | 2h |

*Note: `test_async_processing.py` exists (700+ lines) but may not run due to dependencies

**Subtotal:** ~5.5 hours, ~1,325 lines

### Phase 4: API & Web Layer (Priority 2)

**Target:** Ensure API reliability
**Time:** 5-6 hours

| Module | Lines | Current | Priority | Est. Hours |
|--------|-------|---------|----------|------------|
| `web_app.py` | 582 | ❌ No tests | P2 | 2.5h |
| `api_v1.py` | 527 | ❌ No tests | P2 | 2h |
| `api/async_endpoints.py` | 358 | ❌ No tests | P2 | 1.5h |
| `graphql_api.py` | 194 | ❌ No tests | P3 | 1h |

**Subtotal:** ~7 hours, ~1,661 lines

### Phase 5: Security & Compliance (Priority 2)

**Target:** Ensure security features work
**Time:** 4-5 hours

| Module | Lines | Current | Priority | Est. Hours |
|--------|-------|---------|----------|------------|
| `core/two_factor.py` | 303 | ❌ No tests | P1 | 1.5h |
| `core/account_lockout.py` | 259 | ❌ No tests | P1 | 1h |
| `core/security_middleware.py` | 291 | ❌ No tests | P2 | 1.5h |
| `core/security_headers.py` | 250 | ❌ No tests | P2 | 1h |
| `core/api_security.py` | 314 | ❌ No tests | P2 | 1.5h |

**Subtotal:** ~6.5 hours, ~1,417 lines

---

## 📝 Out of Scope (Defer)

### Experimental AI Services (~15,000 lines)

- quantum/* (1,297 lines)
- autonomous/* (1,294 lines)
- multimodal_ai/* (1,133 lines)
- agi/* (951 lines)
- robotics/* (966 lines)
- etc.

### Enterprise/Integration Features (~10,000 lines)

- Enterprise billing, whitelabel
- Third-party integrations (CRM, ERP)
- IoT/Edge AI
- Blockchain

**Total deferred:** ~25,000 lines (can test in integration phase)

---

## 🎯 Execution Plan

### Week 1: Core (Days 1-3)

**Day 1:**
- ✅ Analyze coverage (DONE)
- 🔄 `core/validator.py` (3h)
- 🔄 `core/email_verification.py` (2h)

**Day 2:**
- 🔄 Complete `core/auth.py` (2h)
- 🔄 Complete `core/database.py` (2h)
- 🔄 `core/parser.py` (1.5h)

**Day 3:**
- 🔄 `core/logger.py` (1h)
- 🔄 `core/database_universal.py` (3h)

**Target:** ~50% coverage

### Week 2: Async/ML & API (Days 4-6)

**Day 4:**
- 🔄 Fix/verify async tests
- 🔄 `core/async_ml.py` (2h)
- 🔄 `core/async_io.py` (1.5h)

**Day 5:**
- 🔄 `web_app.py` (2.5h)
- 🔄 `api_v1.py` (2h)

**Day 6:**
- 🔄 `api/async_endpoints.py` (1.5h)
- 🔄 Complete `ml/semantic_search.py` (1h)
- 🔄 Complete `analytics/bi_dashboard.py` (1.5h)

**Target:** ~65% coverage

### Week 3: Security (Days 7-8)

**Day 7:**
- 🔄 `core/two_factor.py` (1.5h)
- 🔄 `core/account_lockout.py` (1h)
- 🔄 `core/security_middleware.py` (1.5h)
- 🔄 `core/security_headers.py` (1h)

**Day 8:**
- 🔄 `core/api_security.py` (1.5h)
- 🔄 Final verification
- 🔄 Generate coverage report

**Target:** ~80%+ coverage

---

## 📈 Progress Tracking

### Metrics

1. **Module Coverage:** 0 / 35 priority modules tested
2. **Overall Coverage:** 21% → 80% (target)
3. **Test Quality:** TBD

### Daily Checkpoints

```bash
# Run static analysis
python scripts/analyze_test_coverage.py

# Run pytest coverage
pytest --cov=src --cov-report=term

# Commit progress
git add tests/
git commit -m "test: add tests for module X"
```

---

## 🔧 Testing Guidelines

### Test Structure

```python
"""Tests for src/core/module.py"""
import pytest
from src.core.module import ClassName

class TestClassName:
    def test_initialization(self):
        obj = ClassName()
        assert obj is not None

    @pytest.mark.parametrize("input,expected", [
        ("valid", True),
        ("invalid", False),
    ])
    def test_validation(self, input, expected):
        result = obj.validate(input)
        assert result == expected
```

### Coverage Goals

- **Minimum:** 70% per module
- **Target:** 80% per module
- **Ideal:** 90%+ per module

---

## ✅ Success Criteria

1. ✅ Overall coverage **80%+**
2. ✅ All 35 priority modules tested
3. ✅ All tests passing (100% pass rate)
4. ✅ CI/CD pipeline green
5. ✅ Documentation updated

---

## 📚 Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific module
pytest tests/unit/core/test_validator.py

# Static analysis
python scripts/analyze_test_coverage.py
```

---

## 📊 Expected Outcomes

### After Completion

- **Coverage:** 21% → 80%
- **New tests:** ~35 files
- **Test lines:** +30,000
- **Production readiness:** 90% → 100%

---

**Status:** Ready to execute
**Priority:** P1 - Critical
**Completion:** 3-4 weeks
