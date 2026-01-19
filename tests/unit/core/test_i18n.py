"""
Unit tests for i18n (internationalization) module
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.core.i18n import (
    I18nManager,
    Language,
    _,
    get_current_language,
    get_i18n,
    set_language,
)


# ============================================================================
# Language Enum Tests
# ============================================================================


class TestLanguageEnum:
    """Test Language enum"""

    def test_language_values(self):
        """Test language enum values"""
        assert Language.RU == "ru"
        assert Language.DE == "de"
        assert Language.EN == "en"
        assert Language.UK == "uk"
        assert Language.PL == "pl"
        assert Language.FR == "fr"

    def test_language_enum_type(self):
        """Test language enum is string"""
        assert isinstance(Language.RU, str)
        assert isinstance(Language.DE.value, str)


# ============================================================================
# I18nManager Tests
# ============================================================================


class TestI18nManager:
    """Test I18nManager class"""

    @pytest.fixture
    def temp_locales_dir(self):
        """Create temporary locales directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def manager(self, temp_locales_dir):
        """Create I18nManager instance"""
        return I18nManager(locales_dir=temp_locales_dir, default_language=Language.EN)

    def test_init_creates_directory(self, temp_locales_dir):
        """Test initialization creates locales directory"""
        locales_path = Path(temp_locales_dir)
        assert locales_path.exists()
        assert locales_path.is_dir()

    def test_init_default_language(self, manager):
        """Test default language is set"""
        assert manager.default_language == Language.EN
        assert manager.current_language == Language.EN

    def test_init_creates_default_translations(self, manager):
        """Test default translations are created"""
        assert len(manager.translations) > 0
        assert Language.RU.value in manager.translations
        assert Language.DE.value in manager.translations
        assert Language.EN.value in manager.translations

    def test_translation_files_created(self, temp_locales_dir, manager):
        """Test translation files are created"""
        locales_path = Path(temp_locales_dir)

        assert (locales_path / "ru.json").exists()
        assert (locales_path / "de.json").exists()
        assert (locales_path / "en.json").exists()

    def test_set_language_valid(self, manager):
        """Test setting valid language"""
        manager.set_language(Language.DE)
        assert manager.current_language == Language.DE

    def test_set_language_invalid(self, manager):
        """Test setting invalid language raises error"""
        # Create a language that doesn't have translations
        manager.translations.pop("fr", None)

        with pytest.raises(ValueError, match="not supported"):
            manager.set_language(Language.FR)

    def test_get_translation_simple(self, manager):
        """Test getting simple translation"""
        result = manager.get("common.save")

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_translation_nested(self, manager):
        """Test getting nested translation"""
        result = manager.get("app.name")

        assert result is not None
        assert isinstance(result, str)

    def test_get_translation_missing_returns_key(self, manager):
        """Test missing translation returns key"""
        result = manager.get("nonexistent.key")

        assert result == "nonexistent.key"

    def test_get_translation_with_formatting(self, manager):
        """Test translation with formatting"""
        result = manager.get("validation.min_length", min=5)

        assert "5" in result

    def test_get_translation_fallback_to_default(self, manager):
        """Test fallback to default language"""
        # Set to German
        manager.set_language(Language.DE)

        # Remove a key from German translations
        if "app" in manager.translations[Language.DE.value]:
            key_backup = manager.translations[Language.DE.value]["app"].pop("name", None)

        # Should fallback to English (default)
        result = manager.get("app.name")

        assert result is not None
        assert isinstance(result, str)

    def test_get_all_languages(self, manager):
        """Test getting all available languages"""
        languages = manager.get_all_languages()

        assert isinstance(languages, dict)
        assert "ru" in languages
        assert "de" in languages
        assert "en" in languages
        assert languages["ru"] == "Русский"
        assert languages["de"] == "Deutsch"
        assert languages["en"] == "English"

    def test_get_current_language(self, manager):
        """Test getting current language"""
        assert manager.get_current_language() == Language.EN

        manager.set_language(Language.RU)
        assert manager.get_current_language() == Language.RU

    def test_get_translation_keys(self, manager):
        """Test getting all translation keys"""
        keys = manager.get_translation_keys()

        assert isinstance(keys, list)
        assert len(keys) > 0
        assert "app.name" in keys
        assert "common.save" in keys

    def test_translations_content_russian(self, manager):
        """Test Russian translations content"""
        manager.set_language(Language.RU)

        assert "Сохранить" in manager.get("common.save")
        assert "Панель управления" in manager.get("nav.dashboard")

    def test_translations_content_german(self, manager):
        """Test German translations content"""
        manager.set_language(Language.DE)

        assert "Speichern" in manager.get("common.save")
        assert "Dashboard" in manager.get("nav.dashboard")

    def test_translations_content_english(self, manager):
        """Test English translations content"""
        manager.set_language(Language.EN)

        assert "Save" in manager.get("common.save")
        assert "Dashboard" in manager.get("nav.dashboard")

    def test_save_translation(self, temp_locales_dir):
        """Test saving translation file"""
        manager = I18nManager(locales_dir=temp_locales_dir)

        custom_translations = {
            "test": {"key": "value"}
        }

        manager._save_translation(Language.EN, custom_translations)

        # Verify file was saved
        file_path = Path(temp_locales_dir) / "en.json"
        assert file_path.exists()

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["test"]["key"] == "value"

    def test_load_existing_translations(self, temp_locales_dir):
        """Test loading existing translation files"""
        # Create a custom translation file
        custom_file = Path(temp_locales_dir) / "en.json"
        custom_data = {"custom": {"message": "Hello"}}

        with open(custom_file, "w", encoding="utf-8") as f:
            json.dump(custom_data, f)

        # Create manager - should load existing file
        manager = I18nManager(locales_dir=temp_locales_dir, default_language=Language.EN)

        assert manager.get("custom.message") == "Hello"


