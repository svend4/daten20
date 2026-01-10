# Архитектура Системы Управления Документами (Document Management System)

## 🎯 Общая Концепция

Комплексная система из 6 взаимосвязанных модулей для работы с мега-шаблоном интегрированного профессионального планирования услуг персонального бюджета.

## 📦 Структура Проекта

```
daten20/
├── mSchablone                          # Исходный шаблон документ
├── README.md                           # Основная документация
├── ARCHITECTURE.md                     # Этот файл
├── requirements.txt                    # Зависимости Python
├── setup.py                           # Установочный скрипт
│
├── src/                               # Исходный код
│   ├── __init__.py
│   ├── template_analyzer.py           # Модуль 1: Анализатор шаблонов
│   ├── financial_calculator.py        # Модуль 2: Финансовый калькулятор
│   ├── document_generator.py          # Модуль 3: Генератор документов
│   ├── interactive_editor.py          # Модуль 4: Интерактивный редактор
│   ├── service_manager.py             # Модуль 5: Менеджер услуг
│   ├── web_app.py                     # Модуль 6: Web интерфейс
│   │
│   ├── core/                          # Базовые компоненты
│   │   ├── __init__.py
│   │   ├── parser.py                  # Парсер документов
│   │   ├── validator.py               # Валидатор данных
│   │   ├── exporter.py                # Экспорт в разные форматы
│   │   └── database.py                # Работа с БД
│   │
│   ├── models/                        # Модели данных
│   │   ├── __init__.py
│   │   ├── service.py                 # Модель услуги
│   │   ├── financial.py               # Финансовые данные
│   │   └── template.py                # Модель шаблона
│   │
│   └── utils/                         # Утилиты
│       ├── __init__.py
│       ├── helpers.py                 # Вспомогательные функции
│       ├── constants.py               # Константы
│       └── formatting.py              # Форматирование вывода
│
├── web/                               # Web интерфейс
│   ├── static/                        # Статические файлы
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/                     # HTML шаблоны
│       ├── base.html
│       ├── dashboard.html
│       ├── editor.html
│       └── reports.html
│
├── data/                              # Данные
│   ├── services.db                    # SQLite база данных
│   ├── templates/                     # Шаблоны документов
│   └── exports/                       # Сгенерированные документы
│
├── config/                            # Конфигурации
│   ├── default_config.yaml            # Дефолтная конфигурация
│   └── examples/                      # Примеры заполнения
│       ├── example_service_1.yaml
│       └── example_service_2.json
│
├── tests/                             # Тесты
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_calculator.py
│   └── test_generator.py
│
└── docs/                              # Документация
    ├── USER_GUIDE.md                  # Руководство пользователя
    ├── API.md                         # API документация
    └── EXAMPLES.md                    # Примеры использования
```

## 🔧 Модули Системы

### 1. Template Analyzer (Анализатор Шаблонов)

**Назначение:** Парсинг и анализ структуры шаблона

**Функции:**
- Извлечение структуры блоков (0, I-X)
- Поиск всех переменных вида {Variable_Name}
- Валидация целостности разделов
- Генерация карты документа
- Статистика по шаблону

**Основные методы:**
```python
parse_template(file_path) -> TemplateStructure
extract_variables() -> List[Variable]
validate_structure() -> ValidationReport
get_block_content(block_id) -> BlockContent
get_statistics() -> TemplateStats
```

### 2. Financial Calculator (Финансовый Калькулятор)

**Назначение:** Расчет стоимости услуг по формулам

**Функции:**
- Расчет почасовой ставки с учетом всех отчислений
- Социальные выплаты (KV, PV, RV, AV, UV)
- Умлаги (U1, U2, U3)
- Надбавки (ночь, выходные, праздники, срочность)
- Материалы, административные расходы
- Региональные коэффициенты
- Итоговая стоимость услуги

**Формулы:**
```python
# Социальные отчисления работодателя
employer_contributions = brutto * (KV_ER + PV_ER + RV_ER + AV_ER + UV_ER) / 100

# Умлаги
umlages = brutto * (U1 + U2 + U3) / 100

# Базовая стоимость часа
base_cost = brutto + employer_contributions + umlages

# С учетом надбавок
final_cost = base_cost * (1 + surcharges) * region_coefficient
```

