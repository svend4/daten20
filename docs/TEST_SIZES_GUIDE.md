# Руководство по организации тестов по размерам

## Обзор

Этот документ описывает систему организации тестов по размерам (Test Sizes) в проекте Daten20, основанную на стандарте Google Test Sizes.

## Категории размеров тестов

### 🟢 Small Tests (Малые тесты)

**Характеристики:**
- ⏱️ Время выполнения: < 1 секунда
- 🚫 Без I/O операций (файлы, база данных, сеть)
- 🔒 Без внешних зависимостей
- ✅ Детерминированные (всегда одинаковый результат)
- 🎯 Тестируют одну единицу кода (функцию, метод, класс)

**Когда использовать:**
- Unit тесты для чистых функций
- Тесты бизнес-логики
- Тесты утилит и хелперов
- Тесты валидаторов
- Тесты парсеров (с моками для I/O)

**Пример:**
```python
import pytest

@pytest.mark.small
@pytest.mark.unit
def test_password_validation():
    """Test password validation logic"""
    from src.utils.validators import validate_password

    # Valid password
    assert validate_password("StrongP@ss123") is True

    # Too short
    assert validate_password("weak") is False

    # No special characters
    assert validate_password("WeakPassword123") is False
```

---

### 🟡 Medium Tests (Средние тесты)

**Характеристики:**
- ⏱️ Время выполнения: < 5 минут
- 💾 Могут использовать локальные ресурсы (файлы, локальная БД)
- 🔌 Без реальных внешних API/сервисов
- 🔄 Могут использовать моки для внешних зависимостей
- 🧩 Тестируют взаимодействие между компонентами

**Когда использовать:**
- Integration тесты
- Тесты API endpoints
- Тесты с базой данных (тестовая БД)
- Тесты с файловой системой
- Тесты сервисного слоя

**Пример:**
```python
import pytest

@pytest.mark.medium
@pytest.mark.integration
def test_user_registration_flow(test_db, client):
    """Test complete user registration flow"""
    # Test database interaction and API endpoint
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'StrongP@ss123'
    })

    assert response.status_code == 201
    assert 'user_id' in response.json

    # Verify database state
    from src.models import User
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
```

---

### 🔴 Large Tests (Расширенные тесты)

**Характеристики:**
- ⏱️ Время выполнения: без ограничений (обычно > 5 минут)
- 🌐 Могут использовать реальные внешние сервисы
- 🔗 Полная end-to-end интеграция
- 📊 Могут быть недетерминированными
- 🎭 Тестируют полные пользовательские сценарии

**Когда использовать:**
- E2E тесты
- Тесты полных workflows
- Performance тесты
- Load тесты
- Smoke тесты продакшн-окружения

**Пример:**
```python
import pytest

@pytest.mark.large
@pytest.mark.e2e
@pytest.mark.slow
def test_complete_document_processing_workflow(client, test_files):
    """Test complete document processing from upload to export"""
    # Upload document
    upload_response = client.post('/api/documents/upload',
        files={'file': test_files['sample.pdf']})
    doc_id = upload_response.json['document_id']

    # Process document (OCR, AI analysis)
    process_response = client.post(f'/api/documents/{doc_id}/process')
    assert process_response.status_code == 200

    # Wait for processing to complete
    import time
    for _ in range(30):  # Wait up to 30 seconds
        status = client.get(f'/api/documents/{doc_id}/status').json
        if status['state'] == 'completed':
            break
        time.sleep(1)

    assert status['state'] == 'completed'

    # Verify results
    results = client.get(f'/api/documents/{doc_id}/results').json
    assert results['text_content']
    assert results['ai_analysis']

    # Export document
    export_response = client.get(f'/api/documents/{doc_id}/export')
    assert export_response.status_code == 200
```

---

## Запуск тестов по размерам

### Запустить только малые тесты (быстрые)
```bash
pytest -m small
```

### Запустить только средние тесты
```bash
pytest -m medium
```

### Запустить только расширенные тесты
```bash
pytest -m large
```

### Запустить малые и средние (без медленных)
```bash
pytest -m "small or medium"
```

### Запустить все кроме расширенных
```bash
pytest -m "not large"
```

