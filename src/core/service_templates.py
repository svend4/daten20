"""
Service Templates System

Pre-configured templates for common service types.
Allows quick service creation with standard configurations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from src.models import ServiceConfig, BasicInfo, FinancialData


@dataclass
class ServiceTemplate:
    """Service template definition"""
    id: str
    name: str
    category: str
    description: str
    default_region: str
    default_brutto_rate: float
    default_hours_per_month: int
    use_umlages: bool
    tags: List[str]
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ServiceTemplate':
        """Create from dictionary"""
        return cls(**data)


class ServiceTemplateManager:
    """Manages service templates"""

    def __init__(self, templates_dir: str = "data/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates_file = self.templates_dir / "service_templates.json"

        # Initialize with default templates if file doesn't exist
        if not self.templates_file.exists():
            self._create_default_templates()

    def _create_default_templates(self):
        """Create default service templates"""
        default_templates = [
            # Daily Living Assistance
            ServiceTemplate(
                id="daily_shopping",
                name="Shopping Assistance",
                category="Daily Living",
                description="Assistance with grocery shopping and errands",
                default_region="Bavaria",
                default_brutto_rate=38.50,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["shopping", "errands", "daily_living"],
                notes="Standard rate for shopping assistance services"
            ),
            ServiceTemplate(
                id="daily_cleaning",
                name="Household Cleaning",
                category="Daily Living",
                description="Household cleaning and maintenance services",
                default_region="Bavaria",
                default_brutto_rate=35.00,
                default_hours_per_month=120,
                use_umlages=True,
                tags=["cleaning", "household", "daily_living"],
                notes="Includes basic cleaning tasks"
            ),
            ServiceTemplate(
                id="daily_cooking",
                name="Meal Preparation",
                category="Daily Living",
                description="Meal planning and cooking assistance",
                default_region="Bavaria",
                default_brutto_rate=40.00,
                default_hours_per_month=100,
                use_umlages=True,
                tags=["cooking", "meals", "daily_living"],
                notes="Includes meal planning and preparation"
            ),
            ServiceTemplate(
                id="daily_laundry",
                name="Laundry Services",
                category="Daily Living",
                description="Washing, drying, and ironing services",
                default_region="Bavaria",
                default_brutto_rate=32.00,
                default_hours_per_month=80,
                use_umlages=True,
                tags=["laundry", "household", "daily_living"],
                notes="Basic laundry services"
            ),

            # Personal Care
            ServiceTemplate(
                id="care_personal_hygiene",
                name="Personal Hygiene Assistance",
                category="Personal Care",
                description="Assistance with bathing, grooming, and personal care",
                default_region="Bavaria",
                default_brutto_rate=45.00,
                default_hours_per_month=140,
                use_umlages=True,
                tags=["personal_care", "hygiene", "caregiving"],
                notes="Requires trained caregiver"
            ),
            ServiceTemplate(
                id="care_medication",
                name="Medication Management",
                category="Personal Care",
                description="Medication reminders and assistance",
                default_region="Bavaria",
                default_brutto_rate=48.00,
                default_hours_per_month=80,
                use_umlages=True,
                tags=["medication", "health", "caregiving"],
                notes="Medical training recommended"
            ),
            ServiceTemplate(
                id="care_mobility",
                name="Mobility Assistance",
                category="Personal Care",
                description="Assistance with walking, transfers, and mobility",
                default_region="Bavaria",
                default_brutto_rate=43.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["mobility", "physical_assistance", "caregiving"],
                notes="May require special equipment"
            ),

            # Transportation
            ServiceTemplate(
                id="transport_medical",
                name="Medical Appointments Transport",
                category="Transportation",
                description="Transportation to medical appointments",
                default_region="Bavaria",
                default_brutto_rate=42.00,
                default_hours_per_month=60,
                use_umlages=True,
                tags=["transportation", "medical", "appointments"],
                notes="Includes waiting time"
            ),
            ServiceTemplate(
                id="transport_social",
                name="Social Activities Transport",
                category="Transportation",
                description="Transportation to social and recreational activities",
                default_region="Bavaria",
                default_brutto_rate=38.00,
                default_hours_per_month=80,
                use_umlages=True,
                tags=["transportation", "social", "recreation"],
                notes="Flexible scheduling"
            ),

            # Social Participation
            ServiceTemplate(
                id="social_companion",
                name="Social Companionship",
                category="Social Participation",
                description="Companionship and social interaction",
                default_region="Bavaria",
                default_brutto_rate=36.00,
                default_hours_per_month=120,
                use_umlages=True,
                tags=["social", "companionship", "activities"],
                notes="Promotes social engagement"
            ),
            ServiceTemplate(
                id="social_activities",
                name="Recreational Activities",
                category="Social Participation",
                description="Participation in hobbies and recreational activities",
                default_region="Bavaria",
                default_brutto_rate=37.00,
                default_hours_per_month=100,
                use_umlages=True,
                tags=["recreation", "hobbies", "social"],
                notes="Tailored to individual interests"
            ),

            # Professional Services
            ServiceTemplate(
                id="prof_nursing",
                name="Professional Nursing Care",
                category="Professional Services",
                description="Skilled nursing care services",
                default_region="Bavaria",
                default_brutto_rate=55.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["nursing", "medical", "professional"],
                notes="Requires qualified nurse"
            ),
            ServiceTemplate(
                id="prof_therapy",
                name="Therapeutic Services",
                category="Professional Services",
                description="Physical or occupational therapy",
                default_region="Bavaria",
                default_brutto_rate=58.00,
                default_hours_per_month=80,
                use_umlages=True,
                tags=["therapy", "rehabilitation", "professional"],
                notes="Certified therapist required"
            ),
            ServiceTemplate(
                id="prof_counseling",
                name="Social Counseling",
                category="Professional Services",
                description="Professional social work and counseling",
                default_region="Bavaria",
                default_brutto_rate=52.00,
                default_hours_per_month=60,
                use_umlages=True,
                tags=["counseling", "social_work", "professional"],
                notes="Licensed social worker required"
            ),

            # Specialized Care
            ServiceTemplate(
                id="spec_dementia",
                name="Dementia Care",
                category="Specialized Care",
                description="Specialized care for dementia patients",
                default_region="Bavaria",
                default_brutto_rate=50.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["dementia", "specialized", "caregiving"],
                notes="Dementia training required"
            ),
            ServiceTemplate(
                id="spec_disability",
                name="Disability Support Services",
                category="Specialized Care",
                description="Support for individuals with disabilities",
                default_region="Bavaria",
                default_brutto_rate=47.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["disability", "specialized", "support"],
                notes="Disability awareness training recommended"
            ),
            ServiceTemplate(
                id="spec_palliative",
                name="Palliative Care",
                category="Specialized Care",
                description="End-of-life care and support",
                default_region="Bavaria",
                default_brutto_rate=60.00,
                default_hours_per_month=120,
                use_umlages=True,
                tags=["palliative", "end_of_life", "specialized"],
                notes="Palliative care certification required"
            ),

            # Emergency/Crisis
            ServiceTemplate(
                id="emergency_respite",
                name="Emergency Respite Care",
                category="Emergency Services",
                description="Temporary emergency caregiving services",
                default_region="Bavaria",
                default_brutto_rate=53.00,
                default_hours_per_month=100,
                use_umlages=True,
                tags=["emergency", "respite", "temporary"],
                notes="Available on short notice"
            ),
            ServiceTemplate(
                id="emergency_crisis",
                name="Crisis Intervention",
                category="Emergency Services",
                description="Immediate crisis response and support",
                default_region="Bavaria",
                default_brutto_rate=65.00,
                default_hours_per_month=60,
                use_umlages=True,
                tags=["emergency", "crisis", "immediate"],
                notes="24/7 availability required"
            ),

            # Administrative Support
            ServiceTemplate(
                id="admin_paperwork",
                name="Administrative Assistance",
                category="Administrative",
                description="Help with paperwork and administrative tasks",
                default_region="Bavaria",
                default_brutto_rate=40.00,
                default_hours_per_month=40,
                use_umlages=True,
                tags=["administrative", "paperwork", "support"],
                notes="Includes correspondence and organization"
            ),
            ServiceTemplate(
                id="admin_finance",
                name="Financial Management Support",
                category="Administrative",
                description="Assistance with bills and financial matters",
                default_region="Bavaria",
                default_brutto_rate=45.00,
                default_hours_per_month=30,
                use_umlages=True,
                tags=["financial", "administrative", "support"],
                notes="Financial literacy required"
            ),
        ]

        self.save_templates(default_templates)

    def get_all_templates(self) -> List[ServiceTemplate]:
        """Get all templates"""
        if not self.templates_file.exists():
            return []

        with open(self.templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [ServiceTemplate.from_dict(t) for t in data]

    def get_template_by_id(self, template_id: str) -> Optional[ServiceTemplate]:
        """Get template by ID"""
        templates = self.get_all_templates()
        for template in templates:
            if template.id == template_id:
                return template
        return None

    def get_templates_by_category(self, category: str) -> List[ServiceTemplate]:
        """Get all templates in a category"""
        templates = self.get_all_templates()
        return [t for t in templates if t.category == category]

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        templates = self.get_all_templates()
        return sorted(list(set(t.category for t in templates)))

    def search_templates(self, query: str) -> List[ServiceTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        templates = self.get_all_templates()

        results = []
        for template in templates:
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    def save_templates(self, templates: List[ServiceTemplate]):
        """Save templates to file"""
        data = [t.to_dict() for t in templates]

        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_template(self, template: ServiceTemplate) -> bool:
        """Add a new template"""
        templates = self.get_all_templates()

        # Check if ID already exists
        if any(t.id == template.id for t in templates):
            return False

        templates.append(template)
        self.save_templates(templates)
        return True

    def update_template(self, template_id: str, updated_template: ServiceTemplate) -> bool:
        """Update an existing template"""
        templates = self.get_all_templates()

        for i, template in enumerate(templates):
            if template.id == template_id:
                # Preserve the original ID
                updated_template.id = template_id
                templates[i] = updated_template
                self.save_templates(templates)
                return True

        return False

    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        templates = self.get_all_templates()
        original_count = len(templates)

        templates = [t for t in templates if t.id != template_id]

        if len(templates) < original_count:
            self.save_templates(templates)
            return True

        return False

    def create_service_from_template(
        self,
        template_id: str,
        service_name: Optional[str] = None,
        region: Optional[str] = None,
        **overrides
    ) -> Optional[ServiceConfig]:
        """Create a service configuration from a template"""
        template = self.get_template_by_id(template_id)

        if not template:
            return None

        # Use template values or overrides
        final_name = service_name or template.name
        final_region = region or template.default_region
        final_brutto_rate = overrides.get('brutto_rate', template.default_brutto_rate)
        final_hours = overrides.get('hours_per_month', template.default_hours_per_month)

        # Create service configuration
        service = ServiceConfig(
            basic_info=BasicInfo(
                service_name=final_name,
                region=final_region
            ),
            financial=FinancialData(
                brutto_rate=final_brutto_rate,
                hours_per_month=final_hours
            )
        )

        return service

    def export_templates(self, output_path: str) -> bool:
        """Export templates to a file"""
        try:
            templates = self.get_all_templates()
            data = [t.to_dict() for t in templates]

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    def import_templates(self, input_path: str, merge: bool = False) -> bool:
        """Import templates from a file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            new_templates = [ServiceTemplate.from_dict(t) for t in data]

            if merge:
                # Merge with existing templates
                existing_templates = self.get_all_templates()
                existing_ids = {t.id for t in existing_templates}

                # Add only new templates
                for template in new_templates:
                    if template.id not in existing_ids:
                        existing_templates.append(template)

                self.save_templates(existing_templates)
            else:
                # Replace all templates
                self.save_templates(new_templates)

            return True
        except Exception:
            return False


# Global instance
_template_manager: Optional[ServiceTemplateManager] = None


def get_template_manager() -> ServiceTemplateManager:
    """Get global template manager instance"""
    global _template_manager

    if _template_manager is None:
        _template_manager = ServiceTemplateManager()

    return _template_manager
