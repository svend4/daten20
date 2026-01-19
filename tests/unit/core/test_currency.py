"""
Unit tests for currency conversion module
"""

import json
import os
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.core.currency import (
    CurrencyConverter,
    DEFAULT_RATES,
    get_currency_converter,
    init_currency,
)


# ============================================================================
# CurrencyConverter Tests
# ============================================================================


class TestCurrencyConverter:
    """Test CurrencyConverter class"""

    def test_init_default(self):
        """Test default initialization"""
        converter = CurrencyConverter()

        assert converter.base_currency == "EUR"
        assert converter.enable_cache is True
        assert len(converter.rates) > 0

    def test_init_custom_base(self):
        """Test initialization with custom base currency"""
        converter = CurrencyConverter(base_currency="USD")

        assert converter.base_currency == "USD"

    def test_init_no_cache(self):
        """Test initialization without cache"""
        converter = CurrencyConverter(enable_cache=False)

        assert converter.enable_cache is False
        assert converter.cache is None

    def test_default_rates_loaded(self):
        """Test default rates are loaded"""
        converter = CurrencyConverter()

        assert "EUR" in converter.rates
        assert "USD" in converter.rates
        assert "GBP" in converter.rates

    def test_set_rate(self):
        """Test setting exchange rate"""
        converter = CurrencyConverter()

        converter.set_rate("JPY", Decimal("130.00"))

        assert converter.rates["JPY"] == Decimal("130.00")

    def test_set_rate_lowercase(self):
        """Test setting rate with lowercase currency"""
        converter = CurrencyConverter()

        converter.set_rate("jpy", Decimal("130.00"))

        assert "JPY" in converter.rates

    def test_get_rate_exists(self):
        """Test getting existing rate"""
        converter = CurrencyConverter()

        rate = converter.get_rate("USD")

        assert rate is not None
        assert isinstance(rate, Decimal)

    def test_get_rate_not_exists(self):
        """Test getting non-existent rate"""
        converter = CurrencyConverter()

        rate = converter.get_rate("XYZ")

        assert rate is None

    def test_get_rate_lowercase(self):
        """Test getting rate with lowercase currency"""
        converter = CurrencyConverter()

        rate = converter.get_rate("usd")

        assert rate is not None

    def test_convert_same_currency(self):
        """Test converting same currency"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("100.00"), "EUR", "EUR")

        assert result == Decimal("100.00")

    def test_convert_eur_to_usd(self):
        """Test converting EUR to USD"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("100.00"), "EUR", "USD")

        assert result > Decimal("100.00")  # USD rate > 1.0

    def test_convert_usd_to_eur(self):
        """Test converting USD to EUR"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("108.00"), "USD", "EUR")

        # Should be approximately 100 EUR
        assert Decimal("99") < result < Decimal("101")

    def test_convert_rounds_to_2_decimals(self):
        """Test result is rounded to 2 decimal places"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("100.00"), "EUR", "USD")

        # Check has exactly 2 decimal places
        assert result.as_tuple().exponent == -2

    def test_convert_unsupported_from_currency(self):
        """Test converting from unsupported currency"""
        converter = CurrencyConverter()

        with pytest.raises(ValueError, match="Unsupported currency"):
            converter.convert(Decimal("100.00"), "XYZ", "EUR")

    def test_convert_unsupported_to_currency(self):
        """Test converting to unsupported currency"""
        converter = CurrencyConverter()

        with pytest.raises(ValueError, match="Unsupported currency"):
            converter.convert(Decimal("100.00"), "EUR", "XYZ")

    def test_convert_with_cache(self):
        """Test conversion uses cache"""
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        converter = CurrencyConverter(enable_cache=True)
        converter.cache = mock_cache

        result = converter.convert(Decimal("100.00"), "EUR", "USD")

        # Should check cache
        assert mock_cache.get.called
        # Should set cache
        assert mock_cache.set.called

    def test_convert_cache_hit(self):
        """Test conversion returns cached value"""
        mock_cache = MagicMock()
        mock_cache.get.return_value = Decimal("108.00")

        converter = CurrencyConverter(enable_cache=True)
        converter.cache = mock_cache

        result = converter.convert(Decimal("100.00"), "EUR", "USD")

        assert result == Decimal("108.00")

    def test_get_supported_currencies(self):
        """Test getting supported currencies"""
        converter = CurrencyConverter()

        currencies = converter.get_supported_currencies()

        assert isinstance(currencies, list)
        assert "EUR" in currencies
        assert "USD" in currencies
        assert currencies == sorted(currencies)  # Should be sorted

    def test_format_amount_eur(self):
        """Test formatting EUR amount"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("100.50"), "EUR")

        assert "€" in formatted
        assert "100.50" in formatted

    def test_format_amount_usd(self):
        """Test formatting USD amount"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("100.50"), "USD")

        assert "$" in formatted
        assert "100.50" in formatted

    def test_format_amount_gbp(self):
        """Test formatting GBP amount"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("100.50"), "GBP")

        assert "£" in formatted
        assert "100.50" in formatted

    def test_format_amount_pln(self):
        """Test formatting PLN amount"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("435.00"), "PLN")

        assert "zł" in formatted
        assert "435.00" in formatted

    def test_format_amount_unsupported(self):
        """Test formatting unsupported currency"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("100.00"), "XYZ")

        assert "XYZ" in formatted
        assert "100.00" in formatted

    def test_load_rates_from_file(self):
        """Test loading rates from JSON file"""
        converter = CurrencyConverter()

        # Create temporary rates file
        rates_data = {"EUR": 1.0, "USD": 1.10, "GBP": 0.85}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(rates_data, f)
            temp_file = f.name

        try:
            converter.load_rates_from_file(temp_file)

            assert converter.rates["USD"] == Decimal("1.10")
            assert converter.rates["GBP"] == Decimal("0.85")
        finally:
            os.unlink(temp_file)

    def test_load_rates_from_file_invalid(self):
        """Test loading rates from invalid file"""
        converter = CurrencyConverter()

        with pytest.raises(Exception):
            converter.load_rates_from_file("/nonexistent/file.json")

    def test_save_rates_to_file(self):
        """Test saving rates to JSON file"""
        converter = CurrencyConverter()
        converter.set_rate("JPY", Decimal("130.00"))

        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            converter.save_rates_to_file(temp_file)

            # Verify file was created and contains data
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)

            assert "EUR" in saved_data
            assert "JPY" in saved_data
            assert saved_data["JPY"] == 130.0
        finally:
            os.unlink(temp_file)


# ============================================================================
# Global Functions Tests
# ============================================================================


class TestGlobalFunctions:
    """Test global helper functions"""

    def test_get_currency_converter(self):
        """Test getting global converter"""
        converter = get_currency_converter()

        assert isinstance(converter, CurrencyConverter)
        assert converter.base_currency == "EUR"

    def test_get_currency_converter_singleton(self):
        """Test converter is singleton"""
        converter1 = get_currency_converter("EUR")
        converter2 = get_currency_converter("EUR")

        assert converter1 is converter2

    def test_get_currency_converter_different_base(self):
        """Test getting converter with different base"""
        converter_usd = get_currency_converter("USD")
        converter_eur = get_currency_converter("EUR")

        assert converter_usd is not converter_eur
        assert converter_eur.base_currency == "EUR"

    def test_init_currency(self):
        """Test initializing currency system"""
        init_currency(base_currency="EUR")

        converter = get_currency_converter("EUR")
        assert converter.base_currency == "EUR"

    def test_init_currency_with_file(self):
        """Test initializing with rates file"""
        rates_data = {"EUR": 1.0, "USD": 1.15}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(rates_data, f)
            temp_file = f.name

        try:
            init_currency(base_currency="EUR", rates_file=temp_file)

            converter = get_currency_converter("EUR")
            assert converter.rates["USD"] == Decimal("1.15")
        finally:
            os.unlink(temp_file)


# ============================================================================
# Default Rates Tests
# ============================================================================


class TestDefaultRates:
    """Test default exchange rates"""

    def test_default_rates_exist(self):
        """Test default rates are defined"""
        assert len(DEFAULT_RATES) > 0

    def test_default_rates_have_eur(self):
        """Test EUR is in default rates"""
        assert "EUR" in DEFAULT_RATES
        assert DEFAULT_RATES["EUR"] == Decimal("1.0")

    def test_default_rates_have_major_currencies(self):
        """Test major currencies are in default rates"""
        assert "USD" in DEFAULT_RATES
        assert "GBP" in DEFAULT_RATES
        assert "CHF" in DEFAULT_RATES

    def test_default_rates_are_decimal(self):
        """Test default rates are Decimal type"""
        for rate in DEFAULT_RATES.values():
            assert isinstance(rate, Decimal)

    def test_default_rates_positive(self):
        """Test all rates are positive"""
        for rate in DEFAULT_RATES.values():
            assert rate > 0


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases"""

    def test_convert_zero_amount(self):
        """Test converting zero amount"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("0.00"), "EUR", "USD")

        assert result == Decimal("0.00")

    def test_convert_large_amount(self):
        """Test converting large amount"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("1000000.00"), "EUR", "USD")

        assert result > Decimal("1000000.00")

    def test_convert_small_amount(self):
        """Test converting small amount"""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("0.01"), "EUR", "USD")

        assert result > Decimal("0.00")

    def test_format_amount_negative(self):
        """Test formatting negative amount"""
        converter = CurrencyConverter()

        formatted = converter.format_amount(Decimal("-100.00"), "EUR")

        assert "-" in formatted
        assert "€" in formatted

    def test_cache_invalidation_on_rate_change(self):
        """Test cache is invalidated when rate changes"""
        mock_cache = MagicMock()
        converter = CurrencyConverter(enable_cache=True)
        converter.cache = mock_cache

        converter.set_rate("USD", Decimal("1.20"))

        # Cache delete should be called
        assert mock_cache.delete.called
