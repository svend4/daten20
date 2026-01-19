"""
Currency Conversion Module

Provides currency conversion functionality for financial calculations.
Supports multiple currencies with configurable exchange rates.
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional

from .cache import get_cache_manager

logger = logging.getLogger("dms.currency")


# Default exchange rates (relative to EUR)
DEFAULT_RATES = {
    "EUR": Decimal("1.0"),
    "USD": Decimal("1.08"),  # 1 EUR = 1.08 USD
    "GBP": Decimal("0.86"),  # 1 EUR = 0.86 GBP
    "CHF": Decimal("0.96"),  # 1 EUR = 0.96 CHF
    "PLN": Decimal("4.35"),  # 1 EUR = 4.35 PLN
    "CZK": Decimal("24.50"), # 1 EUR = 24.50 CZK
    "RUB": Decimal("90.00"), # 1 EUR = 90.00 RUB (approximate)
}


class CurrencyConverter:
    """Currency converter with caching support"""

    def __init__(self, base_currency: str = "EUR", enable_cache: bool = True):
        """
        Initialize currency converter

        Args:
            base_currency: Base currency code (default: EUR)
            enable_cache: Enable caching of conversion rates
        """
        self.base_currency = base_currency.upper()
        self.rates = DEFAULT_RATES.copy()
        self.enable_cache = enable_cache

        if enable_cache:
            self.cache = get_cache_manager()
        else:
            self.cache = None

        logger.info(f"Currency converter initialized with base: {self.base_currency}")

    def load_rates_from_file(self, file_path: str) -> None:
        """
        Load exchange rates from JSON file

        Args:
            file_path: Path to JSON file with rates

        File format:
        {
            "EUR": 1.0,
            "USD": 1.08,
            ...
        }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rates_data = json.load(f)

            # Convert to Decimal
            self.rates = {
                currency: Decimal(str(rate))
                for currency, rate in rates_data.items()
            }

            logger.info(f"Loaded {len(self.rates)} currency rates from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load rates from {file_path}: {e}")
            raise

    def save_rates_to_file(self, file_path: str) -> None:
        """
        Save current exchange rates to JSON file

        Args:
            file_path: Path to output JSON file
        """
        try:
            rates_data = {
                currency: float(rate)
                for currency, rate in self.rates.items()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(rates_data, f, indent=2)

            logger.info(f"Saved {len(self.rates)} currency rates to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save rates to {file_path}: {e}")
            raise

    def set_rate(self, currency: str, rate: Decimal) -> None:
        """
        Set exchange rate for a currency

        Args:
            currency: Currency code
            rate: Exchange rate relative to base currency
        """
        currency = currency.upper()
        self.rates[currency] = Decimal(str(rate))
        logger.debug(f"Set rate for {currency}: {rate}")

        # Invalidate cache for this currency
        if self.enable_cache and self.cache:
            cache_key = f"currency_convert:{self.base_currency}:{currency}"
            self.cache.delete(cache_key)

    def get_rate(self, currency: str) -> Optional[Decimal]:
        """
        Get exchange rate for a currency

        Args:
            currency: Currency code

        Returns:
            Exchange rate or None if not found
        """
        currency = currency.upper()
        return self.rates.get(currency)

    def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount

        Raises:
            ValueError: If currency not supported
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Same currency - no conversion needed
        if from_currency == to_currency:
            return amount

        # Try to get from cache
        cache_key = f"currency_convert:{from_currency}:{to_currency}:{amount}"
        if self.enable_cache and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Currency conversion cache HIT: {from_currency}->{to_currency}")
                return cached_result

        # Get rates
        from_rate = self.rates.get(from_currency)
        to_rate = self.rates.get(to_currency)

        if from_rate is None:
            raise ValueError(f"Unsupported currency: {from_currency}")
        if to_rate is None:
            raise ValueError(f"Unsupported currency: {to_currency}")

        # Convert: amount_in_base = amount / from_rate, then amount_in_target = amount_in_base * to_rate
        amount_in_base = amount / from_rate
        result = amount_in_base * to_rate

        # Round to 2 decimal places
        result = result.quantize(Decimal("0.01"))

        # Cache the result
        if self.enable_cache and self.cache:
            self.cache.set(cache_key, result, timeout=3600)  # 1 hour
            logger.debug(f"Currency conversion cache SET: {from_currency}->{to_currency}")

        logger.debug(f"Converted {amount} {from_currency} to {result} {to_currency}")
        return result

    def get_supported_currencies(self) -> list:
        """Get list of supported currency codes"""
        return sorted(self.rates.keys())

    def format_amount(self, amount: Decimal, currency: str) -> str:
        """
        Format amount with currency symbol

        Args:
            amount: Amount to format
            currency: Currency code

        Returns:
            Formatted string
        """
        currency = currency.upper()

        # Currency symbols
        symbols = {
            "EUR": "€",
            "USD": "$",
            "GBP": "£",
            "CHF": "CHF",
            "PLN": "zł",
            "CZK": "Kč",
            "RUB": "₽",
        }

        symbol = symbols.get(currency, currency)

        # Format amount
        if currency in ["EUR", "GBP", "CHF"]:
            # Symbol before amount
            return f"{symbol}{amount:.2f}"
        else:
            # Symbol after amount
            return f"{amount:.2f} {symbol}"


# Global instance
_converter: Optional[CurrencyConverter] = None


def get_currency_converter(base_currency: str = "EUR") -> CurrencyConverter:
    """Get or create global currency converter instance"""
    global _converter
    if _converter is None or _converter.base_currency != base_currency:
        _converter = CurrencyConverter(base_currency=base_currency)
    return _converter


def init_currency(base_currency: str = "EUR", rates_file: Optional[str] = None):
    """
    Initialize currency system

    Args:
        base_currency: Base currency code
        rates_file: Optional path to JSON file with custom rates
    """
    global _converter
    _converter = CurrencyConverter(base_currency=base_currency)

    if rates_file:
        _converter.load_rates_from_file(rates_file)

    logger.info(f"Currency system initialized with base: {base_currency}")
