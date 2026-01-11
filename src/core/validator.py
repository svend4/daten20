"""Validation utilities for template data"""

from typing import Dict, Any, List
from ..models.template import ValidationResult, Variable
from ..utils.helpers import (
    validate_date, validate_email, validate_phone,
    validate_required_fields, parse_number
)


class TemplateValidator:
    """Validator for template data"""

    def __init__(self):
        """Initialize validator"""
        pass

    def validate_variable(self, variable: Variable) -> ValidationResult:
        """
        Validate a single variable

        Args:
            variable: Variable to validate

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Check if required variable has value
        if variable.required and variable.value is None:
            result.add_missing(variable.name)
            return result

        # If no value, skip type validation
        if variable.value is None:
            return result

        # Validate based on data type
        value = variable.value

        if variable.data_type == "date":
            if not validate_date(value):
                result.add_invalid(variable.name, "Invalid date format. Use DD.MM.YYYY")

        elif variable.data_type == "email":
            if not validate_email(value):
                result.add_invalid(variable.name, "Invalid email address")

        elif variable.data_type == "phone":
            if not validate_phone(value):
                result.add_invalid(variable.name, "Invalid phone number")

        elif variable.data_type == "number":
            if parse_number(value) is None:
                result.add_invalid(variable.name, "Invalid number format")

        elif variable.data_type == "percentage":
            num = parse_number(value)
            if num is None or num < 0 or num > 100:
                result.add_invalid(variable.name, "Invalid percentage (must be 0-100)")

        return result

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate service configuration

        Args:
            config: Configuration dictionary

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        # Required fields
        required = [
            "basic_info.service_name",
            "basic_info.target_group",
            "basic_info.region",
            "financial.brutto_rate"
        ]

        missing = validate_required_fields(config, required)
        for field in missing:
            result.add_missing(field)

        # Validate financial data
        if "financial" in config:
            self._validate_financial(config["financial"], result)

        # Validate system settings
        if "system_settings" in config:
            self._validate_system_settings(config["system_settings"], result)

        return result

    def _validate_financial(self, financial: Dict[str, Any], result: ValidationResult) -> None:
        """Validate financial parameters"""
        # Check brutto_rate
        if "brutto_rate" in financial:
            rate = parse_number(str(financial["brutto_rate"]))
            if rate is None or rate <= 0:
                result.add_invalid("financial.brutto_rate", "Must be a positive number")

        # Validate insurance rates
        if "insurance_rates" in financial:
            for key, value in financial["insurance_rates"].items():
                num = parse_number(str(value))
                if num is None or num < 0 or num > 100:
                    result.add_invalid(f"financial.insurance_rates.{key}",
                                       "Must be a percentage between 0 and 100")

        # Validate umlages
        if "umlages" in financial:
            for key, value in financial["umlages"].items():
                num = parse_number(str(value))
                if num is None or num < 0 or num > 100:
                    result.add_invalid(f"financial.umlages.{key}",
                                       "Must be a percentage between 0 and 100")

        # Validate region coefficient
        if "region_coefficient" in financial:
            coef = parse_number(str(financial["region_coefficient"]))
            if coef is None or coef <= 0 or coef > 3:
                result.add_invalid("financial.region_coefficient",
                                   "Must be between 0 and 3")

    def _validate_system_settings(self, settings: Dict[str, Any], result: ValidationResult) -> None:
        """Validate system settings"""
        # Check umlages vs vacation reserve
        use_umlages = settings.get("use_umlages", True)
        use_reserve = settings.get("use_vacation_reserve", False)

        if use_umlages and use_reserve:
            result.add_error("Cannot use both umlages and vacation reserve simultaneously")

        # Check surcharge base
        valid_bases = ["full_cost", "brutto_only"]
        surcharge_base = settings.get("surcharge_base", "full_cost")
        if surcharge_base not in valid_bases:
            result.add_invalid("system_settings.surcharge_base",
                               f"Must be one of: {', '.join(valid_bases)}")

        # Check service type
        valid_types = ["domestic", "social", "medical", "professional", "educational"]
        service_type = settings.get("service_type", "social")
        if service_type not in valid_types:
            result.add_invalid("system_settings.service_type",
                               f"Must be one of: {', '.join(valid_types)}")

    def validate_filled_template(self, variables: List[Variable]) -> ValidationResult:
        """
        Validate filled template

        Args:
            variables: List of all variables

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        for var in variables:
            var_result = self.validate_variable(var)

            # Merge results
            result.errors.extend(var_result.errors)
            result.warnings.extend(var_result.warnings)
            result.missing_required.extend(var_result.missing_required)
            result.invalid_values.update(var_result.invalid_values)

            if not var_result.is_valid:
                result.is_valid = False

        return result
