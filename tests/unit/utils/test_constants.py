"""
Comprehensive tests for Constants Module

Tests cover:
- Template blocks structure and completeness
- Service types definitions
- Insurance rates (health, pension, unemployment, etc.)
- Umlages (additional contributions)
- Surcharges (night, weekend, holiday, urgent)
- Regional coefficients for German states
- Funding sources list
- Export formats
- Database and file paths
- Validation patterns (regex)
- Calculation modes and surcharge bases
- CLI colors and icons
- Default configuration template
"""

import pytest
import re

from src.utils.constants import (
    TEMPLATE_BLOCKS,
    SERVICE_TYPES,
    DEFAULT_INSURANCE_RATES,
    DEFAULT_UMLAGES,
    DEFAULT_SURCHARGES,
    REGIONAL_COEFFICIENTS,
    FUNDING_SOURCES,
    EXPORT_FORMATS,
    DATABASE_FILE,
    DATABASE_SCHEMA_VERSION,
    TEMPLATE_FILE,
    CONFIG_DIR,
    EXAMPLES_DIR,
    EXPORTS_DIR,
    TEMPLATES_DIR,
    VARIABLE_PATTERN,
    DATE_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    CALCULATION_MODES,
    SURCHARGE_BASES,
    COLORS,
    ICONS,
    DEFAULT_CONFIG,
)


class TestTemplateBlocks:
    """Test template blocks structure"""

    def test_template_blocks_exists(self):
        """Test TEMPLATE_BLOCKS exists and is a dict"""
        assert TEMPLATE_BLOCKS is not None
        assert isinstance(TEMPLATE_BLOCKS, dict)

    def test_template_blocks_count(self):
        """Test template blocks has correct number of entries"""
        assert len(TEMPLATE_BLOCKS) == 11

    def test_template_blocks_keys(self):
        """Test template blocks has sequential integer keys 0-10"""
        expected_keys = list(range(11))
        actual_keys = sorted(TEMPLATE_BLOCKS.keys())
        assert actual_keys == expected_keys

    def test_template_blocks_values_are_strings(self):
        """Test all template block values are strings"""
        for value in TEMPLATE_BLOCKS.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_template_blocks_contain_russian_text(self):
        """Test template blocks contain Russian characters"""
        # At least some blocks should have Russian characters
        has_cyrillic = any(any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in value)
                          for value in TEMPLATE_BLOCKS.values())
        assert has_cyrillic is True


class TestServiceTypes:
    """Test service types definitions"""

    def test_service_types_exists(self):
        """Test SERVICE_TYPES exists and is a dict"""
        assert SERVICE_TYPES is not None
        assert isinstance(SERVICE_TYPES, dict)

    def test_service_types_keys(self):
        """Test service types has expected keys"""
        expected_keys = {"domestic", "social", "medical", "professional", "educational"}
        actual_keys = set(SERVICE_TYPES.keys())
        assert actual_keys == expected_keys

    def test_service_types_values_are_strings(self):
        """Test all service type values are strings"""
        for value in SERVICE_TYPES.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_service_types_contain_descriptions(self):
        """Test service types contain both Russian and German text"""
        for value in SERVICE_TYPES.values():
            # Should contain Russian text and German text in parentheses
            assert "(" in value and ")" in value


class TestInsuranceRates:
    """Test insurance rates structure and values"""

    def test_insurance_rates_exists(self):
        """Test DEFAULT_INSURANCE_RATES exists"""
        assert DEFAULT_INSURANCE_RATES is not None
        assert isinstance(DEFAULT_INSURANCE_RATES, dict)

    def test_insurance_rates_keys(self):
        """Test insurance rates has expected keys"""
        expected_keys = {"kv_er", "kv_zusatz_er", "pv_er", "pv_er_sn", "rv_er", "av_er", "uv_er"}
        actual_keys = set(DEFAULT_INSURANCE_RATES.keys())
        assert actual_keys == expected_keys

    def test_insurance_rates_are_floats(self):
        """Test all insurance rates are numeric"""
        for key, value in DEFAULT_INSURANCE_RATES.items():
            assert isinstance(value, (int, float))
            assert value >= 0

    def test_insurance_rates_reasonable_ranges(self):
        """Test insurance rates are in reasonable percentage ranges"""
        for key, value in DEFAULT_INSURANCE_RATES.items():
            assert 0 <= value <= 20, f"{key} rate {value} outside reasonable range 0-20%"

    def test_specific_insurance_rates(self):
        """Test specific insurance rate values"""
        assert DEFAULT_INSURANCE_RATES["kv_er"] == 7.3  # Health insurance
        assert DEFAULT_INSURANCE_RATES["rv_er"] == 9.3  # Pension insurance
        assert DEFAULT_INSURANCE_RATES["av_er"] == 1.2  # Unemployment insurance


