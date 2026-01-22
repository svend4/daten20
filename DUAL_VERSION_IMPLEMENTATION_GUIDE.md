# Dual-Version Implementation Guide: NumPy → Pure Python

**Дата**: 2026-01-20
**Для**: TOP 5 модулей DATEN20

---

## 📖 Обзор

Это практическое руководство показывает **как** преобразовать NumPy код в Pure Python для создания dual-version модулей.

**Цель**: Создать Pure Python версии для:
- v15: quantum_ml (1,248 строк)
- v4.4: bci (1,562 строк)
- v13: explainable (1,535 строк)
- v14: neurosymbolic (1,459 строк)
- v18: ai_safety (2,183 строк)

---

## 🔄 Основные паттерны преобразования

### 1. Векторные операции

#### NumPy:
```python
import numpy as np

# Создание массива
data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

# Скалярное произведение
result = np.dot(vector1, vector2)

# Норма (длина вектора)
norm = np.linalg.norm(vector)
```

#### Pure Python:
```python
import math

# Создание "массива" (список)
data = [1.0, 2.0, 3.0, 4.0, 5.0]

# Скалярное произведение
def dot_product(v1: List[float], v2: List[float]) -> float:
    """Dot product: v1 · v2"""
    return sum(a * b for a, b in zip(v1, v2))

result = dot_product(vector1, vector2)

# Норма (длина вектора)
def vector_norm(v: List[float]) -> float:
    """L2 norm: ||v||"""
    return math.sqrt(sum(x * x for x in v))

norm = vector_norm(vector)
```

---

### 2. Матричные операции

#### NumPy:
```python
# Создание матрицы
matrix = np.zeros((3, 4))
matrix = np.ones((2, 2))
matrix = np.eye(5)  # Identity matrix

# Умножение матриц
result = np.dot(matrix1, matrix2)

# Транспонирование
transposed = matrix.T
```

#### Pure Python:
```python
# Создание матрицы (список списков)
def zeros_matrix(rows: int, cols: int) -> List[List[float]]:
    """Create zero matrix"""
    return [[0.0 for _ in range(cols)] for _ in range(rows)]

def ones_matrix(rows: int, cols: int) -> List[List[float]]:
    """Create ones matrix"""
    return [[1.0 for _ in range(cols)] for _ in range(rows)]

def identity_matrix(size: int) -> List[List[float]]:
    """Create identity matrix"""
    matrix = zeros_matrix(size, size)
    for i in range(size):
        matrix[i][i] = 1.0
    return matrix

matrix = zeros_matrix(3, 4)

# Умножение матриц
def matrix_multiply(m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
    """Matrix multiplication: m1 @ m2"""
    rows1, cols1 = len(m1), len(m1[0])
    rows2, cols2 = len(m2), len(m2[0])

    if cols1 != rows2:
        raise ValueError(f"Incompatible shapes: ({rows1}, {cols1}) @ ({rows2}, {cols2})")

    result = zeros_matrix(rows1, cols2)
    for i in range(rows1):
        for j in range(cols2):
            result[i][j] = sum(m1[i][k] * m2[k][j] for k in range(cols1))

    return result

result = matrix_multiply(matrix1, matrix2)

# Транспонирование
def transpose(matrix: List[List[float]]) -> List[List[float]]:
    """Transpose matrix"""
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]

transposed = transpose(matrix)
```

---

### 3. Элемент-wise операции

#### NumPy:
```python
# Element-wise операции
result = arr1 + arr2  # Addition
result = arr1 * arr2  # Multiplication
result = arr1 ** 2    # Power
result = np.exp(arr)  # Exponential
result = np.sin(arr)  # Sine
result = np.sqrt(arr) # Square root
```

#### Pure Python:
```python
# Element-wise операции
result = [a + b for a, b in zip(arr1, arr2)]  # Addition
result = [a * b for a, b in zip(arr1, arr2)]  # Multiplication
result = [x ** 2 for x in arr1]                # Power
result = [math.exp(x) for x in arr]            # Exponential
result = [math.sin(x) for x in arr]            # Sine
result = [math.sqrt(x) for x in arr]           # Square root
```

---

### 4. Статистические функции

#### NumPy:
```python
# Статистика
mean = np.mean(data)
std = np.std(data)
min_val = np.min(data)
max_val = np.max(data)
sum_val = np.sum(data)
```

