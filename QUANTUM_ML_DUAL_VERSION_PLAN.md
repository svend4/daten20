# v15: quantum_ml - Dual-Version Implementation Plan

**Дата**: 2026-01-20
**Файл**: 1,248 строк
**Время**: 4-6 часов
**Статус**: В процессе

---

## 📋 СТРУКТУРА ФАЙЛА

### Текущая структура (NumPy версия):

```
quantum_ml_services.py (1,248 строк):
├── Imports (строки 1-36)
├── Enumerations (37-83)
├── Dataclasses (90-179)
├── 1. QuantumFeatureMap (186-362)
├── 2. QuantumNeuralNetwork (369-558)
├── 3. QuantumSVM (565-698)
├── 4. QuantumKMeans (705-878)
├── 5. QuantumClassifier (885-1019)
├── 6. QMLTrainer (1026-1126)
├── 7. HybridOptimizer (1133-1195)
└── 8. QuantumMLSystem (1202-1248)
```

---

## 🔧 ПЛАН ПРЕОБРАЗОВАНИЯ

### Шаг 1: Подготовка (5 минут)

✅ **Сделано**:
- Скопировали `quantum_ml_services.py` → `quantum_ml_services_numpy.py`

**Следующее**:
- Создать `quantum_ml_services.py` (Pure Python)
- Обновить `__init__.py`

---

### Шаг 2: Базовые утилиты (30 минут)

**Создать helper функции для математики**:

```python
# Pure Python math utilities
def vector_norm(v: List[float]) -> float:
    """L2 norm: ||v||"""
    return math.sqrt(sum(x * x for x in v))

def dot_product(v1: List[float], v2: List[float]) -> float:
    """Dot product: v1 · v2"""
    return sum(a * b for a, b in zip(v1, v2))

def normalize_vector(v: List[float]) -> List[float]:
    """Normalize vector to unit length"""
    norm = vector_norm(v)
    if norm == 0:
        return v
    return [x / norm for x in v]

def pad_vector(v: List[float], target_size: int) -> List[float]:
    """Pad vector with zeros"""
    if len(v) >= target_size:
        return v[:target_size]
    return v + [0.0] * (target_size - len(v))
```

---

### Шаг 3: Enums и Dataclasses (10 минут)

**Скопировать без изменений** (строки 44-83):
- FeatureEncoding
- EntanglementPattern
- QuantumKernel
- OptimizerType
- MeasurementBasis

**Обновить dataclasses** (строки 90-179):

```python
# БЫЛО (NumPy):
@dataclass
class QuantumMLResult:
    predictions: np.ndarray
    probabilities: Optional[np.ndarray] = None

# СТАЛО (Pure Python):
@dataclass
class QuantumMLResult:
    predictions: List[float]  # Change np.ndarray → List[float]
    probabilities: Optional[List[float]] = None
```

Изменить во всех dataclasses:
- `np.ndarray` → `List[float]`
- `np.ndarray` → `List[List[float]]` (для матриц)

---

### Шаг 4: QuantumFeatureMap (1 час)

**Ключевые методы**:

#### 4.1 encode_amplitude (строки 206-225)

```python
# NumPy версия:
def encode_amplitude(self, data: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(data)
    if norm > 0:
        normalized = data / norm
    else:
        normalized = data

    dim = 2 ** self.num_qubits
    if len(normalized) < dim:
        normalized = np.pad(normalized, (0, dim - len(normalized)))
    elif len(normalized) > dim:
        normalized = normalized[:dim]

    return normalized

# Pure Python версия:
def encode_amplitude(self, data: List[float]) -> List[float]:
    """Amplitude encoding - Pure Python"""
    # Normalize
    norm = math.sqrt(sum(x * x for x in data))
    if norm > 0:
        normalized = [x / norm for x in data]
    else:
        normalized = data.copy()

    # Pad to power of 2
    dim = 2 ** self.num_qubits
    if len(normalized) < dim:
        normalized = normalized + [0.0] * (dim - len(normalized))
    elif len(normalized) > dim:
        normalized = normalized[:dim]

    return normalized
```

#### 4.2 encode_angle (строки 227-240)