class TestUmlages:
    """Test umlages (additional contributions)"""

    def test_umlages_exists(self):
        """Test DEFAULT_UMLAGES exists"""
        assert DEFAULT_UMLAGES is not None
        assert isinstance(DEFAULT_UMLAGES, dict)

    def test_umlages_keys(self):
        """Test umlages has expected keys"""
        expected_keys = {"u1", "u2", "u3"}
        actual_keys = set(DEFAULT_UMLAGES.keys())
        assert actual_keys == expected_keys

    def test_umlages_are_numeric(self):
        """Test all umlages are numeric"""
        for key, value in DEFAULT_UMLAGES.items():
            assert isinstance(value, (int, float))
            assert value >= 0

    def test_umlages_reasonable_ranges(self):
        """Test umlages are in reasonable percentage ranges"""
        for key, value in DEFAULT_UMLAGES.items():
            assert 0 <= value <= 5, f"{key} rate {value} outside reasonable range 0-5%"


class TestSurcharges:
    """Test surcharge types and percentages"""

    def test_surcharges_exists(self):
        """Test DEFAULT_SURCHARGES exists"""
        assert DEFAULT_SURCHARGES is not None
        assert isinstance(DEFAULT_SURCHARGES, dict)

    def test_surcharges_keys(self):
        """Test surcharges has expected keys"""
        expected_keys = {"night", "weekend", "holiday", "urgent"}
        actual_keys = set(DEFAULT_SURCHARGES.keys())
        assert actual_keys == expected_keys

    def test_surcharges_are_numeric(self):
        """Test all surcharges are numeric"""
        for key, value in DEFAULT_SURCHARGES.items():
            assert isinstance(value, (int, float))
            assert value >= 0

    def test_surcharges_reasonable_ranges(self):
        """Test surcharges are reasonable percentages"""
        for key, value in DEFAULT_SURCHARGES.items():
            assert 0 <= value <= 200, f"{key} surcharge {value} outside reasonable range"

    def test_surcharge_hierarchy(self):
        """Test surcharges follow expected hierarchy"""
        # Holiday should typically be highest
        assert DEFAULT_SURCHARGES["holiday"] >= DEFAULT_SURCHARGES["weekend"]
        assert DEFAULT_SURCHARGES["weekend"] >= DEFAULT_SURCHARGES["night"]


class TestRegionalCoefficients:
    """Test regional coefficients for German states"""

    def test_regional_coefficients_exists(self):
        """Test REGIONAL_COEFFICIENTS exists"""
        assert REGIONAL_COEFFICIENTS is not None
        assert isinstance(REGIONAL_COEFFICIENTS, dict)

    def test_regional_coefficients_count(self):
        """Test has 16 German states"""
        assert len(REGIONAL_COEFFICIENTS) == 16

    def test_regional_coefficients_are_numeric(self):
        """Test all coefficients are numeric"""
        for state, value in REGIONAL_COEFFICIENTS.items():
            assert isinstance(value, (int, float))
            assert value > 0

    def test_regional_coefficients_reasonable_ranges(self):
        """Test coefficients are in reasonable range"""
        for state, value in REGIONAL_COEFFICIENTS.items():
            assert 0.5 <= value <= 2.0, f"{state} coefficient {value} outside reasonable range"

    def test_specific_states_exist(self):
        """Test specific major states exist"""
        major_states = ["Bayern", "Berlin", "Hamburg", "Baden-Württemberg"]
        for state in major_states:
            assert state in REGIONAL_COEFFICIENTS

    def test_expensive_regions(self):
        """Test expensive regions have higher coefficients"""
        # Hamburg and Berlin should be among the highest
        assert REGIONAL_COEFFICIENTS["Hamburg"] >= 1.20
        assert REGIONAL_COEFFICIENTS["Berlin"] >= 1.15


