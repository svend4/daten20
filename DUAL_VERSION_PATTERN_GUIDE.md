# Dual-Version Pattern Guide: NumPy + Pure Python

**Дата**: 2026-01-20
**Автор**: DATEN20 Development Team

---

## 📋 Обзор (Overview)

**Dual-Version Pattern (Паттерн двух версий)** - это архитектурный паттерн, который позволяет иметь **две реализации одного и того же модуля**:

1. **Pure Python версия** - работает везде, не требует зависимостей (stdlib only)
2. **NumPy-ускоренная версия** - в 10-100x быстрее, требует numpy

**Ключевое отличие**: Обе версии имеют **идентичный API** (100% совместимость), но разную производительность.

---

## 🎯 Когда использовать Dual-Version Pattern

### ✅ Используйте Dual-Version когда:

- Модуль выполняет математические вычисления (матрицы, векторы, статистика)
- Производительность критична (обработка больших данных)
- Нужна поддержка окружений БЕЗ numpy (embedded, minimal containers)
- Можно достичь 10x+ ускорения с numpy
- Обе версии выполняют ОДИНАКОВУЮ логику, но разными способами

**Примеры из DATEN20**:
- ✅ `continual_learning`: EWC algorithm (математика, векторы)
- ✅ `neurosymbolic`: Symbolic reasoning (логика, операции над множествами)
- ✅ `quantum_ml`: Quantum state simulation (линейная алгебра)

### ❌ НЕ используйте Dual-Version когда:

- Модуль не выполняет интенсивных вычислений
- NumPy не даст значительного ускорения (< 2x)
- Логика зависит от внешних API (HTTP, файлы, БД)
- Достаточно graceful degradation (опциональный импорт)

**Примеры из DATEN20**:
- ❌ `webhooks`: HTTP delivery (сеть, не вычисления)
- ❌ `calendar`: API calls (внешние сервисы)
- ❌ `basic_ai_pipeline`: Оркестрация (используйте graceful degradation)

---

## 🏗️ Структура Dual-Version Pattern

### Файловая структура

```
src/my_module/
├── __init__.py                    # Conditional imports
├── algorithm.py                   # Pure Python version (DEFAULT)
├── algorithm_numpy.py             # NumPy version (OPTIONAL)
└── my_module_services.py          # Other services (optional)
```

### Пример: Референсная реализация EWC

```
src/continual_learning/
├── __init__.py                           # ✅ Conditional imports
├── ewc_algorithm.py                      # ✅ Pure Python (458 lines)
├── ewc_algorithm_numpy.py                # ✅ NumPy version (513 lines)
└── continual_learning_services.py        # Other services
```

---

## 📝 Шаг 1: Pure Python версия (Базовая)

Создайте базовую версию используя ТОЛЬКО Python stdlib.

**Файл**: `src/my_module/algorithm.py`

```python
"""
My Algorithm - Pure Python Version

Zero dependencies! Works everywhere.
Uses only Python stdlib (lists, math module, etc.)
"""

import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class TaskResult:
    """Result of algorithm execution"""
    task_id: int
    score: float
    data: List[float]
    success: bool


class MyAlgorithm:
    """
    Core algorithm implementation using pure Python.

    Uses only Python stdlib - no external dependencies!
    Performance: Good for small datasets (< 1000 samples)
    """

    def __init__(self, param: float = 1.0):
        """Initialize algorithm"""
        self.param = param
        self.weights = [random.uniform(-1.0, 1.0) for _ in range(10)]

    def compute(self, inputs: List[float]) -> float:
        """
        Main computation using pure Python.

        Uses list comprehensions and math module.
        """
        # Example: weighted sum
        result = sum(w * x for w, x in zip(self.weights, inputs))

        # Apply activation
        return 1.0 / (1.0 + math.exp(-result))

    def train(self, data: List[Tuple[List[float], float]], epochs: int = 100) -> TaskResult:
        """
        Training loop using pure Python.

        Uses standard Python loops.
        """
        for epoch in range(epochs):
            random.shuffle(data)

            for inputs, target in data:
                # Forward pass
                output = self.compute(inputs)

                # Update weights (gradient descent)
                error = target - output
                for i in range(len(self.weights)):
                    gradient = error * inputs[i]
                    self.weights[i] += 0.1 * gradient

        # Compute final score
        total_error = 0.0
        for inputs, target in data:
            output = self.compute(inputs)
            total_error += (target - output) ** 2

        score = 1.0 - (total_error / len(data))

        return TaskResult(
            task_id=1,
            score=score,
            data=self.weights.copy(),
            success=True
        )


def generate_data(num_samples: int = 100) -> List[Tuple[List[float], float]]:
    """Generate training data (compatible with both versions)"""
    data = []
    for _ in range(num_samples):
        inputs = [random.uniform(0.0, 1.0) for _ in range(10)]
        target = 1.0 if sum(inputs[:5]) > 2.5 else 0.0
        data.append((inputs, target))
    return data
```

