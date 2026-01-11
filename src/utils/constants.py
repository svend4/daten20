"""Constants for the Document Management System"""

# Template structure - all blocks in the mega-template
TEMPLATE_BLOCKS = {
    0: "ПАСПОРТ И ВХОДНЫЕ ДАННЫЕ (Технический фундамент)",
    1: "КОНЦЕПТУАЛЬНЫЕ ОСНОВЫ И СУЩНОСТЬ УСЛУГИ",
    2: "ПРАКТИЧЕСКАЯ ОРГАНИЗАЦИЯ И СТРУКТУРА УСЛУГИ",
    3: "ДОКУМЕНТООБОРОТ И ПРАВОВЫЕ ОСНОВАНИЯ",
    4: "ВАРИАНТЫ РЕАЛИЗАЦИИ И ПОДДЕРЖКИ",
    5: "ИНТЕГРАЦИЯ ТЕХНОЛОГИЙ И ИННОВАЦИЙ",
    6: "ПРИМЕНЕНИЕ И АДАПТАЦИЯ ПО ГРУППАМ",
    7: "ФИНАНСОВЫЕ СТРАТЕГИИ И ПРОГРАММЫ",
    8: "ДИНАМИЧЕСКАЯ АДАПТАЦИЯ И УПРАВЛЕНИЕ ИЗМЕНЕНИЯМИ",
    9: "УПРАВЛЕНИЕ РИСКАМИ И КАЧЕСТВОМ",
    10: "СПЕЦИАЛИЗИРОВАННЫЕ ФУНКЦИИ И ЭКОНОМИЧЕСКОЕ ПЛАНИРОВАНИЕ"
}

# Service types
SERVICE_TYPES = {
    "domestic": "Домашние услуги (Hauswirtschaft, Garten, Reparaturen)",
    "social": "Социальные услуги (Begleitung, Kommunikation, Freizeit)",
    "medical": "Медицинские услуги (Behandlungspflege, Therapiebegleitung)",
    "professional": "Профессиональные услуги (Arbeitsassistenz, Studienbegleitung)",
    "educational": "Образовательные услуги (Lernbegleitung, Schulassistenz)"
}

# Social insurance rates (employer's share) - default values for 2026
DEFAULT_INSURANCE_RATES = {
    "kv_er": 7.3,        # Krankenversicherung (Health insurance)
    "kv_zusatz_er": 0.8, # Additional health insurance contribution
    "pv_er": 1.525,      # Pflegeversicherung (Care insurance)
    "pv_er_sn": 2.025,   # Care insurance for Saxony
    "rv_er": 9.3,        # Rentenversicherung (Pension insurance)
    "av_er": 1.2,        # Arbeitslosenversicherung (Unemployment insurance)
    "uv_er": 1.3         # Unfallversicherung (Accident insurance)
}

# Umlages (additional contributions) - default values
DEFAULT_UMLAGES = {
    "u1": 0.9,   # Sick pay compensation
    "u2": 0.4,   # Maternity protection
    "u3": 0.09   # Insolvency insurance
}

# Surcharge types and default percentages
DEFAULT_SURCHARGES = {
    "night": 25,      # Night work
    "weekend": 50,    # Weekend work
    "holiday": 100,   # Holiday work
    "urgent": 15      # Urgent/emergency services
}

# Regional coefficients for different German states
REGIONAL_COEFFICIENTS = {
    "Baden-Württemberg": 1.15,
    "Bayern": 1.12,
    "Berlin": 1.20,
    "Brandenburg": 1.00,
    "Bremen": 1.10,
    "Hamburg": 1.25,
    "Hessen": 1.15,
    "Mecklenburg-Vorpommern": 0.95,
    "Niedersachsen": 1.05,
    "Nordrhein-Westfalen": 1.10,
    "Rheinland-Pfalz": 1.05,
    "Saarland": 1.00,
    "Sachsen": 0.95,
    "Sachsen-Anhalt": 0.95,
    "Schleswig-Holstein": 1.08,
    "Thüringen": 0.95
}

# Funding sources
FUNDING_SOURCES = [
    "Eingliederungshilfe",
    "Pflegekasse",
    "Krankenkasse",
    "Sozialamt",
    "Rentenversicherung",
    "Unfallversicherung",
    "Selbstzahler"
]

# Export formats
EXPORT_FORMATS = {
    "txt": "Plain Text",
    "md": "Markdown",
    "html": "HTML",
    "pdf": "PDF",
    "docx": "Microsoft Word",
    "json": "JSON",
    "yaml": "YAML"
}

# Database configuration
DATABASE_FILE = "data/services.db"
DATABASE_SCHEMA_VERSION = 1

# File paths
TEMPLATE_FILE = "mSchablone"
CONFIG_DIR = "config"
EXAMPLES_DIR = "config/examples"
EXPORTS_DIR = "data/exports"
TEMPLATES_DIR = "data/templates"

# Validation patterns
VARIABLE_PATTERN = r'\{([A-Za-z0-9_]+)\}'  # Matches {Variable_Name}
DATE_PATTERN = r'\d{2}\.\d{2}\.\d{4}'       # DD.MM.YYYY
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^[\d\s\-\+\(\)]+$'

# Calculation modes
CALCULATION_MODES = {
    "with_umlages": "С использованием U-умлаг (U1/U2/U3)",
    "with_reserve": "С резервом на отпуск/больничные без U1/U2"
}

# Surcharge application base
SURCHARGE_BASES = {
    "full_cost": "К полной стоимости часа (включая накладные)",
    "brutto_only": "К ставке брутто (без материалов/админа)"
}

# Color codes for CLI output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m"
}

# Icons for CLI
ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "question": "?",
    "arrow": "→",
    "bullet": "•"
}

# Default configuration template
DEFAULT_CONFIG = {
    "basic_info": {
        "service_name": "",
        "target_group": "",
        "region": "",
        "provider_type": "",
        "document_date": "",
        "document_version": "1.0",
        "responsible_person": ""
    },
    "financial": {
        "brutto_rate": 0.0,
        "employer_rates": DEFAULT_INSURANCE_RATES.copy(),
        "umlages": DEFAULT_UMLAGES.copy(),
        "surcharges": DEFAULT_SURCHARGES.copy(),
        "materials_per_month": 0.0,
        "materials_per_hour": 0.0,
        "admin_percent": 0.0,
        "admin_per_hour": 0.0,
        "region_coefficient": 1.0
    },
    "system_settings": {
        "use_umlages": True,
        "use_vacation_reserve": False,
        "surcharge_base": "full_cost",
        "service_type": "social"
    },
    "funding": {
        "payer": "",
        "documents": []
    }
}