```python
# NumPy версия:
def encode_angle(self, data: np.ndarray) -> List[Tuple[str, int, float]]:
    angles = data[:self.num_qubits]
    gates = []
    for i, angle in enumerate(angles):
        gates.append(("ry", i, float(angle)))
    return gates

# Pure Python версия:
def encode_angle(self, data: List[float]) -> List[Tuple[str, int, float]]:
    """Angle encoding - Pure Python (NO CHANGES NEEDED!)"""
    angles = data[:self.num_qubits]
    gates = []
    for i, angle in enumerate(angles):
        gates.append(("ry", i, float(angle)))
    return gates
```

**Замечание**: Этот метод уже не зависит от NumPy!

---

### Шаг 5: QuantumNeuralNetwork (1-1.5 часа)

**Задача**: Заменить матричные операции

#### Пример: forward pass (строки ~400-450)

```python
# NumPy версия:
def forward(self, params: np.ndarray, data: np.ndarray) -> np.ndarray:
    state = self.feature_map.encode_amplitude(data)

    # Apply parameterized gates
    for layer in range(self.num_layers):
        for i in range(self.num_qubits):
            idx = layer * self.num_qubits + i
            angle = params[idx]
            # Rotation matrix
            rotation = np.array([[np.cos(angle/2), -np.sin(angle/2)],
                                 [np.sin(angle/2), np.cos(angle/2)]])
            # Apply rotation...

# Pure Python версия:
def forward(self, params: List[float], data: List[float]) -> List[float]:
    """Forward pass - Pure Python"""
    state = self.feature_map.encode_amplitude(data)

    # Apply parameterized gates
    for layer in range(self.num_layers):
        for i in range(self.num_qubits):
            idx = layer * self.num_qubits + i
            angle = params[idx]
            # Rotation (simplified for pure python)
            cos_half = math.cos(angle / 2)
            sin_half = math.sin(angle / 2)
            rotation = [[cos_half, -sin_half],
                       [sin_half, cos_half]]
            # Apply rotation using pure python matrix ops...

    return state
```

**Helper для матричного умножения**:

```python
def apply_2x2_gate(state: List[float], gate: List[List[float]], qubit_idx: int) -> List[float]:
    """Apply 2x2 gate to specific qubit (simplified)"""
    # Simplified implementation
    # Full implementation requires tensor product logic
    new_state = state.copy()
    # ... apply gate to qubit_idx
    return new_state
```

---

### Шаг 6: QuantumSVM (1 час)

**Ключевые методы**:

#### quantum_kernel (строки ~600-630)

```python
# NumPy версия:
async def quantum_kernel(self, x1: np.ndarray, x2: np.ndarray) -> float:
    state1 = self.feature_map.encode_amplitude(x1)
    state2 = self.feature_map.encode_amplitude(x2)

    # Fidelity: |<ψ₁|ψ₂>|²
    inner_product = np.abs(np.dot(np.conj(state1), state2))
    return float(inner_product ** 2)

# Pure Python версия:
async def quantum_kernel(self, x1: List[float], x2: List[float]) -> float:
    """Quantum kernel - Pure Python"""
    state1 = self.feature_map.encode_amplitude(x1)
    state2 = self.feature_map.encode_amplitude(x2)

    # Fidelity: |<ψ₁|ψ₂>|² (for real states, conj = identity)
    inner_product = abs(sum(a * b for a, b in zip(state1, state2)))
    return inner_product ** 2
```

---

### Шаг 7: QuantumKMeans (1 час)

**Ключевые методы**:

#### _compute_centroids (строки ~800-820)

```python
# NumPy версия:
def _compute_centroids(self, X: np.ndarray, labels: np.ndarray, k: int) -> np.ndarray:
    centroids = np.zeros((k, X.shape[1]))
    for i in range(k):
        cluster_points = X[labels == i]
        if len(cluster_points) > 0:
            centroids[i] = cluster_points.mean(axis=0)
    return centroids

# Pure Python версия:
def _compute_centroids(self, X: List[List[float]], labels: List[int], k: int) -> List[List[float]]:
    """Compute centroids - Pure Python"""
    n_features = len(X[0])
    centroids = [[0.0] * n_features for _ in range(k)]

    for i in range(k):
        # Find points in cluster i
        cluster_points = [X[j] for j, label in enumerate(labels) if label == i]

        if len(cluster_points) > 0:
            # Compute mean
            for f in range(n_features):
                centroids[i][f] = sum(p[f] for p in cluster_points) / len(cluster_points)

    return centroids
```

