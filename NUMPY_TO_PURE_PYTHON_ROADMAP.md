# NumPy → Pure Python: Roadmap

**Дата**: 2026-01-20
**Статус**: Анализ завершен, готово к реализации

---

## 🎯 ЦЕЛЬ

Создать dual-version pattern (NumPy + Pure Python) для всех математических модулей DATEN20.

**Почему**:
- ✅ Maximum Performance: NumPy версия 10-100x быстрее
- ✅ Maximum Compatibility: Pure Python работает везде (zero dependencies)
- ✅ Zero Tradeoffs: 100% API compatibility

---

## 📊 ИТОГИ АНАЛИЗА

### Найдено модулей:

| Категория | Количество | Строк кода |
|-----------|-----------|------------|
| **Уже имеют dual-version** | 1 | 971 |
| **Высокий приоритет** | 5 | 7,987 |
| **Средний приоритет** | 2 | 2,500 |
| **Не подходят** | 19+ | - |

### TOP 5 Кандидатов:

1. **v15: quantum_ml** (1,248 строк) - Квантовые вычисления ⭐⭐⭐⭐⭐
2. **v4.4: bci** (1,562 строк) - DSP, обработка сигналов ⭐⭐⭐⭐⭐
3. **v13: explainable** (1,535 строк) - XAI, SHAP, LIME ⭐⭐⭐⭐
4. **v14: neurosymbolic** (1,459 строк) - Embeddings, TransE ⭐⭐⭐⭐
5. **v18: ai_safety** (2,183 строк) - Adversarial robustness ⭐⭐⭐⭐

**Общий объем работы**: ~23-33 часа для TOP 5

---

## 📚 СОЗДАННАЯ ДОКУМЕНТАЦИЯ

### 1. DUAL_VERSION_PATTERN_GUIDE.md (650+ строк)
**Что**: Полное руководство по dual-version pattern

**Содержание**:
- Что такое dual-version vs graceful degradation
- Когда использовать каждый паттерн
- Пошаговая инструкция создания dual-version модуля
- Примеры кода (Pure Python + NumPy)
- Checklist для реализации

**Для кого**: Понимание концепции

---

### 2. DUAL_VERSION_ANALYSIS.md (350+ строк)
**Что**: Детальный анализ всех модулей DATEN20

**Содержание**:
- Список всех 27 файлов с NumPy
- Классификация по приоритетам
- Детальное описание TOP 5 кандидатов
- Примеры использования NumPy в каждом модуле
- Оценка сложности и времени

**Для кого**: Планирование работы

---

### 3. DUAL_VERSION_IMPLEMENTATION_GUIDE.md (500+ строк)
**Что**: Практическое руководство по преобразованию NumPy → Pure Python

**Содержание**:
- Основные паттерны преобразования:
  - Векторные операции (dot product, norm)
  - Матричные операции (multiply, transpose)
  - Element-wise операции
  - Статистические функции
  - Random операции
  - Специальные операции (clip, argmax, etc.)
- **3 практических примера** из quantum_ml:
  - Amplitude encoding
  - Quantum kernel
  - Angle encoding
- Шаблон dual-version модуля
- План реализации по шагам
- Частые ошибки

**Для кого**: Практическая реализация

---

### 4. examples/dual_version_example/ (работающий пример)
**Что**: Полностью рабочий пример dual-version модуля

**Файлы**:
- `vector_similarity.py` - Pure Python версия
- `vector_similarity_numpy.py` - NumPy версия
- `__init__.py` - Conditional imports
- `test_dual_version.py` - Тесты API совместимости
- `README.md` - Документация

**Для кого**: Справочная реализация

---

## 🗺️ ДОРОЖНАЯ КАРТА

### Фаза 1: Высокоприоритетные модули (рекомендуемый порядок)

#### 1.1 v15: quantum_ml (4-6 часов)
**Приоритет**: ⭐⭐⭐⭐⭐ МАКСИМАЛЬНЫЙ

**Шаги**:
1. Переименовать: `quantum_ml_services.py` → `quantum_ml_services_numpy.py`
2. Создать: `quantum_ml_services.py` (Pure Python)
3. Обновить: `__init__.py` (conditional imports)
4. Тестировать: API совместимость
5. Benchmark: производительность

**Key функции для преобразования**:
- `encode_amplitude()` - нормализация векторов
- `encode_angle()` - scaling и нормализация
- `quantum_kernel()` - dot products, fidelity
- Variational circuits - матричные операции

**Ожидаемое ускорение**: 50-100x с NumPy

---

#### 1.2 v14: neurosymbolic (3-5 часов)
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

**Шаги**: Аналогично quantum_ml

**Key функции для преобразования**:
- TransE embeddings - `np.linalg.norm`, векторные операции
- Neural Module Networks - attention maps
- Knowledge Graph reasoning - векторные представления

**Ожидаемое ускорение**: 10-50x с NumPy

---

#### 1.3 v13: explainable (4-6 часов)
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

**Key функции**:
- SHAP values - численные вычисления
- LIME - `np.linalg.norm`, `np.exp`, веса
- Integrated Gradients - численное интегрирование
- Partial Dependence - `np.linspace`, интерполяция

**Ожидаемое ускорение**: 20-50x с NumPy

---

### Фаза 2: DSP и безопасность (сложные модули)

#### 2.1 v4.4: bci (6-8 часов)
**Приоритет**: ⭐⭐⭐⭐⭐ МАКСИМАЛЬНЫЙ
**Сложность**: ОЧЕНЬ ВЫСОКАЯ (DSP алгоритмы)

