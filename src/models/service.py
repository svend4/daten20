"""Service data model"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .financial import FinancialParameters, CostBreakdown


@dataclass
class BasicInfo:
    """Basic service information"""
    service_name: str = ""
    target_group: str = ""
    region: str = ""
    provider_type: str = ""
    document_date: str = ""
    document_version: str = "1.0"
    responsible_person: str = ""


@dataclass
class Funding:
    """Funding information"""
    payer: str = ""
    documents: List[str] = field(default_factory=list)


@dataclass
class SystemSettings:
    """System settings for calculation"""
    use_umlages: bool = True
    use_vacation_reserve: bool = False
    surcharge_base: str = "full_cost"  # "full_cost" or "brutto_only"
    service_type: str = "social"  # domestic, social, medical, professional, educational


@dataclass
class Service:
    """Complete service definition"""
    id: Optional[int] = None
    basic_info: BasicInfo = field(default_factory=BasicInfo)
    financial: FinancialParameters = field(default_factory=FinancialParameters)
    system_settings: SystemSettings = field(default_factory=SystemSettings)
    funding: Funding = field(default_factory=Funding)

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = 1

    # Filled template content
    filled_content: Optional[str] = None

    # Financial calculation results
    cost_breakdown: Optional[CostBreakdown] = None

    # Additional data
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert service to dictionary"""
        return {
            "id": self.id,
            "basic_info": {
                "service_name": self.basic_info.service_name,
                "target_group": self.basic_info.target_group,
                "region": self.basic_info.region,
                "provider_type": self.basic_info.provider_type,
                "document_date": self.basic_info.document_date,
                "document_version": self.basic_info.document_version,
                "responsible_person": self.basic_info.responsible_person
            },
            "financial": {
                "brutto_rate": float(self.financial.brutto_rate),
                "insurance_rates": {
                    "kv_er": float(self.financial.insurance_rates.kv_er),
                    "pv_er": float(self.financial.insurance_rates.pv_er),
                    "rv_er": float(self.financial.insurance_rates.rv_er),
                    "av_er": float(self.financial.insurance_rates.av_er),
                    "uv_er": float(self.financial.insurance_rates.uv_er)
                },
                "umlages": {
                    "u1": float(self.financial.umlages.u1),
                    "u2": float(self.financial.umlages.u2),
                    "u3": float(self.financial.umlages.u3)
                },
                "materials_per_month": float(self.financial.materials_per_month),
                "admin_percent": float(self.financial.admin_percent),
                "region_coefficient": float(self.financial.region_coefficient)
            },
            "system_settings": {
                "use_umlages": self.system_settings.use_umlages,
                "use_vacation_reserve": self.system_settings.use_vacation_reserve,
                "surcharge_base": self.system_settings.surcharge_base,
                "service_type": self.system_settings.service_type
            },
            "funding": {
                "payer": self.funding.payer,
                "documents": self.funding.documents
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "custom_fields": self.custom_fields
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Service':
        """Create service from dictionary"""
        from decimal import Decimal

        service = cls()

        # Basic info
        if "basic_info" in data:
            bi = data["basic_info"]
            service.basic_info = BasicInfo(
                service_name=bi.get("service_name", ""),
                target_group=bi.get("target_group", ""),
                region=bi.get("region", ""),
                provider_type=bi.get("provider_type", ""),
                document_date=bi.get("document_date", ""),
                document_version=bi.get("document_version", "1.0"),
                responsible_person=bi.get("responsible_person", "")
            )

        # Financial parameters
        if "financial" in data:
            fin = data["financial"]
            service.financial.brutto_rate = Decimal(str(fin.get("brutto_rate", 0)))

            if "insurance_rates" in fin:
                ins = fin["insurance_rates"]
                service.financial.insurance_rates.kv_er = Decimal(str(ins.get("kv_er", 7.3)))
                service.financial.insurance_rates.pv_er = Decimal(str(ins.get("pv_er", 1.525)))
                service.financial.insurance_rates.rv_er = Decimal(str(ins.get("rv_er", 9.3)))
                service.financial.insurance_rates.av_er = Decimal(str(ins.get("av_er", 1.2)))
                service.financial.insurance_rates.uv_er = Decimal(str(ins.get("uv_er", 1.3)))

            if "umlages" in fin:
                uml = fin["umlages"]
                service.financial.umlages.u1 = Decimal(str(uml.get("u1", 0.9)))
                service.financial.umlages.u2 = Decimal(str(uml.get("u2", 0.4)))
                service.financial.umlages.u3 = Decimal(str(uml.get("u3", 0.09)))

            service.financial.materials_per_month = Decimal(str(fin.get("materials_per_month", 0)))
            service.financial.admin_percent = Decimal(str(fin.get("admin_percent", 0)))
            service.financial.region_coefficient = Decimal(str(fin.get("region_coefficient", 1.0)))

        # System settings
        if "system_settings" in data:
            ss = data["system_settings"]
            service.system_settings = SystemSettings(
                use_umlages=ss.get("use_umlages", True),
                use_vacation_reserve=ss.get("use_vacation_reserve", False),
                surcharge_base=ss.get("surcharge_base", "full_cost"),
                service_type=ss.get("service_type", "social")
            )

        # Funding
        if "funding" in data:
            fund = data["funding"]
            service.funding = Funding(
                payer=fund.get("payer", ""),
                documents=fund.get("documents", [])
            )

        # Metadata
        service.id = data.get("id")
        service.version = data.get("version", 1)
        service.custom_fields = data.get("custom_fields", {})

        if data.get("created_at"):
            service.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            service.updated_at = datetime.fromisoformat(data["updated_at"])

        return service

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Service':
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))
