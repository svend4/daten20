# План Восстановления и Улучшения Тестов
# Test Restoration and Enhancement Plan

**Дата:** 2026-01-21
**Статус:** 📋 К ВЫПОЛНЕНИЮ
**Приоритет:** 🔴 ВЫСОКИЙ

---

## 📋 Резюме

Этот документ содержит **конкретный план действий** по восстановлению упрощенных тестов и улучшению качества тестового покрытия.

### Проблема

В процессе TASK 7 были обнаружены случаи **упрощения тестов** вместо их улучшения. Необходимо:
1. Восстановить оригинальные строгие тесты
2. Исправить код для прохождения строгих тестов
3. Предотвратить будущие упрощения
4. Улучшить и расширить тестовое покрытие

---

## 🎯 Цели

| Цель | Текущее | Целевое | Срок |
|------|---------|---------|------|
| Упрощенные тесты | 3+ | 0 | 2 дня |
| Строгость assertions (avg tolerance) | 0.5 | < 0.05 | 2 дня |
| pytest.raises для error cases | Частично | 100% | 2 дня |
| Автоматический контроль | Нет | Полный | 3 дня |
| Методология сверки | Нет | Внедрена | 3 дня |

---

## 📊 Фазы Плана

### Фаза 1: НЕМЕДЛЕННОЕ ВОССТАНОВЛЕНИЕ (День 1-2)
**Приоритет:** 🔴 КРИТИЧЕСКИЙ

### Фаза 2: АВТОМАТИЗАЦИЯ КОНТРОЛЯ (День 2-3)
**Приоритет:** 🟡 ВЫСОКИЙ

### Фаза 3: УЛУЧШЕНИЕ И РАСШИРЕНИЕ (День 4-7)
**Приоритет:** 🟢 СРЕДНИЙ

---

## 🔴 ФАЗА 1: Немедленное Восстановление

### День 1: Восстановление test_classifier_comprehensive.py

#### Задача 1.1: Восстановить test_prediction_before_training

**Статус:** ⏳ К выполнению
**Файл:** `tests/unit/ml/test_classifier_comprehensive.py`
**Строки:** 252-260

**Текущий код (НЕПРАВИЛЬНЫЙ):**
```python
def test_prediction_before_training(self, classifier):
    """Test prediction before training returns default result"""
    result = classifier.predict("some text")
    # Should return a valid result even if not trained
    assert isinstance(result, ClassificationResult)
    assert result.category in DocumentCategory
    # Confidence should be low or default
    assert 0.0 <= result.confidence <= 1.0
```

**Восстановить на (ПРАВИЛЬНЫЙ):**
```python
def test_prediction_before_training(self, classifier):
    """Test prediction before training raises error"""
    with pytest.raises(ValueError, match="must be trained"):
        classifier.predict("some text")
```

**Исправить код:** `src/ml/classifier.py`
```python
class TfidfSVMClassifier:
    # ...

    def predict(self, text: str) -> ClassificationResult:
        """Predict document category"""
        if not self.is_trained:
            raise ValueError("Classifier must be trained before making predictions")

        # ... existing prediction logic ...
```

**Action Items:**
- [ ] Восстановить оригинальный тест
- [ ] Добавить is_trained проверку в predict()
- [ ] Добавить unit test для is_trained property
- [ ] Запустить тесты и убедиться что проходят
- [ ] Commit: "fix(ml): restore strict test for untrained classifier prediction"

---

#### Задача 1.2: Восстановить строгий tolerance в test_confidence_calculation

**Статус:** ⏳ К выполнению
**Файл:** `tests/unit/ml/test_classifier_comprehensive.py`
**Строки:** 332-338

**Текущий код (СМЯГЧЕННЫЙ):**
```python
def test_confidence_calculation(self, classifier, training_samples):
    classifier.train(training_samples)
    result = classifier.predict("invoice payment billing")

    # Confidence should be reasonable and related to max probability
    max_prob = max(result.probabilities.values()) if result.probabilities else 0.5
    # Allow some tolerance - confidence should be close to max prob
    assert abs(result.confidence - max_prob) < 0.5  # ❌ Tolerance 50%!
    assert 0.0 <= result.confidence <= 1.0
```

