# 🤝 Contributing to Document Management System

Спасибо за интерес к вкладу в Document Management System! Мы приветствуем вклад от сообщества.

---

## 📋 Содержание

- [Code of Conduct](#code-of-conduct)
- [Как начать](#как-начать)
- [Процесс разработки](#процесс-разработки)
- [Стиль кода](#стиль-кода)
- [Тестирование](#тестирование)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Отчеты об ошибках](#отчеты-об-ошибках)
- [Запросы функций](#запросы-функций)

---

## 📜 Code of Conduct

### Наши стандарты

Мы ожидаем, что все участники будут:
- ✅ Использовать приветливый и инклюзивный язык
- ✅ Уважать различные точки зрения и опыт
- ✅ Принимать конструктивную критику
- ✅ Фокусироваться на том, что лучше для сообщества
- ✅ Проявлять эмпатию к другим участникам

---

## 🚀 Как начать

### 1. Fork и Clone репозитория

\`\`\`bash
# Fork репозитория через GitHub UI

# Clone вашего fork
git clone https://github.com/YOUR_USERNAME/daten20.git
cd daten20

# Добавить upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/daten20.git
\`\`\`

### 2. Настройка окружения

\`\`\`bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\\Scripts\\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt  # для разработки

# Установить pre-commit hooks
pre-commit install

# Установить spaCy модели
python -m spacy download en_core_web_sm
python -m spacy download ru_core_news_sm
\`\`\`

### 3. Инициализировать базу данных

\`\`\`bash
# Создать тестовую базу данных
python -c "from src.core.database import Database; Database().init_db()"
\`\`\`

### 4. Запустить тесты

\`\`\`bash
# Запустить все тесты
pytest

# Запустить с покрытием
pytest --cov=src --cov-report=html
\`\`\`

---

## 🔄 Процесс разработки

### Workflow

1. **Создать issue** (если его еще нет) описывая bug или feature
2. **Создать ветку** из \`main\` для вашей работы
3. **Разработать** изменения с тестами
4. **Запустить тесты** и убедиться, что все проходит
5. **Commit** изменения следуя нашим guidelines
6. **Push** в ваш fork
7. **Создать Pull Request** к \`main\` ветке

### Naming веток

Используйте следующий формат для названий веток:

\`\`\`
feature/short-description    # Новая функция
bugfix/short-description     # Исправление ошибки
docs/short-description       # Изменения в документации
refactor/short-description   # Рефакторинг
test/short-description       # Добавление тестов
\`\`\`

**Примеры:**
- \`feature/add-ocr-support\`
- \`bugfix/fix-pdf-parsing\`
- \`docs/update-api-guide\`

---

## 🎨 Стиль кода

### Python Code Style

Мы следуем **PEP 8** с некоторыми дополнениями:

- **Форматирование:** Используем \`black\` для автоформатирования
- **Импорты:** Сортируем с помощью \`isort\`
- **Linting:** Проверяем с помощью \`flake8\` и \`pylint\`
- **Type hints:** Используем аннотации типов где возможно

### Запуск форматирования

\`\`\`bash
# Автоформатирование кода
black src/ tests/

# Сортировка импортов
isort src/ tests/

# Проверка стиля
flake8 src/ tests/
pylint src/
\`\`\`

### Примеры стиля

**✅ Хорошо:**

\`\`\`python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents with various formats."""
    
    def __init__(self, config: dict) -> None:
        """Initialize processor with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._cache: dict = {}
    
    def process(self, file_path: str) -> Optional[dict]:
        """Process a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Processed document data or None if failed
            
        Raises:
            ValueError: If file_path is invalid
        """
        if not file_path:
            raise ValueError("file_path cannot be empty")
        
        logger.info(f"Processing document: {file_path}")
        return self._extract_content(file_path)
    
    def _extract_content(self, file_path: str) -> dict:
        """Extract content from file (private method)."""
        # Implementation
        pass
\`\`\`

**❌ Плохо:**

\`\`\`python
import logging
from typing import *

def process(fp):  # No type hints
    if not fp:
        return None  # No logging
    # No docstring
    return extract(fp)
\`\`\`

### Docstrings

Используем **Google-style docstrings**:

\`\`\`python
def function_name(param1: int, param2: str) -> bool:
    """Short description of function.
    
    Longer description if needed. Can span multiple lines.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is negative
        TypeError: When param2 is not a string
        
    Example:
        >>> function_name(42, "hello")
        True
    """
    pass
\`\`\`

---

## 🧪 Тестирование

### Требования к тестам

- **Все новые функции должны иметь тесты**
- **Покрытие кода:** Стремимся к 80%+
- **Типы тестов:**
  - Unit tests для функций/методов
  - Integration tests для взаимодействия модулей
  - End-to-end tests для полных workflows

### Структура тестов

\`\`\`
tests/
├── unit/               # Unit tests
│   ├── core/
│   ├── ml/
│   └── ...
├── integration/        # Integration tests
├── performance/        # Performance tests
└── fixtures/          # Test data and fixtures
\`\`\`

### Написание тестов

\`\`\`python
import pytest
from src.core.parser import DocumentParser

class TestDocumentParser:
    """Tests for DocumentParser class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.parser = DocumentParser()
    
    def test_parse_pdf_success(self):
        """Test successful PDF parsing."""
        result = self.parser.parse("tests/fixtures/sample.pdf")
        assert result is not None
        assert "text" in result
        assert len(result["text"]) > 0
    
    def test_parse_invalid_file(self):
        """Test parsing with invalid file."""
        with pytest.raises(ValueError):
            self.parser.parse("")
    
    @pytest.mark.parametrize("file_ext,expected", [
        (".pdf", "pdf"),
        (".docx", "docx"),
        (".txt", "txt"),
    ])
    def test_detect_format(self, file_ext, expected):
        """Test format detection for different extensions."""
        result = self.parser.detect_format(f"test{file_ext}")
        assert result == expected
\`\`\`

### Запуск тестов

\`\`\`bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=html

# Только unit tests
pytest tests/unit/

# Конкретный файл
pytest tests/unit/test_parser.py

# Конкретный тест
pytest tests/unit/test_parser.py::TestDocumentParser::test_parse_pdf_success

# С verbose output
pytest -v

# Остановиться на первой ошибке
pytest -x
\`\`\`

---

## 📝 Commit Guidelines

### Формат commit message

\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

### Types

- **feat:** Новая функция
- **fix:** Исправление ошибки
- **docs:** Изменения в документации
- **style:** Форматирование, отсутствующие точки с запятой и т.д.
- **refactor:** Рефакторинг кода
- **test:** Добавление или изменение тестов
- **chore:** Обслуживание (зависимости, конфиги и т.д.)
- **perf:** Улучшение производительности

### Примеры

**✅ Хорошие commit messages:**

\`\`\`
feat(parser): add support for DOCX files

Add DocumentParser class that can parse DOCX files using python-docx library.
Includes tests and documentation.

Closes #123
\`\`\`

\`\`\`
fix(api): fix authentication token validation

Token expiration was not properly checked causing security issue.
Now properly validates exp claim in JWT token.

Fixes #456
\`\`\`

\`\`\`
docs(readme): update installation instructions

Add Docker installation method and improve clarity of manual installation steps.
\`\`\`

**❌ Плохие commit messages:**

\`\`\`
update stuff
fix bug
changes
wip
\`\`\`

---

## 🔀 Pull Request Process

### Перед созданием PR

- ✅ Убедитесь, что все тесты проходят
- ✅ Добавьте новые тесты для новой функциональности
- ✅ Обновите документацию если необходимо
- ✅ Запустите линтеры и исправьте ошибки
- ✅ Обновите CHANGELOG.md если применимо

### Создание PR

1. **Sync с upstream**

\`\`\`bash
git fetch upstream
git rebase upstream/main
\`\`\`

2. **Push в ваш fork**

\`\`\`bash
git push origin your-branch-name
\`\`\`

3. **Создать PR через GitHub UI**

### Шаблон описания PR

\`\`\`markdown
## Description
Brief description of the changes

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran

## Checklist:
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #issue_number
\`\`\`

### Review процесс

- PR должен быть одобрен минимум одним maintainer
- Все комментарии должны быть addressed
- CI/CD проверки должны пройти
- После одобрения, maintainer сделает merge

---

## 🐛 Отчеты об ошибках

### Перед созданием отчета

- Проверьте, не существует ли уже такого issue
- Попробуйте воспроизвести на последней версии
- Соберите необходимую информацию

### Шаблон отчета об ошибке

\`\`\`markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python Version: [e.g. 3.9.7]
 - Project Version: [e.g. 4.1]

**Additional context**
Add any other context about the problem here.

**Logs**
If applicable, add relevant log output.
\`\`\`

---

## 💡 Запросы функций

### Шаблон запроса функции

\`\`\`markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Would you be willing to implement this feature?**
- [ ] Yes
- [ ] No
- [ ] Need help
\`\`\`

---

## 🏗️ Архитектура проекта

### Основные компоненты

\`\`\`
src/
├── core/           # Основная функциональность (парсинг, экспорт, БД)
├── ml/             # Machine Learning модули
├── models/         # Data models
├── analytics/      # Аналитика и BI
├── utils/          # Утилиты
└── enterprise/     # Enterprise функции
\`\`\`

### Принципы

- **DRY (Don't Repeat Yourself):** Избегайте дублирования кода
- **SOLID:** Следуйте принципам SOLID
- **Separation of Concerns:** Четкое разделение ответственности
- **Testability:** Код должен легко тестироваться
- **Documentation:** Код должен быть хорошо документирован

---

## 📚 Дополнительные ресурсы

- [README.md](README.md) - Основная документация
- [ARCHITECTURE.md](ARCHITECTURE.md) - Техническая архитектура
- [API.md](docs/API.md) - API документация
- [Development Environment Setup](docs/DEVELOPMENT.md)

---

## 🙏 Благодарности

Спасибо всем, кто вносит вклад в проект! Ваш вклад делает проект лучше.

---

## 📞 Вопросы?

Если у вас есть вопросы, вы можете:
- Создать issue с меткой "question"
- Начать discussion в GitHub Discussions
- Написать на support@example.com

---

**Спасибо за вклад в Document Management System!** 🎉