class TestFundingSources:
    """Test funding sources list"""

    def test_funding_sources_exists(self):
        """Test FUNDING_SOURCES exists"""
        assert FUNDING_SOURCES is not None
        assert isinstance(FUNDING_SOURCES, list)

    def test_funding_sources_count(self):
        """Test has expected number of funding sources"""
        assert len(FUNDING_SOURCES) == 7

    def test_funding_sources_are_strings(self):
        """Test all funding sources are strings"""
        for source in FUNDING_SOURCES:
            assert isinstance(source, str)
            assert len(source) > 0

    def test_specific_funding_sources(self):
        """Test specific funding sources exist"""
        expected_sources = ["Eingliederungshilfe", "Pflegekasse", "Selbstzahler"]
        for source in expected_sources:
            assert source in FUNDING_SOURCES


class TestExportFormats:
    """Test export formats"""

    def test_export_formats_exists(self):
        """Test EXPORT_FORMATS exists"""
        assert EXPORT_FORMATS is not None
        assert isinstance(EXPORT_FORMATS, dict)

    def test_export_formats_keys(self):
        """Test export formats has expected keys"""
        expected_keys = {"txt", "md", "html", "pdf", "docx", "json", "yaml"}
        actual_keys = set(EXPORT_FORMATS.keys())
        assert actual_keys == expected_keys

    def test_export_formats_values_are_strings(self):
        """Test all format descriptions are strings"""
        for key, value in EXPORT_FORMATS.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_specific_format_descriptions(self):
        """Test specific format descriptions"""
        assert EXPORT_FORMATS["pdf"] == "PDF"
        assert EXPORT_FORMATS["json"] == "JSON"
        assert "Word" in EXPORT_FORMATS["docx"]


class TestDatabaseAndFilePaths:
    """Test database and file path constants"""

    def test_database_file_exists(self):
        """Test DATABASE_FILE is defined"""
        assert DATABASE_FILE is not None
        assert isinstance(DATABASE_FILE, str)
        assert len(DATABASE_FILE) > 0

    def test_database_file_path(self):
        """Test database file has correct path"""
        assert "data" in DATABASE_FILE
        assert DATABASE_FILE.endswith(".db")

    def test_database_schema_version(self):
        """Test database schema version is defined"""
        assert DATABASE_SCHEMA_VERSION is not None
        assert isinstance(DATABASE_SCHEMA_VERSION, int)
        assert DATABASE_SCHEMA_VERSION > 0

    def test_template_file_defined(self):
        """Test template file is defined"""
        assert TEMPLATE_FILE is not None
        assert isinstance(TEMPLATE_FILE, str)

    def test_directory_paths_defined(self):
        """Test all directory paths are defined"""
        paths = [CONFIG_DIR, EXAMPLES_DIR, EXPORTS_DIR, TEMPLATES_DIR]
        for path in paths:
            assert path is not None
            assert isinstance(path, str)
            assert len(path) > 0