**Восстановить на (СТРОГИЙ):**
```python
def test_confidence_calculation(self, classifier, training_samples):
    """Test confidence matches maximum probability"""
    classifier.train(training_samples)
    result = classifier.predict("invoice payment billing")

    # Confidence должен точно соответствовать максимальной вероятности
    max_prob = max(result.probabilities.values())
    assert abs(result.confidence - max_prob) < 0.01  # ✅ Tolerance 1%

    # Дополнительные проверки
    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence > 0  # Confidence не должен быть нулевым для обученной модели
```

**Исправить код:** `src/ml/classifier.py`
```python
def predict(self, text: str) -> ClassificationResult:
    # ... existing code ...

    # Правильный расчет confidence
    probabilities = self.model.predict_proba(features)[0]
    confidence = float(max(probabilities))  # Confidence = max probability

    return ClassificationResult(
        category=predicted_category,
        confidence=confidence,
        probabilities=prob_dict
    )
```

**Action Items:**
- [ ] Восстановить строгий tolerance (0.01)
- [ ] Проверить правильность расчета confidence в коде
- [ ] Убедиться что confidence = max(probabilities)
- [ ] Добавить дополнительные assertions
- [ ] Commit: "fix(ml): restore strict confidence calculation test (1% tolerance)"

---

#### Задача 1.3: Восстановить требование >= 2 категории в test_multiclass_classification

**Статус:** ⏳ К выполнению
**Файл:** `tests/unit/ml/test_classifier_comprehensive.py`
**Строки:** 340-356

**Текущий код (ОСЛАБЛЕННЫЙ):**
```python
def test_multiclass_classification(self, classifier, training_samples):
    """Test multiclass classification"""
    classifier.train(training_samples)

    # Get predictions for different categories with more specific keywords
    results = [
        classifier.predict("invoice payment billing statement"),
        classifier.predict("contract agreement legal terms conditions"),
        classifier.predict("report summary monthly quarterly analysis")
    ]

    # Should predict different categories (though with limited training data might not always work)
    categories = {r.category for r in results}
    # With small training set, at least check that predictions are valid
    assert len(categories) >= 1  # ❌ Только 1 категория!
    for r in results:
        assert r.category in DocumentCategory
```

**Восстановить и УЛУЧШИТЬ:**
```python
def test_multiclass_classification(self, classifier):
    """Test multiclass classification with diverse training data"""
    # Улучшенные training samples с явными различиями
    enhanced_training_samples = [
        # INVOICE category - финансовые термины
        Sample(text="invoice payment due amount total", label=DocumentCategory.INVOICE),
        Sample(text="bill charges fees invoice number", label=DocumentCategory.INVOICE),
        Sample(text="payment invoice billing statement", label=DocumentCategory.INVOICE),

        # CONTRACT category - юридические термины
        Sample(text="contract agreement terms conditions party", label=DocumentCategory.CONTRACT),
        Sample(text="legal agreement contract parties obligations", label=DocumentCategory.CONTRACT),
        Sample(text="terms conditions contract signed agreement", label=DocumentCategory.CONTRACT),

        # REPORT category - аналитические термины
        Sample(text="report analysis summary findings results", label=DocumentCategory.REPORT),
        Sample(text="quarterly report summary performance metrics", label=DocumentCategory.REPORT),
        Sample(text="annual report analysis statistics data", label=DocumentCategory.REPORT),
    ]

    classifier.train(enhanced_training_samples)

    # Тестируем с более специфичными запросами
    results = [
        classifier.predict("invoice payment billing statement charges"),
        classifier.predict("contract agreement legal terms conditions obligations"),
        classifier.predict("report summary analysis findings quarterly")
    ]

    # Должно предсказать МИНИМУМ 2 разные категории ✅
    categories = {r.category for r in results}
    assert len(categories) >= 2, f"Expected >= 2 categories, got {len(categories)}: {categories}"

    # Дополнительная проверка - каждая предикция valid
    for r in results:
        assert r.category in DocumentCategory
        assert r.confidence > 0.3  # Разумная уверенность для обученной модели
```

**Action Items:**
- [ ] Восстановить требование >= 2 категории
- [ ] Улучшить training data для лучшего разделения
- [ ] Добавить больше training samples (9 вместо 3)
- [ ] Использовать более специфичные ключевые слова
- [ ] Добавить проверку confidence > 0.3
- [ ] Commit: "fix(ml): restore multiclass test requirement (>=2 categories) with enhanced training data"