**Ключевые особенности Pure Python версии**:
- ✅ Использует `list`, `math`, `random` (stdlib only)
- ✅ Циклы `for` вместо векторизации
- ✅ List comprehensions для простоты
- ✅ Работает везде (Python 3.9+)

---

## 🚀 Шаг 2: NumPy-ускоренная версия

Создайте NumPy версию с **идентичным API** но векторизованными операциями.

**Файл**: `src/my_module/algorithm_numpy.py`

```python
"""
My Algorithm - NumPy-Accelerated Version

Performance: 10-100x faster than pure Python!
Requires: numpy

API-compatible with algorithm.py (pure Python version).
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    raise ImportError(
        "NumPy not available! Install with: pip install numpy\n"
        "Or use pure Python version: from my_module import MyAlgorithm"
    )


@dataclass
class TaskResult:
    """Result of algorithm execution (same as pure Python version)"""
    task_id: int
    score: float
    data: List[float]  # Still return list for API compatibility
    success: bool


class MyAlgorithmNumpy:
    """
    Core algorithm implementation using NumPy.

    Same API as MyAlgorithm but 10-100x faster!
    Uses vectorized operations and matrix math.
    """

    def __init__(self, param: float = 1.0):
        """Initialize algorithm (same API as pure Python)"""
        self.param = param
        # Use NumPy arrays instead of lists
        self.weights = np.random.uniform(-1.0, 1.0, size=10)

    def compute(self, inputs: List[float]) -> float:
        """
        Main computation using NumPy (vectorized).

        Same API but uses np.dot for speed!
        """
        # Convert to numpy array
        x = np.array(inputs)

        # Vectorized: w · x (dot product)
        result = np.dot(self.weights, x)

        # Apply activation (handles overflow better)
        return float(1.0 / (1.0 + np.exp(-np.clip(result, -500, 500))))

    def compute_batch(self, inputs_batch: np.ndarray) -> np.ndarray:
        """
        Batch computation (MUCH faster for multiple inputs).

        Args:
            inputs_batch: Shape (batch_size, num_features)

        Returns:
            outputs: Shape (batch_size,)
        """
        # Matrix multiply: (batch_size, features) @ (features,) -> (batch_size,)
        activations = inputs_batch @ self.weights

        # Vectorized sigmoid
        return 1.0 / (1.0 + np.exp(-np.clip(activations, -500, 500)))

    def train(self, data: List[Tuple[List[float], float]], epochs: int = 100) -> TaskResult:
        """
        Training loop using NumPy (vectorized).

        Same API as pure Python but 10-100x faster!
        """
        # Convert to numpy arrays for vectorization
        inputs_array = np.array([inp for inp, _ in data])
        targets_array = np.array([tgt for _, tgt in data])

        for epoch in range(epochs):
            # Shuffle using numpy (faster)
            indices = np.random.permutation(len(data))
            inputs_shuffled = inputs_array[indices]
            targets_shuffled = targets_array[indices]

            # Vectorized training loop
            for i in range(len(data)):
                x = inputs_shuffled[i]
                target = targets_shuffled[i]

                # Forward pass (vectorized)
                output = 1.0 / (1.0 + np.exp(-np.clip(np.dot(self.weights, x), -500, 500)))

                # Update weights (vectorized!)
                error = target - output
                gradients = error * x  # Vectorized: element-wise multiply
                self.weights += 0.1 * gradients  # Vectorized: element-wise add

        # Compute final score (vectorized!)
        outputs = self.compute_batch(inputs_array)
        errors = targets_array - outputs
        total_error = np.sum(errors ** 2)
        score = 1.0 - (total_error / len(data))

        return TaskResult(
            task_id=1,
            score=float(score),
            data=self.weights.tolist(),  # Convert back to list for API compatibility
            success=True
        )


def generate_data(num_samples: int = 100) -> List[Tuple[List[float], float]]:
    """Generate training data (same as pure Python version)"""
    data = []
    for _ in range(num_samples):
        inputs = [random.uniform(0.0, 1.0) for _ in range(10)]
        target = 1.0 if sum(inputs[:5]) > 2.5 else 0.0
        data.append((inputs, target))
    return data
```