class TestValidationPatterns:
    """Test regex validation patterns"""

    def test_variable_pattern_exists(self):
        """Test VARIABLE_PATTERN is defined"""
        assert VARIABLE_PATTERN is not None
        assert isinstance(VARIABLE_PATTERN, str)

    def test_variable_pattern_matches_valid(self):
        """Test variable pattern matches valid variables"""
        pattern = re.compile(VARIABLE_PATTERN)

        valid_variables = ["{Variable_Name}", "{test123}", "{ABC}"]
        for var in valid_variables:
            assert pattern.search(var) is not None

    def test_variable_pattern_rejects_invalid(self):
        """Test variable pattern rejects invalid variables"""
        pattern = re.compile(VARIABLE_PATTERN)

        invalid_variables = ["{}", "{with-dash}", "{with space}"]
        for var in invalid_variables:
            assert pattern.search(var) is None

    def test_date_pattern_matches_valid(self):
        """Test date pattern matches valid dates"""
        pattern = re.compile(DATE_PATTERN)

        valid_dates = ["01.01.2024", "31.12.2025", "15.06.2026"]
        for date in valid_dates:
            assert pattern.search(date) is not None

    def test_email_pattern_matches_valid(self):
        """Test email pattern matches valid emails"""
        pattern = re.compile(EMAIL_PATTERN)

        valid_emails = ["user@example.com", "test.user@domain.co.uk", "admin+tag@site.org"]
        for email in valid_emails:
            assert pattern.match(email) is not None

    def test_email_pattern_rejects_invalid(self):
        """Test email pattern rejects invalid emails"""
        pattern = re.compile(EMAIL_PATTERN)

        invalid_emails = ["notanemail", "@example.com", "user@", "user @example.com"]
        for email in invalid_emails:
            assert pattern.match(email) is None

    def test_phone_pattern_matches_valid(self):
        """Test phone pattern matches valid phone numbers"""
        pattern = re.compile(PHONE_PATTERN)

        valid_phones = ["+49 151 12345678", "(030) 123-4567", "0151-12345678"]
        for phone in valid_phones:
            assert pattern.match(phone) is not None


class TestCalculationModes:
    """Test calculation modes"""

    def test_calculation_modes_exists(self):
        """Test CALCULATION_MODES exists"""
        assert CALCULATION_MODES is not None
        assert isinstance(CALCULATION_MODES, dict)

    def test_calculation_modes_keys(self):
        """Test calculation modes has expected keys"""
        expected_keys = {"with_umlages", "with_reserve"}
        actual_keys = set(CALCULATION_MODES.keys())
        assert actual_keys == expected_keys

    def test_calculation_modes_values_are_strings(self):
        """Test all mode descriptions are strings"""
        for value in CALCULATION_MODES.values():
            assert isinstance(value, str)
            assert len(value) > 0


class TestSurchargeBase:
    """Test surcharge application bases"""

    def test_surcharge_bases_exists(self):
        """Test SURCHARGE_BASES exists"""
        assert SURCHARGE_BASES is not None
        assert isinstance(SURCHARGE_BASES, dict)

    def test_surcharge_bases_keys(self):
        """Test surcharge bases has expected keys"""
        expected_keys = {"full_cost", "brutto_only"}
        actual_keys = set(SURCHARGE_BASES.keys())
        assert actual_keys == expected_keys

    def test_surcharge_bases_values_are_strings(self):
        """Test all base descriptions are strings"""
        for value in SURCHARGE_BASES.values():
            assert isinstance(value, str)
            assert len(value) > 0


class TestColors:
    """Test CLI color codes"""

    def test_colors_exists(self):
        """Test COLORS exists"""
        assert COLORS is not None
        assert isinstance(COLORS, dict)

    def test_colors_has_basic_colors(self):
        """Test COLORS has basic color codes"""
        basic_colors = ["reset", "bold", "red", "green", "yellow", "blue"]
        for color in basic_colors:
            assert color in COLORS

    def test_colors_are_ansi_codes(self):
        """Test all colors are ANSI escape codes"""
        for key, value in COLORS.items():
            assert isinstance(value, str)
            assert value.startswith("\033[")

    def test_reset_color_exists(self):
        """Test reset color is defined"""
        assert "reset" in COLORS
        assert COLORS["reset"] == "\033[0m"


class TestIcons:
    """Test CLI icons"""

    def test_icons_exists(self):
        """Test ICONS exists"""
        assert ICONS is not None
        assert isinstance(ICONS, dict)

    def test_icons_has_expected_keys(self):
        """Test ICONS has expected keys"""
        expected_keys = {"success", "error", "warning", "info", "question", "arrow", "bullet"}
        actual_keys = set(ICONS.keys())
        assert actual_keys == expected_keys

    def test_icons_are_unicode(self):
        """Test all icons are strings"""
        for key, value in ICONS.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_specific_icons(self):
        """Test specific icon values"""
        assert ICONS["success"] == "✓"
        assert ICONS["error"] == "✗"
        assert ICONS["warning"] == "⚠"


