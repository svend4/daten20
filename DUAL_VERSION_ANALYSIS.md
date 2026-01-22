# Dual-Version Pattern: Анализ модулей DATEN20

**Дата**: 2026-01-20
**Ветка**: `claude/update-dev-status-hdrB8`

---

## 📊 Обзор

Проведен полный анализ всех модулей DATEN20 для определения кандидатов на dual-version pattern (NumPy + Pure Python).

**Найдено**:
- **27 файлов** используют NumPy
- **1 модуль** уже имеет dual-version (continual_learning)
- **5 модулей** - высокий приоритет для dual-version
- **~8,000 строк** кода требуют создания Pure Python версий

---

## ✅ УЖЕ ИМЕЮТ DUAL-VERSION

### v21: continual_learning (21.0.0)

**Статус**: ✅ ОБРАЗЦОВАЯ РЕАЛИЗАЦИЯ

**Файлы**:
- `ewc_algorithm.py` - Pure Python (458 строк)
- `ewc_algorithm_numpy.py` - NumPy (513 строк)
- `__init__.py` - Conditional imports с HAS_NUMPY

**Производительность**: 100x ускорение с NumPy

**Использовать как reference** для всех новых dual-version модулей!

---

## 🔥 TOP 5 КАНДИДАТОВ (высокий приоритет)

### 1. v15: quantum_ml (15.0.0) ⭐⭐⭐⭐⭐

**Размер**: 1,248 строк
**Тип**: Квантовые вычисления
**Статус**: Только NumPy → Нужна Pure Python версия

**Использование NumPy**:
- Квантовые операции: `np.linalg.norm`, amplitude encoding
- Матричные операции для параметризованных схем
- Kernel методы: фиделити, проекции
- Feature encoding: amplitude, angle, IQP, Pauli

**Примеры кода**:
```python
def encode_amplitude(self, data: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(data)
    normalized = data / norm if norm > 0 else data

async def quantum_kernel(self, x1: np.ndarray, x2: np.ndarray) -> float:
    # Fidelity calculation using np.dot, np.conj
```

**Оценка сложности**: ВЫСОКАЯ
**Оценка ускорения**: 50-100x с NumPy
**Приоритет**: ⭐⭐⭐⭐⭐ МАКСИМАЛЬНЫЙ

---

### 2. v4.4: bci (Brain-Computer Interface) ⭐⭐⭐⭐⭐

**Размер**: 1,562 строк
**Тип**: Обработка сигналов (DSP)
**Статус**: Только NumPy → Нужна Pure Python версия

**Использование NumPy**:
- Цифровая фильтрация: IIR, FIR, bandpass, notch filters
- FFT, спектральный анализ, PSD
- Hjorth параметры
- Band powers: delta, theta, alpha, beta, gamma
- Artifact rejection, CAR

**Примеры кода**:
```python
def _apply_iir(self, x: np.ndarray, b: List[float], a: List[float]) -> np.ndarray:
    y = np.zeros_like(x)
    for n in range(len(x)):
        y[n] = b[0] * x[n] + b[1] * x[n-1] - a[1] * y[n-1]

def apply_car(self, signal: np.ndarray) -> np.ndarray:
    avg = np.mean(signal, axis=0)
    return signal - avg
```

**Дополнительные файлы**:
- `bci_services.py` (основная логика)
- `signal_processing.py` (математические функции)

**Оценка сложности**: ОЧЕНЬ ВЫСОКАЯ (DSP алгоритмы)
**Оценка ускорения**: 100x с NumPy
**Приоритет**: ⭐⭐⭐⭐⭐ МАКСИМАЛЬНЫЙ

---

### 3. v13: explainable (XAI) ⭐⭐⭐⭐

**Размер**: 1,535 строк
**Тип**: Explainable AI (XAI)
**Статус**: Только NumPy → Нужна Pure Python версия

**Использование NumPy**:
- SHAP values calculation
- LIME: `np.linalg.norm`, `np.exp` для весов
- Градиенты: Integrated Gradients, GradCAM
- Permutation importance
- Partial dependence: `np.linspace`, `np.sin`

