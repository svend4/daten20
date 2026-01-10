"""
Internationalization (i18n) Support

Provides multi-language support for the application.
"""

from typing import Dict, Optional, Any
from pathlib import Path
import json
from enum import Enum


class Language(str, Enum):
    """Supported languages"""
    RU = "ru"  # Russian
    DE = "de"  # German
    EN = "en"  # English
    UK = "uk"  # Ukrainian
    PL = "pl"  # Polish
    FR = "fr"  # French


class I18nManager:
    """Internationalization manager"""

    def __init__(self, locales_dir: str = "locales", default_language: Language = Language.RU):
        self.locales_dir = Path(locales_dir)
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}

        # Create locales directory if it doesn't exist
        self.locales_dir.mkdir(parents=True, exist_ok=True)

        # Load translations
        self._load_translations()

        # Create default translations if they don't exist
        if not self.translations:
            self._create_default_translations()

    def _load_translations(self):
        """Load all translation files"""
        for lang in Language:
            lang_file = self.locales_dir / f"{lang.value}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang.value] = json.load(f)

    def _create_default_translations(self):
        """Create default translation files"""
        # Russian translations
        russian = {
            "app": {
                "name": "Система управления документами",
                "version": "Версия",
                "welcome": "Добро пожаловать",
                "logout": "Выход",
                "login": "Вход",
                "settings": "Настройки"
            },
            "nav": {
                "dashboard": "Панель управления",
                "services": "Услуги",
                "calculator": "Калькулятор",
                "generator": "Генератор",
                "analytics": "Аналитика",
                "search": "Поиск",
                "import_export": "Импорт/Экспорт",
                "templates": "Шаблоны"
            },
            "common": {
                "save": "Сохранить",
                "cancel": "Отмена",
                "delete": "Удалить",
                "edit": "Редактировать",
                "view": "Просмотр",
                "create": "Создать",
                "update": "Обновить",
                "search": "Поиск",
                "filter": "Фильтр",
                "export": "Экспорт",
                "import": "Импорт",
                "yes": "Да",
                "no": "Нет",
                "back": "Назад",
                "next": "Далее",
                "previous": "Предыдущий",
                "finish": "Завершить",
                "loading": "Загрузка...",
                "error": "Ошибка",
                "success": "Успешно",
                "warning": "Предупреждение",
                "info": "Информация"
            },
            "services": {
                "title": "Услуги",
                "service_name": "Название услуги",
                "region": "Регион",
                "rate": "Ставка",
                "hours": "Часы в месяц",
                "create_service": "Создать услугу",
                "edit_service": "Редактировать услугу",
                "delete_service": "Удалить услугу",
                "no_services": "Нет услуг",
                "total_services": "Всего услуг",
                "active_services": "Активные услуги"
            },
            "calculator": {
                "title": "Калькулятор",
                "calculate": "Рассчитать",
                "result": "Результат",
                "brutto_rate": "Брутто ставка",
                "netto_rate": "Нетто ставка",
                "insurance": "Страхование",
                "taxes": "Налоги",
                "total_cost": "Общая стоимость"
            },
            "auth": {
                "username": "Имя пользователя",
                "password": "Пароль",
                "email": "Email",
                "login": "Войти",
                "logout": "Выйти",
                "register": "Регистрация",
                "forgot_password": "Забыли пароль?",
                "reset_password": "Сбросить пароль",
                "change_password": "Изменить пароль"
            },
            "errors": {
                "404": "Страница не найдена",
                "500": "Внутренняя ошибка сервера",
                "invalid_input": "Неверный ввод",
                "required_field": "Обязательное поле",
                "access_denied": "Доступ запрещен",
                "not_found": "Не найдено",
                "already_exists": "Уже существует"
            },
            "validation": {
                "required": "Это поле обязательно",
                "min_length": "Минимальная длина: {min}",
                "max_length": "Максимальная длина: {max}",
                "invalid_email": "Неверный email",
                "invalid_number": "Неверное число",
                "min_value": "Минимальное значение: {min}",
                "max_value": "Максимальное значение: {max}"
            }
        }

        # German translations
        german = {
            "app": {
                "name": "Dokumentenverwaltungssystem",
                "version": "Version",
                "welcome": "Willkommen",
                "logout": "Abmelden",
                "login": "Anmelden",
                "settings": "Einstellungen"
            },
            "nav": {
                "dashboard": "Dashboard",
                "services": "Dienstleistungen",
                "calculator": "Rechner",
                "generator": "Generator",
                "analytics": "Analytik",
                "search": "Suche",
                "import_export": "Import/Export",
                "templates": "Vorlagen"
            },
            "common": {
                "save": "Speichern",
                "cancel": "Abbrechen",
                "delete": "Löschen",
                "edit": "Bearbeiten",
                "view": "Ansehen",
                "create": "Erstellen",
                "update": "Aktualisieren",
                "search": "Suche",
                "filter": "Filter",
                "export": "Export",
                "import": "Import",
                "yes": "Ja",
                "no": "Nein",
                "back": "Zurück",
                "next": "Weiter",
                "previous": "Vorherige",
                "finish": "Fertig",
                "loading": "Laden...",
                "error": "Fehler",
                "success": "Erfolg",
                "warning": "Warnung",
                "info": "Information"
            },
            "services": {
                "title": "Dienstleistungen",
                "service_name": "Dienstleistungsname",
                "region": "Region",
                "rate": "Rate",
                "hours": "Stunden pro Monat",
                "create_service": "Dienstleistung erstellen",
                "edit_service": "Dienstleistung bearbeiten",
                "delete_service": "Dienstleistung löschen",
                "no_services": "Keine Dienstleistungen",
                "total_services": "Gesamt Dienstleistungen",
                "active_services": "Aktive Dienstleistungen"
            },
            "calculator": {
                "title": "Rechner",
                "calculate": "Berechnen",
                "result": "Ergebnis",
                "brutto_rate": "Bruttorate",
                "netto_rate": "Nettorate",
                "insurance": "Versicherung",
                "taxes": "Steuern",
                "total_cost": "Gesamtkosten"
            },
            "auth": {
                "username": "Benutzername",
                "password": "Passwort",
                "email": "E-Mail",
                "login": "Anmelden",
                "logout": "Abmelden",
                "register": "Registrieren",
                "forgot_password": "Passwort vergessen?",
                "reset_password": "Passwort zurücksetzen",
                "change_password": "Passwort ändern"
            },
            "errors": {
                "404": "Seite nicht gefunden",
                "500": "Interner Serverfehler",
                "invalid_input": "Ungültige Eingabe",
                "required_field": "Pflichtfeld",
                "access_denied": "Zugriff verweigert",
                "not_found": "Nicht gefunden",
                "already_exists": "Bereits vorhanden"
            },
            "validation": {
                "required": "Dieses Feld ist erforderlich",
                "min_length": "Mindestlänge: {min}",
                "max_length": "Maximale Länge: {max}",
                "invalid_email": "Ungültige E-Mail",
                "invalid_number": "Ungültige Nummer",
                "min_value": "Mindestwert: {min}",
                "max_value": "Maximalwert: {max}"
            }
        }

        # English translations
        english = {
            "app": {
                "name": "Document Management System",
                "version": "Version",
                "welcome": "Welcome",
                "logout": "Logout",
                "login": "Login",
                "settings": "Settings"
            },
            "nav": {
                "dashboard": "Dashboard",
                "services": "Services",
                "calculator": "Calculator",
                "generator": "Generator",
                "analytics": "Analytics",
                "search": "Search",
                "import_export": "Import/Export",
                "templates": "Templates"
            },
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "view": "View",
                "create": "Create",
                "update": "Update",
                "search": "Search",
                "filter": "Filter",
                "export": "Export",
                "import": "Import",
                "yes": "Yes",
                "no": "No",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "finish": "Finish",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information"
            },
            "services": {
                "title": "Services",
                "service_name": "Service Name",
                "region": "Region",
                "rate": "Rate",
                "hours": "Hours per Month",
                "create_service": "Create Service",
                "edit_service": "Edit Service",
                "delete_service": "Delete Service",
                "no_services": "No Services",
                "total_services": "Total Services",
                "active_services": "Active Services"
            },
            "calculator": {
                "title": "Calculator",
                "calculate": "Calculate",
                "result": "Result",
                "brutto_rate": "Gross Rate",
                "netto_rate": "Net Rate",
                "insurance": "Insurance",
                "taxes": "Taxes",
                "total_cost": "Total Cost"
            },
            "auth": {
                "username": "Username",
                "password": "Password",
                "email": "Email",
                "login": "Login",
                "logout": "Logout",
                "register": "Register",
                "forgot_password": "Forgot Password?",
                "reset_password": "Reset Password",
                "change_password": "Change Password"
            },
            "errors": {
                "404": "Page Not Found",
                "500": "Internal Server Error",
                "invalid_input": "Invalid Input",
                "required_field": "Required Field",
                "access_denied": "Access Denied",
                "not_found": "Not Found",
                "already_exists": "Already Exists"
            },
            "validation": {
                "required": "This field is required",
                "min_length": "Minimum length: {min}",
                "max_length": "Maximum length: {max}",
                "invalid_email": "Invalid email",
                "invalid_number": "Invalid number",
                "min_value": "Minimum value: {min}",
                "max_value": "Maximum value: {max}"
            }
        }

        # Save translations
        self._save_translation(Language.RU, russian)
        self._save_translation(Language.DE, german)
        self._save_translation(Language.EN, english)

        # Reload translations
        self._load_translations()

    def _save_translation(self, language: Language, translations: Dict):
        """Save translation file"""
        lang_file = self.locales_dir / f"{language.value}.json"
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)

    def set_language(self, language: Language):
        """Set current language"""
        if language.value in self.translations:
            self.current_language = language
        else:
            raise ValueError(f"Language '{language.value}' not supported")

    def get(self, key: str, **kwargs) -> str:
        """Get translation for key"""
        # Split key by dots for nested access
        keys = key.split('.')

        # Get translation from current language
        translation = self.translations.get(self.current_language.value, {})

        # Navigate nested structure
        for k in keys:
            if isinstance(translation, dict):
                translation = translation.get(k)
            else:
                translation = None
                break

        # Fallback to default language if not found
        if translation is None:
            translation = self.translations.get(self.default_language.value, {})
            for k in keys:
                if isinstance(translation, dict):
                    translation = translation.get(k)
                else:
                    translation = None
                    break

        # Fallback to key itself if still not found
        if translation is None:
            translation = key

        # Format with kwargs if provided
        if isinstance(translation, str) and kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return translation

    def get_all_languages(self) -> Dict[str, str]:
        """Get all available languages"""
        return {
            Language.RU.value: "Русский",
            Language.DE.value: "Deutsch",
            Language.EN.value: "English",
            Language.UK.value: "Українська",
            Language.PL.value: "Polski",
            Language.FR.value: "Français"
        }

    def get_current_language(self) -> Language:
        """Get current language"""
        return self.current_language

    def get_translation_keys(self) -> list:
        """Get all translation keys"""
        def extract_keys(d, prefix=''):
            keys = []
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    keys.extend(extract_keys(v, full_key))
                else:
                    keys.append(full_key)
            return keys

        if self.current_language.value in self.translations:
            return extract_keys(self.translations[self.current_language.value])
        return []


# Global instance
_i18n_manager: Optional[I18nManager] = None


def get_i18n() -> I18nManager:
    """Get global i18n manager instance"""
    global _i18n_manager

    if _i18n_manager is None:
        _i18n_manager = I18nManager()

    return _i18n_manager


def _(key: str, **kwargs) -> str:
    """Shortcut for getting translation"""
    return get_i18n().get(key, **kwargs)


def set_language(language: Language):
    """Set current language"""
    get_i18n().set_language(language)


def get_current_language() -> Language:
    """Get current language"""
    return get_i18n().get_current_language()
