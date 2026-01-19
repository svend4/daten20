"""Financial data models"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class InsuranceRates:
    """Social insurance rates (employer's share)"""

    kv_er: Decimal = Decimal("7.3")  # Health insurance
    kv_zusatz_er: Decimal = Decimal("0.8")  # Additional health insurance
    pv_er: Decimal = Decimal("1.525")  # Care insurance
    pv_er_sn: Decimal = Decimal("2.025")  # Care insurance for Saxony
    rv_er: Decimal = Decimal("9.3")  # Pension insurance
    av_er: Decimal = Decimal("1.2")  # Unemployment insurance
    uv_er: Decimal = Decimal("1.3")  # Accident insurance

    def total(self, is_saxony: bool = False) -> Decimal:
        """Calculate total insurance rate"""
        pv = self.pv_er_sn if is_saxony else self.pv_er
        return self.kv_er + self.kv_zusatz_er + pv + self.rv_er + self.av_er + self.uv_er


@dataclass
class Umlages:
    """Umlage contributions"""

    u1: Decimal = Decimal("0.9")  # Sick pay compensation
    u2: Decimal = Decimal("0.4")  # Maternity protection
    u3: Decimal = Decimal("0.09")  # Insolvency insurance

    def total(self, exclude_u1_u2: bool = False) -> Decimal:
        """Calculate total umlages"""
        if exclude_u1_u2:
            return self.u3
        return self.u1 + self.u2 + self.u3


@dataclass
class Surcharges:
    """Surcharge rates for special conditions"""

    night: Decimal = Decimal("25")  # Night work
    weekend: Decimal = Decimal("50")  # Weekend work
    holiday: Decimal = Decimal("100")  # Holiday work
    urgent: Decimal = Decimal("15")  # Urgent/emergency services

    def get(self, surcharge_type: str) -> Decimal:
        """Get surcharge by type"""
        return getattr(self, surcharge_type, Decimal("0"))


@dataclass
class FinancialParameters:
    """All financial parameters for cost calculation"""

    brutto_rate: Decimal  # Hourly gross rate
    insurance_rates: InsuranceRates = field(default_factory=InsuranceRates)
    umlages: Umlages = field(default_factory=Umlages)
    surcharges: Surcharges = field(default_factory=Surcharges)
    materials_per_month: Decimal = Decimal("0")  # Monthly materials cost
    materials_per_hour: Decimal = Decimal("0")  # Hourly materials cost
    admin_percent: Decimal = Decimal("0")  # Admin as percentage
    admin_per_hour: Decimal = Decimal("0")  # Admin per hour
    region_coefficient: Decimal = Decimal("1.0")  # Regional multiplier
    is_saxony: bool = False  # Special rule for Saxony
    use_umlages: bool = True  # Use U1/U2/U3
    use_vacation_reserve: bool = False  # Use vacation reserve instead
    vacation_reserve_percent: Decimal = Decimal("0")  # Vacation reserve percentage
    surcharge_base: str = "full_cost"  # "full_cost" or "brutto_only"

    def __post_init__(self):
        """Convert numeric types to Decimal if needed"""
        if not isinstance(self.brutto_rate, Decimal):
            self.brutto_rate = Decimal(str(self.brutto_rate))
        if not isinstance(self.materials_per_month, Decimal):
            self.materials_per_month = Decimal(str(self.materials_per_month))
        if not isinstance(self.materials_per_hour, Decimal):
            self.materials_per_hour = Decimal(str(self.materials_per_hour))
        if not isinstance(self.admin_percent, Decimal):
            self.admin_percent = Decimal(str(self.admin_percent))
        if not isinstance(self.admin_per_hour, Decimal):
            self.admin_per_hour = Decimal(str(self.admin_per_hour))
        if not isinstance(self.region_coefficient, Decimal):
            self.region_coefficient = Decimal(str(self.region_coefficient))
        if not isinstance(self.vacation_reserve_percent, Decimal):
            self.vacation_reserve_percent = Decimal(str(self.vacation_reserve_percent))


@dataclass
class CostBreakdown:
    """Detailed cost breakdown"""

    brutto_rate: Decimal

    # Insurance contributions
    kv_contribution: Decimal = Decimal("0")
    pv_contribution: Decimal = Decimal("0")
    rv_contribution: Decimal = Decimal("0")
    av_contribution: Decimal = Decimal("0")
    uv_contribution: Decimal = Decimal("0")
    total_insurance: Decimal = Decimal("0")

    # Umlages
    u1_contribution: Decimal = Decimal("0")
    u2_contribution: Decimal = Decimal("0")
    u3_contribution: Decimal = Decimal("0")
    total_umlages: Decimal = Decimal("0")

    # Alternative: Vacation reserve
    vacation_reserve: Decimal = Decimal("0")

    # Materials and admin
    materials_cost: Decimal = Decimal("0")
    admin_cost: Decimal = Decimal("0")

    # Base costs
    base_hourly_cost: Decimal = Decimal("0")

    # Surcharges
    surcharges_applied: Dict[str, Decimal] = field(default_factory=dict)
    total_surcharge: Decimal = Decimal("0")

    # Regional
    region_coefficient: Decimal = Decimal("1.0")

    # Final
    final_hourly_rate: Decimal = Decimal("0")

    calculation_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    calculation_mode: str = "with_umlages"  # "with_umlages" or "with_reserve"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "brutto_rate": float(self.brutto_rate),
            "insurance": {
                "kv": float(self.kv_contribution),
                "pv": float(self.pv_contribution),
                "rv": float(self.rv_contribution),
                "av": float(self.av_contribution),
                "uv": float(self.uv_contribution),
                "total": float(self.total_insurance),
            },
            "umlages": {
                "u1": float(self.u1_contribution),
                "u2": float(self.u2_contribution),
                "u3": float(self.u3_contribution),
                "total": float(self.total_umlages),
            },
            "vacation_reserve": float(self.vacation_reserve),
            "materials": float(self.materials_cost),
            "admin": float(self.admin_cost),
            "base_cost": float(self.base_hourly_cost),
            "surcharges": {k: float(v) for k, v in self.surcharges_applied.items()},
            "total_surcharge": float(self.total_surcharge),
            "region_coefficient": float(self.region_coefficient),
            "final_rate": float(self.final_hourly_rate),
            "date": self.calculation_date,
            "mode": self.calculation_mode,
        }


@dataclass
class ServiceCost:
    """Total cost for a service"""

    hourly_rate: Decimal
    hours: Decimal
    total_cost: Decimal
    breakdown: CostBreakdown

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "hourly_rate": float(self.hourly_rate),
            "hours": float(self.hours),
            "total_cost": float(self.total_cost),
            "breakdown": self.breakdown.to_dict(),
        }