#### Pure Python:
```python
# Статистика
mean = sum(data) / len(data)

def std_dev(data: List[float]) -> float:
    """Standard deviation"""
    mean_val = sum(data) / len(data)
    variance = sum((x - mean_val) ** 2 for x in data) / len(data)
    return math.sqrt(variance)

std = std_dev(data)
min_val = min(data)
max_val = max(data)
sum_val = sum(data)
```

---

### 5. Random операции

#### NumPy:
```python
# Random
random_array = np.random.randn(10)  # Normal distribution
random_uniform = np.random.uniform(0, 1, size=10)
random_int = np.random.randint(0, 10, size=5)
choice = np.random.choice([1, 2, 3, 4, 5])
```

#### Pure Python:
```python
import random

# Random
random_array = [random.gauss(0, 1) for _ in range(10)]  # Normal distribution
random_uniform = [random.uniform(0, 1) for _ in range(10)]
random_int = [random.randint(0, 9) for _ in range(5)]
choice = random.choice([1, 2, 3, 4, 5])
```

---

### 6. Специальные операции

#### NumPy:
```python
# Clipping
clipped = np.clip(array, min_val, max_val)

# Concatenation
concat = np.concatenate([arr1, arr2])

# Reshape
reshaped = array.reshape(3, 4)

# Argmax / Argmin
max_index = np.argmax(array)
min_index = np.argmin(array)
```

#### Pure Python:
```python
# Clipping
def clip(array: List[float], min_val: float, max_val: float) -> List[float]:
    """Clip values"""
    return [max(min_val, min(max_val, x)) for x in array]

clipped = clip(array, min_val, max_val)

# Concatenation
concat = arr1 + arr2  # Lists concatenate with +

# Reshape (сложнее, нужна логика)
def reshape(array: List[float], rows: int, cols: int) -> List[List[float]]:
    """Reshape 1D array to 2D"""
    if len(array) != rows * cols:
        raise ValueError(f"Cannot reshape {len(array)} elements to ({rows}, {cols})")

    return [array[i*cols:(i+1)*cols] for i in range(rows)]

reshaped = reshape(array, 3, 4)

# Argmax / Argmin
max_index = max(range(len(array)), key=lambda i: array[i])
min_index = min(range(len(array)), key=lambda i: array[i])
```

---

## 📋 ПРИМЕРЫ ИЗ quantum_ml

### Пример 1: Amplitude Encoding

#### NumPy версия (original):
```python
def encode_amplitude(self, data: np.ndarray) -> np.ndarray:
    """
    Amplitude encoding: encode data into quantum state amplitudes.

    Requires normalization: ||ψ|| = 1
    """
    # Normalize
    norm = np.linalg.norm(data)
    if norm == 0:
        return data

    normalized = data / norm

    # Pad to power of 2
    num_qubits = int(np.ceil(np.log2(len(data))))
    padded_size = 2 ** num_qubits

    if len(data) < padded_size:
        padded = np.zeros(padded_size)
        padded[:len(data)] = normalized
        return padded

    return normalized
```

#### Pure Python версия:
```python
def encode_amplitude(self, data: List[float]) -> List[float]:
    """
    Amplitude encoding: encode data into quantum state amplitudes.

    Requires normalization: ||ψ|| = 1
    Pure Python implementation (no NumPy).
    """
    # Normalize
    norm = math.sqrt(sum(x * x for x in data))
    if norm == 0:
        return data

    normalized = [x / norm for x in data]

    # Pad to power of 2
    num_qubits = int(math.ceil(math.log2(len(data))))
    padded_size = 2 ** num_qubits

    if len(data) < padded_size:
        padded = [0.0] * padded_size
        padded[:len(data)] = normalized
        return padded

    return normalized
```

---

### Пример 2: Quantum Kernel (Fidelity)

#### NumPy версия (original):
```python
async def quantum_kernel(self, x1: np.ndarray, x2: np.ndarray,
                        kernel_type: QuantumKernel = QuantumKernel.FIDELITY) -> float:
    """
    Compute quantum kernel between two data points.

    Returns inner product in quantum feature space.
    """
    # Encode features
    state1 = self.encode_amplitude(x1)
    state2 = self.encode_amplitude(x2)

    if kernel_type == QuantumKernel.FIDELITY:
        # Fidelity kernel: |<ψ₁|ψ₂>|²
        inner_product = np.abs(np.dot(np.conj(state1), state2))
        return float(inner_product ** 2)

    elif kernel_type == QuantumKernel.PROJECTED:
        # Projected kernel: <ψ₁|M|ψ₂>
        # For simplicity, use measurement in computational basis
        return float(np.dot(state1, state2))

    else:
        # Default: dot product
        return float(np.dot(state1, state2))
```