**Ключевые особенности NumPy версии**:
- ✅ Класс `MyAlgorithmNumpy` (добавили суффикс "Numpy")
- ✅ **Идентичный API**: те же методы, те же параметры, те же типы возврата
- ✅ Внутри: `np.array` вместо `list`, векторизация, `np.dot`
- ✅ Новые методы для производительности: `compute_batch()`
- ✅ Конвертация: `.tolist()` для API совместимости

---

## 🔌 Шаг 3: Условный импорт в `__init__.py`

Создайте умный импорт, который автоматически выбирает версию.

**Файл**: `src/my_module/__init__.py`

```python
"""
My Module - Dual-Version Support

Two implementations available:
1. Pure Python (default): Zero dependencies, works everywhere
2. NumPy version: 10-100x faster, requires numpy

Example usage (automatic selection):
    from my_module import MyAlgorithm, HAS_NUMPY

    # Will use NumPy version if available, otherwise pure Python
    algo = MyAlgorithm(param=1.0)

Example usage (explicit version selection):
    from my_module import HAS_NUMPY

    if HAS_NUMPY:
        from my_module import MyAlgorithmNumpy
        algo = MyAlgorithmNumpy(param=1.0)
    else:
        from my_module import MyAlgorithmPython
        algo = MyAlgorithmPython(param=1.0)
"""

__version__ = "1.0.0"

# ALWAYS import pure Python version (default, always available)
from .algorithm import (
    MyAlgorithm as MyAlgorithmPython,  # Rename for clarity
    TaskResult,
    generate_data
)

# Try to import NumPy version (optional, 10-100x faster)
try:
    from .algorithm_numpy import (
        MyAlgorithmNumpy,
        TaskResult as TaskResultNumpy,  # Same structure
        generate_data as generate_data_numpy  # Same API
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Export intelligent default: NumPy if available, otherwise pure Python
if HAS_NUMPY:
    MyAlgorithm = MyAlgorithmNumpy  # Use fast version
else:
    MyAlgorithm = MyAlgorithmPython  # Fallback to pure Python

__all__ = [
    "__version__",
    # Default (auto-selected based on numpy availability)
    "MyAlgorithm",
    # Pure Python (always available)
    "MyAlgorithmPython",
    # Data structures
    "TaskResult",
    "generate_data",
    # Version flag
    "HAS_NUMPY",
]

# Add NumPy-specific exports if available
if HAS_NUMPY:
    __all__.extend([
        "MyAlgorithmNumpy",
        "TaskResultNumpy",
        "generate_data_numpy",
    ])
```

**Ключевые аспекты**:
- ✅ **ВСЕГДА** импортируем Pure Python версию (базовая)
- ✅ **TRY** импортировать NumPy версию (опциональная)
- ✅ Флаг `HAS_NUMPY` показывает доступность
- ✅ `MyAlgorithm` = умный алиас (автоматический выбор)
- ✅ Обе версии доступны явно (`MyAlgorithmPython`, `MyAlgorithmNumpy`)

---

## 💻 Использование Dual-Version Pattern

### Вариант 1: Автоматический выбор (рекомендуется)

```python
from my_module import MyAlgorithm, generate_data, HAS_NUMPY

# MyAlgorithm автоматически выберет быструю версию если numpy доступен
algo = MyAlgorithm(param=1.0)

# Генерируем данные
data = generate_data(num_samples=1000)

# Тренируем (будет использовать NumPy если доступен, иначе pure Python)
result = algo.train(data, epochs=100)

print(f"Using NumPy: {HAS_NUMPY}")
print(f"Score: {result.score:.4f}")
```

### Вариант 2: Явный выбор версии

```python
from my_module import HAS_NUMPY

if HAS_NUMPY:
    print("Using NumPy-accelerated version (10-100x faster)")
    from my_module import MyAlgorithmNumpy
    algo = MyAlgorithmNumpy(param=1.0)
else:
    print("Using pure Python version (zero dependencies)")
    from my_module import MyAlgorithmPython
    algo = MyAlgorithmPython(param=1.0)

# Остальной код одинаковый (100% API compatibility!)
data = generate_data(1000)
result = algo.train(data, epochs=100)
```

### Вариант 3: Принудительное использование Pure Python

```python
# Используем pure Python даже если numpy доступен
from my_module import MyAlgorithmPython

algo = MyAlgorithmPython(param=1.0)
# ...
```

---

## 🎯 Сравнение с Graceful Degradation

### Dual-Version Pattern

**Что это**: Две ОТДЕЛЬНЫЕ реализации одного модуля

