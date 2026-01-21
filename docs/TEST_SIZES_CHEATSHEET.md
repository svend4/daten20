# Шпаргалка по размерам тестов (Test Sizes Cheat Sheet)

## Быстрый старт

### Запуск тестов

```bash
# Быстрые тесты (перед коммитом)
./scripts/run_tests_by_size.sh small

# Средние тесты (локальная разработка)
./scripts/run_tests_by_size.sh medium

# Все тесты кроме медленных (рекомендуется)
./scripts/run_tests_by_size.sh quick

# Полный набор (перед PR)
./scripts/run_tests_by_size.sh ci
```

---

## Типы тестов по размеру

| Размер | Время | I/O | Сеть | Когда использовать |
|--------|-------|-----|------|-------------------|
| 🟢 **Small** | < 1s | ❌ Нет | ❌ Нет | Unit тесты, бизнес-логика |
| 🟡 **Medium** | < 5min | ✅ Локально | ❌ Нет | API, БД, интеграция |
| 🔴 **Large** | > 5min | ✅ Да | ✅ Да | E2E, нагрузка, workflows |

---

## Маркировка тестов

### На уровне файла (все тесты в файле)
```python
import pytest

pytestmark = pytest.mark.small

def test_something():
    pass
```

### На уровне класса
```python
@pytest.mark.medium
class TestUserAPI:
    def test_create(self):
        pass
```

### На уровне функции
```python
@pytest.mark.large
def test_full_workflow():
    pass
```

### Комбинирование маркеров
```python
@pytest.mark.small
@pytest.mark.unit
@pytest.mark.security
def test_password_validation():
    pass
```

---

## Когда какой размер использовать

### 🟢 Small Tests
```python
# ✅ Хорошо - чистая логика
@pytest.mark.small
def test_calculate_discount():
    result = calculate_discount(100, 0.2)
    assert result == 80

# ❌ Плохо - использует БД
def test_save_user():
    user = User(name="test")
    db.session.add(user)
    db.session.commit()  # I/O!
```

### 🟡 Medium Tests
```python
# ✅ Хорошо - использует тестовую БД
@pytest.mark.medium
def test_user_crud(test_db):
    user = User(name="test")
    test_db.add(user)
    test_db.commit()

    retrieved = User.query.get(user.id)
    assert retrieved.name == "test"

# ❌ Плохо - простая логика без I/O
def test_string_length():
    assert len("hello") == 5  # Это small тест!
```

### 🔴 Large Tests
```python
# ✅ Хорошо - полный E2E сценарий
@pytest.mark.large
def test_complete_checkout_flow(client):
    # 1. Регистрация
    client.post('/register', json={...})

    # 2. Вход
    token = client.post('/login', json={...})

    # 3. Добавление в корзину
    client.post('/cart/add', json={...})

    # 4. Оформление заказа
    order = client.post('/checkout', json={...})

    # 5. Оплата (может использовать внешний API)
    payment = client.post('/payment', json={...})

    assert order.status == 'completed'
```

---

## Команды для разных ситуаций

### Локальная разработка

```bash
# Перед коммитом (< 1 минуты)
./scripts/run_tests_by_size.sh small

# Перед пушем (< 10 минут)
./scripts/run_tests_by_size.sh quick

# Проверка конкретного модуля
pytest tests/unit/core/test_auth.py -m small
```

### CI/CD Pipeline

```bash
# На Pull Request
./scripts/run_tests_by_size.sh ci

# На main branch
./scripts/run_tests_by_size.sh all

# Ночные тесты
./scripts/run_tests_by_size.sh large
```

### Отладка

```bash
# Только упавшие тесты
pytest --lf -m small

# Остановка на первой ошибке
./scripts/run_tests_by_size.sh small -f

# Verbose вывод
./scripts/run_tests_by_size.sh small -v

# Показать медленные тесты
pytest -m small --durations=10
```

---

## Примеры из реальных проектов

### Small Test - Валидация пароля
```python
import pytest

pytestmark = pytest.mark.small

def test_password_strength():
    """Тест чистой логики без зависимостей"""
    from src.utils.validators import is_strong_password

    assert is_strong_password("Weak") is False
    assert is_strong_password("StrongP@ss123") is True
```

