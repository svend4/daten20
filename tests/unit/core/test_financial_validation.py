"""
Tests for financial validation module.
"""

import os
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from src.core.financial_validation import FinancialValidator
from src.core.input_validation import ValidationError


@pytest.fixture
def validator():
    """Create validator instance."""
    return FinancialValidator()


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    # Cleanup
    import shutil

    try:
        shutil.rmtree(tmpdir)
    except:
        pass


class TestDecimalValidation:
    """Tests for decimal validation."""

    def test_validate_decimal_valid_int(self, validator):
        """Test validating integer."""
        result = validator.validate_decimal(25, "test_param")
        assert result == Decimal("25")
        assert isinstance(result, Decimal)

    def test_validate_decimal_valid_float(self, validator):
        """Test validating float."""
        result = validator.validate_decimal(25.5, "test_param")
        assert result == Decimal("25.5")

    def test_validate_decimal_valid_string(self, validator):
        """Test validating string number."""
        result = validator.validate_decimal("25.5", "test_param")
        assert result == Decimal("25.5")

    def test_validate_decimal_string_with_comma(self, validator):
        """Test validating string with comma."""
        result = validator.validate_decimal("25,5", "test_param")
        assert result == Decimal("25.5")

    def test_validate_decimal_invalid_string(self, validator):
        """Test invalid string raises error."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal("abc", "test_param")
        assert "must be a valid number" in str(exc.value)

    def test_validate_decimal_nan(self, validator):
        """Test NaN raises error."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal(float("nan"), "test_param")
        assert "must be a finite number" in str(exc.value)

    def test_validate_decimal_infinity(self, validator):
        """Test infinity raises error."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal(float("inf"), "test_param")
        assert "must be a finite number" in str(exc.value)

    def test_validate_decimal_min_value(self, validator):
        """Test minimum value validation."""
        result = validator.validate_decimal(10, "test_param", min_value=Decimal("0"))
        assert result == Decimal("10")

        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal(-5, "test_param", min_value=Decimal("0"))
        assert "must be at least 0" in str(exc.value)

    def test_validate_decimal_max_value(self, validator):
        """Test maximum value validation."""
        result = validator.validate_decimal(50, "test_param", max_value=Decimal("100"))
        assert result == Decimal("50")

        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal(150, "test_param", max_value=Decimal("100"))
        assert "cannot exceed 100" in str(exc.value)

    def test_validate_decimal_zero_not_allowed(self, validator):
        """Test zero not allowed."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_decimal(0, "test_param", allow_zero=False)
        assert "cannot be zero" in str(exc.value)


class TestBruttoRateValidation:
    """Tests for brutto rate validation."""

    def test_validate_brutto_rate_valid(self, validator):
        """Test valid brutto rate."""
        result = validator.validate_brutto_rate(25.0)
        assert result == Decimal("25.0")

    def test_validate_brutto_rate_zero(self, validator):
        """Test zero brutto rate."""
        result = validator.validate_brutto_rate(0)
        assert result == Decimal("0")

    def test_validate_brutto_rate_negative(self, validator):
        """Test negative brutto rate raises error."""
        with pytest.raises(ValidationError):
            validator.validate_brutto_rate(-10)

    def test_validate_brutto_rate_exceeds_max(self, validator):
        """Test exceeding maximum."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_brutto_rate(2000000)
        assert "cannot exceed 1000000" in str(exc.value)


class TestRegionCoefficientValidation:
    """Tests for region coefficient validation."""

    def test_validate_coefficient_valid(self, validator):
        """Test valid coefficient."""
        result = validator.validate_region_coefficient(1.5)
        assert result == Decimal("1.5")

    def test_validate_coefficient_by_region_name(self, validator):
        """Test validation by region name."""
        result = validator.validate_region_coefficient(None, region_name="Bayern")
        assert result > Decimal("1.0")  # Bayern has coefficient > 1.0

    def test_validate_coefficient_invalid_region(self, validator):
        """Test invalid region name."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_region_coefficient(None, region_name="InvalidRegion")
        assert "Invalid region" in str(exc.value)

    def test_validate_coefficient_too_small(self, validator):
        """Test coefficient too small."""
        with pytest.raises(ValidationError):
            validator.validate_region_coefficient(0.05)

    def test_validate_coefficient_too_large(self, validator):
        """Test coefficient too large."""
        with pytest.raises(ValidationError):
            validator.validate_region_coefficient(15)

    def test_validate_coefficient_zero_not_allowed(self, validator):
        """Test zero coefficient."""
        with pytest.raises(ValidationError):
            validator.validate_region_coefficient(0)