---

### День 2: Полный Аудит и Исправление Других Упрощений

#### Задача 2.1: Запустить автоматический аудит

**Команды:**
```bash
# Создать и запустить audit script
chmod +x scripts/audit_test_simplifications.sh
./scripts/audit_test_simplifications.sh HEAD~30..HEAD

# Результат сохранится в: test_simplification_audit_YYYYMMDD_HHMMSS.md
```

**Action Items:**
- [ ] Запустить audit script
- [ ] Проанализировать отчет
- [ ] Идентифицировать все упрощенные тесты
- [ ] Создать issue для каждого найденного упрощения
- [ ] Приоритизировать по критичности

---

#### Задача 2.2: Проверить performance tests

**Файл:** `tests/unit/ml/test_classifier_comprehensive.py`

**Текущий код:**
```python
@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
def test_training_performance(self, classifier, large_training_set, benchmark):
    """Benchmark training performance"""
    result = benchmark(classifier.train, large_training_set)
```

**Анализ:**
- ℹ️ Это разумное решение для dev окружения
- ✅ Но для CI/CD нужно требовать pytest-benchmark

**Решение:**
```python
# В requirements-dev.txt
pytest-benchmark>=4.0.0

# В requirements-test.txt (для CI/CD)
pytest-benchmark>=4.0.0

# В pytest.ini добавить
[pytest]
# ... existing config ...

# Для CI/CD environment variable
# CI=true означает что пропуск performance tests не допускается
```

**В тесте:**
```python
import os

# Проверка только если CI=true
IN_CI = os.getenv('CI', 'false').lower() == 'true'

@pytest.mark.skipif(not BENCHMARK_AVAILABLE and not IN_CI,
                    reason="pytest-benchmark not installed (skip allowed in dev)")
def test_training_performance(self, classifier, large_training_set, benchmark):
    """Benchmark training performance"""
    if not BENCHMARK_AVAILABLE and IN_CI:
        pytest.fail("pytest-benchmark is required in CI environment")

    result = benchmark(classifier.train, large_training_set)
```

**Action Items:**
- [ ] Добавить pytest-benchmark в requirements-test.txt
- [ ] Обновить performance tests с CI check
- [ ] Обновить CI/CD workflow для установки pytest-benchmark
- [ ] Commit: "test(ml): require pytest-benchmark in CI environment"

---

#### Задача 2.3: Сравнить метрики тестов

**Команды:**
```bash
# Установить первоначальное состояние (до TASK 7)
BEFORE_TASK7=$(git log --all --oneline --grep="TASK 7" | tail -1 | cut -d' ' -f1)

# Сравнить метрики
python scripts/compare_test_metrics.py $BEFORE_TASK7~1 HEAD tests/unit/ml/test_classifier_comprehensive.py > test_metrics_comparison.md

# Просмотреть отчет
cat test_metrics_comparison.md
```

**Action Items:**
- [ ] Сравнить метрики тестов до и после TASK 7
- [ ] Идентифицировать все изменения с tolerance > 10%
- [ ] Идентифицировать удаления pytest.raises
- [ ] Создать список для восстановления
- [ ] Документировать находки

---

## 🟡 ФАЗА 2: Автоматизация Контроля

### День 2-3: Внедрение Защитных Механизмов

#### Задача 3.1: Создать Pre-Commit Hook

**Файл:** `scripts/install_hooks.sh`

```bash
#!/bin/bash
# Установка git hooks для контроля качества тестов

echo "Installing test quality hooks..."

# Создать pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook для проверки качества тестов

# ... (код из TEST_QUALITY_METHODOLOGY.md)
EOF

chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed"
echo ""
echo "The hook will warn about:"
echo "  - Removed pytest.raises"
echo "  - Changed comparison assertions"
echo "  - Modified numeric values in assertions"
echo ""
echo "To bypass (NOT recommended): git commit --no-verify"
```

**Action Items:**
- [ ] Создать scripts/install_hooks.sh
- [ ] Запустить ./scripts/install_hooks.sh
- [ ] Протестировать hook с тестовым коммитом
- [ ] Документировать в README.md
- [ ] Commit: "ci: add pre-commit hook for test quality control"

---

