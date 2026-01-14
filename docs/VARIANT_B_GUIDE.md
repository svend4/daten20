# 🏥 VARIANT B: mSchablone SERVICE MANAGEMENT APPLICATION - COMPLETE GUIDE

**Version:** 1.0.0
**Created:** 2026-01-14
**Status:** Implementation Ready
**Complexity:** Medium (Specialized Domain)
**Estimated LOC:** 5,000+ lines (backend) + 1,500+ lines (frontend)

---

## 🎯 EXECUTIVE SUMMARY

**Variant B** is a **specialized Service Management Application** built around the mSchablone template, designed for **German personal budget service planning and financial calculations**. This application handles complex German social insurance contributions (KV, PV, RV, AV, UV) and provides comprehensive service planning capabilities.

### Key Capabilities

| Category | Features | Target Users |
|----------|----------|--------------|
| **Service Management** | CRUD operations, Category management, Specifications | Service Planners, Administrators |
| **Financial Calculations** | German social contributions, Budget planning, Cost forecasting | Financial Controllers, Accountants |
| **Template Processing** | mSchablone parsing, Multi-language support, Validation | System Administrators |
| **Report Generation** | PDF, Excel, Word reports, Email delivery | Managers, External Stakeholders |
| **Admin Interface** | Web-based management, User permissions, Audit trails | System Administrators |

### Domain Context

**Personal Budget (Persönliches Budget)** is a German social service delivery model where individuals with disabilities or special needs receive financial resources to purchase services directly. This application manages:

- Service identification and specifications
- Financial calculations including employer contributions
- Regional coefficient adjustments
- Multi-level service descriptions
- Risk assessments and sustainability planning

---

## 📐 SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   VARIANT B ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                       │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  Web Admin Interface (Jinja2 Templates)                     │   │
│  │  - Service Management UI  - Financial Calculator UI         │   │
│  │  - Report Builder         - User Management                 │   │
│  │  - Dashboard with KPIs    - Audit Log Viewer                │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │ HTTP/REST API                               │
│  ┌────────────────────▼───────────────────────────────────────┐   │
│  │                    APPLICATION LAYER                        │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  FastAPI Application                                        │   │
│  │  - Authentication (JWT)                                     │   │
│  │  - Authorization (RBAC)                                     │   │
│  │  - Request Validation (Pydantic)                            │   │
│  │  - API Documentation (OpenAPI/Swagger)                      │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │                                             │
│  ┌────────────────────▼───────────────────────────────────────┐   │
│  │                    BUSINESS LOGIC LAYER                     │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │
│  │  │  mSchablone  │  │   Service    │  │  Financial   │     │   │
│  │  │   Parser     │  │  Management  │  │  Calculator  │     │   │
│  │  │              │  │              │  │              │     │   │
│  │  │ • Template   │  │ • CRUD Ops   │  │ • KV, PV, RV │     │   │
│  │  │   Parsing    │  │ • Categories │  │ • AV, UV     │     │   │
│  │  │ • Validation │  │ • Specs      │  │ • Hourly Rate│     │   │
│  │  │ • Multi-lang │  │ • Regional   │  │ • Budget Plan│     │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │
│  │  │   Report     │  │    User      │  │    Audit     │     │   │
│  │  │  Generator   │  │  Management  │  │     Log      │     │   │
│  │  │              │  │              │  │              │     │   │
│  │  │ • PDF        │  │ • Roles      │  │ • Changes    │     │   │
│  │  │ • Excel      │  │ • Permissions│  │ • Access     │     │   │
│  │  │ • Word       │  │ • Org Mgmt   │  │ • Actions    │     │   │
│  │  │ • Email      │  │              │  │              │     │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘ │
│                       │                                             │
│  ┌────────────────────▼───────────────────────────────────────┐   │
│  │                    DATA ACCESS LAYER                        │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  SQLAlchemy ORM  │  Redis Cache  │  Celery Task Queue     │   │
│  └────────────────────┬───────────────────────────────────────┘   │
│                       │                                             │
│  ┌────────────────────▼───────────────────────────────────────┐   │
│  │                    PERSISTENCE LAYER                        │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  PostgreSQL (Primary)  │  Redis (Cache)  │  S3 (Documents)│   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 MODULE SPECIFICATIONS

### Module 1: mSchablone Parser