**Основные методы:**
```python
calculate_hourly_rate(params) -> HourlyRate
calculate_surcharge(base, surcharge_type) -> Decimal
calculate_total_cost(hours, params) -> TotalCost
generate_breakdown() -> CostBreakdown
export_calculation(format) -> str
```

### 3. Document Generator (Генератор Документов)

**Назначение:** Генерация заполненных документов из шаблонов

**Функции:**
- Загрузка конфигурации (YAML/JSON)
- Подстановка значений в переменные
- Генерация финальных документов
- Экспорт в форматы: TXT, PDF, DOCX, HTML, Markdown
- Пакетная генерация

**Workflow:**
1. Загрузить шаблон
2. Загрузить конфигурацию с данными
3. Валидировать данные
4. Заполнить переменные
5. Экспортировать результат

**Основные методы:**
```python
load_config(config_path) -> ServiceConfig
fill_template(template, config) -> FilledDocument
export_to_pdf(document, output_path)
export_to_docx(document, output_path)
export_to_html(document, output_path)
batch_generate(configs) -> List[Document]
```

### 4. Interactive Editor (Интерактивный Редактор)

**Назначение:** CLI интерфейс для пошагового заполнения

**Функции:**
- Пошаговое заполнение всех разделов
- Контекстная помощь по каждому полю
- Валидация введенных данных
- Автосохранение прогресса
- Предпросмотр результата
- Экспорт в выбранном формате

**Интерфейс:**
```
=== Интерактивный Редактор Шаблона ===

Раздел 0.1: Базовая идентификация услуги

[1/6] Название услуги:
Подсказка: Краткое название услуги (например, "Сопровождение в общественных местах")
> _

[2/6] Целевая группа:
Подсказка: Категории получателей (например, "Люди с физическими ограничениями")
> _
```

**Основные методы:**
```python
start_session() -> EditorSession
prompt_section(section_id) -> SectionData
validate_input(field, value) -> ValidationResult
save_progress(session) -> bool
preview_document(session) -> str
export_session(session, format) -> str
```

### 5. Service Manager (Менеджер Услуг)

**Назначение:** База данных и управление созданными планами

**Функции:**
- SQLite база данных услуг
- CRUD операции (Create, Read, Update, Delete)
- Поиск и фильтрация
- Версионирование услуг
- Статистика и аналитика
- Экспорт отчетов

**Схема БД:**
```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    target_group TEXT,
    region TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER,
    config_json TEXT,
    template_id INTEGER
);

CREATE TABLE financial_data (
    id INTEGER PRIMARY KEY,
    service_id INTEGER,
    brutto_rate REAL,
    total_cost REAL,
    calculation_json TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE versions (
    id INTEGER PRIMARY KEY,
    service_id INTEGER,
    version_number INTEGER,
    config_snapshot TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id)
);
```

**Основные методы:**
```python
create_service(config) -> Service
get_service(service_id) -> Service
update_service(service_id, config) -> Service
delete_service(service_id) -> bool
search_services(query) -> List[Service]
get_statistics() -> Statistics
export_report(format) -> str
```

### 6. Web Application (Web Интерфейс)

**Назначение:** Браузерный интерфейс для всех функций

**Технологии:**
- Backend: Flask
- Frontend: Bootstrap 5 + JavaScript
- Визуализация: Chart.js
- Формы: WTForms

**Страницы:**
1. **Dashboard** - Обзор всех услуг, статистика
2. **Editor** - Визуальный редактор шаблонов
3. **Calculator** - Финансовый калькулятор
4. **Library** - Библиотека созданных услуг
5. **Reports** - Отчеты и аналитика
6. **Settings** - Настройки системы

**API Endpoints:**
```
GET    /api/services              - Список услуг
POST   /api/services              - Создать услугу
GET    /api/services/:id          - Получить услугу
PUT    /api/services/:id          - Обновить услугу
DELETE /api/services/:id          - Удалить услугу
POST   /api/calculate             - Расчет стоимости
POST   /api/generate              - Генерация документа
GET    /api/statistics            - Статистика
```

## 🔄 Взаимодействие Модулей