#### Задача 3.2: Настроить GitHub Actions для Test Quality Check

**Файл:** `.github/workflows/test-quality-check.yml`

```yaml
name: Test Quality Check

on:
  pull_request:
    paths:
      - 'tests/**/*.py'

jobs:
  check-test-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pytest pytest-benchmark
          pip install -r requirements.txt

      - name: Run audit script
        run: |
          chmod +x scripts/audit_test_simplifications.sh
          ./scripts/audit_test_simplifications.sh ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}

      - name: Check for suspicious changes
        run: |
          if grep -q "🔴.*SUSPICIOUS" test_simplification_audit_*.md; then
            echo "::error::Suspicious test simplifications detected!"
            echo "Please review the audit report"
            exit 1
          fi

      - name: Upload audit report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-quality-audit
          path: test_simplification_audit_*.md
```

**Action Items:**
- [ ] Создать .github/workflows/test-quality-check.yml
- [ ] Протестировать workflow на тестовом PR
- [ ] Настроить required check в GitHub repo settings
- [ ] Документировать в CONTRIBUTING.md
- [ ] Commit: "ci: add GitHub Actions workflow for test quality check"

---

#### Задача 3.3: Создать Automation Scripts

**Script 1:** `scripts/audit_test_simplifications.sh`
- ✅ Уже создан в TEST_QUALITY_METHODOLOGY.md
- [ ] Скопировать в scripts/
- [ ] chmod +x
- [ ] Протестировать

**Script 2:** `scripts/compare_test_metrics.py`
- ✅ Уже создан в TEST_QUALITY_METHODOLOGY.md
- [ ] Скопировать в scripts/
- [ ] chmod +x
- [ ] Протестировать

**Script 3:** `scripts/restore_strict_tests.py` (новый)

```python
#!/usr/bin/env python3
"""
Автоматически восстанавливает строгие версии тестов из git истории
"""

import subprocess
import sys
import re
from typing import List, Tuple

def get_original_test(commit: str, file_path: str, function_name: str) -> str:
    """Получить оригинальную версию теста"""
    try:
        content = subprocess.check_output(
            ['git', 'show', f'{commit}:{file_path}'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8')

        # Найти функцию
        pattern = rf'(def {function_name}\(.*?\):.*?)(?=\n(?:def |class |\Z))'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1)
        return None
    except:
        return None

def restore_test(file_path: str, function_name: str, original_commit: str):
    """Восстановить тест из оригинального коммита"""
    original = get_original_test(original_commit, file_path, function_name)

    if not original:
        print(f"❌ Could not find original version of {function_name}")
        return False

    print(f"Found original test:\n{original[:200]}...")
    print("\nRestore? (y/n): ", end='')

    if input().lower() != 'y':
        print("Skipped")
        return False

    # TODO: Implement actual restoration logic
    print(f"✅ Would restore {function_name} (not implemented yet)")
    return True

def main():
    # Список тестов для восстановления
    tests_to_restore = [
        {
            'file': 'tests/unit/ml/test_classifier_comprehensive.py',
            'function': 'test_prediction_before_training',
            'original_commit': 'HEAD~6'  # До упрощения
        },
        {
            'file': 'tests/unit/ml/test_classifier_comprehensive.py',
            'function': 'test_confidence_calculation',
            'original_commit': 'HEAD~6'
        },
        {
            'file': 'tests/unit/ml/test_classifier_comprehensive.py',
            'function': 'test_multiclass_classification',
            'original_commit': 'HEAD~6'
        },
    ]

    print("🔄 Test Restoration Tool")
    print("=" * 50)
    print()

    for test in tests_to_restore:
        print(f"Processing: {test['function']}")
        restore_test(test['file'], test['function'], test['original_commit'])
        print()

if __name__ == '__main__':
    main()
```

**Action Items:**
- [ ] Создать scripts/restore_strict_tests.py
- [ ] Реализовать логику восстановления
- [ ] Протестировать на test_classifier_comprehensive.py
- [ ] Документировать использование

---

## 🟢 ФАЗА 3: Улучшение и Расширение

### День 4-5: Расширение Тестового Покрытия

#### Задача 4.1: Добавить Test Size markers ко всем тестам

**Статус:** Только 1% тестов имеют размер markers