**Примеры кода**:
```python
async def explain_lime(self, model_id: str, instance: np.ndarray, num_samples: int):
    noise = np.random.randn(*instance.shape) * 0.1
    distance = np.linalg.norm(noise)
    weight = np.exp(-(distance**2) / 1.0)

async def partial_dependence(self, model_id: str, feature_index: int, X: np.ndarray):
    grid_values = np.linspace(X[:, feature_index].min(),
                              X[:, feature_index].max(),
                              grid_resolution)
```

**Оценка сложности**: ВЫСОКАЯ
**Оценка ускорения**: 20-50x с NumPy
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

---

### 4. v14: neurosymbolic (14.0.0) ⭐⭐⭐⭐

**Размер**: 1,459 строк
**Тип**: Нейросимволический AI
**Статус**: Только NumPy → Нужна Pure Python версия

**Использование NumPy**:
- Knowledge Graph Embeddings: TransE, ComplEx
- Differentiable reasoning: `np.linalg.norm`
- Neural Module Networks: attention maps
- Logic Tensor Networks: векторные представления

**Примеры кода**:
```python
# TransE embedding
h = self.entity_embeddings.get(head, np.zeros(self.embedding_dim))
r = self.relation_embeddings.get(relation, np.zeros(self.embedding_dim))
t = self.entity_embeddings.get(tail, np.zeros(self.embedding_dim))
distance = np.linalg.norm(h + r - t)

async def _find_module(self, features: np.ndarray, params: Dict) -> np.ndarray:
    return np.random.rand(14, 14)  # attention map
```

**Оценка сложности**: СРЕДНЯЯ
**Оценка ускорения**: 10-50x с NumPy
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

---

### 5. v18: ai_safety (18.0.0) ⭐⭐⭐⭐

**Размер**: 2,183 строк
**Тип**: AI Safety & Adversarial Robustness
**Статус**: Только NumPy → Нужна Pure Python версия

**Использование NumPy**:
- Adversarial attacks: FGSM, PGD, C&W
- Perturbation generation: `np.random.uniform`, `np.clip`
- Robustness metrics: `np.linalg.norm`
- Differential privacy: noise injection

**Примеры кода**:
```python
async def generate_adversarial_example(self, input_data: np.ndarray, epsilon: float):
    if attack_type == AttackType.FGSM:
        perturbation = np.random.uniform(-epsilon, epsilon, input_data.shape)
    elif attack_type == AttackType.PGD:
        perturbation = np.clip(perturbation, -epsilon, epsilon)

    adversarial_input = np.clip(adversarial_input, 0.0, 1.0)
    perturbation_norm = float(np.linalg.norm(perturbation))
```

**Оценка сложности**: ВЫСОКАЯ
**Оценка ускорения**: 20-50x с NumPy
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

---

## ⚡ СРЕДНИЙ ПРИОРИТЕТ

### v19: ai_agents (19.0.0) ⭐⭐

**Размер**: ~1,500 строк
**Статус**: Только NumPy, но в основном orchestration

**Использование NumPy**: Embeddings и простые операции
- Memory embeddings: `np.random.randn`, `np.linalg.norm`
- Similarity: dot products
- Random sampling

**Приоритет**: ⭐⭐ СРЕДНИЙ (большая часть кода - orchestration)

---

### v20: human_ai_collab (20.0.0) ⭐

**Размер**: ~1,000 строк
**Статус**: Только NumPy, но минимальное использование

**Использование NumPy**: Очень легкое
- `np.random.randint` для decomposition
- `np.mean` для метрик
- `np.random.random` для симуляций

**Приоритет**: ⭐ НИЗКИЙ (можно заменить на random/statistics)

---

## ❌ НЕ ПОДХОДЯТ ДЛЯ DUAL-VERSION

### Модули без NumPy:
- v16: edge_ai
- v17: multimodal_ai
- v22-v30: world_models, self_improving, emergent, и т.д.

### Модули с тривиальным использованием NumPy:
- v6: consciousness (только `np.eye`, `np.mean`)
- v7: emotions (только `np.mean`, `np.log1p`)

---

## 📊 СТАТИСТИКА

### Общая картина:

| Категория | Количество модулей | Строк кода |
|-----------|-------------------|-----------|
| **Уже dual-version** | 1 (continual_learning) | ~971 |
| **Высокий приоритет** | 5 модулей | ~7,987 |
| **Средний приоритет** | 2 модуля | ~2,500 |
| **Низкий/не подходят** | 19+ модулей | - |

### TOP 5: Оценка работы

