#!/usr/bin/env python3
"""
Financial Calculator - Финансовый калькулятор

Расчет стоимости услуг с учетом всех социальных отчислений,
умлаг, надбавок и региональных коэффициентов.

Улучшения v1.0.1:
- Добавлено кэширование расчетов
- Добавлен экспорт результатов в JSON/YAML
- Улучшена производительность повторных расчетов
"""

import argparse
import hashlib
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cache import get_cache_manager
from src.core.currency import CurrencyConverter, get_currency_converter
from src.core.financial_validation import FinancialValidator
from src.core.input_validation import InputValidator, ValidationError
from src.models.financial import CostBreakdown, FinancialParameters, InsuranceRates, ServiceCost, Surcharges, Umlages
from src.utils.constants import REGIONAL_COEFFICIENTS
from src.utils.formatting import (
    bold,
    colored,
    divider,
    error,
    header,
    info,
    key_value,
    section,
    success,
    table,
    warning,
)
from src.utils.helpers import format_currency, format_percentage, load_config, round_currency

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class FinancialCalculator:
    """Main Financial Calculator class with caching and multi-currency support"""

    def __init__(self, enable_cache: bool = True, currency: str = "EUR"):
        """
        Initialize calculator

        Args:
            enable_cache: Enable caching of calculation results (default: True)
            currency: Base currency for calculations (default: EUR)
        """
        self.validator = FinancialValidator()
        self.enable_cache = enable_cache
        self.currency = currency.upper()

        # Initialize cache if enabled
        if enable_cache:
            self.cache = get_cache_manager()
        else:
            self.cache = None

        # Initialize currency converter
        self.currency_converter = get_currency_converter(base_currency=self.currency)

    def _generate_cache_key(self, params: FinancialParameters, suffix: str = "") -> str:
        """Generate cache key from parameters"""
        # Create a dict of all parameters for hashing
        params_dict = {
            'brutto_rate': float(params.brutto_rate),
            'insurance_rates': {
                'kv_er': float(params.insurance_rates.kv_er),
                'kv_zusatz_er': float(params.insurance_rates.kv_zusatz_er),
                'pv_er': float(params.insurance_rates.pv_er),
                'pv_er_sn': float(params.insurance_rates.pv_er_sn),
                'rv_er': float(params.insurance_rates.rv_er),
                'av_er': float(params.insurance_rates.av_er),
                'uv_er': float(params.insurance_rates.uv_er),
            },
            'umlages': {
                'u1': float(params.umlages.u1),
                'u2': float(params.umlages.u2),
                'u3': float(params.umlages.u3),
            },
            'use_umlages': params.use_umlages,
            'vacation_reserve_percent': float(params.vacation_reserve_percent),
            'materials_per_hour': float(params.materials_per_hour),
            'admin_percent': float(params.admin_percent),
            'admin_per_hour': float(params.admin_per_hour),
            'region_coefficient': float(params.region_coefficient),
            'is_saxony': params.is_saxony,
            'surcharge_base': params.surcharge_base,
        }

        # Convert to JSON string and hash
        params_json = json.dumps(params_dict, sort_keys=True)
        params_hash = hashlib.md5(params_json.encode()).hexdigest()

        return f"financial_calc:{params_hash}:{suffix}"

    def calculate_hourly_rate(self, params: FinancialParameters) -> CostBreakdown:
        """
        Calculate hourly rate with full breakdown (with caching)

        Args:
            params: Financial parameters

        Returns:
            CostBreakdown with all calculations

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate all financial parameters comprehensively
        self.validator.validate_financial_parameters(params)

        # Try to get from cache
        cache_key = self._generate_cache_key(params, "hourly_rate")
        if self.enable_cache and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        breakdown = CostBreakdown(brutto_rate=params.brutto_rate)

        # Step 1: Calculate social insurance contributions (employer's share)
        breakdown.kv_contribution = self._calculate_percentage(
            params.brutto_rate, params.insurance_rates.kv_er + params.insurance_rates.kv_zusatz_er
        )
        breakdown.pv_contribution = self._calculate_percentage(
            params.brutto_rate, params.insurance_rates.pv_er_sn if params.is_saxony else params.insurance_rates.pv_er
        )
        breakdown.rv_contribution = self._calculate_percentage(params.brutto_rate, params.insurance_rates.rv_er)
        breakdown.av_contribution = self._calculate_percentage(params.brutto_rate, params.insurance_rates.av_er)
        breakdown.uv_contribution = self._calculate_percentage(params.brutto_rate, params.insurance_rates.uv_er)

        breakdown.total_insurance = (
            breakdown.kv_contribution
            + breakdown.pv_contribution
            + breakdown.rv_contribution
            + breakdown.av_contribution
            + breakdown.uv_contribution
        )

        # Step 2: Calculate umlages OR vacation reserve (mutually exclusive)
        if params.use_umlages:
            breakdown.u1_contribution = self._calculate_percentage(params.brutto_rate, params.umlages.u1)
            breakdown.u2_contribution = self._calculate_percentage(params.brutto_rate, params.umlages.u2)
            breakdown.u3_contribution = self._calculate_percentage(params.brutto_rate, params.umlages.u3)
            breakdown.total_umlages = breakdown.u1_contribution + breakdown.u2_contribution + breakdown.u3_contribution
            breakdown.vacation_reserve = Decimal("0")
            breakdown.calculation_mode = "with_umlages"
        else:
            # Use vacation reserve instead
            breakdown.vacation_reserve = self._calculate_percentage(
                params.brutto_rate + breakdown.total_insurance, params.vacation_reserve_percent
            )
            breakdown.u1_contribution = Decimal("0")
            breakdown.u2_contribution = Decimal("0")
            breakdown.u3_contribution = self._calculate_percentage(
                params.brutto_rate, params.umlages.u3
            )  # U3 is always included
            breakdown.total_umlages = breakdown.u3_contribution
            breakdown.calculation_mode = "with_reserve"

        # Step 3: Add materials and admin costs
        breakdown.materials_cost = params.materials_per_hour
        if params.admin_percent > 0:
            base_for_admin = params.brutto_rate + breakdown.total_insurance + breakdown.total_umlages
            breakdown.admin_cost = self._calculate_percentage(base_for_admin, params.admin_percent)
        else:
            breakdown.admin_cost = params.admin_per_hour

        # Step 4: Calculate base hourly cost (before surcharges and region coefficient)
        breakdown.base_hourly_cost = (
            params.brutto_rate
            + breakdown.total_insurance
            + breakdown.total_umlages
            + breakdown.vacation_reserve
            + breakdown.materials_cost
            + breakdown.admin_cost
        )

        # Step 5: Apply region coefficient
        breakdown.region_coefficient = params.region_coefficient
        breakdown.final_hourly_rate = breakdown.base_hourly_cost * params.region_coefficient

        # Round to 2 decimal places
        breakdown.final_hourly_rate = round_currency(float(breakdown.final_hourly_rate))

        # Cache the result
        if self.enable_cache and self.cache:
            self.cache.set(cache_key, breakdown, timeout=3600)  # 1 hour

        return breakdown

    def calculate_with_surcharge(self, params: FinancialParameters, surcharge_types: List[str]) -> CostBreakdown:
        """
        Calculate hourly rate with surcharges

        Args:
            params: Financial parameters
            surcharge_types: List of surcharge types to apply

        Returns:
            CostBreakdown with surcharges

        Raises:
            ValidationError: If surcharge types are invalid
        """
        # Validate surcharge types and values
        for surcharge_type in surcharge_types:
            surcharge_value = params.surcharges.get(surcharge_type)
            self.validator.validate_surcharge(surcharge_type, surcharge_value)

        # Get base calculation and create a copy to avoid modifying cached object
        base_breakdown = self.calculate_hourly_rate(params)

        # Create a copy of the breakdown to avoid modifying cached object
        from copy import deepcopy
        breakdown = deepcopy(base_breakdown)

        # Calculate surcharges
        total_surcharge_percent = Decimal("0")
        for surcharge_type in surcharge_types:
            surcharge_value = params.surcharges.get(surcharge_type)

            breakdown.surcharges_applied[surcharge_type] = surcharge_value
            total_surcharge_percent += surcharge_value

        # Apply surcharges based on configuration
        if total_surcharge_percent > 0:
            if params.surcharge_base == "full_cost":
                # Apply to full cost
                surcharge_amount = self._calculate_percentage(breakdown.final_hourly_rate, total_surcharge_percent)
            else:  # brutto_only
                # Apply to brutto rate only
                surcharge_amount = self._calculate_percentage(params.brutto_rate, total_surcharge_percent)

            breakdown.total_surcharge = surcharge_amount
            breakdown.final_hourly_rate += surcharge_amount
            breakdown.final_hourly_rate = round_currency(float(breakdown.final_hourly_rate))

        return breakdown

    def calculate_total_cost(
        self, params: FinancialParameters, hours: Decimal, surcharge_types: Optional[List[str]] = None
    ) -> ServiceCost:
        """
        Calculate total cost for service

        Args:
            params: Financial parameters
            hours: Number of hours
            surcharge_types: Optional list of surcharges to apply

        Returns:
            ServiceCost with total calculation

        Raises:
            ValidationError: If hours are invalid
        """
        # Validate hours
        validated_hours = self.validator.validate_hours(hours)

        if surcharge_types:
            breakdown = self.calculate_with_surcharge(params, surcharge_types)
        else:
            breakdown = self.calculate_hourly_rate(params)

        total_cost = breakdown.final_hourly_rate * hours
        total_cost = round_currency(float(total_cost))

        return ServiceCost(
            hourly_rate=breakdown.final_hourly_rate, hours=hours, total_cost=total_cost, breakdown=breakdown
        )

    def _calculate_percentage(self, base: Decimal, percentage: Decimal) -> Decimal:
        """Calculate percentage of base amount"""
        result = base * (percentage / Decimal("100"))
        return round_currency(float(result))

    def print_breakdown(self, breakdown: CostBreakdown, detailed: bool = True) -> None:
        """
        Print cost breakdown

        Args:
            breakdown: Cost breakdown to print
            detailed: Show detailed breakdown
        """
        print(section("РАСЧЕТ СТОИМОСТИ УСЛУГИ"))

        # Basic rate
        print(bold("Базовая ставка:"))
        print(key_value("  Ставка брутто", format_currency(float(breakdown.brutto_rate))))
        print()

        # Insurance contributions
        if detailed:
            print(bold("Социальные отчисления работодателя:"))
            print(key_value("  KV (Krankenversicherung)", format_currency(float(breakdown.kv_contribution))))
            print(key_value("  PV (Pflegeversicherung)", format_currency(float(breakdown.pv_contribution))))
            print(key_value("  RV (Rentenversicherung)", format_currency(float(breakdown.rv_contribution))))
            print(key_value("  AV (Arbeitslosenversicherung)", format_currency(float(breakdown.av_contribution))))
            print(key_value("  UV (Unfallversicherung)", format_currency(float(breakdown.uv_contribution))))
            print(key_value("  ИТОГО отчисления", format_currency(float(breakdown.total_insurance)), 35))
            print()

        # Umlages or vacation reserve
        if breakdown.calculation_mode == "with_umlages":
            if detailed:
                print(bold("Умлаги (Umlages):"))
                print(key_value("  U1 (Erstattung Krankheit)", format_currency(float(breakdown.u1_contribution))))
                print(key_value("  U2 (Erstattung Mutterschaft)", format_currency(float(breakdown.u2_contribution))))
                print(key_value("  U3 (Insolvenzgeldumlage)", format_currency(float(breakdown.u3_contribution))))
                print(key_value("  ИТОГО умлаги", format_currency(float(breakdown.total_umlages)), 35))
                print()
        else:
            print(bold("Резерв на отпуск/больничные:"))
            print(key_value("  Резерв", format_currency(float(breakdown.vacation_reserve))))
            print(key_value("  U3 (всегда включен)", format_currency(float(breakdown.u3_contribution))))
            print()

        # Materials and admin
        if breakdown.materials_cost > 0 or breakdown.admin_cost > 0:
            if detailed:
                print(bold("Материалы и административные расходы:"))
                if breakdown.materials_cost > 0:
                    print(key_value("  Материалы/связь/проезд", format_currency(float(breakdown.materials_cost))))
                if breakdown.admin_cost > 0:
                    print(key_value("  Административные расходы", format_currency(float(breakdown.admin_cost))))
                print()

        # Base cost
        print(bold("Базовая стоимость часа:"))
        print(key_value("  До региональной корректировки", format_currency(float(breakdown.base_hourly_cost))))
        print()

        # Regional coefficient
        if breakdown.region_coefficient != Decimal("1.0"):
            print(bold("Региональный коэффициент:"))
            print(key_value("  Коэффициент", f"{float(breakdown.region_coefficient):.2f}"))
            print()

        # Surcharges
        if breakdown.surcharges_applied:
            print(bold("Надбавки:"))
            surcharge_names = {
                "night": "Ночная работа",
                "weekend": "Выходные дни",
                "holiday": "Праздничные дни",
                "urgent": "Срочность",
            }
            for surcharge_type, percent in breakdown.surcharges_applied.items():
                name = surcharge_names.get(surcharge_type, surcharge_type)
                print(key_value(f"  {name}", format_percentage(float(percent))))
            print(key_value("  ИТОГО надбавки", format_currency(float(breakdown.total_surcharge)), 35))
            print()

        # Final rate
        print(bold("ИТОГОВАЯ СТОИМОСТЬ ЧАСА:"))
        print(colored(key_value("  ", format_currency(float(breakdown.final_hourly_rate))), "green"))
        print()

    def compare_modes(self, params: FinancialParameters) -> None:
        """
        Compare calculation with umlages vs vacation reserve

        Args:
            params: Financial parameters
        """
        print(section("СРАВНЕНИЕ РЕЖИМОВ РАСЧЕТА"))

        # Mode 1: With umlages
        params1 = params
        params1.use_umlages = True
        params1.use_vacation_reserve = False
        breakdown1 = self.calculate_hourly_rate(params1)

        # Mode 2: With vacation reserve
        params2 = params
        params2.use_umlages = False
        params2.use_vacation_reserve = True
        breakdown2 = self.calculate_hourly_rate(params2)

        # Comparison table
        rows = [
            [
                "Ставка брутто",
                format_currency(float(breakdown1.brutto_rate)),
                format_currency(float(breakdown2.brutto_rate)),
            ],
            [
                "Социальные отчисления",
                format_currency(float(breakdown1.total_insurance)),
                format_currency(float(breakdown2.total_insurance)),
            ],
            [
                "Умлаги (U1+U2+U3)",
                format_currency(float(breakdown1.total_umlages)),
                format_currency(float(breakdown2.total_umlages)),
            ],
            [
                "Резерв отпуск/больничные",
                format_currency(float(breakdown1.vacation_reserve)),
                format_currency(float(breakdown2.vacation_reserve)),
            ],
            [
                "Материалы",
                format_currency(float(breakdown1.materials_cost)),
                format_currency(float(breakdown2.materials_cost)),
            ],
            [
                "Администрирование",
                format_currency(float(breakdown1.admin_cost)),
                format_currency(float(breakdown2.admin_cost)),
            ],
            ["", "", ""],
            [
                bold("ИТОГО"),
                bold(format_currency(float(breakdown1.final_hourly_rate))),
                bold(format_currency(float(breakdown2.final_hourly_rate))),
            ],
        ]

        headers = ["Компонент", "С умлагами", "С резервом"]
        print(table(headers, rows))
        print()

        # Show difference
        diff = breakdown1.final_hourly_rate - breakdown2.final_hourly_rate
        if diff > 0:
            print(info(f"Расчет с умлагами дороже на {format_currency(float(diff))}"))
        elif diff < 0:
            print(info(f"Расчет с резервом дороже на {format_currency(float(abs(diff)))}"))
        else:
            print(info("Стоимость одинаковая в обоих режимах"))
        print()

    def convert_result(self, amount: Decimal, to_currency: str) -> Decimal:
        """
        Convert calculation result to another currency

        Args:
            amount: Amount in base currency
            to_currency: Target currency code

        Returns:
            Converted amount
        """
        return self.currency_converter.convert(amount, self.currency, to_currency)

    def show_multi_currency(self, amount: Decimal, currencies: Optional[list] = None) -> None:
        """
        Show amount in multiple currencies

        Args:
            amount: Amount in base currency
            currencies: List of currency codes (None = show all supported)
        """
        if currencies is None:
            currencies = self.currency_converter.get_supported_currencies()

        print(section(f"КОНВЕРТАЦИЯ ВАЛЮТ (База: {self.currency})"))

        rows = []
        for currency in currencies:
            if currency == self.currency:
                rows.append([currency, self.currency_converter.format_amount(amount, currency), "(база)"])
            else:
                try:
                    converted = self.convert_result(amount, currency)
                    rows.append([currency, self.currency_converter.format_amount(converted, currency), ""])
                except ValueError as e:
                    rows.append([currency, "не поддерживается", ""])

        headers = ["Валюта", "Сумма", ""]
        print(table(headers, rows))
        print()

    def export_result(self, breakdown: CostBreakdown, output_file: str, format: str = 'auto') -> None:
        """
        Export calculation result to JSON or YAML file

        Args:
            breakdown: Cost breakdown to export
            output_file: Output file path
            format: Output format ('json', 'yaml', 'auto')
        """
        # Auto-detect format from extension
        if format == 'auto':
            ext = Path(output_file).suffix.lower()
            if ext in ['.yaml', '.yml']:
                format = 'yaml'
            else:
                format = 'json'

        # Convert breakdown to dict
        data = {
            'brutto_rate': float(breakdown.brutto_rate),
            'insurance_contributions': {
                'kv': float(breakdown.kv_contribution),
                'pv': float(breakdown.pv_contribution),
                'rv': float(breakdown.rv_contribution),
                'av': float(breakdown.av_contribution),
                'uv': float(breakdown.uv_contribution),
                'total': float(breakdown.total_insurance)
            },
            'umlages': {
                'u1': float(breakdown.u1_contribution),
                'u2': float(breakdown.u2_contribution),
                'u3': float(breakdown.u3_contribution),
                'total': float(breakdown.total_umlages)
            },
            'vacation_reserve': float(breakdown.vacation_reserve),
            'materials_cost': float(breakdown.materials_cost),
            'admin_cost': float(breakdown.admin_cost),
            'base_hourly_cost': float(breakdown.base_hourly_cost),
            'region_coefficient': float(breakdown.region_coefficient),
            'total_surcharge': float(breakdown.total_surcharge),
            'final_hourly_rate': float(breakdown.final_hourly_rate),
            'calculation_mode': breakdown.calculation_mode,
            'surcharges_applied': {k: float(v) for k, v in breakdown.surcharges_applied.items()}
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == 'yaml':
                    if not YAML_AVAILABLE:
                        print(error("PyYAML не установлен. Установите: pip install pyyaml"))
                        return
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            print(success(f"Результат экспортирован в {output_file} ({format.upper()})"))
        except Exception as e:
            print(error(f"Ошибка при экспорте: {e}"))

    def get_cache_stats(self) -> None:
        """Show cache statistics"""
        if not self.enable_cache or not self.cache:
            print(warning("Кэширование отключено"))
            return

        stats = self.cache.get_stats()
        print(section("СТАТИСТИКА КЭША"))
        print(key_value("Бэкенд", stats['backend']))
        print(key_value("Попаданий", str(stats['hits'])))
        print(key_value("Промахов", str(stats['misses'])))
        print(key_value("Всего запросов", str(stats['total_requests'])))
        print(key_value("Процент попаданий", f"{stats['hit_rate']}%"))
        print()

    def clear_cache(self) -> None:
        """Clear calculator cache"""
        if not self.enable_cache or not self.cache:
            print(warning("Кэширование отключено"))
            return

        self.cache.clear()
        print(success("Кэш очищен"))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Финансовый калькулятор стоимости услуг (v1.0.1 с кэшированием)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--brutto", type=float, default=25.0, help="Ставка брутто €/ч (по умолчанию: 25.0)")

    parser.add_argument(
        "--region", choices=list(REGIONAL_COEFFICIENTS.keys()), help="Регион (автоматический коэффициент)"
    )

    parser.add_argument("--coefficient", type=float, default=1.0, help="Региональный коэффициент (по умолчанию: 1.0)")

    parser.add_argument("--materials", type=float, default=0.0, help="Материалы €/ч (по умолчанию: 0.0)")

    parser.add_argument("--admin", type=float, default=5.0, help="Административные расходы %% (по умолчанию: 5.0)")

    parser.add_argument("--hours", type=float, help="Количество часов для расчета итоговой стоимости")

    parser.add_argument(
        "--surcharge",
        action="append",
        choices=["night", "weekend", "holiday", "urgent"],
        help="Добавить надбавку (можно указать несколько раз)",
    )

    parser.add_argument(
        "--mode",
        choices=["umlages", "reserve", "compare"],
        default="umlages",
        help="Режим расчета (по умолчанию: umlages)",
    )

    parser.add_argument("--config", help="Загрузить параметры из YAML/JSON файла")

    parser.add_argument("--detailed", action="store_true", help="Показать детальный расчет")

    # Export options
    parser.add_argument("--export", metavar="FILE", help="Экспортировать результат в JSON/YAML")
    parser.add_argument("--export-format", choices=['json', 'yaml', 'auto'], default='auto',
                       help="Формат экспорта (по умолчанию: auto)")

    # Cache options
    parser.add_argument("--no-cache", action="store_true", help="Отключить кэширование")
    parser.add_argument("--cache-stats", action="store_true", help="Показать статистику кэша")
    parser.add_argument("--clear-cache", action="store_true", help="Очистить кэш")

    # Currency options
    parser.add_argument("--currency", choices=['EUR', 'USD', 'GBP', 'CHF', 'PLN', 'CZK', 'RUB'],
                       default='EUR', help="Базовая валюта расчета (по умолчанию: EUR)")
    parser.add_argument("--show-currencies", action="store_true",
                       help="Показать результат в нескольких валютах")
    parser.add_argument("--convert-to", action="append",
                       help="Конвертировать результат в указанную валюту")

    args = parser.parse_args()

    # Create calculator
    calc = FinancialCalculator(enable_cache=not args.no_cache, currency=args.currency)

    # Handle cache-only commands
    if args.clear_cache:
        calc.clear_cache()
        return

    if args.cache_stats and not any([args.hours, args.mode == "compare"]):
        calc.get_cache_stats()
        return

    # Validate CLI arguments
    try:
        validated_args = calc.validator.validate_cli_args(vars(args))
    except ValidationError as e:
        print(error(f"Ошибка валидации аргументов: {e}"))
        return 1

    # Create parameters
    if args.config:
        try:
            config = load_config(args.config)
            from src.models.service import Service

            service = Service.from_dict(config)
            params = service.financial
        except Exception as e:
            print(error(f"Ошибка при загрузке конфигурации: {e}"))
            return
    else:
        params = FinancialParameters(brutto_rate=Decimal(str(args.brutto)))
        params.materials_per_hour = Decimal(str(args.materials))
        params.admin_percent = Decimal(str(args.admin))

        if args.region:
            params.region_coefficient = Decimal(str(REGIONAL_COEFFICIENTS[args.region]))
        else:
            params.region_coefficient = Decimal(str(args.coefficient))

        if args.mode == "reserve":
            params.use_umlages = False
            params.use_vacation_reserve = True
            params.vacation_reserve_percent = Decimal("12.0")  # ~12% for vacation

    print(header("ФИНАНСОВЫЙ КАЛЬКУЛЯТОР"))

    if args.mode == "compare":
        calc.compare_modes(params)
    else:
        if args.hours:
            # Calculate total cost
            cost = calc.calculate_total_cost(params, Decimal(str(args.hours)), args.surcharge)
            calc.print_breakdown(cost.breakdown, args.detailed)

            print(section("ИТОГОВАЯ СТОИМОСТЬ"))
            print(key_value("Часов", f"{float(cost.hours):.1f}"))
            print(key_value("Ставка за час", format_currency(float(cost.hourly_rate))))
            print(bold(key_value("ИТОГО", format_currency(float(cost.total_cost)))))
            print()

            # Export if requested
            if args.export:
                calc.export_result(cost.breakdown, args.export, format=args.export_format)

            # Show currency conversions if requested
            if args.show_currencies:
                calc.show_multi_currency(cost.total_cost)
            elif args.convert_to:
                calc.show_multi_currency(cost.total_cost, currencies=args.convert_to)
        else:
            # Calculate hourly rate only
            if args.surcharge:
                breakdown = calc.calculate_with_surcharge(params, args.surcharge)
            else:
                breakdown = calc.calculate_hourly_rate(params)

            calc.print_breakdown(breakdown, args.detailed)

            # Export if requested
            if args.export:
                calc.export_result(breakdown, args.export, format=args.export_format)

            # Show currency conversions if requested
            if args.show_currencies:
                calc.show_multi_currency(breakdown.final_hourly_rate)
            elif args.convert_to:
                calc.show_multi_currency(breakdown.final_hourly_rate, currencies=args.convert_to)

    # Show cache stats at the end if requested
    if args.cache_stats and not args.clear_cache:
        calc.get_cache_stats()


if __name__ == "__main__":
    main()