```
┌─────────────────────┐
│   Web Interface     │
│    (Flask App)      │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────────┐
│Template│   │  Service   │
│Analyzer│◄──┤  Manager   │
└────┬───┘   └──────┬─────┘
     │              │
     ▼              ▼
┌────────────┐  ┌──────────┐
│ Document   │  │Financial │
│ Generator  │  │Calculator│
└────────────┘  └──────────┘
     │              │
     └──────┬───────┘
            ▼
    ┌───────────────┐
    │ Interactive   │
    │    Editor     │
    └───────────────┘
```

## 🎨 Дизайн-паттерны

### 1. Factory Pattern
Для создания различных экспортеров документов

### 2. Strategy Pattern
Для различных алгоритмов расчета (с U-млажами или с резервом)

### 3. Observer Pattern
Для отслеживания изменений в редакторе

### 4. Repository Pattern
Для работы с базой данных

### 5. Builder Pattern
Для пошагового построения конфигурации услуги

## 📊 Форматы Данных

### Конфигурация услуги (YAML)
```yaml
basic_info:
  service_name: "Сопровождение в магазин"
  target_group: "Люди с ограниченной мобильностью"
  region: "Berlin"
  provider_type: "Квалифицированный ассистент"

financial:
  brutto_rate: 25.50
  employer_rates:
    kv_er: 7.3
    pv_er: 1.525
    rv_er: 9.3
    av_er: 1.2
    uv_er: 1.3
  umlages:
    u1: 0.9
    u2: 0.4
    u3: 0.09
  surcharges:
    night: 25
    weekend: 50
    holiday: 100
    urgent: 15
  materials_per_month: 50
  admin_percent: 5
  region_coefficient: 1.15

system_settings:
  use_umlages: true
  use_vacation_reserve: false
  surcharge_base: "full_cost"
  service_type: "social"
```

### Финансовый отчет (JSON)
```json
{
  "service_id": 12345,
  "calculation_date": "2026-01-10",
  "base_rate": 25.50,
  "contributions": {
    "kv": 1.86,
    "pv": 0.39,
    "rv": 2.37,
    "av": 0.31,
    "uv": 0.33
  },
  "umlages": {
    "u1": 0.23,
    "u2": 0.10,
    "u3": 0.02
  },
  "total_base_cost": 31.11,
  "surcharges_applied": ["weekend"],
  "final_hourly_rate": 35.77,
  "breakdown": "..."
}
```

## 🔐 Безопасность

1. **Валидация входных данных** - все пользовательские данные валидируются
2. **SQL Injection защита** - используется ORM/параметризованные запросы
3. **XSS защита** - экранирование HTML в web интерфейсе
4. **Безопасное хранение** - конфигурации в YAML, без выполнения кода
5. **Логирование** - все операции логируются

## 📈 Масштабируемость

1. **Модульная архитектура** - каждый модуль независим
2. **API-first подход** - все функции доступны через API
3. **База данных** - легко мигрировать с SQLite на PostgreSQL
4. **Кэширование** - результаты расчетов кэшируются
5. **Асинхронность** - пакетная генерация в фоне

## 🧪 Тестирование

1. **Unit тесты** - для каждого модуля
2. **Integration тесты** - для взаимодействия модулей
3. **E2E тесты** - для web интерфейса
4. **Тестовые данные** - примеры конфигураций

## 📚 Документация

1. **README.md** - быстрый старт
2. **ARCHITECTURE.md** - архитектура (этот файл)
3. **USER_GUIDE.md** - руководство пользователя
4. **API.md** - документация API
5. **EXAMPLES.md** - примеры использования
6. **Docstrings** - в коде

## 🚀 Roadmap

### Phase 1 - MVP (Текущая)
- ✅ Template Analyzer
- ✅ Financial Calculator
- ✅ Document Generator
- ✅ Interactive Editor
- ✅ Service Manager
- ✅ Basic Web UI

### Phase 2 - Enhancement
- Multi-language support (полностью двуязычный интерфейс)
- Advanced analytics
- REST API documentation (OpenAPI/Swagger)
- PDF генерация с логотипами
- Email уведомления

### Phase 3 - Enterprise
- Multi-user support
- Role-based access control
- Cloud deployment
- Mobile app
- Integration с внешними системами

## 💻 Требования

### Минимальные
- Python 3.8+
- 100MB дискового пространства
- 512MB RAM

### Рекомендуемые
- Python 3.10+
- 1GB дискового пространства
- 2GB RAM
- Современный браузер (Chrome, Firefox, Edge)

## 📄 Лицензия

MIT License - свободное использование и модификация