**File:** `variant_b/parser/template_parser.py`
**Lines of Code:** ~600
**Dependencies:** re, json, yaml, pydantic

#### Template Structure

The mSchablone template contains:

```
1. Service Identification (Leistungsidentifikation)
   - Service ID, Name, Category
   - Provider information
   - Service description (multi-level)

2. Financial Parameters (Finanzparameter)
   - Base hourly rate (Stundensatz)
   - Employer contributions:
     * KV (Krankenversicherung - Health Insurance): 7.3%
     * PV (Pflegeversicherung - Long-term Care Insurance): 1.525%
     * RV (Rentenversicherung - Pension Insurance): 9.3%
     * AV (Arbeitslosenversicherung - Unemployment Insurance): 1.2%
     * UV (Unfallversicherung - Accident Insurance): Variable

3. System Settings (Systemeinstellungen)
   - Calculation modes
   - Regional coefficients
   - Currency settings
   - Tax configurations

4. Service Categories (Leistungskategorien)
   - Household services (Haushalt)
   - Social services (Soziale Betreuung)
   - Medical services (Medizinische Versorgung)
   - Professional services (Berufliche Unterstützung)
   - Educational services (Bildung)

5. Risk Assessment (Risikobewertung)
   - Risk identification
   - Mitigation strategies
   - Monitoring plans

6. Implementation Phases (Umsetzungsphasen)
   - Phase definitions
   - Milestones
   - Dependencies

7. Sustainability Criteria (Nachhaltigkeitskriterien)
   - Environmental impact
   - Social responsibility
   - Economic viability
```

#### Parser Class Structure

