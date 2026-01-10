# 📋 Document Management System

**Комплексная система управления документами для планирования социальных услуг**

Профессиональная система для работы с мега-шаблоном интегрированного профессионального планирования услуг персонального бюджета.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Возможности

### 6 Интегрированных Модулей:

1. **📊 Template Analyzer** - Анализ структуры шаблонов
   - Парсинг и извлечение структуры документа
   - Поиск и валидация переменных
   - Статистика и аналитика шаблонов

2. **💰 Financial Calculator** - Финансовый калькулятор
   - Расчет стоимости услуг с учетом всех отчислений
   - Социальные выплаты (KV, PV, RV, AV, UV)
   - Умлаги (U1, U2, U3) или резерв отпуск/больничные
   - Надбавки и региональные коэффициенты

3. **📄 Document Generator** - Генератор документов
   - Автоматическое заполнение шаблонов
   - Экспорт в TXT, HTML, Markdown, PDF*, DOCX*
   - Пакетная генерация документов

4. **✏️ Interactive Editor** - Интерактивный редактор
   - Пошаговое заполнение шаблона
   - Контекстная помощь и валидация
   - Предпросмотр и экспорт

5. **🗄️ Service Manager** - Менеджер услуг
   - База данных SQLite
   - CRUD операции
   - Поиск и фильтрация
   - Версионирование услуг

6. **🌐 Web Interface*** - Веб-интерфейс (в разработке)

*Требуют дополнительных зависимостей

---

## 🚀 Быстрый старт

### Установка

```bash
# Установить базовые зависимости
pip install -r requirements.txt

# Или установить с дополнительными возможностями
pip install -e ".[all]"  # Все функции (PDF, DOCX, Web)
```

### Первое использование

```bash
# 1. Анализ шаблона
python src/template_analyzer.py

# 2. Расчет стоимости
python src/financial_calculator.py --brutto 25 --region Berlin --hours 10

# 3. Интерактивное создание услуги
python src/interactive_editor.py

# 4. Генерация документа из примера
python src/document_generator.py config/examples/example_service_shopping_assistance.yaml -o output.html -f html
```

---

## 📚 Документация

### Template Analyzer

```bash
python src/template_analyzer.py              # Общая информация
python src/template_analyzer.py --blocks     # Список блоков
python src/template_analyzer.py --variables  # Все переменные
python src/template_analyzer.py --stats      # Детальная статистика
python src/template_analyzer.py --search "text"  # Поиск
```

### Financial Calculator

```bash
python src/financial_calculator.py --brutto 25.50 --region Berlin
python src/financial_calculator.py --brutto 25 --surcharge weekend --hours 8
python src/financial_calculator.py --brutto 25 --mode compare  # Сравнение режимов
```

### Document Generator

```bash
python src/document_generator.py config.yaml -o output.html -f html
python src/document_generator.py --batch config/examples --format html
```

### Interactive Editor

```bash
python src/interactive_editor.py  # Интерактивное пошаговое заполнение
```

### Service Manager

```bash
python src/service_manager.py add config.yaml      # Добавить услугу
python src/service_manager.py list                 # Список услуг
python src/service_manager.py show 1               # Показать услугу
python src/service_manager.py search "query"       # Поиск
python src/service_manager.py stats                # Статистика
```

---

## 📁 Структура проекта

```
daten20/
├── mSchablone                   # Мега-шаблон (4360 строк)
├── README.md                    # Этот файл
├── ARCHITECTURE.md              # Детальная архитектура
├── requirements.txt             # Зависимости
│
├── src/                         # Исходный код
│   ├── template_analyzer.py     # Анализатор
│   ├── financial_calculator.py  # Калькулятор
│   ├── document_generator.py    # Генератор
│   ├── interactive_editor.py    # Редактор
│   ├── service_manager.py       # Менеджер
│   ├── core/                    # Базовые компоненты
│   ├── models/                  # Модели данных
│   └── utils/                   # Утилиты
│
├── config/examples/             # Примеры конфигураций
└── data/                        # База данных и экспорты
```

---

## 💡 Примеры

### Создание новой услуги

```bash
# 1. Интерактивное создание
python src/interactive_editor.py

# 2. Генерация документа
python src/document_generator.py config/my_service.yaml -o output.html -f html

# 3. Добавление в базу
python src/service_manager.py add config/my_service.yaml
```

### Пакетная обработка

```bash
# Генерация документов из директории
python src/document_generator.py --batch config/examples --format html
```

---

## 📊 Возможности финансового калькулятора

- ✅ Социальные отчисления работодателя (KV, PV, RV, AV, UV)
- ✅ Умлаги (U1, U2, U3) или резерв отпуск/больничные
- ✅ Надбавки (ночь, выходные, праздники, срочность)
- ✅ Региональные коэффициенты для всех земель Германии
- ✅ Материалы и административные расходы
- ✅ Детальный breakdown расчета

---

## 🔧 Конфигурационные файлы

Примеры в `config/examples/`:
- `example_service_shopping_assistance.yaml` - Сопровождение в магазин
- `example_service_work_assistance.json` - Ассистент на работе
- `example_service_therapy.yaml` - Сопровождение на терапию

Структура конфигурации:
```yaml
basic_info:
  service_name: "Название"
  target_group: "Целевая группа"
  region: "Berlin"

financial:
  brutto_rate: 25.50
  # ... подробные параметры

system_settings:
  use_umlages: true
  service_type: "social"

funding:
  payer: "Eingliederungshilfe"
```

---

## 📝 Лицензия

MIT License

---

## 📞 Поддержка

- **Документация**: См. `ARCHITECTURE.md` для детальной архитектуры
- **Примеры**: См. `config/examples/`
- **Issues**: GitHub Issues

---

**Создано для социальных служб**

*Версия 1.0.0 - Январь 2026*