class TestDefaultConfig:
    """Test default configuration template"""

    def test_default_config_exists(self):
        """Test DEFAULT_CONFIG exists"""
        assert DEFAULT_CONFIG is not None
        assert isinstance(DEFAULT_CONFIG, dict)

    def test_default_config_top_level_keys(self):
        """Test DEFAULT_CONFIG has top-level keys"""
        expected_keys = {"basic_info", "financial", "system_settings", "funding"}
        actual_keys = set(DEFAULT_CONFIG.keys())
        assert actual_keys == expected_keys

    def test_default_config_basic_info(self):
        """Test basic_info section in default config"""
        basic_info = DEFAULT_CONFIG["basic_info"]
        assert isinstance(basic_info, dict)

        expected_fields = ["service_name", "target_group", "region", "provider_type"]
        for field in expected_fields:
            assert field in basic_info

    def test_default_config_financial(self):
        """Test financial section in default config"""
        financial = DEFAULT_CONFIG["financial"]
        assert isinstance(financial, dict)

        expected_fields = ["brutto_rate", "employer_rates", "umlages", "surcharges"]
        for field in expected_fields:
            assert field in financial

    def test_default_config_system_settings(self):
        """Test system_settings section in default config"""
        settings = DEFAULT_CONFIG["system_settings"]
        assert isinstance(settings, dict)

        assert "use_umlages" in settings
        assert "use_vacation_reserve" in settings
        assert isinstance(settings["use_umlages"], bool)
        assert isinstance(settings["use_vacation_reserve"], bool)

    def test_default_config_references_other_constants(self):
        """Test default config references other constants"""
        # employer_rates should reference DEFAULT_INSURANCE_RATES
        employer_rates = DEFAULT_CONFIG["financial"]["employer_rates"]
        assert set(employer_rates.keys()) == set(DEFAULT_INSURANCE_RATES.keys())

        # umlages should reference DEFAULT_UMLAGES
        umlages = DEFAULT_CONFIG["financial"]["umlages"]
        assert set(umlages.keys()) == set(DEFAULT_UMLAGES.keys())


class TestConstantsIntegrity:
    """Test overall constants integrity and consistency"""

    def test_no_none_values_in_dicts(self):
        """Test no None values in main dictionaries"""
        dicts_to_check = [
            SERVICE_TYPES,
            DEFAULT_INSURANCE_RATES,
            DEFAULT_UMLAGES,
            DEFAULT_SURCHARGES,
            REGIONAL_COEFFICIENTS,
            EXPORT_FORMATS,
            CALCULATION_MODES,
            SURCHARGE_BASES,
            COLORS,
            ICONS,
        ]

        for d in dicts_to_check:
            for key, value in d.items():
                assert value is not None, f"None value found for key: {key}"

    def test_no_empty_strings_in_required_fields(self):
        """Test no empty strings in descriptive fields"""
        fields_to_check = [
            SERVICE_TYPES.values(),
            EXPORT_FORMATS.values(),
            FUNDING_SOURCES,
        ]

        for field_collection in fields_to_check:
            for value in field_collection:
                assert len(value) > 0, "Empty string found in required field"

    def test_all_patterns_are_valid_regex(self):
        """Test all regex patterns are valid"""
        patterns = [VARIABLE_PATTERN, DATE_PATTERN, EMAIL_PATTERN, PHONE_PATTERN]

        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error:
                pytest.fail(f"Invalid regex pattern: {pattern}")

    def test_constants_are_immutable_types(self):
        """Test constants use appropriate immutable types where expected"""
        # These should be strings
        string_constants = [DATABASE_FILE, TEMPLATE_FILE, CONFIG_DIR]
        for const in string_constants:
            assert isinstance(const, str)

        # DATABASE_SCHEMA_VERSION should be int
        assert isinstance(DATABASE_SCHEMA_VERSION, int)
