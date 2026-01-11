"""Unit tests for Financial Calculator"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from decimal import Decimal

from src.financial_calculator import FinancialCalculator
from src.models.financial import FinancialParameters, InsuranceRates, Umlages


class TestFinancialCalculator:
    """Test Financial Calculator"""

    def setup_method(self):
        """Setup before each test"""
        self.calculator = FinancialCalculator()

    def test_basic_calculation(self):
        """Test basic hourly rate calculation"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))

        breakdown = self.calculator.calculate_hourly_rate(params)

        assert breakdown.brutto_rate == Decimal("25.00")
        assert breakdown.final_hourly_rate > breakdown.brutto_rate
        assert breakdown.total_insurance > 0
        assert breakdown.total_umlages > 0

    def test_insurance_contributions(self):
        """Test social insurance calculations"""
        params = FinancialParameters(brutto_rate=Decimal("100.00"))

        breakdown = self.calculator.calculate_hourly_rate(params)

        # Check that all insurance components are calculated
        assert breakdown.kv_contribution > 0
        assert breakdown.pv_contribution > 0
        assert breakdown.rv_contribution > 0
        assert breakdown.av_contribution > 0
        assert breakdown.uv_contribution > 0

        # Total should be sum of components
        total = (breakdown.kv_contribution + breakdown.pv_contribution +
                breakdown.rv_contribution + breakdown.av_contribution +
                breakdown.uv_contribution)

        assert abs(float(breakdown.total_insurance - total)) < 0.01

    def test_umlages_mode(self):
        """Test calculation with umlages"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))
        params.use_umlages = True
        params.use_vacation_reserve = False

        breakdown = self.calculator.calculate_hourly_rate(params)

        assert breakdown.calculation_mode == "with_umlages"
        assert breakdown.total_umlages > 0
        assert breakdown.vacation_reserve == Decimal("0")

    def test_vacation_reserve_mode(self):
        """Test calculation with vacation reserve"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))
        params.use_umlages = False
        params.use_vacation_reserve = True
        params.vacation_reserve_percent = Decimal("12.0")

        breakdown = self.calculator.calculate_hourly_rate(params)

        assert breakdown.calculation_mode == "with_reserve"
        assert breakdown.vacation_reserve > 0
        # U1 and U2 should be 0, but U3 should still be included
        assert breakdown.u1_contribution == Decimal("0")
        assert breakdown.u2_contribution == Decimal("0")
        assert breakdown.u3_contribution > Decimal("0")

    def test_regional_coefficient(self):
        """Test regional coefficient application"""
        params1 = FinancialParameters(brutto_rate=Decimal("25.00"))
        params1.region_coefficient = Decimal("1.0")

        params2 = FinancialParameters(brutto_rate=Decimal("25.00"))
        params2.region_coefficient = Decimal("1.20")

        breakdown1 = self.calculator.calculate_hourly_rate(params1)
        breakdown2 = self.calculator.calculate_hourly_rate(params2)

        # With coefficient 1.2, final rate should be 20% higher
        expected_rate = breakdown1.base_hourly_cost * Decimal("1.20")
        assert abs(float(breakdown2.final_hourly_rate - expected_rate)) < 0.01

    def test_materials_cost(self):
        """Test materials cost inclusion"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))
        params.materials_per_hour = Decimal("2.50")

        breakdown = self.calculator.calculate_hourly_rate(params)

        assert breakdown.materials_cost == Decimal("2.50")
        assert breakdown.final_hourly_rate > breakdown.brutto_rate + Decimal("2.50")

    def test_admin_costs_percentage(self):
        """Test administrative costs as percentage"""
        params = FinancialParameters(brutto_rate=Decimal("100.00"))
        params.admin_percent = Decimal("10.0")

        breakdown = self.calculator.calculate_hourly_rate(params)

        # Admin should be approximately 10% of base
        base = params.brutto_rate + breakdown.total_insurance + breakdown.total_umlages
        expected_admin = base * Decimal("0.10")

        assert abs(float(breakdown.admin_cost - expected_admin)) < 0.5

    def test_surcharges(self):
        """Test surcharge calculations"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))

        # Calculate without surcharge
        breakdown1 = self.calculator.calculate_hourly_rate(params)

        # Calculate with weekend surcharge (50%)
        breakdown2 = self.calculator.calculate_with_surcharge(params, ['weekend'])

        assert breakdown2.final_hourly_rate > breakdown1.final_hourly_rate
        assert 'weekend' in breakdown2.surcharges_applied

    def test_total_cost(self):
        """Test total cost calculation"""
        params = FinancialParameters(brutto_rate=Decimal("25.00"))
        hours = Decimal("10")

        service_cost = self.calculator.calculate_total_cost(params, hours)

        assert service_cost.hours == hours
        assert service_cost.total_cost == service_cost.hourly_rate * hours

    def test_zero_brutto_rate(self):
        """Test handling of zero brutto rate"""
        params = FinancialParameters(brutto_rate=Decimal("0"))

        breakdown = self.calculator.calculate_hourly_rate(params)

        assert breakdown.brutto_rate == Decimal("0")
        assert breakdown.final_hourly_rate >= Decimal("0")

    def test_percentage_calculation_helper(self):
        """Test percentage calculation helper"""
        result = self.calculator._calculate_percentage(Decimal("100"), Decimal("10"))

        assert result == Decimal("10.00")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