### Medium Test - API Endpoint
```python
@pytest.mark.medium
def test_create_document(client, auth_headers, test_db):
    """Тест API с базой данных"""
    response = client.post('/api/documents/',
        headers=auth_headers,
        json={'title': 'Test', 'content': 'Content'}
    )

    assert response.status_code == 201
    assert 'document_id' in response.json
```

### Large Test - E2E Workflow
```python
@pytest.mark.large
@pytest.mark.slow
def test_document_processing_pipeline(client, auth_headers):
    """Полный E2E тест с обработкой документа"""
    # Upload (может занять время)
    upload = client.post('/api/upload', files=...)
    doc_id = upload.json['id']

    # OCR Processing (медленная операция)
    client.post(f'/api/documents/{doc_id}/ocr')

    # Ждем завершения (может быть > 1 минуты)
    for _ in range(60):
        status = client.get(f'/api/documents/{doc_id}/status')
        if status.json['state'] == 'completed':
            break
        time.sleep(1)

    assert status.json['state'] == 'completed'
```

---

## Советы и best practices

### ✅ Делайте

- Пишите больше small тестов - они быстрые и надежные
- Используйте моки для внешних зависимостей в small тестах
- Группируйте тесты по размерам в отдельные файлы
- Запускайте small тесты при каждом сохранении файла
- Используйте `quick` режим для ежедневной разработки

### ❌ Не делайте

- Не помечайте slow тесты как small
- Не используйте реальную БД в small тестах
- Не делайте HTTP запросы в small/medium тестах (используйте моки)
- Не запускайте large тесты на каждый коммит
- Не игнорируйте медленные тесты - оптимизируйте или перемаркируйте

---

## Поиск и фильтрация

```bash
# Найти все small тесты
pytest --collect-only -m small

# Найти small тесты в specific директории
pytest tests/unit/ --collect-only -m small

# Комбинирование условий
pytest -m "small and security"        # Small И security
pytest -m "small or medium"           # Small ИЛИ medium
pytest -m "small and not slow"        # Small НО не slow
pytest -m "(small or medium) and api" # Комплексные условия

# Найти тесты без маркера размера
pytest --collect-only | grep -v "small\|medium\|large"
```

---

## Makefile shortcuts

Добавьте в ваш `Makefile`:

```makefile
.PHONY: test-small test-medium test-large test-quick test-all

test-small:
	@./scripts/run_tests_by_size.sh small

test-medium:
	@./scripts/run_tests_by_size.sh medium

test-large:
	@./scripts/run_tests_by_size.sh large

test-quick:
	@./scripts/run_tests_by_size.sh quick

test-all:
	@./scripts/run_tests_by_size.sh all

test: test-quick  # default
```

Использование:
```bash
make test-small   # Быстрые тесты
make test-quick   # Рекомендуемые тесты
make test         # То же что test-quick
```

---

## Интеграция с IDE

### VS Code
Добавьте в `.vscode/settings.json`:
```json
{
  "python.testing.pytestArgs": [
    "-v",
    "-m", "small or medium"
  ]
}
```

### PyCharm
1. Run → Edit Configurations
2. Python tests → pytest
3. Additional Arguments: `-m "small or medium"`

---

## Мониторинг производительности

```bash
# Показать самые медленные small тесты
pytest -m small --durations=20

# Найти small тесты, которые выполняются > 1 секунды
pytest -m small --durations=0 | grep -E "[0-9]+\.[0-9]+s" | awk '$1 > 1'

# Профилирование тестов
pytest -m small --profile

# С coverage и временем
pytest -m small --cov=src --durations=10
```

---

## Частые проблемы

### Проблема: Small тест выполняется > 1 секунды

**Решение:**
1. Проверьте на скрытые I/O операции
2. Используйте моки для медленных операций
3. Перемаркируйте как `medium`, если I/O необходим

### Проблема: Medium тест нестабилен (flaky)

**Решение:**
1. Добавьте явные ожидания (не sleep)
2. Изолируйте тестовые данные
3. Проверьте состояние БД между тестами

### Проблема: Large тесты падают на CI

**Решение:**
1. Проверьте таймауты
2. Убедитесь в доступности внешних ресурсов
3. Добавьте retry логику для нестабильных операций

---

## Полезные ссылки

- [Полное руководство](./TEST_SIZES_GUIDE.md)
- [Примеры тестов](../tests/examples/)
- [Google Test Sizes](https://testing.googleblog.com/2010/12/test-sizes.html)
- [pytest markers documentation](https://docs.pytest.org/en/stable/example/markers.html)