| Модуль | Строк | Сложность | Время | Приоритет |
|--------|-------|-----------|-------|-----------|
| quantum_ml | 1,248 | Высокая | ~4-6 ч | ⭐⭐⭐⭐⭐ |
| bci | 1,562 | Очень высокая | ~6-8 ч | ⭐⭐⭐⭐⭐ |
| explainable | 1,535 | Высокая | ~4-6 ч | ⭐⭐⭐⭐ |
| neurosymbolic | 1,459 | Средняя | ~3-5 ч | ⭐⭐⭐⭐ |
| ai_safety | 2,183 | Высокая | ~6-8 ч | ⭐⭐⭐⭐ |

**Итого**: ~23-33 часа работы для TOP 5

---

## 🎯 РЕКОМЕНДУЕМЫЙ ПЛАН ДЕЙСТВИЙ

### Фаза 1: Высокоприоритетные модули (в порядке)

1. **v15: quantum_ml**
   - Причина: математически интенсивный, четкая логика
   - Файлы: `quantum_ml_services.py` → `quantum_ml_services_numpy.py` + `quantum_ml_algorithm.py`

2. **v14: neurosymbolic**
   - Причина: средняя сложность, хорошее ускорение
   - Файлы: `neurosymbolic_services.py` → dual-version

3. **v13: explainable**
   - Причина: XAI важен, много численных методов
   - Файлы: `explainable_services.py` → dual-version

### Фаза 2: DSP и безопасность

4. **v4.4: bci**
   - Причина: DSP критичен для производительности
   - Файлы: `bci_services.py` + `signal_processing.py` → dual-version

5. **v18: ai_safety**
   - Причина: adversarial attacks требуют скорости
   - Файлы: `ai_safety_services.py` → dual-version

### Фаза 3: Остальные (опционально)

6. **v19: ai_agents** - если нужно
7. **v20: human_ai_collab** - низкий приоритет

---

## 🔨 ПЛАН РЕАЛИЗАЦИИ (на примере quantum_ml)

### Структура файлов:

```
src/quantum_ml/
├── __init__.py                          # Обновить: conditional imports
├── quantum_ml_services.py               # Переименовать → quantum_ml_services_numpy.py
├── quantum_ml_algorithm.py              # СОЗДАТЬ: Pure Python версия
└── README_DUAL_VERSION.md               # СОЗДАТЬ: Документация
```

### Шаги:

1. **Переименовать существующий файл**:
   ```bash
   mv quantum_ml_services.py quantum_ml_services_numpy.py
   ```

2. **Создать Pure Python версию**:
   - Скопировать структуру из quantum_ml_services_numpy.py
   - Заменить NumPy операции на Pure Python:
     - `np.array` → `list`
     - `np.linalg.norm` → `math.sqrt(sum(x**2 for x in vector))`
     - `np.dot` → `sum(a*b for a,b in zip(v1, v2))`
     - `np.zeros` → `[0.0] * size`

3. **Обновить __init__.py**:
   ```python
   # Pure Python (always available)
   from .quantum_ml_algorithm import QuantumMLSystem as QuantumMLPython

   # NumPy version (optional)
   try:
       from .quantum_ml_services_numpy import QuantumMLSystem as QuantumMLNumpy
       HAS_NUMPY = True
   except ImportError:
       HAS_NUMPY = False

   # Smart alias
   if HAS_NUMPY:
       QuantumMLSystem = QuantumMLNumpy
   else:
       QuantumMLSystem = QuantumMLPython
   ```

4. **Тестирование**:
   - Проверить Pure Python версия работает без numpy
   - Проверить NumPy версия работает с numpy
   - Сравнить результаты (должны быть идентичны)
   - Замерить производительность

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

1. ✅ Анализ завершен
2. ⏳ Начать с quantum_ml (v15)
3. ⏳ Создать Pure Python версию
4. ⏳ Обновить __init__.py
5. ⏳ Тестирование
6. ⏳ Повторить для остальных TOP 5

---

## 📚 СПРАВОЧНЫЕ МАТЕРИАЛЫ

- **Руководство**: `/DUAL_VERSION_PATTERN_GUIDE.md`
- **Пример**: `/examples/dual_version_example/`
- **Референс**: `/src/continual_learning/` (EWC dual-version)

---

**Статус**: Анализ завершен, готовы к реализации ✅