### Комбинирование маркеров
```bash
# Unit тесты, которые являются малыми
pytest -m "unit and small"

# Integration тесты средние и большие
pytest -m "integration and (medium or large)"

# Все тесты безопасности, кроме медленных
pytest -m "security and not large"
```

---

## Рекомендации по организации

### 1. Структура директорий

```
tests/
├── unit/               # В основном small тесты
│   ├── core/
│   ├── models/
│   └── utils/
├── integration/        # В основном medium тесты
│   ├── api/
│   ├── database/
│   └── services/
├── e2e/               # В основном large тесты
│   ├── workflows/
│   └── scenarios/
└── performance/       # Все large тесты
    ├── load/
    └── stress/
```

### 2. Маркировка тестов

#### На уровне модуля (весь файл)
```python
import pytest

# Все тесты в этом файле - малые unit тесты
pytestmark = [pytest.mark.small, pytest.mark.unit]

def test_something():
    pass

def test_another():
    pass
```

#### На уровне класса
```python
@pytest.mark.medium
@pytest.mark.integration
class TestUserService:
    def test_create_user(self):
        pass

    def test_update_user(self):
        pass
```

#### На уровне функции
```python
@pytest.mark.small
def test_fast_unit():
    pass

@pytest.mark.large
@pytest.mark.slow
def test_slow_e2e():
    pass
```

### 3. Стратегия выполнения тестов

#### На локальной разработке
```bash
# Быстрая проверка перед коммитом (< 1 минуты)
pytest -m small

# Более полная проверка (< 10 минут)
pytest -m "small or medium"
```

#### В CI/CD pipeline

**Pull Request проверка:**
```bash
# Быстрые проверки на каждый PR
pytest -m "small or (medium and not slow)"
```

**Main branch проверка:**
```bash
# Полная проверка на main
pytest -m "small or medium or large"
```

**Ночные тесты:**
```bash
# Все тесты включая performance
pytest -m "small or medium or large or performance"
```

---

## Примеры реальных тестов

### Small Test - Парсер документов

```python
"""
tests/unit/core/test_parser_small.py
"""
import pytest
from unittest.mock import Mock

pytestmark = pytest.mark.small

def test_parse_document_metadata():
    """Test document metadata parsing without I/O"""
    from src.core.parser import DocumentParser

    # Mock data instead of real file
    mock_content = b'%PDF-1.4\n%Title: Test Document'

    parser = DocumentParser()
    metadata = parser.parse_metadata(mock_content)

    assert metadata['format'] == 'PDF'
    assert metadata['version'] == '1.4'
    assert 'Test Document' in metadata['title']

def test_validate_document_format():
    """Test format validation logic"""
    from src.core.parser import DocumentParser

    parser = DocumentParser()

    assert parser.is_valid_format('application/pdf') is True
    assert parser.is_valid_format('application/msword') is True
    assert parser.is_valid_format('text/plain') is False
    assert parser.is_valid_format('invalid') is False
```

### Medium Test - API Integration

```python
"""
tests/integration/test_document_api_medium.py
"""
import pytest
from io import BytesIO

pytestmark = pytest.mark.medium

def test_document_upload_and_retrieval(client, test_db):
    """Test document upload and retrieval flow"""
    # Upload document
    data = {
        'file': (BytesIO(b'Test content'), 'test.txt')
    }

    response = client.post('/api/documents/upload',
                          data=data,
                          content_type='multipart/form-data')

    assert response.status_code == 201
    doc_id = response.json['document_id']

    # Retrieve document
    get_response = client.get(f'/api/documents/{doc_id}')
    assert get_response.status_code == 200
    assert get_response.json['filename'] == 'test.txt'

def test_document_search(client, test_db, sample_documents):
    """Test document search functionality"""
    # Search by keyword
    response = client.get('/api/documents/search?q=contract')

    assert response.status_code == 200
    results = response.json['results']
    assert len(results) > 0
    assert all('contract' in doc['title'].lower()
              for doc in results)
```

### Large Test - E2E Workflow