```python
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator
import re
import yaml


class ServiceIdentification(BaseModel):
    """Service identification data"""
    service_id: str
    name: str
    category: str
    subcategory: Optional[str]
    provider_name: str
    provider_id: str
    description_level_1: str
    description_level_2: Optional[str]
    description_level_3: Optional[str]
    keywords: List[str]


class FinancialParameters(BaseModel):
    """Financial calculation parameters"""
    base_hourly_rate: Decimal
    employer_contributions: Dict[str, Decimal] = {
        'KV': Decimal('7.3'),   # Krankenversicherung
        'PV': Decimal('1.525'), # Pflegeversicherung
        'RV': Decimal('9.3'),   # Rentenversicherung
        'AV': Decimal('1.2'),   # Arbeitslosenversicherung
        'UV': Decimal('1.6')    # Unfallversicherung (example)
    }
    regional_coefficient: Decimal = Decimal('1.0')
    currency: str = 'EUR'


class SystemSettings(BaseModel):
    """System configuration"""
    calculation_mode: str  # 'gross', 'net'
    regional_zone: str     # 'zone_1', 'zone_2', etc.
    tax_year: int
    include_vat: bool = True
    vat_rate: Decimal = Decimal('19.0')


class mSchabloneParser:
    """
    Parser for mSchablone template

    Capabilities:
    - Parse Russian/German bilingual content
    - Extract structured data
    - Validate required fields
    - Handle multiple encoding formats
    - Support versioning
    """

    def __init__(self, template_path: str):
        self.template_path = template_path
        self.raw_content = None
        self.parsed_data = {}
        self.version = None

    def load_template(self) -> 'mSchabloneParser':
        """Load template file"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.raw_content = f.read()
        return self

    def detect_version(self) -> str:
        """Detect template version"""
        version_pattern = r'VERSION:\s*(\d+\.\d+)'
        match = re.search(version_pattern, self.raw_content)
        self.version = match.group(1) if match else '1.0'
        return self.version

    def parse_service_identification(self) -> ServiceIdentification:
        """Extract service identification section"""
        # Extract service ID
        service_id_pattern = r'LEISTUNGS-ID:\s*([A-Z0-9-]+)'
        service_id = re.search(
            service_id_pattern,
            self.raw_content
        ).group(1)

        # Extract service name
        name_pattern = r'LEISTUNGSNAME:\s*(.+?)(?:\n|$)'
        name = re.search(name_pattern, self.raw_content).group(1).strip()

        # Extract category
        category_pattern = r'KATEGORIE:\s*(.+?)(?:\n|$)'
        category = re.search(
            category_pattern,
            self.raw_content
        ).group(1).strip()

        # Build ServiceIdentification object
        return ServiceIdentification(
            service_id=service_id,
            name=name,
            category=category,
            # ... extract other fields
        )

    def parse_financial_parameters(self) -> FinancialParameters:
        """Extract financial parameters"""
        # Extract base hourly rate
        rate_pattern = r'STUNDENSATZ:\s*(\d+[.,]\d+)'
        rate_str = re.search(rate_pattern, self.raw_content).group(1)
        base_rate = Decimal(rate_str.replace(',', '.'))

        # Extract employer contributions if customized
        contributions = {}
        for contrib_type in ['KV', 'PV', 'RV', 'AV', 'UV']:
            pattern = f'{contrib_type}:\s*(\d+[.,]\d+)%?'
            match = re.search(pattern, self.raw_content)
            if match:
                contributions[contrib_type] = Decimal(
                    match.group(1).replace(',', '.')
                )

        # Extract regional coefficient
        regional_pattern = r'REGIONAL-KOEFFIZIENT:\s*(\d+[.,]\d+)'
        match = re.search(regional_pattern, self.raw_content)
        regional_coef = Decimal(
            match.group(1).replace(',', '.')
        ) if match else Decimal('1.0')

        return FinancialParameters(
            base_hourly_rate=base_rate,
            employer_contributions=contributions,
            regional_coefficient=regional_coef
        )

    def parse_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract service categories and subcategories"""
        categories = {
            'haushalt': [],        # Household
            'sozial': [],          # Social
            'medizinisch': [],     # Medical
            'beruflich': [],       # Professional
            'bildung': []          # Educational
        }

        # Parse each category section
        category_sections = re.findall(
            r'=== (.+?) ===\n(.*?)(?===|$)',
            self.raw_content,
            re.DOTALL
        )

        for category_name, content in category_sections:
            category_key = self._normalize_category(category_name)
            if category_key in categories:
                services = self._extract_services_from_section(content)
                categories[category_key] = services

        return categories

    def validate(self) -> List[str]:
        """Validate parsed data"""
        errors = []

        # Check required fields
        required_fields = [
            'service_id', 'name', 'category',
            'base_hourly_rate'
        ]

        for field in required_fields:
            if field not in self.parsed_data:
                errors.append(f"Missing required field: {field}")

        # Validate financial parameters
        if 'base_hourly_rate' in self.parsed_data:
            rate = self.parsed_data['base_hourly_rate']
            if rate <= 0:
                errors.append("Base hourly rate must be positive")

        # Validate employer contributions sum
        if 'employer_contributions' in self.parsed_data:
            total = sum(self.parsed_data['employer_contributions'].values())
            if total > 50:  # Sanity check: >50% seems wrong
                errors.append(
                    f"Employer contributions total ({total}%) seems too high"
                )

        return errors

    def export_to_dict(self) -> Dict[str, Any]:
        """Export parsed data as dictionary"""
        return self.parsed_data

    def export_to_json(self, file_path: str):
        """Export parsed data as JSON"""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                self.parsed_data,
                f,
                indent=2,
                ensure_ascii=False,
                default=str
            )

    def export_to_yaml(self, file_path: str):
        """Export parsed data as YAML"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.parsed_data,
                f,
                allow_unicode=True,
                default_flow_style=False
            )

    # Helper methods
    def _normalize_category(self, category: str) -> str:
        """Normalize category name"""
        mapping = {
            'haushalt': 'haushalt',
            'household': 'haushalt',
            'sozial': 'sozial',
            'social': 'sozial',
            'medizinisch': 'medizinisch',
            'medical': 'medizinisch',
            'beruflich': 'beruflich',
            'professional': 'beruflich',
            'bildung': 'bildung',
            'educational': 'bildung'
        }
        return mapping.get(category.lower(), 'other')

    def _extract_services_from_section(
        self,
        content: str
    ) -> List[Dict[str, Any]]:
        """Extract individual services from category section"""
        services = []
        # Implementation depends on template format
        return services
```

#### Usage Example

```python
# Parse mSchablone template
parser = mSchabloneParser('/path/to/mSchablone')
parser.load_template()
parser.detect_version()

# Extract data
service_id = parser.parse_service_identification()
financial = parser.parse_financial_parameters()
categories = parser.parse_categories()

# Validate
errors = parser.validate()
if errors:
    print("Validation errors:", errors)
else:
    print("Template is valid!")

# Export
parser.export_to_json('parsed_template.json')
parser.export_to_yaml('parsed_template.yaml')
```

