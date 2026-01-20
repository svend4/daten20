# Dual-Version Pattern Example: Vector Similarity

**Практический пример паттерна "Две версии"** (NumPy + Pure Python)

Этот пример демонстрирует, как правильно создать модуль с двумя версиями:
- **Pure Python версия**: Работает везде, stdlib only
- **NumPy версия**: 10-100x быстрее, требует numpy

---

## 📁 Структура

```
dual_version_example/
├── __init__.py                     # Умный импорт (auto-select version)
├── vector_similarity.py            # Pure Python версия
├── vector_similarity_numpy.py      # NumPy версия
├── test_dual_version.py            # Тесты (проверка совместимости)
└── README.md                       # Эта документация
```

---

## 🚀 Использование

### Вариант 1: Автоматический выбор (рекомендуется)

```python
from dual_version_example import VectorSimilarity, HAS_NUMPY

# VectorSimilarity автоматически выберет NumPy если доступен
calc = VectorSimilarity()

# Вычисляем сходство
v1 = [1.0, 2.0, 3.0, 4.0, 5.0]
v2 = [2.0, 4.0, 6.0, 8.0, 10.0]

result = calc.compute_similarity(v1, v2)

print(f"Using NumPy: {HAS_NUMPY}")
print(f"Cosine similarity: {result.cosine_similarity:.4f}")
print(f"Euclidean distance: {result.euclidean_distance:.4f}")
```

### Вариант 2: Явный выбор версии

```python
from dual_version_example import HAS_NUMPY

if HAS_NUMPY:
    print("Using NumPy version (10-100x faster)")
    from dual_version_example import VectorSimilarityNumpy
    calc = VectorSimilarityNumpy()
else:
    print("Using pure Python version")
    from dual_version_example import VectorSimilarityPython
    calc = VectorSimilarityPython()

# API одинаковый для обеих версий!
result = calc.compute_similarity([1, 2, 3], [4, 5, 6])
```

### Вариант 3: Принудительно Pure Python

```python
# Всегда используем pure Python (даже если numpy доступен)
from dual_version_example import VectorSimilarityPython

calc = VectorSimilarityPython()
result = calc.compute_similarity([1, 2, 3], [4, 5, 6])
```

---

## 🎯 API Reference

Обе версии имеют **идентичный API**:

### `VectorSimilarity` / `VectorSimilarityNumpy`

#### Методы:

**`dot_product(v1, v2) -> float`**
```python
# Скалярное произведение
dot = calc.dot_product([1, 2, 3], [4, 5, 6])
# Returns: 32.0
```

**`norm(v) -> float`**
```python
# L2 норма (длина вектора)
length = calc.norm([3, 4])
# Returns: 5.0
```

**`cosine_similarity(v1, v2) -> float`**
```python
# Косинусное сходство [-1, 1]
sim = calc.cosine_similarity([1, 2, 3], [2, 4, 6])
# Returns: 1.0 (одно направление)
```

**`euclidean_distance(v1, v2) -> float`**
```python
# Евклидово расстояние
dist = calc.euclidean_distance([1, 2], [4, 6])
# Returns: 5.0
```

**`compute_similarity(v1, v2) -> SimilarityResult`**
```python
# Все метрики сразу
result = calc.compute_similarity([1, 2, 3], [4, 5, 6])
print(result.cosine_similarity)    # 0.9746
print(result.euclidean_distance)   # 5.1962
print(result.vector1_norm)         # 3.7417
print(result.vector2_norm)         # 8.7750
```

**`find_most_similar(query, vectors) -> (int, float)`**
```python
# Найти наиболее похожий вектор
query = [1.0, 2.0, 3.0]
candidates = [
    [1.0, 2.0, 3.0],   # Идентичный
    [2.0, 4.0, 6.0],   # Похожий
    [3.0, 2.0, 1.0],   # Другой
]

idx, similarity = calc.find_most_similar(query, candidates)
# Returns: (0, 1.0) - первый вектор идентичен
```

---

## ⚡ Производительность

### Benchmark: Pure Python vs NumPy

