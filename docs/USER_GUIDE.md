# Руководство пользователя

## Содержание

1. [Введение](#введение)
2. [Начало работы](#начало-работы)
3. [Модули системы](#модули-системы)
4. [Типичные сценарии использования](#типичные-сценарии-использования)
5. [Советы и best practices](#советы-и-best-practices)

---

## Введение

Document Management System - это комплексное решение для работы с шаблонами планирования социальных услуг. Система состоит из 6 взаимосвязанных модулей, каждый из которых решает определенную задачу.

### Для кого эта система?

- Организации социальных услуг
- Координаторы персональных бюджетов
- Поставщики услуг ассистенции
- Финансовые отделы

---

## Начало работы

### Установка

```bash
pip install -r requirements.txt
```

### Проверка установки

```bash
# Должно показать информацию о шаблоне
python src/template_analyzer.py
```

---

## Модули системы

### 1. Template Analyzer - Анализатор шаблонов

**Назначение:** Исследование структуры шаблона

**Когда использовать:**
- Нужно понять структуру шаблона
- Найти все переменные
- Получить статистику

**Примеры:**
```bash
# Общий обзор
python src/template_analyzer.py

# Список блоков
python src/template_analyzer.py --blocks

# Поиск текста
python src/template_analyzer.py --search "надбавка"
```

### 2. Financial Calculator - Финансовый калькулятор

**Назначение:** Расчет стоимости услуг

**Когда использовать:**
- Нужно рассчитать почасовую ставку
- Сравнить разные режимы расчета
- Понять breakdown стоимости

**Примеры:**
```bash
# Простой расчет
python src/financial_calculator.py --brutto 25 --region Berlin

# С надбавками
python src/financial_calculator.py --brutto 25 --surcharge weekend

# Сравнение режимов
python src/financial_calculator.py --brutto 25 --mode compare
```

### 3. Document Generator - Генератор документов

**Назначение:** Создание заполненных документов

**Когда использовать:**
- Нужно сгенерировать заполненный документ
- Пакетная генерация документов
- Экспорт в разные форматы

**Примеры:**
```bash
# Генерация HTML
python src/document_generator.py config.yaml -o output.html -f html

# Пакетная генерация
python src/document_generator.py --batch config/examples --format html
```

### 4. Interactive Editor - Интерактивный редактор

**Назначение:** Пошаговое создание конфигурации

**Когда использовать:**
- Первое создание услуги
- Не знаете структуру конфигурации
- Нужна помощь при заполнении

**Примеры:**
```bash
# Запустить интерактивный режим
python src/interactive_editor.py
```

**Процесс:**
1. Заполнение базовой информации
2. Финансовые параметры
3. Системные настройки
4. Источники финансирования
5. Сохранение и генерация

### 5. Service Manager - Менеджер услуг

**Назначение:** Управление базой данных услуг

**Когда использовать:**
- Хранение созданных услуг
- Поиск и фильтрация
- Версионирование

**Примеры:**
```bash
# Добавить услугу
python src/service_manager.py add config.yaml

# Список услуг
python src/service_manager.py list

# Поиск
python src/service_manager.py search "сопровождение"

# Статистика
python src/service_manager.py stats
```

---

## Типичные сценарии использования

### Сценарий 1: Создание новой услуги с нуля

```bash
# Шаг 1: Интерактивное создание
python src/interactive_editor.py

# Следуйте подсказкам, заполните все поля
# Конфигурация сохранится в config/my_service.yaml

# Шаг 2: Генерация документа (опционально)
python src/document_generator.py config/my_service.yaml -o my_service.html -f html

# Шаг 3: Добавление в базу данных
python src/service_manager.py add config/my_service.yaml
```

### Сценарий 2: Расчет и сравнение стоимости

```bash
# Расчет для Berlin
python src/financial_calculator.py --brutto 25 --region Berlin --detailed

# Расчет для Hamburg
python src/financial_calculator.py --brutto 25 --region Hamburg --detailed

# Сравнение режимов (умлаги vs резерв)
python src/financial_calculator.py --brutto 25 --mode compare
```

### Сценарий 3: Массовая генерация документов

```bash
# Создайте конфигурации в config/batch/

# Пакетная генерация
python src/document_generator.py --batch config/batch --output-dir exports --format html

# Все документы будут созданы в exports/
```

### Сценарий 4: Анализ существующих услуг

```bash
# Статистика базы
python src/service_manager.py stats

# Услуги по региону
python src/service_manager.py list --region Berlin

# Поиск по ключевому слову
python src/service_manager.py search "ассистент"

# Детали услуги
python src/service_manager.py show 5 --detailed
```

---

## Советы и best practices

### Организация конфигураций

1. **Используйте понятные имена файлов**
   ```
   service_shopping_assistance_berlin.yaml
   service_work_assistance_hamburg.yaml
   ```

2. **Группируйте по типам или регионам**
   ```
   config/
   ├── berlin/
   │   ├── service1.yaml
   │   └── service2.yaml
   └── hamburg/
       ├── service1.yaml
       └── service2.yaml
   ```

3. **Версионируйте конфигурации**
   - Используйте git для версионирования
   - Поле `document_version` в конфигурации

### Финансовые расчеты

1. **Проверяйте региональные коэффициенты**
   - Они меняются со временем
   - Актуализируйте в `src/utils/constants.py`

2. **Выбор режима расчета**
   - `use_umlages: true` - стандартный режим
   - `use_vacation_reserve: true` - альтернативный

3. **Документируйте источники ставок**
   - Используйте поле для источника коэффициента
   - Указывайте дату актуализации

### Работа с базой данных

1. **Регулярные бэкапы**
   ```bash
   cp data/services.db data/services_backup_$(date +%Y%m%d).db
   ```

2. **Экспорт важных услуг**
   ```bash
   python src/service_manager.py export 1 backup/service_1.yaml
   ```

3. **Использование поиска**
   - Поиск ищет в названии и целевой группе
   - Используйте фильтры для точности

### Генерация документов

1. **Выбор формата**
   - **HTML** - для просмотра в браузере, красивое оформление
   - **TXT** - для простого текста
   - **Markdown** - для дальнейшей обработки
   - **PDF*** - для печати (требует weasyprint)
   - **DOCX*** - для редактирования (требует python-docx)

2. **Проверка незаполненных переменных**
   - Генератор предупредит о незаполненных полях
   - Проверьте перед финальной генерацией

### Автоматизация

1. **Скрипты для повторяющихся задач**
   ```bash
   # generate_all.sh
   #!/bin/bash
   for config in config/active/*.yaml; do
       python src/document_generator.py "$config" -f html
   done
   ```

2. **Регулярная актуализация**
   - Обновление ставок
   - Изменение коэффициентов
   - Проверка соответствия законодательству

---

## Часто задаваемые вопросы

### Как изменить региональный коэффициент?

Отредактируйте `src/utils/constants.py`, раздел `REGIONAL_COEFFICIENTS`

### Как добавить новый тип услуги?

Добавьте в `src/utils/constants.py`, раздел `SERVICE_TYPES`

### Как сделать бэкап базы данных?

```bash
cp data/services.db data/services_backup.db
```

### Почему PDF/DOCX не работает?

Установите дополнительные зависимости:
```bash
pip install weasyprint  # для PDF
pip install python-docx # для DOCX
```

### Как обновить услугу в базе?

Экспортируйте, отредактируйте, удалите старую, добавьте новую:
```bash
python src/service_manager.py export 1 service.yaml
# Отредактируйте service.yaml
python src/service_manager.py delete 1 --force
python src/service_manager.py add service.yaml
```

---

## Дополнительная помощь

- См. `ARCHITECTURE.md` для технических деталей
- См. `config/examples/` для примеров конфигураций
- GitHub Issues для вопросов и багов

---

*Последнее обновление: Январь 2026*