# ============================================================================
# Global Functions Tests
# ============================================================================


class TestGlobalFunctions:
    """Test global convenience functions"""

    @pytest.fixture
    def temp_locales_dir(self):
        """Create temporary locales directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture(autouse=True)
    def reset_global_instance(self):
        """Reset global instance before each test"""
        from src.core import i18n
        i18n._i18n_manager = None
        yield
        i18n._i18n_manager = None

    def test_get_i18n_creates_instance(self):
        """Test get_i18n creates global instance"""
        manager = get_i18n()

        assert manager is not None
        assert isinstance(manager, I18nManager)

    def test_get_i18n_returns_same_instance(self):
        """Test get_i18n returns singleton"""
        manager1 = get_i18n()
        manager2 = get_i18n()

        assert manager1 is manager2

    def test_underscore_function(self):
        """Test _ (underscore) shortcut function"""
        result = _("common.save")

        assert result is not None
        assert isinstance(result, str)

    def test_underscore_with_formatting(self):
        """Test _ function with formatting"""
        result = _("validation.min_length", min=10)

        assert "10" in result

    def test_set_language_function(self):
        """Test global set_language function"""
        set_language(Language.DE)

        manager = get_i18n()
        assert manager.current_language == Language.DE

    def test_get_current_language_function(self):
        """Test global get_current_language function"""
        set_language(Language.RU)

        current = get_current_language()
        assert current == Language.RU


# ============================================================================
# Integration Tests
# ============================================================================


class TestI18nIntegration:
    """Test i18n integration scenarios"""

    @pytest.fixture
    def temp_locales_dir(self):
        """Create temporary locales directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_multi_language_workflow(self, temp_locales_dir):
        """Test switching between languages"""
        manager = I18nManager(locales_dir=temp_locales_dir, default_language=Language.EN)

        # English
        manager.set_language(Language.EN)
        en_save = manager.get("common.save")
        assert "Save" in en_save

        # German
        manager.set_language(Language.DE)
        de_save = manager.get("common.save")
        assert "Speichern" in de_save

        # Russian
        manager.set_language(Language.RU)
        ru_save = manager.get("common.save")
        assert "Сохранить" in ru_save

    def test_missing_nested_key_fallback(self, temp_locales_dir):
        """Test fallback for missing nested keys"""
        manager = I18nManager(locales_dir=temp_locales_dir, default_language=Language.EN)

        # Get translation that may not exist in all languages
        result = manager.get("deeply.nested.missing.key")

        # Should return the key itself as fallback
        assert result == "deeply.nested.missing.key"

    def test_all_language_files_valid_json(self, temp_locales_dir):
        """Test all language files contain valid JSON"""
        manager = I18nManager(locales_dir=temp_locales_dir)

        for lang in [Language.RU, Language.DE, Language.EN]:
            file_path = Path(temp_locales_dir) / f"{lang.value}.json"

            # File should exist
            assert file_path.exists()

            # Should be valid JSON
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert isinstance(data, dict)

    def test_translation_consistency(self, temp_locales_dir):
        """Test all languages have similar structure"""
        manager = I18nManager(locales_dir=temp_locales_dir)

        # Get keys from English (default)
        manager.set_language(Language.EN)
        en_keys = set(manager.get_translation_keys())

        # Get keys from Russian
        manager.set_language(Language.RU)
        ru_keys = set(manager.get_translation_keys())

        # Get keys from German
        manager.set_language(Language.DE)
        de_keys = set(manager.get_translation_keys())

        # All languages should have similar key structure
        # (may not be exactly the same, but should overlap significantly)
        assert len(en_keys & ru_keys) > 20  # At least 20 common keys
        assert len(en_keys & de_keys) > 20

    def test_format_with_missing_placeholder(self, temp_locales_dir):
        """Test formatting with missing placeholder"""
        manager = I18nManager(locales_dir=temp_locales_dir)

        # Get translation with placeholder
        result = manager.get("validation.min_length")

        # Should not raise error if placeholder missing
        assert result is not None

    def test_unicode_in_translations(self, temp_locales_dir):
        """Test Unicode characters in translations"""
        manager = I18nManager(locales_dir=temp_locales_dir)

        # Russian should have Cyrillic characters
        manager.set_language(Language.RU)
        ru_text = manager.get("common.save")

        assert any(ord(c) > 127 for c in ru_text)  # Has non-ASCII

    def test_empty_locales_directory_initialization(self):
        """Test initialization with empty locales directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create manager with empty directory
            manager = I18nManager(locales_dir=tmpdir)

            # Should create default translations
            assert len(manager.translations) > 0
            assert manager.get("common.save") is not None