**План:**
```bash
# Автоматически определить и пометить тесты
python scripts/auto_mark_test_sizes.py tests/

# Результат: добавит @pytest.mark.small/medium/large к тестам
```

**Критерии:**
- Small: нет I/O, нет network, < 1 sec
- Medium: локальные ресурсы, mocked deps, < 5 min
- Large: полная интеграция, E2E, unlimited

**Action Items:**
- [ ] Создать scripts/auto_mark_test_sizes.py
- [ ] Запустить для tests/unit/ (majority = small)
- [ ] Запустить для tests/integration/ (majority = medium)
- [ ] Запустить для tests/e2e/ (majority = large)
- [ ] Проверить pytest -m small работает
- [ ] Commit: "test: add size markers to all existing tests"

---

#### Задача 4.2: Добавить Edge Case Tests для Classifier

**Новые тесты для добавления:**

```python
class TestClassifierEdgeCases:
    """Edge cases and boundary conditions"""

    def test_empty_text_prediction(self, trained_classifier):
        """Test prediction with empty text"""
        with pytest.raises(ValueError, match="empty"):
            trained_classifier.predict("")

    def test_very_long_text_prediction(self, trained_classifier):
        """Test prediction with extremely long text"""
        long_text = "word " * 100000  # 100k words
        result = trained_classifier.predict(long_text)
        assert isinstance(result, ClassificationResult)

    def test_special_characters_only(self, trained_classifier):
        """Test prediction with only special characters"""
        result = trained_classifier.predict("!@#$%^&*()")
        assert isinstance(result, ClassificationResult)

    def test_unicode_text(self, trained_classifier):
        """Test prediction with Unicode text"""
        texts = [
            "Документ по-русски",  # Russian
            "中文文档",  # Chinese
            "日本語の文書",  # Japanese
            "مستند عربي",  # Arabic
        ]
        for text in texts:
            result = trained_classifier.predict(text)
            assert isinstance(result, ClassificationResult)

    def test_mixed_language_text(self, trained_classifier):
        """Test prediction with mixed languages"""
        result = trained_classifier.predict("English text with русский и 中文")
        assert isinstance(result, ClassificationResult)

    def test_training_with_single_sample(self, classifier):
        """Test training with only one sample"""
        samples = [Sample(text="invoice", label=DocumentCategory.INVOICE)]
        with pytest.raises(ValueError, match="at least 2"):
            classifier.train(samples)

    def test_training_with_single_category(self, classifier):
        """Test training with all samples in same category"""
        samples = [
            Sample(text=f"invoice {i}", label=DocumentCategory.INVOICE)
            for i in range(10)
        ]
        # Должно работать, но warning
        with pytest.warns(UserWarning, match="single category"):
            classifier.train(samples)

    def test_predict_probability_sum(self, trained_classifier):
        """Test that probabilities sum to 1.0"""
        result = trained_classifier.predict("test document")
        total = sum(result.probabilities.values())
        assert abs(total - 1.0) < 0.01

    def test_confidence_bounds(self, trained_classifier):
        """Test confidence is always between 0 and 1"""
        for _ in range(100):  # Test with random texts
            result = trained_classifier.predict(f"random text {_}")
            assert 0.0 <= result.confidence <= 1.0

    def test_thread_safety(self, trained_classifier):
        """Test classifier is thread-safe"""
        import threading

        results = []
        def predict():
            result = trained_classifier.predict("test")
            results.append(result)

        threads = [threading.Thread(target=predict) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(isinstance(r, ClassificationResult) for r in results)
```

**Action Items:**
- [ ] Добавить новый test class TestClassifierEdgeCases
- [ ] Реализовать все 11 edge case tests
- [ ] Убедиться что все тесты проходят
- [ ] Если нет - исправить код, не тесты!
- [ ] Commit: "test(ml): add comprehensive edge case tests for classifier"

---

#### Задача 4.3: Добавить Property-Based Testing

**Использовать Hypothesis для генеративного тестирования:**