#### Pure Python версия:
```python
async def quantum_kernel(self, x1: List[float], x2: List[float],
                        kernel_type: QuantumKernel = QuantumKernel.FIDELITY) -> float:
    """
    Compute quantum kernel between two data points.

    Returns inner product in quantum feature space.
    Pure Python implementation (no NumPy).
    """
    # Encode features
    state1 = self.encode_amplitude(x1)
    state2 = self.encode_amplitude(x2)

    if kernel_type == QuantumKernel.FIDELITY:
        # Fidelity kernel: |<ψ₁|ψ₂>|²
        # For real numbers: conjugate = identity
        inner_product = abs(sum(a * b for a, b in zip(state1, state2)))
        return inner_product ** 2

    elif kernel_type == QuantumKernel.PROJECTED:
        # Projected kernel: <ψ₁|M|ψ₂>
        # For simplicity, use measurement in computational basis
        return sum(a * b for a, b in zip(state1, state2))

    else:
        # Default: dot product
        return sum(a * b for a, b in zip(state1, state2))
```

---

### Пример 3: Angle Encoding

#### NumPy версия (original):
```python
def encode_angle(self, data: np.ndarray) -> List[float]:
    """
    Angle encoding: encode data as rotation angles.

    Each feature → rotation angle for qubit
    """
    # Scale to [0, 2π]
    min_val = np.min(data)
    max_val = np.max(data)

    if max_val == min_val:
        return [0.0] * len(data)

    # Normalize to [0, 1]
    normalized = (data - min_val) / (max_val - min_val)

    # Scale to [0, 2π]
    angles = normalized * 2 * np.pi

    return angles.tolist()
```

#### Pure Python версия:
```python
def encode_angle(self, data: List[float]) -> List[float]:
    """
    Angle encoding: encode data as rotation angles.

    Each feature → rotation angle for qubit
    Pure Python implementation (no NumPy).
    """
    # Scale to [0, 2π]
    min_val = min(data)
    max_val = max(data)

    if max_val == min_val:
        return [0.0] * len(data)

    # Normalize to [0, 1]
    normalized = [(x - min_val) / (max_val - min_val) for x in data]

    # Scale to [0, 2π]
    angles = [x * 2 * math.pi for x in normalized]

    return angles
```

---

## 🛠️ ШАБЛОН DUAL-VERSION МОДУЛЯ

### Структура файлов:

```
src/quantum_ml/
├── __init__.py                        # Conditional imports
├── quantum_ml_services.py             # Pure Python (NEW)
├── quantum_ml_services_numpy.py       # NumPy (RENAME from old)
└── README_DUAL_VERSION.md             # Documentation
```

### Шаблон __init__.py:

```python
"""
Quantum Machine Learning Platform v15.0

Dual-version implementation:
- Pure Python: Works everywhere, no dependencies
- NumPy: 50-100x faster, requires numpy

Example usage (automatic selection):
    from quantum_ml import QuantumMLSystem, HAS_NUMPY

    qml = QuantumMLSystem(config)  # Auto-selects best version
    print(f"Using NumPy: {HAS_NUMPY}")

Example usage (explicit version):
    from quantum_ml import HAS_NUMPY

    if HAS_NUMPY:
        from quantum_ml import QuantumMLSystemNumpy
        qml = QuantumMLSystemNumpy(config)
    else:
        from quantum_ml import QuantumMLSystemPython
        qml = QuantumMLSystemPython(config)
"""

__version__ = "15.0.0"

# ALWAYS import Pure Python version (default, always available)
from .quantum_ml_services import (
    QuantumMLSystem as QuantumMLSystemPython,
    QuantumCircuitConfig,
    FeatureEncoding,
    EntanglementPattern,
    QuantumKernel,
    # ... all other exports
)

# TRY to import NumPy version (optional, 50-100x faster)
try:
    from .quantum_ml_services_numpy import (
        QuantumMLSystem as QuantumMLSystemNumpy,
        # Same exports as Pure Python
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Export intelligent default: NumPy if available, otherwise Pure Python
if HAS_NUMPY:
    QuantumMLSystem = QuantumMLSystemNumpy  # Use fast version
else:
    QuantumMLSystem = QuantumMLSystemPython  # Fallback to pure Python

__all__ = [
    "__version__",
    # Default (auto-selected)
    "QuantumMLSystem",
    # Pure Python (always available)
    "QuantumMLSystemPython",
    # Data structures (same for both)
    "QuantumCircuitConfig",
    "FeatureEncoding",
    # ... all other exports
    # Version flag
    "HAS_NUMPY",
]

# Add NumPy version to exports if available
if HAS_NUMPY:
    __all__.append("QuantumMLSystemNumpy")
```