```python
# Два файла:
# - algorithm.py (pure Python)
# - algorithm_numpy.py (NumPy)

class MyAlgorithm:
    def compute(self, x):
        return sum(w * x for w, x in ...)  # Pure Python

class MyAlgorithmNumpy:
    def compute(self, x):
        return np.dot(self.weights, x)  # NumPy
```

**Когда использовать**:
- ✅ Математические вычисления (векторы, матрицы)
- ✅ Производительность критична (10-100x ускорение)
- ✅ Обе версии выполняют ОДИНАКОВУЮ логику

### Graceful Degradation Pattern

**Что это**: Один модуль с опциональными возможностями

```python
# Один файл: pipeline.py

try:
    from src.quantum_ml import get_quantum_optimizer
    HAS_QUANTUM = True
except ImportError:
    HAS_QUANTUM = False

class Pipeline:
    def __init__(self):
        if HAS_QUANTUM:
            self.quantum = get_quantum_optimizer()  # Опция 1
        else:
            self.quantum = None  # Опция 2: не используем

    def solve(self, task):
        if self.quantum:
            return self.quantum.solve(task)  # С quantum
        else:
            return self.classical_solve(task)  # Без quantum
```

**Когда использовать**:
- ✅ Оркестрация модулей (pipeline)
- ✅ Опциональные возможности (можно работать без них)
- ✅ Разная логика (с quantum / без quantum)

### Таблица сравнения

| Критерий | Dual-Version | Graceful Degradation |
|----------|--------------|----------------------|
| **Файлы** | 2 файла (algorithm.py + algorithm_numpy.py) | 1 файл (pipeline.py) |
| **API** | Идентичный API в обеих версиях | Разная логика с/без зависимости |
| **Логика** | Одинаковая логика, разная реализация | Разная логика |
| **Производительность** | 10-100x ускорение с NumPy | Не критично |
| **Цель** | Оптимизация вычислений | Опциональные возможности |
| **Пример** | EWC algorithm (math) | Basic AI Pipeline (orchestration) |

---

## 📊 Референсная реализация: EWC Algorithm

**Лучший пример Dual-Version Pattern в DATEN20**:

### Файлы

```
src/continual_learning/
├── __init__.py                    # Conditional imports
├── ewc_algorithm.py               # Pure Python (458 lines)
├── ewc_algorithm_numpy.py         # NumPy version (513 lines)
└── continual_learning_services.py
```

### Сравнение производительности

```python
# Pure Python version
from continual_learning import ElasticWeightConsolidation

ewc = ElasticWeightConsolidation(num_inputs=3)
# Performance: ~5 seconds for 100 epochs

# NumPy version
from continual_learning import ElasticWeightConsolidationNumpy

ewc = ElasticWeightConsolidationNumpy(num_inputs=3)
# Performance: ~0.05 seconds for 100 epochs (100x faster!)
```

### API совместимость

```python
# Обе версии имеют ИДЕНТИЧНЫЙ API:

# Pure Python
ewc1 = ElasticWeightConsolidation(num_inputs=3, ewc_lambda=5000.0)
result1 = ewc1.train_task(task, epochs=100, use_ewc=True)

# NumPy (100% identical API!)
ewc2 = ElasticWeightConsolidationNumpy(num_inputs=3, ewc_lambda=5000.0)
result2 = ewc2.train_task(task, epochs=100, use_ewc=True)

# Результаты одинаковые (same TaskResult structure)
assert result1.task_id == result2.task_id
assert type(result1.weights) == type(result2.weights)  # Both lists
```

### Автоматический выбор

```python
from continual_learning import ElasticWeightConsolidation, HAS_NUMPY

# Автоматически использует NumPy если доступен
ewc = ElasticWeightConsolidation(num_inputs=3)

print(f"Using NumPy: {HAS_NUMPY}")
# Output: Using NumPy: True (если numpy установлен)
```

---

## 📋 Checklist: Создание Dual-Version Module

### ✅ Шаг 1: Pure Python версия
- [ ] Создать `module_name/algorithm.py`
- [ ] Использовать ТОЛЬКО stdlib (list, math, random)
- [ ] Реализовать основные классы и функции
- [ ] Добавить docstrings
- [ ] Протестировать без внешних зависимостей

### ✅ Шаг 2: NumPy версия
- [ ] Создать `module_name/algorithm_numpy.py`
- [ ] Скопировать структуру из Pure Python версии
- [ ] Добавить суффикс "Numpy" к классам
- [ ] Заменить списки на `np.array`
- [ ] Заменить циклы на векторизацию (`np.dot`, `@`)
- [ ] Добавить batch методы для производительности
- [ ] Обеспечить 100% API совместимость
- [ ] Конвертировать возвращаемые значения (.tolist())