**Key функции**:
- IIR/FIR фильтры - рекурсивные уравнения
- FFT - придется использовать naive O(n²) или библиотеку
- Спектральный анализ - PSD, band powers
- Hjorth параметры - статистика

**Примечание**: Рассмотреть использование библиотеки `scipy` как опциональной зависимости

**Ожидаемое ускорение**: 100x с NumPy

---

#### 2.2 v18: ai_safety (6-8 часов)
**Приоритет**: ⭐⭐⭐⭐ ВЫСОКИЙ

**Key функции**:
- FGSM/PGD attacks - clipping, нормы
- Adversarial perturbations - random noise
- Robustness metrics - `np.linalg.norm`

**Ожидаемое ускорение**: 20-50x с NumPy

---

### Фаза 3: Опциональные модули

#### 3.1 v19: ai_agents (опционально)
**Приоритет**: ⭐⭐ СРЕДНИЙ

Большая часть - orchestration. NumPy используется минимально (embeddings).

**Решение**: Может быть достаточно простой замены `np.random` → `random`

---

#### 3.2 v20: human_ai_collab (опционально)
**Приоритет**: ⭐ НИЗКИЙ

Тривиальное использование NumPy (`np.mean`, `np.random.randint`).

**Решение**: Простая замена на stdlib `statistics` и `random`

---

## ⏱️ TIMELINE

### Оценка времени:

| Модуль | Время | Когда |
|--------|-------|-------|
| quantum_ml | 4-6 ч | Фаза 1.1 |
| neurosymbolic | 3-5 ч | Фаза 1.2 |
| explainable | 4-6 ч | Фаза 1.3 |
| bci | 6-8 ч | Фаза 2.1 |
| ai_safety | 6-8 ч | Фаза 2.2 |

**Фаза 1 (TOP 3)**: 11-17 часов
**Фаза 2 (DSP + Safety)**: 12-16 часов
**Итого для TOP 5**: 23-33 часа

---

## 🎯 РЕКОМЕНДАЦИИ

### Начать с:

**1. quantum_ml** - лучший кандидат для старта:
- ✅ Высокий приоритет
- ✅ Четкая математическая логика
- ✅ Средняя сложность
- ✅ Большое ускорение (50-100x)

### Использовать как референс:

**continual_learning** - образцовая реализация dual-version:
- `ewc_algorithm.py` - Pure Python (458 строк)
- `ewc_algorithm_numpy.py` - NumPy (513 строк)
- `__init__.py` - Conditional imports

### Тестирование:

Для каждого модуля обязательно:
1. ✅ Pure Python работает без numpy
2. ✅ NumPy версия работает с numpy
3. ✅ Результаты идентичны (в пределах floating point precision)
4. ✅ NumPy версия значительно быстрее (10x+)

---

## 📦 ЧТО УЖЕ ГОТОВО

### ✅ Документация (100%)
- Dual-version pattern guide
- Детальный анализ модулей
- Практическое руководство по преобразованию
- Работающий пример (vector similarity)

### ✅ Анализ (100%)
- 27 файлов с NumPy найдены
- TOP 5 кандидатов определены
- Оценка сложности и времени
- Примеры преобразований

### ⏳ Реализация (0%)
- quantum_ml - не начато
- neurosymbolic - не начато
- explainable - не начато
- bci - не начато
- ai_safety - не начато

---

## 🚀 НАЧАЛО РАБОТЫ

### Для quantum_ml (первый модуль):

```bash
cd src/quantum_ml

# 1. Backup
cp quantum_ml_services.py quantum_ml_services.backup

# 2. Rename to NumPy version
mv quantum_ml_services.py quantum_ml_services_numpy.py

# 3. Create Pure Python version
# Используй DUAL_VERSION_IMPLEMENTATION_GUIDE.md
# Следуй примерам преобразования

# 4. Update __init__.py
# Добавь conditional imports (см. шаблон в guide)

# 5. Test
python -m pytest tests/test_quantum_ml.py
```

---

## 📝 ЧЕКЛИСТ ДЛЯ КАЖДОГО МОДУЛЯ

- [ ] Backup оригинального файла
- [ ] Переименовать в *_numpy.py
- [ ] Создать Pure Python версию
- [ ] Заменить все NumPy операции (см. guide)
- [ ] Обновить docstrings ("Pure Python implementation")
- [ ] Обновить __init__.py (conditional imports)
- [ ] Создать HAS_NUMPY флаг
- [ ] Создать умный алиас
- [ ] Тесты: Pure Python без numpy ✓
- [ ] Тесты: NumPy версия с numpy ✓
- [ ] Тесты: Идентичные результаты ✓
- [ ] Benchmark: производительность
- [ ] Документация: README_DUAL_VERSION.md
- [ ] Commit & push

---

## 📚 СПРАВОЧНЫЕ МАТЕРИАЛЫ

| Документ | Для чего |
|----------|----------|
| `DUAL_VERSION_PATTERN_GUIDE.md` | Понимание концепции |
| `DUAL_VERSION_ANALYSIS.md` | Выбор модулей и планирование |
| `DUAL_VERSION_IMPLEMENTATION_GUIDE.md` | Практическая реализация |
| `examples/dual_version_example/` | Справочный код |
| `src/continual_learning/` | Образцовая реализация (EWC) |

---

## 🎓 ИТОГ

**Анализ завершен** ✅
**Документация готова** ✅
**Примеры созданы** ✅
**План утвержден** ✅

**Готово к реализации!** 🚀

**Следующий шаг**: Начать с v15: quantum_ml (4-6 часов работы)