```python
from hypothesis import given, strategies as st

class TestClassifierProperties:
    """Property-based tests using Hypothesis"""

    @given(st.text(min_size=1, max_size=1000))
    def test_predict_always_returns_valid_category(self, trained_classifier, text):
        """Property: predict always returns valid category for any text"""
        result = trained_classifier.predict(text)
        assert result.category in DocumentCategory

    @given(st.lists(st.text(min_size=10), min_size=2, max_size=20))
    def test_batch_predict_consistency(self, trained_classifier, texts):
        """Property: batch predict should give same results as individual predicts"""
        individual = [trained_classifier.predict(t) for t in texts]
        batch = trained_classifier.predict_batch(texts)

        assert len(individual) == len(batch)
        for ind, bat in zip(individual, batch):
            assert ind.category == bat.category
            assert abs(ind.confidence - bat.confidence) < 0.01

    @given(st.integers(min_value=10, max_value=1000))
    def test_training_with_varying_sizes(self, classifier, n):
        """Property: training should work with any reasonable dataset size"""
        samples = [
            Sample(text=f"text {i}", label=DocumentCategory.INVOICE)
            for i in range(n)
        ]
        classifier.train(samples)
        assert classifier.is_trained
```

**Action Items:**
- [ ] Установить hypothesis: pip install hypothesis
- [ ] Добавить в requirements-test.txt
- [ ] Создать TestClassifierProperties class
- [ ] Реализовать 3+ property-based tests
- [ ] Commit: "test(ml): add property-based tests using Hypothesis"

---

### День 6-7: Документация и Best Practices

#### Задача 5.1: Обновить TEST_7 документацию

**Файлы для обновления:**

1. **TASK_7_TEST_COVERAGE_PLAN.md**
   - [ ] Добавить раздел "⚠️ Правила Изменения Тестов"
   - [ ] Добавить ссылку на TEST_QUALITY_METHODOLOGY.md
   - [ ] Обновить success criteria

2. **TASK_7_OVERALL_PROGRESS.md**
   - [ ] Добавить раздел "🔴 Обнаруженные Проблемы"
   - [ ] Документировать упрощения
   - [ ] Добавить раздел "✅ Восстановление"

3. **README.md**
   - [ ] Добавить раздел "Test Quality Standards"
   - [ ] Ссылка на TEST_QUALITY_METHODOLOGY.md
   - [ ] Инструкции по установке hooks

---

#### Задача 5.2: Создать Test Writing Guide

**Файл:** `docs/TEST_WRITING_GUIDE.md`

**Содержание:**
```markdown
# Test Writing Guide

## Quick Start

### Good Test Example
[Показать пример хорошего теста]

### Bad Test Example
[Показать антипаттерны]

## Test Structure
- Arrange
- Act
- Assert

## Test Sizes
- When to use Small
- When to use Medium
- When to use Large

## Fixtures Best Practices

## Assertions Guidelines

## Edge Cases Checklist

## Common Pitfalls
```

**Action Items:**
- [ ] Создать docs/TEST_WRITING_GUIDE.md
- [ ] Заполнить все разделы
- [ ] Добавить 10+ примеров
- [ ] Peer review
- [ ] Commit: "docs: add comprehensive test writing guide"

---

#### Задача 5.3: Code Review Guidelines

**Файл:** `docs/CODE_REVIEW_GUIDELINES.md`

**Раздел для тестов:**
```markdown
## Reviewing Test Changes

### Red Flags 🚩
- [ ] Removed pytest.raises
- [ ] Increased tolerance > 10%
- [ ] Removed assertions
- [ ] Lowered requirements (counts, thresholds)

### Must Check ✅
- [ ] Test Change Request filled (for simplifications)
- [ ] Technical justification provided
- [ ] Edge cases covered
- [ ] Test size markers present
- [ ] Docstrings clear

### Approval Rules
- Standard changes: 1 reviewer
- Simplifications: 2 reviewers + tech lead
```

**Action Items:**
- [ ] Создать docs/CODE_REVIEW_GUIDELINES.md
- [ ] Добавить раздел для review тестов
- [ ] Получить одобрение tech lead
- [ ] Commit: "docs: add code review guidelines for test changes"

---

## 📊 Метрики Успеха

### Восстановление (День 1-2)

| Метрика | Начало | Цель | Текущее |
|---------|--------|------|---------|
| Упрощенные тесты в test_classifier_comprehensive.py | 3 | 0 | ⏳ |
| Avg tolerance | 0.5 | < 0.05 | ⏳ |
| pytest.raises для error cases | 0 | 3 | ⏳ |
| Test pass rate | 95% | 100% | ⏳ |

### Автоматизация (День 2-3)