```python
"""
tests/e2e/test_document_lifecycle_large.py
"""
import pytest
import time

pytestmark = [pytest.mark.large, pytest.mark.e2e]

@pytest.mark.slow
def test_complete_document_lifecycle(client, test_files, test_db):
    """
    Test complete document lifecycle:
    Upload -> Process -> Analyze -> Export -> Archive
    """
    # 1. Upload
    with open(test_files['complex_document.pdf'], 'rb') as f:
        upload_response = client.post('/api/documents/upload',
            data={'file': (f, 'complex_document.pdf')},
            content_type='multipart/form-data')

    assert upload_response.status_code == 201
    doc_id = upload_response.json['document_id']

    # 2. OCR Processing (slow operation)
    process_response = client.post(f'/api/documents/{doc_id}/ocr')
    assert process_response.status_code == 202

    # Wait for OCR completion
    for _ in range(60):  # Wait up to 60 seconds
        status = client.get(f'/api/documents/{doc_id}/status').json
        if status['ocr_status'] == 'completed':
            break
        time.sleep(1)

    assert status['ocr_status'] == 'completed'

    # 3. AI Analysis (slow operation)
    analyze_response = client.post(f'/api/documents/{doc_id}/analyze')
    assert analyze_response.status_code == 202

    # Wait for analysis
    for _ in range(30):
        status = client.get(f'/api/documents/{doc_id}/status').json
        if status['analysis_status'] == 'completed':
            break
        time.sleep(1)

    assert status['analysis_status'] == 'completed'

    # 4. Verify analysis results
    results = client.get(f'/api/documents/{doc_id}/analysis').json
    assert results['entities']
    assert results['sentiment']
    assert results['categories']

    # 5. Export to multiple formats
    for format in ['pdf', 'docx', 'html']:
        export_response = client.get(
            f'/api/documents/{doc_id}/export?format={format}')
        assert export_response.status_code == 200
        assert len(export_response.data) > 0

    # 6. Archive document
    archive_response = client.post(f'/api/documents/{doc_id}/archive')
    assert archive_response.status_code == 200

    # 7. Verify archived state
    final_status = client.get(f'/api/documents/{doc_id}').json
    assert final_status['status'] == 'archived'
```

---

## Скрипты для запуска

См. `/scripts/run_tests_by_size.sh` для готовых скриптов запуска тестов разного размера.

---

## Метрики и мониторинг

### Целевые метрики времени выполнения:

| Размер | Целевое время | Максимум | Частота запуска |
|--------|--------------|----------|-----------------|
| Small  | < 500ms      | 1s       | При каждом коммите |
| Medium | < 2 мин      | 5 мин    | При PR |
| Large  | < 15 мин     | 30 мин   | На main branch |

### Мониторинг медленных тестов:

```bash
# Показать 20 самых медленных тестов
pytest --durations=20

# С фильтром по размеру
pytest -m small --durations=10  # Найти медленные "small" тесты
```

---

## Часто задаваемые вопросы (FAQ)

### Q: Должен ли каждый тест иметь маркер размера?

**A:** Рекомендуется, но не обязательно. По умолчанию:
- Тесты в `tests/unit/` считаются `small`
- Тесты в `tests/integration/` считаются `medium`
- Тесты в `tests/e2e/` считаются `large`

### Q: Что делать, если тест находится на границе категорий?

**A:** Выбирайте большую категорию. Лучше пометить тест как `medium`, если он иногда занимает > 1 секунды.

### Q: Можно ли использовать несколько маркеров размера?

**A:** Нет, используйте только один маркер размера на тест. Но можно комбинировать с другими маркерами:
```python
@pytest.mark.medium
@pytest.mark.integration
@pytest.mark.security
def test_something():
    pass
```

### Q: Как тестировать код с I/O, чтобы тест остался `small`?

**A:** Используйте моки:
```python
@pytest.mark.small
def test_file_processing(mocker):
    # Mock file operations
    mock_open = mocker.patch('builtins.open',
                            mocker.mock_open(read_data=b'test'))

    from src.processor import process_file
    result = process_file('fake_path.txt')

    assert result is not None
```

---

## Заключение

Организация тестов по размерам помогает:
- ⚡ Ускорить feedback loop при разработке
- 🎯 Оптимизировать CI/CD pipeline
- 📊 Улучшить понимание производительности тестов
- 🔧 Упростить отладку и поддержку

Следуйте принципу: **чем меньше тест, тем лучше** - пишите `small` тесты где возможно.