Тест: 1000 векторов, 100 измерений, найти наиболее похожий

```
Pure Python версия:
  - Время: ~500 ms
  - Реализация: циклы for, list comprehensions

NumPy версия:
  - Время: ~5 ms
  - Реализация: векторизация, batch processing
  - Ускорение: 100x быстрее! 🚀
```

### Когда использовать какую версию?

| Размер данных | Pure Python | NumPy |
|---------------|-------------|-------|
| < 10 векторов, < 10 измерений | ✅ Достаточно | ⚡ Overkill |
| 10-100 векторов | ✅ OK | ⚡ Рекомендуется |
| 100-1000 векторов | ⚠️ Медленно | ⚡ **Обязательно** |
| > 1000 векторов | ❌ Слишком медленно | ⚡ **Обязательно** |

---

## 🔍 Внутренняя реализация

### Pure Python: Циклы и list comprehensions

```python
def dot_product(self, v1: List[float], v2: List[float]) -> float:
    # List comprehension + sum()
    return sum(x * y for x, y in zip(v1, v2))

def find_most_similar(self, query, vectors):
    # Цикл for для каждого вектора
    for i, vec in enumerate(vectors):
        similarity = self.cosine_similarity(query, vec)
        if similarity > best_similarity:
            best_similarity = similarity
            best_idx = i
    return best_idx, best_similarity
```

### NumPy: Векторизация и batch processing

```python
def dot_product(self, v1: List[float], v2: List[float]) -> float:
    # Векторизованное скалярное произведение
    arr1 = np.array(v1)
    arr2 = np.array(v2)
    return float(np.dot(arr1, arr2))

def find_most_similar(self, query, vectors):
    # BATCH обработка всех векторов сразу!
    query_arr = np.array(query)
    vectors_arr = np.array(vectors)  # (num_vectors, dim)

    # Матричное умножение для всех сходств сразу
    dots = vectors_arr @ query_arr   # Все dot products сразу!
    query_norm = np.linalg.norm(query_arr)
    vectors_norms = np.linalg.norm(vectors_arr, axis=1)

    # Все косинусные сходства сразу!
    similarities = dots / (vectors_norms * query_norm)

    # Найти максимум
    best_idx = int(np.argmax(similarities))
    return best_idx, float(similarities[best_idx])
```

**Почему NumPy быстрее?**
- ✅ Векторизация (операции над массивами вместо циклов)
- ✅ Batch processing (все векторы обрабатываются сразу)
- ✅ Оптимизированная линейная алгебра (BLAS/LAPACK)
- ✅ C-level реализация (не интерпретация Python)

---

## 🧪 Тестирование

Запустите тесты чтобы убедиться что обе версии работают идентично:

```bash
# Тест pure Python версии (не требует numpy)
python examples/dual_version_example/vector_similarity.py

# Тест NumPy версии (требует numpy)
python examples/dual_version_example/vector_similarity_numpy.py

# Тест совместимости API (требует numpy)
python examples/dual_version_example/test_dual_version.py
```

---

## 📚 Что дальше?

1. **Изучите код**: Откройте `vector_similarity.py` и `vector_similarity_numpy.py`
2. **Сравните реализации**: Обратите внимание на различия (списки vs np.array)
3. **Запустите бенчмарк**: Увидите реальную разницу в производительности
4. **Примените паттерн**: Используйте для своих модулей с математикой

### Рекомендуемые модули для dual-version pattern:

- ✅ `neurosymbolic` (v14): логика, операции над множествами
- ✅ `quantum_ml` (v15): квантовые состояния, линейная алгебра
- ✅ Любой модуль с векторами, матрицами, статистикой

---

## 🎓 См. также

- **Полная документация**: `/DUAL_VERSION_PATTERN_GUIDE.md`
- **Референсная реализация**: `/src/continual_learning/` (EWC algorithm)
- **Graceful degradation**: `/BASIC_AI_PIPELINE_README.md`

---

**Dual-Version Pattern = Maximum Performance + Maximum Compatibility** 🚀