| Метрика | Начало | Цель | Текущее |
|---------|--------|------|---------|
| Pre-commit hook | ❌ | ✅ | ⏳ |
| GitHub Actions check | ❌ | ✅ | ⏳ |
| Audit scripts | ❌ | ✅ | ⏳ |

### Улучшение (День 4-7)

| Метрика | Начало | Цель | Текущее |
|---------|--------|------|---------|
| Тесты с size markers | 1% | 100% | ⏳ |
| Edge case tests | 0 | 11+ | ⏳ |
| Property-based tests | 0 | 3+ | ⏳ |
| Documentation | Частичная | Полная | ⏳ |

---

## ✅ Checklist для Завершения

### Фаза 1: Восстановление ✅
- [ ] test_prediction_before_training восстановлен
- [ ] test_confidence_calculation восстановлен
- [ ] test_multiclass_classification восстановлен и улучшен
- [ ] Код исправлен для прохождения строгих тестов
- [ ] Все тесты проходят
- [ ] Changes committed and pushed

### Фаза 2: Автоматизация ✅
- [ ] Pre-commit hook установлен и работает
- [ ] GitHub Actions workflow настроен
- [ ] Audit scripts созданы и протестированы
- [ ] Documentation обновлена

### Фаза 3: Улучшение ✅
- [ ] Size markers добавлены ко всем тестам
- [ ] Edge case tests добавлены (11+)
- [ ] Property-based tests добавлены (3+)
- [ ] Test Writing Guide создан
- [ ] Code Review Guidelines обновлены

### Финализация ✅
- [ ] Все метрики достигнуты
- [ ] Documentation complete
- [ ] Team training проведено
- [ ] Process внедрен в workflow

---

## 📅 Timeline

```
День 1: Восстановление test_classifier_comprehensive.py
   ├── Задача 1.1: test_prediction_before_training (2h)
   ├── Задача 1.2: test_confidence_calculation (2h)
   └── Задача 1.3: test_multiclass_classification (3h)

День 2: Аудит и Performance Tests
   ├── Задача 2.1: Автоматический аудит (2h)
   ├── Задача 2.2: Performance tests (2h)
   └── Задача 2.3: Метрики сравнения (2h)

День 2-3: Автоматизация
   ├── Задача 3.1: Pre-commit hook (3h)
   ├── Задача 3.2: GitHub Actions (3h)
   └── Задача 3.3: Automation scripts (4h)

День 4-5: Расширение
   ├── Задача 4.1: Size markers (4h)
   ├── Задача 4.2: Edge case tests (6h)
   └── Задача 4.3: Property-based tests (4h)

День 6-7: Документация
   ├── Задача 5.1: Обновить TASK 7 docs (3h)
   ├── Задача 5.2: Test Writing Guide (4h)
   └── Задача 5.3: Code Review Guidelines (2h)

Итого: ~52 hours (7 рабочих дней при 8h/день)
```

---

## 🚨 Риски и Mitigation

### Риск 1: Код не проходит восстановленные строгие тесты

**Вероятность:** Высокая
**Impact:** Средний

**Mitigation:**
- Приоритет на исправление кода, не тестов
- Если невозможно - задокументировать техническое ограничение
- Рассмотреть refactoring кода

### Риск 2: Команда сопротивляется строгим тестам

**Вероятность:** Средняя
**Impact:** Высокий

**Mitigation:**
- Провести обучающую сессию
- Показать примеры багов, пойманных строгими тестами
- Внедрять постепенно с обратной связью

### Риск 3: Pre-commit hooks замедляют workflow

**Вероятность:** Средняя
**Impact:** Низкий

**Mitigation:**
- Оптимизировать скрипты
- Возможность bypass для emergency (с обоснованием)
- Запускать только на измененных тестах

---

## 📞 Контакты и Поддержка

**Вопросы по восстановлению:**
- Create issue с тегом `test-restoration`

**Technical Lead:**
- Review approvals для упрощений

**CI/CD Issues:**
- Create issue с тегом `ci-cd`

---

**Статус:** 📋 ГОТОВ К ВЫПОЛНЕНИЮ
**Приоритет:** 🔴 ВЫСОКИЙ
**Owner:** Development Team
**Start Date:** 2026-01-21 (немедленно)
**Target Completion:** 2026-01-28 (7 дней)