class TestInsuranceRateValidation:
    """Tests for insurance rate validation."""

    def test_validate_insurance_rate_valid(self, validator):
        """Test valid insurance rate."""
        result = validator.validate_insurance_rate("KV", 7.3)
        assert result == Decimal("7.3")

    def test_validate_insurance_rate_with_zusatz(self, validator):
        """Test KV zusatz rate."""
        result = validator.validate_insurance_rate("KV zusatz", 1.3)
        assert result == Decimal("1.3")

    def test_validate_insurance_rate_invalid_name(self, validator):
        """Test invalid rate name."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_insurance_rate("INVALID", 5.0)
        assert "Invalid insurance rate name" in str(exc.value)

    def test_validate_insurance_rate_negative(self, validator):
        """Test negative rate."""
        with pytest.raises(ValidationError):
            validator.validate_insurance_rate("KV", -5)

    def test_validate_insurance_rate_exceeds_max(self, validator):
        """Test exceeding maximum."""
        with pytest.raises(ValidationError):
            validator.validate_insurance_rate("KV", 150)


class TestSurchargeValidation:
    """Tests for surcharge validation."""

    def test_validate_surcharge_valid(self, validator):
        """Test valid surcharge."""
        result = validator.validate_surcharge("night", 25)
        assert result == Decimal("25")

    def test_validate_surcharge_all_types(self, validator):
        """Test all surcharge types."""
        for surcharge_type in ["night", "weekend", "holiday", "urgent"]:
            result = validator.validate_surcharge(surcharge_type, 25)
            assert result == Decimal("25")

    def test_validate_surcharge_invalid_type(self, validator):
        """Test invalid surcharge type."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_surcharge("invalid_type", 25)
        assert "Invalid surcharge type" in str(exc.value)

    def test_validate_surcharge_negative(self, validator):
        """Test negative surcharge."""
        with pytest.raises(ValidationError):
            validator.validate_surcharge("night", -10)

    def test_validate_surcharge_exceeds_max(self, validator):
        """Test exceeding maximum."""
        with pytest.raises(ValidationError):
            validator.validate_surcharge("night", 250)


class TestUmlageValidation:
    """Tests for umlage validation."""

    def test_validate_umlage_valid(self, validator):
        """Test valid umlage."""
        result = validator.validate_umlage("U1", 2.5)
        assert result == Decimal("2.5")

    def test_validate_umlage_all_types(self, validator):
        """Test all umlage types."""
        for umlage_type in ["U1", "U2", "U3"]:
            result = validator.validate_umlage(umlage_type, 1.5)
            assert result == Decimal("1.5")

    def test_validate_umlage_case_insensitive(self, validator):
        """Test case insensitive umlage type."""
        result = validator.validate_umlage("u1", 2.5)
        assert result == Decimal("2.5")

    def test_validate_umlage_invalid_type(self, validator):
        """Test invalid umlage type."""
        with pytest.raises(ValidationError):
            validator.validate_umlage("U4", 1.5)

    def test_validate_umlage_negative(self, validator):
        """Test negative umlage."""
        with pytest.raises(ValidationError):
            validator.validate_umlage("U1", -1)

    def test_validate_umlage_exceeds_max(self, validator):
        """Test exceeding maximum."""
        with pytest.raises(ValidationError):
            validator.validate_umlage("U1", 15)


