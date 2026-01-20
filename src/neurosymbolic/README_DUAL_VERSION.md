# v14: neurosymbolic - Dual-Version Status

**Дата**: 2026-01-20
**Файл**: 1,459 строк
**Время**: 3-5 часов
**Статус**: ПОДГОТОВЛЕНО

---

## 📊 СТАТУС

### ✅ Завершено:

- [x] Backup NumPy версии (`neurosymbolic_services_numpy.py`)
- [x] Анализ использования NumPy

### ⏳ В работе:

- [ ] Pure Python версия (`neurosymbolic_services.py`)
- [ ] Обновление `__init__.py`
- [ ] Тестирование

---

## 📂 СТРУКТУРА

```
src/neurosymbolic/
├── __init__.py                         # TODO: Обновить для dual-version
├── neurosymbolic_services.py           # TODO: Создать Pure Python версию
├── neurosymbolic_services_numpy.py     # ✅ NumPy версия (backup)
└── README_DUAL_VERSION.md              # ✅ Эта документация
```

---

## 🔍 АНАЛИЗ ИСПОЛЬЗОВАНИЯ NUMPY

### Ключевые компоненты (1,459 строк):

1. **LogicTensorNetwork** - Fuzzy logic, T-norms
2. **NeuralModuleNetwork** - Attention maps, composition
3. **KnowledgeGraphEmbeddings** - TransE, ComplEx, RotatE
4. **ProgramSynthesis** - Neural-guided search
5. **DifferentiableReasoning** - Gradient-based logic

### Примеры использования NumPy:

#### 1. Knowledge Graph Embeddings (TransE)

```python
# NumPy версия:
h = self.entity_embeddings.get(head, np.zeros(self.embedding_dim))
r = self.relation_embeddings.get(relation, np.zeros(self.embedding_dim))
t = self.entity_embeddings.get(tail, np.zeros(self.embedding_dim))
distance = np.linalg.norm(h + r - t)

# Pure Python:
h = self.entity_embeddings.get(head, [0.0] * self.embedding_dim)
r = self.relation_embeddings.get(relation, [0.0] * self.embedding_dim)
t = self.entity_embeddings.get(tail, [0.0] * self.embedding_dim)
# h + r - t
diff = [h[i] + r[i] - t[i] for i in range(len(h))]
distance = math.sqrt(sum(x * x for x in diff))
```

#### 2. Neural Module Network (Attention)

```python
# NumPy версия:
attention_map = np.random.rand(14, 14)
attention_weights = np.ones(num_objects) / num_objects
result = np.sum(features * attention_weights[:, None], axis=0)

# Pure Python:
attention_map = [[random.random() for _ in range(14)] for _ in range(14)]
attention_weights = [1.0 / num_objects] * num_objects
result = [sum(features[i][j] * attention_weights[i] for i in range(len(features)))
          for j in range(len(features[0]))]
```

#### 3. Fuzzy Logic (T-norms)

```python
# NumPy версия:
def product_tnorm(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return x * y

# Pure Python:
def product_tnorm(self, x: List[float], y: List[float]) -> List[float]:
    return [a * b for a, b in zip(x, y)]
```

---

## 🎯 ПЛАН РЕАЛИЗАЦИИ

### Оценка: 3-5 часов (средняя сложность)

### Шаг 1: Базовые утилиты (30 мин)

```python
# Vector operations
def vector_add(v1: List[float], v2: List[float]) -> List[float]:
    return [a + b for a, b in zip(v1, v2)]

def vector_subtract(v1: List[float], v2: List[float]) -> List[float]:
    return [a - b for a, b in zip(v1, v2)]

def vector_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))

def dot_product(v1: List[float], v2: List[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))
```

### Шаг 2: LogicTensorNetwork (45 мин)

Заменить:
- Fuzzy logic operations (T-norms)
- Satisfaction degree computations
- Grounding functions

### Шаг 3: KnowledgeGraphEmbeddings (1 час)

Ключевые методы:
- `_train_transe()` - TransE embeddings
- `_train_complex()` - ComplEx embeddings
- `query()` - Link prediction

### Шаг 4: NeuralModuleNetwork (1 час)

Заменить:
- Attention maps
- Module composition
- Feature aggregation

### Шаг 5: Остальные компоненты (45 мин)

- ProgramSynthesis
- DifferentiableReasoning
- SemanticParser

### Шаг 6: Обновить __init__.py (15 мин)

Добавить conditional imports.

---

## 💻 КЛЮЧЕВЫЕ ПРЕОБРАЗОВАНИЯ

### 1. Embeddings

```python
# БЫЛО (NumPy):
embedding = np.zeros(dim)
embedding = np.random.randn(dim)

# СТАЛО (Pure Python):
embedding = [0.0] * dim
embedding = [random.gauss(0, 1) for _ in range(dim)]
```

### 2. Vector operations

```python
# БЫЛО:
result = vec1 + vec2  # NumPy element-wise
distance = np.linalg.norm(vec)

# СТАЛО:
result = [a + b for a, b in zip(vec1, vec2)]
distance = math.sqrt(sum(x * x for x in vec))
```

### 3. Random operations

```python
# БЫЛО:
matrix = np.random.rand(n, m)
indices = np.random.randint(0, max_val, size=k)

# СТАЛО:
matrix = [[random.random() for _ in range(m)] for _ in range(n)]
indices = [random.randint(0, max_val-1) for _ in range(k)]
```

---

## 📚 СПРАВОЧНЫЕ МАТЕРИАЛЫ

- **Общий анализ**: `/DUAL_VERSION_ANALYSIS.md`
- **Паттерны преобразования**: `/DUAL_VERSION_IMPLEMENTATION_GUIDE.md`
- **Roadmap**: `/NUMPY_TO_PURE_PYTHON_ROADMAP.md`
- **Summary**: `/DUAL_VERSION_SUMMARY.md`
- **Образец**: `/src/continual_learning/` (EWC dual-version)

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. Создать `neurosymbolic_services.py` (Pure Python)
2. Следовать плану выше (3-5 часов)
3. Обновить `__init__.py`
4. Тестировать dual-version

**Готово к реализации!** 🚀

---

**Создано**: 2026-01-20
**Приоритет**: ⭐⭐⭐⭐ (2nd in TOP 5)