### ✅ Шаг 3: Conditional imports
- [ ] Создать `module_name/__init__.py`
- [ ] Импортировать Pure Python (всегда)
- [ ] Try/except для NumPy версии
- [ ] Создать флаг `HAS_NUMPY`
- [ ] Создать умный алиас (`MyAlgorithm`)
- [ ] Экспортировать обе версии явно
- [ ] Добавить docstring с примерами

### ✅ Шаг 4: Тестирование
- [ ] Тесты для Pure Python версии (без numpy)
- [ ] Тесты для NumPy версии (требует numpy)
- [ ] Тест API совместимости (идентичные результаты)
- [ ] Тест производительности (NumPy быстрее 10x+)
- [ ] Тест автоматического выбора версии

### ✅ Шаг 5: Документация
- [ ] README с описанием обеих версий
- [ ] Примеры использования (auto / explicit)
- [ ] Таблица производительности
- [ ] Инструкции по установке dependencies

---

## 🚀 Производительность: Pure Python vs NumPy

### Типичные ускорения

| Операция | Pure Python | NumPy | Ускорение |
|----------|-------------|-------|-----------|
| **Dot product** (1000 элементов) | 0.5 ms | 0.01 ms | **50x** |
| **Matrix multiply** (100x100) | 50 ms | 0.2 ms | **250x** |
| **Element-wise ops** (10000 элементов) | 5 ms | 0.05 ms | **100x** |
| **Sum/Mean** (10000 элементов) | 1 ms | 0.01 ms | **100x** |
| **Batch processing** (1000 samples) | 500 ms | 5 ms | **100x** |

### EWC Algorithm: Реальные данные

```
Dataset: 50 samples, 3 features, 100 epochs

Pure Python:
  - Fisher computation: 1.2 seconds
  - Training: 4.5 seconds
  - Total: 5.7 seconds

NumPy:
  - Fisher computation: 0.01 seconds
  - Training: 0.04 seconds
  - Total: 0.05 seconds

Speedup: 114x faster! 🚀
```

---

## 📚 Примеры из DATEN20

### ✅ Используют Dual-Version Pattern

1. **`continual_learning`** (v21)
   - Pure: `ewc_algorithm.py`
   - NumPy: `ewc_algorithm_numpy.py`
   - Ускорение: **100x** на больших датасетах
   - Референсная реализация!

### ✅ Могут использовать Dual-Version

2. **`neurosymbolic`** (v14)
   - Текущая: только NumPy
   - Потенциал: Pure Python версия (set operations, logic)
   - Оценка ускорения: **10-50x**

3. **`quantum_ml`** (v15)
   - Текущая: только NumPy (quantum states)
   - Потенциал: Pure Python версия (complex numbers)
   - Оценка ускорения: **50-100x**

### ❌ НЕ подходит Dual-Version

4. **`basic_ai_pipeline`** (v10-v20)
   - Текущая: Graceful degradation ✅ (правильный выбор)
   - Причина: Оркестрация модулей, не вычисления
   - Паттерн: Graceful degradation подходит лучше

5. **`webhooks`** (integration)
   - Текущая: HTTP delivery
   - Причина: Сетевые операции, не математика
   - NumPy не поможет

---

## 🎓 Итоговые рекомендации

### Когда использовать Dual-Version Pattern:

1. ✅ **Математические вычисления**: векторы, матрицы, линейная алгебра
2. ✅ **Производительность критична**: обработка больших данных
3. ✅ **NumPy дает 10x+ ускорение**: batch operations, vectorization
4. ✅ **Нужна поддержка без numpy**: embedded, minimal containers

### Структура:

```
src/my_module/
├── __init__.py              # Умный импорт с HAS_NUMPY
├── algorithm.py             # Pure Python (baseline)
├── algorithm_numpy.py       # NumPy (optimized)
└── README.md               # Документация обеих версий
```

### Ключевые принципы:

1. **100% API совместимость** - идентичные методы, параметры, возвраты
2. **Pure Python = default** - всегда должна быть доступна
3. **NumPy = optional** - ускорение, но не обязательно
4. **Умный импорт** - автоматический выбор версии
5. **Документация** - четкие примеры обеих версий

---

## 📖 См. также

- **Референсная реализация**: `src/continual_learning/` (EWC algorithm)
- **Graceful Degradation**: `BASIC_AI_PIPELINE_README.md`
- **Integration Pattern**: `INTEGRATION_IMPROVEMENTS.md`

---

**Dual-Version Pattern = Maximum Performance + Maximum Compatibility** 🚀