class TestHoursValidation:
    """Tests for hours validation."""

    def test_validate_hours_valid(self, validator):
        """Test valid hours."""
        result = validator.validate_hours(40)
        assert result == Decimal("40")

    def test_validate_hours_zero(self, validator):
        """Test zero hours."""
        result = validator.validate_hours(0)
        assert result == Decimal("0")

    def test_validate_hours_decimal(self, validator):
        """Test decimal hours."""
        result = validator.validate_hours(37.5)
        assert result == Decimal("37.5")

    def test_validate_hours_negative(self, validator):
        """Test negative hours."""
        with pytest.raises(ValidationError):
            validator.validate_hours(-10)

    def test_validate_hours_exceeds_max(self, validator):
        """Test exceeding maximum."""
        with pytest.raises(ValidationError):
            validator.validate_hours(15000)

    def test_validate_hours_warning_on_high_value(self, validator, caplog):
        """Test warning logged for high hours."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = validator.validate_hours(150)
        assert result == Decimal("150")
        assert "unusually high" in caplog.text


class TestConfigFileValidation:
    """Tests for config file validation."""

    def test_validate_config_file_yaml_valid(self, validator, temp_dir):
        """Test valid YAML config file."""
        config_file = os.path.join(temp_dir, "config.yaml")
        with open(config_file, "w") as f:
            f.write("brutto_rate: 25.0\n")

        result = validator.validate_config_file(config_file)
        assert isinstance(result, dict)

    def test_validate_config_file_json_valid(self, validator, temp_dir):
        """Test valid JSON config file."""
        config_file = os.path.join(temp_dir, "config.json")
        with open(config_file, "w") as f:
            f.write('{"brutto_rate": 25.0}')

        result = validator.validate_config_file(config_file)
        assert isinstance(result, dict)

    def test_validate_config_file_not_exists(self, validator):
        """Test non-existent file."""
        with pytest.raises(ValidationError) as exc:
            validator.validate_config_file("/nonexistent/config.yaml")
        assert "does not exist" in str(exc.value)

    def test_validate_config_file_invalid_extension(self, validator, temp_dir):
        """Test invalid file extension."""
        config_file = os.path.join(temp_dir, "config.txt")
        with open(config_file, "w") as f:
            f.write("test")

        with pytest.raises(ValidationError) as exc:
            validator.validate_config_file(config_file)
        assert "must be YAML or JSON" in str(exc.value)

    def test_validate_config_file_invalid_content(self, validator, temp_dir):
        """Test invalid file content."""
        config_file = os.path.join(temp_dir, "config.yaml")
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content:")

        with pytest.raises(ValidationError) as exc:
            validator.validate_config_file(config_file)
        assert "Failed to parse" in str(exc.value)


class TestCLIArgsValidation:
    """Tests for CLI arguments validation."""

    def test_validate_cli_args_basic(self, validator):
        """Test basic CLI args validation."""
        args = {"brutto": 25.0, "hours": 40.0, "mode": "umlages"}

        result = validator.validate_cli_args(args)
        assert "brutto" in result
        assert result["brutto"] == Decimal("25.0")
        assert "hours" in result
        assert result["hours"] == Decimal("40.0")

    def test_validate_cli_args_with_region(self, validator):
        """Test CLI args with region."""
        args = {"brutto": 25.0, "region": "Bayern"}

        result = validator.validate_cli_args(args)
        assert "region" in result
        assert "coefficient" in result
        assert result["coefficient"] > Decimal("1.0")

    def test_validate_cli_args_with_coefficient(self, validator):
        """Test CLI args with coefficient."""
        args = {"brutto": 25.0, "coefficient": 1.5}

        result = validator.validate_cli_args(args)
        assert result["coefficient"] == Decimal("1.5")

    def test_validate_cli_args_with_surcharges(self, validator):
        """Test CLI args with surcharges."""
        args = {"brutto": 25.0, "surcharge": ["night", "weekend"]}

        result = validator.validate_cli_args(args)
        assert "surcharge" in result
        assert result["surcharge"] == ["night", "weekend"]

    def test_validate_cli_args_invalid_mode(self, validator):
        """Test invalid mode."""
        args = {"brutto": 25.0, "mode": "invalid_mode"}

        with pytest.raises(ValidationError) as exc:
            validator.validate_cli_args(args)
        assert "Invalid mode" in str(exc.value)

    def test_validate_cli_args_invalid_surcharge(self, validator):
        """Test invalid surcharge type."""
        args = {"brutto": 25.0, "surcharge": ["invalid_surcharge"]}

        with pytest.raises(ValidationError):
            validator.validate_cli_args(args)

    def test_validate_cli_args_with_none_values(self, validator):
        """Test args with None values."""
        args = {"brutto": 25.0, "region": None, "hours": None}

        result = validator.validate_cli_args(args)
        assert "brutto" in result
        assert "region" not in result or result["region"] is None


class TestFinancialParametersValidation:
    """Tests for complete financial parameters validation."""

    def test_validate_financial_parameters_minimal(self, validator):
        """Test minimal valid parameters."""
        from src.models.financial import FinancialParameters

        params = FinancialParameters(brutto_rate=Decimal("25.0"))
        validator.validate_financial_parameters(params)  # Should not raise

    def test_validate_financial_parameters_invalid_brutto(self, validator):
        """Test invalid brutto rate."""
        from src.models.financial import FinancialParameters

        params = FinancialParameters(brutto_rate=Decimal("-10.0"))
        with pytest.raises(ValidationError):
            validator.validate_financial_parameters(params)

    def test_validate_financial_parameters_mutually_exclusive_warning(self, validator, caplog):
        """Test warning for mutually exclusive options."""
        import logging

        from src.models.financial import FinancialParameters

        params = FinancialParameters(brutto_rate=Decimal("25.0"))
        params.use_umlages = True
        params.use_vacation_reserve = True

        with caplog.at_level(logging.WARNING):
            validator.validate_financial_parameters(params)

        assert "mutually exclusive" in caplog.text.lower() or "both" in caplog.text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