---

## 📝 ПЛАН РЕАЛИЗАЦИИ

### Шаг 1: Подготовка (5 минут)

```bash
cd src/quantum_ml

# Переименовать существующий NumPy файл
mv quantum_ml_services.py quantum_ml_services_numpy.py

# Добавить заголовок в NumPy версию
# (указать что это NumPy-accelerated версия)
```

### Шаг 2: Создание Pure Python версии (4-6 часов)

```bash
# Скопировать структуру
cp quantum_ml_services_numpy.py quantum_ml_services.py

# Редактировать quantum_ml_services.py:
# 1. Удалить импорт numpy
# 2. Заменить все numpy операции на pure Python
# 3. Обновить docstrings (указать "Pure Python implementation")
```

### Шаг 3: Обновление __init__.py (15 минут)

- Добавить conditional imports
- Создать умный алиас
- Обновить __all__

### Шаг 4: Тестирование (1 час)

```python
# Test 1: Pure Python works without numpy
import sys
# Block numpy
sys.modules['numpy'] = None

from quantum_ml import QuantumMLSystem, HAS_NUMPY
assert not HAS_NUMPY
qml = QuantumMLSystem(config)
# ... run tests

# Test 2: NumPy version works with numpy
# (restart Python)
from quantum_ml import QuantumMLSystem, HAS_NUMPY
assert HAS_NUMPY
qml = QuantumMLSystem(config)
# ... run tests

# Test 3: Same results
# Compare Pure Python vs NumPy outputs
# Should be identical (within floating point precision)
```

### Шаг 5: Документация (30 минут)

Создать README_DUAL_VERSION.md с:
- Описанием обеих версий
- Примерами использования
- Benchmark производительности
- Рекомендациями когда использовать какую версию

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ

| Модуль | Строк | Сложность | Время | Приоритет |
|--------|-------|-----------|-------|-----------|
| quantum_ml | 1,248 | Высокая | 4-6 ч | ⭐⭐⭐⭐⭐ |
| neurosymbolic | 1,459 | Средняя | 3-5 ч | ⭐⭐⭐⭐ |
| explainable | 1,535 | Высокая | 4-6 ч | ⭐⭐⭐⭐ |
| bci | 1,562 | Очень высокая | 6-8 ч | ⭐⭐⭐⭐⭐ |
| ai_safety | 2,183 | Высокая | 6-8 ч | ⭐⭐⭐⭐ |

**Итого**: ~23-33 часа для всех TOP 5

---

## 🔍 ЧАСТЫЕ ОШИБКИ

### 1. Забыть про type hints

❌ Неправильно:
```python
def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))
```

✅ Правильно:
```python
def dot_product(v1: List[float], v2: List[float]) -> float:
    """Dot product: v1 · v2"""
    return sum(a * b for a, b in zip(v1, v2))
```

### 2. Не проверять размеры

❌ Неправильно:
```python
result = [a + b for a, b in zip(v1, v2)]  # Молча обрежет если разной длины!
```

✅ Правильно:
```python
if len(v1) != len(v2):
    raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")
result = [a + b for a, b in zip(v1, v2)]
```

### 3. Забыть про возврат типа

NumPy часто возвращает numpy scalars, Pure Python должен возвращать обычные типы:

❌ Может быть проблемой:
```python
return dot_product(v1, v2)  # Может вернуть numpy.float64
```

✅ Правильно:
```python
return float(dot_product(v1, v2))  # Явно конвертируем в float
```

---

## 📚 СПРАВОЧНЫЕ МАТЕРИАЛЫ

- **Основное руководство**: `/DUAL_VERSION_PATTERN_GUIDE.md`
- **Пример**: `/examples/dual_version_example/`
- **Референс**: `/src/continual_learning/` (EWC algorithm)
- **Анализ**: `/DUAL_VERSION_ANALYSIS.md`

---

**Готовы к реализации!** 🚀