---

### Module 2: Financial Calculator

**File:** `variant_b/finance/calculator.py`
**Lines of Code:** ~900
**Dependencies:** decimal, pydantic

#### German Social Contributions

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
from datetime import date


class GermanSocialContributions:
    """
    German social insurance contribution rates (2024)

    Source: German Federal Ministry of Labour and Social Affairs
    """

    # Health Insurance (Krankenversicherung)
    KV_RATE = Decimal('7.3')  # Employer portion
    KV_EMPLOYEE_RATE = Decimal('7.3')  # Employee portion
    KV_ADDITIONAL_RATE = Decimal('1.6')  # Average additional rate

    # Long-term Care Insurance (Pflegeversicherung)
    PV_RATE = Decimal('1.525')  # Base rate
    PV_ADDITIONAL_CHILDLESS = Decimal('0.35')  # Additional for childless 23+

    # Pension Insurance (Rentenversicherung)
    RV_RATE = Decimal('9.3')  # Employer portion
    RV_EMPLOYEE_RATE = Decimal('9.3')  # Employee portion

    # Unemployment Insurance (Arbeitslosenversicherung)
    AV_RATE = Decimal('1.2')  # Employer portion
    AV_EMPLOYEE_RATE = Decimal('1.2')  # Employee portion

    # Accident Insurance (Unfallversicherung)
    # Varies by industry and risk class
    UV_RATE_LOW_RISK = Decimal('1.0')
    UV_RATE_MEDIUM_RISK = Decimal('1.6')
    UV_RATE_HIGH_RISK = Decimal('3.0')

    # Income thresholds (Beitragsbemessungsgrenzen) 2024
    BBG_GRV_WEST = Decimal('87600')  # Pension, West Germany (annual)
    BBG_GRV_EAST = Decimal('85200')  # Pension, East Germany (annual)
    BBG_GKV = Decimal('59850')  # Health insurance (annual)