---

### Шаг 8: QuantumClassifier (30 минут)

**Обновить типы**:

```python
# БЫЛО:
async def predict(self, X: np.ndarray) -> np.ndarray:
    predictions = np.zeros(len(X))
    ...

# СТАЛО:
async def predict(self, X: List[List[float]]) -> List[int]:
    predictions = [0] * len(X)
    ...
```

---

### Шаг 9: QMLTrainer (30 минут)

**Обновить оптимизаторы**:

```python
# Simplified gradient descent (no scipy)
def _gradient_descent(self, params: List[float], grad_fn: Callable) -> List[float]:
    """Simple gradient descent - Pure Python"""
    for epoch in range(self.config.num_epochs):
        gradients = grad_fn(params)
        # Update parameters
        for i in range(len(params)):
            params[i] -= self.config.learning_rate * gradients[i]
    return params
```

---

### Шаг 10: Обновить __init__.py (15 минут)

```python
"""
Quantum Machine Learning Platform v15.0

Dual-version implementation:
- Pure Python: Works everywhere, no dependencies (slower)
- NumPy: 50-100x faster, requires numpy

Example:
    from quantum_ml import QuantumMLSystem, HAS_NUMPY
    qml = QuantumMLSystem(config)
"""

__version__ = "15.0.0"

# ALWAYS import Pure Python version
from .quantum_ml_services import (
    QuantumMLSystem as QuantumMLSystemPython,
    QuantumFeatureMap,
    FeatureEncoding,
    # ... all exports
)

# TRY to import NumPy version
try:
    from .quantum_ml_services_numpy import (
        QuantumMLSystem as QuantumMLSystemNumpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Smart alias
if HAS_NUMPY:
    QuantumMLSystem = QuantumMLSystemNumpy
else:
    QuantumMLSystem = QuantumMLSystemPython

__all__ = [
    "QuantumMLSystem",
    "QuantumMLSystemPython",
    "HAS_NUMPY",
    # ... all other exports
]

if HAS_NUMPY:
    __all__.append("QuantumMLSystemNumpy")
```

---

## ⏱️ TIMELINE

| Шаг | Задача | Время |
|-----|--------|-------|
| 1 | Подготовка | 5 мин |
| 2 | Базовые утилиты | 30 мин |
| 3 | Enums/Dataclasses | 10 мин |
| 4 | QuantumFeatureMap | 1 ч |
| 5 | QuantumNeuralNetwork | 1-1.5 ч |
| 6 | QuantumSVM | 1 ч |
| 7 | QuantumKMeans | 1 ч |
| 8 | QuantumClassifier | 30 мин |
| 9 | QMLTrainer | 30 мин |
| 10 | __init__.py | 15 мин |

**Итого**: ~4-6 часов

---

## 🔨 ПРАКТИЧЕСКАЯ СТРАТЕГИЯ

### Вариант A: Полная реализация (4-6 часов)

Создать полную Pure Python версию всех 1,248 строк.

### Вариант B: Инкрементальная реализация (рекомендуется)

1. **Фаза 1** (1 час): Создать базовую версию с QuantumFeatureMap
2. **Фаза 2** (2 часа): Добавить QNN и QSVM
3. **Фаза 3** (1-2 часа): Добавить остальные компоненты
4. **Фаза 4** (30 мин): Тестирование и оптимизация

### Вариант C: Starter версия (30 минут)

Создать минимальную работающую версию:
- Базовые утилиты
- QuantumFeatureMap (только основные методы)
- Заглушки для остальных классов
- Пометить что "работа в процессе"

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

**Сейчас**: Создать starter версию (Вариант C)
**Потом**: Расширить до полной реализации (Вариант B, фазами)

**Готово к началу работы!** 🚀
