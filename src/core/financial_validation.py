"""
Financial Validation Module

Specialized validation for financial calculator input data.
Provides comprehensive validation for monetary values, percentages,
and financial parameters.
"""

import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from src.core.input_validation import InputValidator, ValidationError
from src.utils.constants import REGIONAL_COEFFICIENTS

if TYPE_CHECKING:
    from src.models.financial import FinancialParameters

logger = logging.getLogger("dms.financial_validation")


class FinancialValidator:
    """
    Specialized validator for financial data.

    Validates monetary values, percentages, rates, and financial parameters
    with appropriate ranges and constraints.
    """

    def __init__(self):
        """Initialize financial validator."""
        self.base_validator = InputValidator()

        # Define financial validation rules
        self.rules = {
            "brutto_rate": {"min": Decimal("0"), "max": Decimal("1000000"), "description": "Brutto hourly rate"},
            "region_coefficient": {"min": Decimal("0.1"), "max": Decimal("10"), "description": "Regional coefficient"},
            "materials_cost": {"min": Decimal("0"), "max": Decimal("100000"), "description": "Materials cost per hour"},
            "admin_percent": {"min": Decimal("0"), "max": Decimal("100"), "description": "Administrative percentage"},
            "insurance_rate": {"min": Decimal("0"), "max": Decimal("100"), "description": "Insurance rate percentage"},
            "surcharge_percent": {"min": Decimal("0"), "max": Decimal("200"), "description": "Surcharge percentage"},
            "umlage_percent": {"min": Decimal("0"), "max": Decimal("10"), "description": "Umlage percentage"},
            "vacation_reserve": {
                "min": Decimal("0"),
                "max": Decimal("50"),
                "description": "Vacation reserve percentage",
            },
            "hours": {"min": Decimal("0"), "max": Decimal("10000"), "description": "Working hours"},
        }

    def validate_decimal(
        self,
        value: Any,
        param_name: str,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        allow_zero: bool = True,
    ) -> Decimal:
        """
        Validate and convert value to Decimal.

        Args:
            value: Value to validate
            param_name: Parameter name for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_zero: Whether zero is allowed

        Returns:
            Validated Decimal value

        Raises:
            ValidationError: If validation fails
        """
        # Convert to Decimal
        try:
            if isinstance(value, str):
                # Remove spaces and replace comma with dot
                value = value.strip().replace(",", ".")

            decimal_value = Decimal(str(value))
        except (ValueError, InvalidOperation) as e:
            raise ValidationError(f"{param_name} must be a valid number, got: {value}")

        # Check for NaN or Infinity
        if not decimal_value.is_finite():
            raise ValidationError(f"{param_name} must be a finite number")

        # Check if zero is allowed
        if not allow_zero and decimal_value == Decimal("0"):
            raise ValidationError(f"{param_name} cannot be zero")

        # Check minimum value
        if min_value is not None and decimal_value < min_value:
            raise ValidationError(f"{param_name} must be at least {min_value}, got: {decimal_value}")

        # Check maximum value
        if max_value is not None and decimal_value > max_value:
            raise ValidationError(f"{param_name} cannot exceed {max_value}, got: {decimal_value}")

        return decimal_value

    def validate_brutto_rate(self, value: Any) -> Decimal:
        """Validate brutto hourly rate."""
        rules = self.rules["brutto_rate"]
        return self.validate_decimal(value, rules["description"], rules["min"], rules["max"])

    def validate_region_coefficient(self, value: Any, region_name: Optional[str] = None) -> Decimal:
        """
        Validate regional coefficient.

        Args:
            value: Coefficient value
            region_name: Optional region name to validate

        Returns:
            Validated coefficient

        Raises:
            ValidationError: If validation fails
        """
        # If region name provided, validate it exists
        if region_name is not None:
            if region_name not in REGIONAL_COEFFICIENTS:
                valid_regions = ", ".join(REGIONAL_COEFFICIENTS.keys())
                raise ValidationError(f"Invalid region: {region_name}. " f"Valid regions: {valid_regions}")
            # Use predefined coefficient
            value = REGIONAL_COEFFICIENTS[region_name]

        rules = self.rules["region_coefficient"]
        return self.validate_decimal(value, rules["description"], rules["min"], rules["max"], allow_zero=False)

    def validate_materials_cost(self, value: Any) -> Decimal:
        """Validate materials cost per hour."""
        rules = self.rules["materials_cost"]
        return self.validate_decimal(value, rules["description"], rules["min"], rules["max"])

    def validate_admin_percent(self, value: Any) -> Decimal:
        """Validate administrative percentage."""
        rules = self.rules["admin_percent"]
        return self.validate_decimal(value, rules["description"], rules["min"], rules["max"])

    def validate_insurance_rate(self, rate_name: str, value: Any) -> Decimal:
        """
        Validate insurance rate.

        Args:
            rate_name: Name of insurance rate (KV, PV, RV, AV, UV, and variants)
            value: Rate percentage

        Returns:
            Validated rate

        Raises:
            ValidationError: If validation fails
        """
        # Normalize rate name (check if starts with valid prefix)
        rate_prefix = rate_name.upper().split()[0]  # "KV zusatz" -> "KV"
        valid_rates = ["KV", "PV", "RV", "AV", "UV"]

        if rate_prefix not in valid_rates:
            raise ValidationError(f"Invalid insurance rate name: {rate_name}. " f"Valid: {', '.join(valid_rates)}")

        rules = self.rules["insurance_rate"]
        return self.validate_decimal(value, f"{rate_name} {rules['description']}", rules["min"], rules["max"])

    def validate_surcharge(self, surcharge_type: str, value: Any) -> Decimal:
        """
        Validate surcharge percentage.

        Args:
            surcharge_type: Type of surcharge (night, weekend, holiday, urgent)
            value: Surcharge percentage

        Returns:
            Validated surcharge

        Raises:
            ValidationError: If validation fails
        """
        valid_types = ["night", "weekend", "holiday", "urgent"]
        if surcharge_type not in valid_types:
            raise ValidationError(f"Invalid surcharge type: {surcharge_type}. " f"Valid: {', '.join(valid_types)}")

        rules = self.rules["surcharge_percent"]
        return self.validate_decimal(value, f"{surcharge_type} surcharge", rules["min"], rules["max"])

    def validate_umlage(self, umlage_type: str, value: Any) -> Decimal:
        """
        Validate umlage percentage.

        Args:
            umlage_type: Type of umlage (U1, U2, U3)
            value: Umlage percentage

        Returns:
            Validated umlage

        Raises:
            ValidationError: If validation fails
        """
        valid_types = ["U1", "U2", "U3"]
        if umlage_type.upper() not in valid_types:
            raise ValidationError(f"Invalid umlage type: {umlage_type}. " f"Valid: {', '.join(valid_types)}")

        rules = self.rules["umlage_percent"]
        return self.validate_decimal(value, f"{umlage_type} umlage", rules["min"], rules["max"])

    def validate_vacation_reserve(self, value: Any) -> Decimal:
        """Validate vacation reserve percentage."""
        rules = self.rules["vacation_reserve"]
        return self.validate_decimal(value, rules["description"], rules["min"], rules["max"])

    def validate_hours(self, value: Any) -> Decimal:
        """Validate working hours."""
        rules = self.rules["hours"]
        decimal_hours = self.validate_decimal(value, rules["description"], rules["min"], rules["max"])

        # Additional check: hours should be reasonable (warn if > 100)
        if decimal_hours > Decimal("100"):
            logger.warning(f"Hours value is unusually high: {decimal_hours}. " "Please verify this is correct.")

        return decimal_hours

    def validate_config_file(self, config_path: str) -> Dict[str, Any]:
        """
        Validate configuration file exists and is readable.

        Args:
            config_path: Path to configuration file

        Returns:
            Loaded configuration

        Raises:
            ValidationError: If file is invalid
        """
        path = Path(config_path)

        # Check file exists and is readable
        if not path.exists():
            raise ValidationError(f"Config file does not exist: {config_path}")

        # Validate file path
        try:
            self.base_validator.validate_file_path(config_path)
        except ValidationError as e:
            raise ValidationError(f"Invalid config file: {e}")

        # Check file extension
        valid_extensions = [".yaml", ".yml", ".json"]
        if path.suffix.lower() not in valid_extensions:
            raise ValidationError(f"Config file must be YAML or JSON, got: {path.suffix}")

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        try:
            file_size = path.stat().st_size
        except (FileNotFoundError, OSError) as e:
            raise ValidationError(f"Cannot access config file: {e}")

        if file_size > max_size:
            raise ValidationError(f"Config file too large: {file_size} bytes (max: {max_size})")

        # Try to load and parse the file
        try:
            from src.utils.helpers import load_config

            config = load_config(config_path)
        except Exception as e:
            raise ValidationError(f"Failed to parse config file: {e}")

        if not isinstance(config, dict):
            raise ValidationError("Config file must contain a dictionary/object")

        logger.info(f"Config file validated: {config_path}")
        return config

    def validate_cli_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate command-line arguments.

        Args:
            args: Dictionary of CLI arguments

        Returns:
            Validated arguments

        Raises:
            ValidationError: If arguments are invalid
        """
        validated = {}

        # Validate brutto rate
        if "brutto" in args and args["brutto"] is not None:
            validated["brutto"] = self.validate_brutto_rate(args["brutto"])

        # Validate region coefficient
        if "coefficient" in args and args["coefficient"] is not None:
            validated["coefficient"] = self.validate_region_coefficient(args["coefficient"])

        # Validate region name
        if "region" in args and args["region"] is not None:
            validated["region"] = args["region"]
            validated["coefficient"] = self.validate_region_coefficient(None, region_name=args["region"])

        # Validate materials cost
        if "materials" in args and args["materials"] is not None:
            validated["materials"] = self.validate_materials_cost(args["materials"])

        # Validate admin percentage
        if "admin" in args and args["admin"] is not None:
            validated["admin"] = self.validate_admin_percent(args["admin"])

        # Validate hours
        if "hours" in args and args["hours"] is not None:
            validated["hours"] = self.validate_hours(args["hours"])

        # Validate surcharges
        if "surcharge" in args and args["surcharge"] is not None:
            surcharges = args["surcharge"] if isinstance(args["surcharge"], list) else [args["surcharge"]]
            for surcharge_type in surcharges:
                self.validate_surcharge(surcharge_type, 25)  # Just validate type
            validated["surcharge"] = surcharges

        # Validate mode
        if "mode" in args and args["mode"] is not None:
            valid_modes = ["umlages", "reserve", "compare"]
            if args["mode"] not in valid_modes:
                raise ValidationError(f"Invalid mode: {args['mode']}. " f"Valid: {', '.join(valid_modes)}")
            validated["mode"] = args["mode"]

        # Validate config file
        if "config" in args and args["config"] is not None:
            validated["config"] = self.validate_config_file(args["config"])

        logger.debug(f"CLI arguments validated: {len(validated)} parameters")
        return validated

    def validate_financial_parameters(self, params: "FinancialParameters") -> None:
        """
        Validate all financial parameters comprehensively.

        Args:
            params: FinancialParameters object to validate

        Raises:
            ValidationError: If any parameter is invalid
        """
        # Validate brutto rate
        self.validate_brutto_rate(params.brutto_rate)

        # Validate region coefficient
        self.validate_region_coefficient(params.region_coefficient)

        # Validate materials cost
        if params.materials_per_hour is not None:
            self.validate_materials_cost(params.materials_per_hour)

        # Validate admin costs
        if params.admin_percent is not None and params.admin_percent > 0:
            self.validate_admin_percent(params.admin_percent)

        # Validate insurance rates
        insurance_rates = [
            ("KV", params.insurance_rates.kv_er),
            ("KV zusatz", params.insurance_rates.kv_zusatz_er),
            ("PV", params.insurance_rates.pv_er),
            ("PV (Saxony)", params.insurance_rates.pv_er_sn),
            ("RV", params.insurance_rates.rv_er),
            ("AV", params.insurance_rates.av_er),
            ("UV", params.insurance_rates.uv_er),
        ]

        for rate_name, rate_value in insurance_rates:
            if rate_value is not None:
                self.validate_insurance_rate(rate_name, rate_value)

        # Validate umlages
        if params.umlages:
            self.validate_umlage("U1", params.umlages.u1)
            self.validate_umlage("U2", params.umlages.u2)
            self.validate_umlage("U3", params.umlages.u3)

        # Validate vacation reserve
        if params.vacation_reserve_percent is not None:
            self.validate_vacation_reserve(params.vacation_reserve_percent)

        # Validate mutually exclusive options
        if params.use_umlages and params.use_vacation_reserve:
            logger.warning("Both use_umlages and use_vacation_reserve are enabled. " "Using umlages mode by default.")

        logger.info("All financial parameters validated successfully")


# Global instance
financial_validator = FinancialValidator()


# Example usage
if __name__ == "__main__":
    import json

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    validator = FinancialValidator()

    # Test validations
    print("\n" + "=" * 60)
    print("Financial Validator Tests")
    print("=" * 60 + "\n")

    # Test brutto rate
    try:
        rate = validator.validate_brutto_rate(25.5)
        print(f"✓ Brutto rate: {rate}")
    except ValidationError as e:
        print(f"✗ Error: {e}")

    # Test invalid rate
    try:
        rate = validator.validate_brutto_rate(-10)
        print(f"✓ Negative rate: {rate}")
    except ValidationError as e:
        print(f"✓ Caught invalid rate: {e}")

    # Test region coefficient
    try:
        coef = validator.validate_region_coefficient(None, region_name="Bayern")
        print(f"✓ Bayern coefficient: {coef}")
    except ValidationError as e:
        print(f"✗ Error: {e}")

    # Test invalid region
    try:
        coef = validator.validate_region_coefficient(None, region_name="InvalidRegion")
    except ValidationError as e:
        print(f"✓ Caught invalid region: {e}")

    # Test CLI args validation
    test_args = {"brutto": 25.0, "region": "Bayern", "materials": 5.0, "admin": 10.0, "hours": 40.0, "mode": "umlages"}

    try:
        validated = validator.validate_cli_args(test_args)
        print(f"\n✓ CLI args validated: {len(validated)} parameters")
        print(json.dumps({k: str(v) for k, v in validated.items()}, indent=2))
    except ValidationError as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("All tests completed")
    print("=" * 60 + "\n")
