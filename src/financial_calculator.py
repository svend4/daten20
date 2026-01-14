#!/usr/bin/env python3
"""
Financial Calculator - Финансовый калькулятор

Расчет стоимости услуг с учетом всех социальных отчислений,
умлаг, надбавок и региональных коэффициентов.
"""

import sys
import argparse
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.financial import (
    FinancialParameters, InsuranceRates, Umlages, Surcharges,
    CostBreakdown, ServiceCost
)
from src.utils.formatting import (
    header, section, success, error, warning, info,
    table, key_value, colored, bold, divider
)
from src.utils.helpers import format_currency, format_percentage, round_currency, load_config
from src.utils.constants import REGIONAL_COEFFICIENTS
from src.core.input_validation import InputValidator, ValidationError
from src.core.financial_validation import FinancialValidator


class FinancialCalculator:
    """Main Financial Calculator class"""

    def __init__(self):
        """Initialize calculator"""
        self.validator = FinancialValidator()

    def calculate_hourly_rate(self, params: FinancialParameters) -> CostBreakdown:
        """
        Calculate hourly rate with full breakdown

        Args:
            params: Financial parameters

        Returns:
            CostBreakdown with all calculations

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate all financial parameters comprehensively
        self.validator.validate_financial_parameters(params)

        breakdown = CostBreakdown(brutto_rate=params.brutto_rate)

        # Step 1: Calculate social insurance contributions (employer's share)
        breakdown.kv_contribution = self._calculate_percentage(
            params.brutto_rate,
            params.insurance_rates.kv_er + params.insurance_rates.kv_zusatz_er
        )
        breakdown.pv_contribution = self._calculate_percentage(
            params.brutto_rate,
            params.insurance_rates.pv_er_sn if params.is_saxony else params.insurance_rates.pv_er
        )
        breakdown.rv_contribution = self._calculate_percentage(
            params.brutto_rate,
            params.insurance_rates.rv_er
        )
        breakdown.av_contribution = self._calculate_percentage(
            params.brutto_rate,
            params.insurance_rates.av_er
        )
        breakdown.uv_contribution = self._calculate_percentage(
            params.brutto_rate,
            params.insurance_rates.uv_er
        )

        breakdown.total_insurance = (
            breakdown.kv_contribution +
            breakdown.pv_contribution +
            breakdown.rv_contribution +
            breakdown.av_contribution +
            breakdown.uv_contribution
        )

        # Step 2: Calculate umlages OR vacation reserve (mutually exclusive)
        if params.use_umlages:
            breakdown.u1_contribution = self._calculate_percentage(
                params.brutto_rate,
                params.umlages.u1
            )
            breakdown.u2_contribution = self._calculate_percentage(
                params.brutto_rate,
                params.umlages.u2
            )
            breakdown.u3_contribution = self._calculate_percentage(
                params.brutto_rate,
                params.umlages.u3
            )
            breakdown.total_umlages = (
                breakdown.u1_contribution +
                breakdown.u2_contribution +
                breakdown.u3_contribution
            )
            breakdown.vacation_reserve = Decimal("0")
            breakdown.calculation_mode = "with_umlages"
        else:
            # Use vacation reserve instead
            breakdown.vacation_reserve = self._calculate_percentage(
                params.brutto_rate + breakdown.total_insurance,
                params.vacation_reserve_percent
            )
            breakdown.u1_contribution = Decimal("0")
            breakdown.u2_contribution = Decimal("0")
            breakdown.u3_contribution = self._calculate_percentage(
                params.brutto_rate,
                params.umlages.u3
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
            params.brutto_rate +
            breakdown.total_insurance +
            breakdown.total_umlages +
            breakdown.vacation_reserve +
            breakdown.materials_cost +
            breakdown.admin_cost
        )

        # Step 5: Apply region coefficient
        breakdown.region_coefficient = params.region_coefficient
        breakdown.final_hourly_rate = breakdown.base_hourly_cost * params.region_coefficient

        # Round to 2 decimal places
        breakdown.final_hourly_rate = round_currency(float(breakdown.final_hourly_rate))

        return breakdown

    def calculate_with_surcharge(
        self,
        params: FinancialParameters,
        surcharge_types: List[str]
    ) -> CostBreakdown:
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

        breakdown = self.calculate_hourly_rate(params)

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
                surcharge_amount = self._calculate_percentage(
                    breakdown.final_hourly_rate,
                    total_surcharge_percent
                )
            else:  # brutto_only
                # Apply to brutto rate only
                surcharge_amount = self._calculate_percentage(
                    params.brutto_rate,
                    total_surcharge_percent
                )

            breakdown.total_surcharge = surcharge_amount
            breakdown.final_hourly_rate += surcharge_amount
            breakdown.final_hourly_rate = round_currency(float(breakdown.final_hourly_rate))

        return breakdown

    def calculate_total_cost(
        self,
        params: FinancialParameters,
        hours: Decimal,
        surcharge_types: Optional[List[str]] = None
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
            hourly_rate=breakdown.final_hourly_rate,
            hours=hours,
            total_cost=total_cost,
            breakdown=breakdown
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
                "urgent": "Срочность"
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
            ["Ставка брутто", format_currency(float(breakdown1.brutto_rate)), format_currency(float(breakdown2.brutto_rate))],
            ["Социальные отчисления", format_currency(float(breakdown1.total_insurance)), format_currency(float(breakdown2.total_insurance))],
            ["Умлаги (U1+U2+U3)", format_currency(float(breakdown1.total_umlages)), format_currency(float(breakdown2.total_umlages))],
            ["Резерв отпуск/больничные", format_currency(float(breakdown1.vacation_reserve)), format_currency(float(breakdown2.vacation_reserve))],
            ["Материалы", format_currency(float(breakdown1.materials_cost)), format_currency(float(breakdown2.materials_cost))],
            ["Администрирование", format_currency(float(breakdown1.admin_cost)), format_currency(float(breakdown2.admin_cost))],
            ["", "", ""],
            [bold("ИТОГО"), bold(format_currency(float(breakdown1.final_hourly_rate))), bold(format_currency(float(breakdown2.final_hourly_rate)))]
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


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Финансовый калькулятор стоимости услуг",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--brutto",
        type=float,
        default=25.0,
        help="Ставка брутто €/ч (по умолчанию: 25.0)"
    )

    parser.add_argument(
        "--region",
        choices=list(REGIONAL_COEFFICIENTS.keys()),
        help="Регион (автоматический коэффициент)"
    )

    parser.add_argument(
        "--coefficient",
        type=float,
        default=1.0,
        help="Региональный коэффициент (по умолчанию: 1.0)"
    )

    parser.add_argument(
        "--materials",
        type=float,
        default=0.0,
        help="Материалы €/ч (по умолчанию: 0.0)"
    )

    parser.add_argument(
        "--admin",
        type=float,
        default=5.0,
        help="Административные расходы %% (по умолчанию: 5.0)"
    )

    parser.add_argument(
        "--hours",
        type=float,
        help="Количество часов для расчета итоговой стоимости"
    )

    parser.add_argument(
        "--surcharge",
        action="append",
        choices=["night", "weekend", "holiday", "urgent"],
        help="Добавить надбавку (можно указать несколько раз)"
    )

    parser.add_argument(
        "--mode",
        choices=["umlages", "reserve", "compare"],
        default="umlages",
        help="Режим расчета (по умолчанию: umlages)"
    )

    parser.add_argument(
        "--config",
        help="Загрузить параметры из YAML/JSON файла"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Показать детальный расчет"
    )

    args = parser.parse_args()

    # Create calculator
    calc = FinancialCalculator()

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
            cost = calc.calculate_total_cost(
                params,
                Decimal(str(args.hours)),
                args.surcharge
            )
            calc.print_breakdown(cost.breakdown, args.detailed)

            print(section("ИТОГОВАЯ СТОИМОСТЬ"))
            print(key_value("Часов", f"{float(cost.hours):.1f}"))
            print(key_value("Ставка за час", format_currency(float(cost.hourly_rate))))
            print(bold(key_value("ИТОГО", format_currency(float(cost.total_cost)))))
            print()
        else:
            # Calculate hourly rate only
            if args.surcharge:
                breakdown = calc.calculate_with_surcharge(params, args.surcharge)
            else:
                breakdown = calc.calculate_hourly_rate(params)

            calc.print_breakdown(breakdown, args.detailed)


if __name__ == "__main__":
    main()