class FinancialCalculator:
    """
    Financial calculator for German personal budget services

    Features:
    - Gross/net salary calculations
    - Employer contribution calculations
    - Regional coefficient adjustments
    - Budget planning
    - Cost forecasting
    """

    def __init__(
        self,
        regional_zone: str = 'west',
        risk_class: str = 'low'
    ):
        self.regional_zone = regional_zone
        self.risk_class = risk_class
        self.contributions = GermanSocialContributions()

    def calculate_employer_contributions(
        self,
        gross_salary: Decimal,
        has_children: bool = True
    ) -> Dict[str, Decimal]:
        """
        Calculate employer social insurance contributions

        Args:
            gross_salary: Gross monthly salary
            has_children: Whether employee has children (affects PV)

        Returns:
            Dictionary with contribution amounts
        """
        contributions = {}

        # Health Insurance (KV)
        contributions['KV'] = (
            gross_salary * self.contributions.KV_RATE / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Long-term Care Insurance (PV)
        pv_rate = self.contributions.PV_RATE
        if not has_children:
            pv_rate += self.contributions.PV_ADDITIONAL_CHILDLESS
        contributions['PV'] = (
            gross_salary * pv_rate / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Pension Insurance (RV)
        contributions['RV'] = (
            gross_salary * self.contributions.RV_RATE / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Unemployment Insurance (AV)
        contributions['AV'] = (
            gross_salary * self.contributions.AV_RATE / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Accident Insurance (UV)
        uv_rate = {
            'low': self.contributions.UV_RATE_LOW_RISK,
            'medium': self.contributions.UV_RATE_MEDIUM_RISK,
            'high': self.contributions.UV_RATE_HIGH_RISK
        }[self.risk_class]
        contributions['UV'] = (
            gross_salary * uv_rate / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Total employer contributions
        contributions['total'] = sum(contributions.values())

        return contributions

    def calculate_hourly_rate(
        self,
        annual_salary: Decimal,
        working_hours_per_week: Decimal = Decimal('40'),
        weeks_per_year: int = 52
    ) -> Decimal:
        """Calculate hourly rate from annual salary"""
        total_hours = working_hours_per_week * weeks_per_year
        hourly_rate = (annual_salary / total_hours).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        return hourly_rate

    def calculate_service_cost(
        self,
        hourly_rate: Decimal,
        hours_per_month: Decimal,
        include_contributions: bool = True,
        regional_coefficient: Decimal = Decimal('1.0'),
        overhead_percentage: Decimal = Decimal('15.0')
    ) -> Dict[str, Decimal]:
        """
        Calculate total service cost including all components

        Args:
            hourly_rate: Base hourly rate
            hours_per_month: Service hours per month
            include_contributions: Include employer contributions
            regional_coefficient: Regional adjustment (e.g., 1.1 for expensive areas)
            overhead_percentage: Administrative overhead percentage

        Returns:
            Cost breakdown dictionary
        """
        result = {}

        # Base cost
        base_cost = (hourly_rate * hours_per_month).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        result['base_cost'] = base_cost

        # Regional adjustment
        regional_adjusted = (base_cost * regional_coefficient).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        result['regional_adjusted'] = regional_adjusted

        # Employer contributions
        if include_contributions:
            contributions = self.calculate_employer_contributions(
                regional_adjusted
            )
            result['contributions'] = contributions
            result['cost_with_contributions'] = (
                regional_adjusted + contributions['total']
            )
        else:
            result['contributions'] = {}
            result['cost_with_contributions'] = regional_adjusted

        # Overhead
        overhead = (
            result['cost_with_contributions'] * overhead_percentage / 100
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        result['overhead'] = overhead

        # Total cost
        result['total_cost'] = result['cost_with_contributions'] + overhead

        # VAT (if applicable)
        vat = (result['total_cost'] * Decimal('19') / 100).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
        result['vat'] = vat
        result['total_with_vat'] = result['total_cost'] + vat

        return result

    def calculate_budget_plan(
        self,
        services: List[Dict[str, Any]],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Create budget plan for multiple services

        Args:
            services: List of service configurations
            months: Planning period in months

        Returns:
            Comprehensive budget plan
        """
        budget = {
            'services': [],
            'monthly_total': Decimal('0'),
            'annual_total': Decimal('0'),
            'breakdown_by_category': {},
            'breakdown_by_cost_type': {
                'base_cost': Decimal('0'),
                'contributions': Decimal('0'),
                'overhead': Decimal('0'),
                'vat': Decimal('0')
            }
        }

        for service in services:
            service_cost = self.calculate_service_cost(
                hourly_rate=service['hourly_rate'],
                hours_per_month=service['hours_per_month'],
                regional_coefficient=service.get(
                    'regional_coefficient',
                    Decimal('1.0')
                ),
                overhead_percentage=service.get(
                    'overhead_percentage',
                    Decimal('15.0')
                )
            )

            service_budget = {
                'name': service['name'],
                'category': service['category'],
                'monthly_cost': service_cost['total_with_vat'],
                'annual_cost': service_cost['total_with_vat'] * months,
                'details': service_cost
            }

            budget['services'].append(service_budget)
            budget['monthly_total'] += service_budget['monthly_cost']

            # Breakdown by category
            category = service['category']
            if category not in budget['breakdown_by_category']:
                budget['breakdown_by_category'][category] = Decimal('0')
            budget['breakdown_by_category'][category] += (
                service_budget['monthly_cost']
            )

            # Breakdown by cost type
            budget['breakdown_by_cost_type']['base_cost'] += (
                service_cost['base_cost']
            )
            budget['breakdown_by_cost_type']['contributions'] += (
                service_cost['contributions'].get('total', Decimal('0'))
            )
            budget['breakdown_by_cost_type']['overhead'] += (
                service_cost['overhead']
            )
            budget['breakdown_by_cost_type']['vat'] += service_cost['vat']

        budget['annual_total'] = budget['monthly_total'] * months

        return budget

    def forecast_costs(
        self,
        current_budget: Dict[str, Any],
        growth_rate: Decimal = Decimal('2.5'),  # Annual growth %
        years: int = 5
    ) -> List[Dict[str, Decimal]]:
        """
        Forecast costs for future years

        Args:
            current_budget: Current budget plan
            growth_rate: Expected annual cost growth percentage
            years: Number of years to forecast

        Returns:
            List of forecasted annual costs
        """
        forecast = []
        current_annual = current_budget['annual_total']

        for year in range(1, years + 1):
            forecasted_amount = (
                current_annual * (
                    (1 + growth_rate / 100) ** year
                )
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            forecast.append({
                'year': year,
                'amount': forecasted_amount,
                'growth_from_baseline': (
                    (forecasted_amount / current_annual - 1) * 100
                ).quantize(Decimal('0.01'))
            })

        return forecast
```

#### API Endpoints

```python
# POST /api/v1/finance/calculate-contributions
# POST /api/v1/finance/calculate-service-cost
# POST /api/v1/finance/create-budget-plan
# POST /api/v1/finance/forecast-costs
# GET  /api/v1/finance/contribution-rates
```

---

### Module 3: Service Management

**File:** `variant_b/services/service_manager.py`
**Lines of Code:** ~800
**Dependencies:** sqlalchemy, pydantic

#### Database Models

```python
from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class ServiceCategory(str, enum.Enum):
    HOUSEHOLD = 'household'
    SOCIAL = 'social'
    MEDICAL = 'medical'
    PROFESSIONAL = 'professional'
    EDUCATIONAL = 'educational'


class ServiceStatus(str, enum.Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ARCHIVED = 'archived'


class Service(Base):
    __tablename__ = 'services'

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(Enum(ServiceCategory), nullable=False)
    subcategory = Column(String(100))
    status = Column(Enum(ServiceStatus), default=ServiceStatus.DRAFT)

    # Descriptions (multi-level)
    description_short = Column(String(500))
    description_medium = Column(Text)
    description_long = Column(Text)

    # Financial parameters
    base_hourly_rate = Column(Numeric(10, 2), nullable=False)
    regional_coefficient = Column(Numeric(5, 2), default=1.0)
    overhead_percentage = Column(Numeric(5, 2), default=15.0)

    # Provider information
    provider_id = Column(String(50), ForeignKey('providers.id'))
    provider = relationship('Provider', back_populates='services')

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(50), ForeignKey('users.id'))
    updated_by = Column(String(50), ForeignKey('users.id'))

    # Audit
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)

    # Relationships
    specifications = relationship(
        'ServiceSpecification',
        back_populates='service'
    )
    budget_items = relationship('BudgetItem', back_populates='service')


class ServiceSpecification(Base):
    __tablename__ = 'service_specifications'

    id = Column(String(50), primary_key=True)
    service_id = Column(String(50), ForeignKey('services.id'))
    service = relationship('Service', back_populates='specifications')

    # Specification details
    key = Column(String(100), nullable=False)
    value = Column(Text)
    data_type = Column(String(20))  # 'string', 'number', 'boolean', 'json'
    unit = Column(String(50))  # 'hours', 'km', 'sessions', etc.

    # Validation
    is_required = Column(Boolean, default=False)
    min_value = Column(Numeric(10, 2))
    max_value = Column(Numeric(10, 2))


class Provider(Base):
    __tablename__ = 'providers'

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    legal_form = Column(String(50))  # 'GmbH', 'e.V.', etc.
    tax_id = Column(String(50))
    address = Column(Text)
    contact_email = Column(String(200))
    contact_phone = Column(String(50))

    # Certification
    is_certified = Column(Boolean, default=False)
    certification_date = Column(DateTime)
    certification_expires = Column(DateTime)

    services = relationship('Service', back_populates='provider')
```

#### Service Manager Class

```python
class ServiceManager:
    """
    Service management system

    Features:
    - CRUD operations for services
    - Category management
    - Provider management
    - Specification templates
    - Versioning
    """

    def __init__(self, db_session):
        self.db = db_session

    def create_service(
        self,
        data: Dict[str, Any],
        user_id: str
    ) -> Service:
        """Create new service"""
        service = Service(
            id=self._generate_service_id(),
            name=data['name'],
            category=ServiceCategory(data['category']),
            subcategory=data.get('subcategory'),
            description_short=data.get('description_short'),
            description_medium=data.get('description_medium'),
            description_long=data.get('description_long'),
            base_hourly_rate=Decimal(str(data['base_hourly_rate'])),
            regional_coefficient=Decimal(
                str(data.get('regional_coefficient', 1.0))
            ),
            overhead_percentage=Decimal(
                str(data.get('overhead_percentage', 15.0))
            ),
            provider_id=data.get('provider_id'),
            created_by=user_id,
            status=ServiceStatus.DRAFT
        )

        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)

        # Add specifications if provided
        if 'specifications' in data:
            for spec_data in data['specifications']:
                self.add_specification(service.id, spec_data)

        return service

    def get_service(self, service_id: str) -> Optional[Service]:
        """Retrieve service by ID"""
        return self.db.query(Service).filter(
            Service.id == service_id
        ).first()

    def update_service(
        self,
        service_id: str,
        data: Dict[str, Any],
        user_id: str
    ) -> Service:
        """Update existing service"""
        service = self.get_service(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")

        # Update fields
        for key, value in data.items():
            if hasattr(service, key) and key not in ['id', 'created_at', 'created_by']:
                setattr(service, key, value)

        service.updated_by = user_id
        service.updated_at = datetime.utcnow()
        service.version += 1

        self.db.commit()
        self.db.refresh(service)

        return service

    def delete_service(self, service_id: str) -> bool:
        """Delete service (soft delete - mark as archived)"""
        service = self.get_service(service_id)
        if not service:
            return False

        service.status = ServiceStatus.ARCHIVED
        self.db.commit()

        return True

    def list_services(
        self,
        category: Optional[ServiceCategory] = None,
        status: Optional[ServiceStatus] = None,
        provider_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Service]:
        """List services with filters"""
        query = self.db.query(Service)

        if category:
            query = query.filter(Service.category == category)
        if status:
            query = query.filter(Service.status == status)
        if provider_id:
            query = query.filter(Service.provider_id == provider_id)

        return query.offset(skip).limit(limit).all()

    def add_specification(
        self,
        service_id: str,
        spec_data: Dict[str, Any]
    ) -> ServiceSpecification:
        """Add specification to service"""
        spec = ServiceSpecification(
            id=self._generate_spec_id(),
            service_id=service_id,
            key=spec_data['key'],
            value=spec_data['value'],
            data_type=spec_data.get('data_type', 'string'),
            unit=spec_data.get('unit'),
            is_required=spec_data.get('is_required', False),
            min_value=spec_data.get('min_value'),
            max_value=spec_data.get('max_value')
        )

        self.db.add(spec)
        self.db.commit()
        self.db.refresh(spec)

        return spec

    def get_service_cost(
        self,
        service_id: str,
        hours_per_month: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate service cost"""
        service = self.get_service(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")

        calculator = FinancialCalculator()
        return calculator.calculate_service_cost(
            hourly_rate=service.base_hourly_rate,
            hours_per_month=hours_per_month,
            regional_coefficient=service.regional_coefficient,
            overhead_percentage=service.overhead_percentage
        )

    def _generate_service_id(self) -> str:
        """Generate unique service ID"""
        import uuid
        return f"SRV-{uuid.uuid4().hex[:8].upper()}"

    def _generate_spec_id(self) -> str:
        """Generate unique specification ID"""
        import uuid
        return f"SPEC-{uuid.uuid4().hex[:8].upper()}"
```

---

### Module 4: Report Generator

**File:** `variant_b/reports/pdf_generator.py`
**Lines of Code:** ~600
**Dependencies:** reportlab, openpyxl, python-docx

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO
from typing import Dict, List, Any


class PDFReportGenerator:
    """
    PDF report generation for services and budgets

    Report types:
    - Service Catalog
    - Budget Plan
    - Financial Summary
    - Cost Forecast
    - Custom Reports
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        """Add custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=30
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceAfter=12
        ))

    def generate_service_catalog(
        self,
        services: List[Service],
        output_path: Optional[str] = None
    ) -> bytes:
        """Generate service catalog PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Title
        title = Paragraph(
            "Leistungskatalog / Service Catalog",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*cm))

        # Services by category
        categories = {}
        for service in services:
            cat = service.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(service)

        for category, cat_services in categories.items():
            # Category heading
            cat_heading = Paragraph(
                category.upper(),
                self.styles['CustomHeading']
            )
            story.append(cat_heading)
            story.append(Spacer(1, 0.3*cm))

            # Services table
            table_data = [[
                'Service ID',
                'Name',
                'Hourly Rate (€)',
                'Status'
            ]]

            for service in cat_services:
                table_data.append([
                    service.id,
                    service.name,
                    f"{service.base_hourly_rate:.2f}",
                    service.status.value
                ])

            table = Table(table_data, colWidths=[4*cm, 8*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            story.append(Spacer(1, 0.5*cm))

        # Build PDF
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def generate_budget_plan(
        self,
        budget: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """Generate budget plan PDF with financial details"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        story = []

        # Title
        title = Paragraph(
            "Budgetplan / Budget Plan",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*cm))

        # Summary
        summary_data = [
            ['Monthly Total', f"€ {budget['monthly_total']:,.2f}"],
            ['Annual Total', f"€ {budget['annual_total']:,.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[10*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.7*cm))

        # Services breakdown
        story.append(Paragraph(
            "Services Breakdown",
            self.styles['CustomHeading']
        ))
        story.append(Spacer(1, 0.3*cm))

        service_data = [['Service', 'Category', 'Monthly Cost (€)']]
        for service in budget['services']:
            service_data.append([
                service['name'],
                service['category'],
                f"{service['monthly_cost']:,.2f}"
            ])

        service_table = Table(
            service_data,
            colWidths=[7*cm, 5*cm, 4*cm]
        )
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(service_table)

        # Build PDF
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes
```

---

## 🔌 API REFERENCE

### Service Management

```http
POST   /api/v1/services                 # Create service
GET    /api/v1/services                 # List services
GET    /api/v1/services/{id}            # Get service details
PUT    /api/v1/services/{id}            # Update service
DELETE /api/v1/services/{id}            # Delete service
POST   /api/v1/services/{id}/specifications  # Add specification
GET    /api/v1/services/{id}/cost       # Calculate cost
```

### Financial Calculations

```http
POST /api/v1/finance/calculate-contributions    # Calculate employer contributions
POST /api/v1/finance/calculate-service-cost     # Calculate service cost
POST /api/v1/finance/create-budget-plan         # Create budget plan
POST /api/v1/finance/forecast-costs             # Forecast future costs
GET  /api/v1/finance/contribution-rates         # Get current contribution rates
```

### Template Processing

```http
POST /api/v1/templates/parse                    # Parse mSchablone template
POST /api/v1/templates/validate                 # Validate template
GET  /api/v1/templates/{id}                     # Get parsed template
POST /api/v1/templates/{id}/export              # Export template (JSON/YAML)
```

### Report Generation

```http
POST /api/v1/reports/service-catalog            # Generate service catalog
POST /api/v1/reports/budget-plan                # Generate budget plan
POST /api/v1/reports/financial-summary          # Generate financial summary
POST /api/v1/reports/custom                     # Generate custom report
GET  /api/v1/reports/{id}/download              # Download report
POST /api/v1/reports/{id}/email                 # Email report
```

---

## 🎨 FRONTEND STRUCTURE

### Admin Interface (Jinja2 Templates)

```
variant_b/frontend/
├── templates/
│   ├── base.html                    # Base template
│   ├── dashboard.html               # Main dashboard
│   ├── services/
│   │   ├── list.html               # Service list
│   │   ├── detail.html             # Service detail
│   │   ├── create.html             # Create service
│   │   └── edit.html               # Edit service
│   ├── finance/
│   │   ├── calculator.html         # Financial calculator
│   │   ├── budget_plan.html        # Budget planner
│   │   └── forecast.html           # Cost forecast
│   ├── reports/
│   │   ├── builder.html            # Report builder
│   │   └── history.html            # Report history
│   └── admin/
│       ├── users.html              # User management
│       ├── providers.html          # Provider management
│       └── settings.html           # System settings
└── static/
    ├── css/
    │   └── admin.css               # Admin styles
    ├── js/
    │   ├── service-manager.js      # Service management logic
    │   ├── calculator.js           # Calculator logic
    │   └── report-builder.js       # Report builder logic
    └── img/
        └── logo.png
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Core Setup (Days 1-3)
- [ ] Create project structure
- [ ] Set up database models
- [ ] Configure authentication
- [ ] Create API framework

### Phase 2: Parser & Calculator (Days 4-7)
- [ ] Implement mSchablone parser
- [ ] Build financial calculator
- [ ] Add German social contribution calculations
- [ ] Write tests for parser and calculator

### Phase 3: Service Management (Days 8-12)
- [ ] Implement service CRUD
- [ ] Create provider management
- [ ] Add specification system
- [ ] Build API endpoints

### Phase 4: Reports & UI (Days 13-17)
- [ ] Build PDF generator
- [ ] Create Excel generator
- [ ] Implement admin interface
- [ ] Add dashboard

### Phase 5: Testing & Deployment (Days 18-21)
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Docker deployment
- [ ] Production release

---

**Document Status:** ✅ Complete and Ready
**Next Document:** [VARIANT_C_GUIDE.md](./VARIANT_C_GUIDE.md)
