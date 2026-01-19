"""
White-Labeling & Customization Framework

Provides white-labeling capabilities:
- Custom branding (logos, colors, themes)
- Domain customization
- Email template customization
- UI component customization
- Multi-language support
- Custom CSS/JavaScript injection
- Widget embedding
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ThemeMode(str, Enum):
    """Theme modes"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class BrandingElement(str, Enum):
    """Branding elements"""

    PRIMARY_LOGO = "primary_logo"
    SECONDARY_LOGO = "secondary_logo"
    FAVICON = "favicon"
    LOGIN_BACKGROUND = "login_background"
    EMAIL_HEADER = "email_header"
    WATERMARK = "watermark"


@dataclass
class ColorScheme:
    """Color scheme configuration"""

    primary: str = "#1976d2"
    secondary: str = "#dc004e"
    success: str = "#4caf50"
    warning: str = "#ff9800"
    error: str = "#f44336"
    info: str = "#2196f3"
    background: str = "#ffffff"
    surface: str = "#f5f5f5"
    text_primary: str = "#212121"
    text_secondary: str = "#757575"


@dataclass
class Typography:
    """Typography configuration"""

    font_family: str = "Roboto, sans-serif"
    font_size_base: int = 14
    font_size_h1: int = 32
    font_size_h2: int = 24
    font_size_h3: int = 20
    font_size_h4: int = 16
    font_size_h5: int = 14
    font_size_h6: int = 12
    line_height: float = 1.5
    letter_spacing: str = "normal"


@dataclass
class BrandAssets:
    """Brand assets"""

    primary_logo_url: Optional[str] = None
    secondary_logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    login_background_url: Optional[str] = None
    email_header_url: Optional[str] = None
    watermark_url: Optional[str] = None
    custom_css_url: Optional[str] = None
    custom_js_url: Optional[str] = None


@dataclass
class EmailTemplate:
    """Email template"""

    id: str
    name: str
    subject: str
    html_body: str
    text_body: str
    variables: List[str] = field(default_factory=list)
    language: str = "en"


@dataclass
class UICustomization:
    """UI customization settings"""

    hide_powered_by: bool = False
    custom_footer_text: Optional[str] = None
    custom_menu_items: List[Dict[str, str]] = field(default_factory=list)
    disabled_features: List[str] = field(default_factory=list)
    custom_dashboard_widgets: List[str] = field(default_factory=list)
    login_message: Optional[str] = None
    support_email: Optional[str] = None
    support_url: Optional[str] = None


@dataclass
class WhiteLabelConfig:
    """White-label configuration"""

    tenant_id: str
    company_name: str
    domain: Optional[str] = None
    subdomain: Optional[str] = None

    # Branding
    brand_assets: BrandAssets = field(default_factory=BrandAssets)
    color_scheme_light: ColorScheme = field(default_factory=ColorScheme)
    color_scheme_dark: Optional[ColorScheme] = None
    typography: Typography = field(default_factory=Typography)
    theme_mode: ThemeMode = ThemeMode.AUTO

    # UI Customization
    ui_customization: UICustomization = field(default_factory=UICustomization)

    # Localization
    default_language: str = "en"
    supported_languages: List[str] = field(default_factory=lambda: ["en"])

    # Custom code
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None

    # Email templates
    email_templates: Dict[str, EmailTemplate] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BrandingManager:
    """Manages branding assets"""

    def __init__(self):
        self.assets_cache: Dict[str, BrandAssets] = {}

    def upload_asset(self, tenant_id: str, asset_type: BrandingElement, file_data: bytes, filename: str) -> str:
        """Upload branding asset"""
        # In production, upload to cloud storage (S3, GCS, Azure Blob)
        asset_url = f"https://cdn.example.com/{tenant_id}/{asset_type.value}/{filename}"

        print(f"[Branding] Uploaded {asset_type.value} for tenant {tenant_id}")
        return asset_url

    def delete_asset(self, tenant_id: str, asset_type: BrandingElement):
        """Delete branding asset"""
        print(f"[Branding] Deleted {asset_type.value} for tenant {tenant_id}")

    def get_assets(self, tenant_id: str) -> BrandAssets:
        """Get all branding assets for tenant"""
        return self.assets_cache.get(tenant_id, BrandAssets())


class ThemeEngine:
    """Generates CSS themes from configuration"""

    def generate_css(self, color_scheme: ColorScheme, typography: Typography, theme_mode: ThemeMode) -> str:
        """Generate CSS from theme configuration"""
        css = f"""
/* Auto-generated theme CSS */
:root {{
    /* Colors */
    --color-primary: {color_scheme.primary};
    --color-secondary: {color_scheme.secondary};
    --color-success: {color_scheme.success};
    --color-warning: {color_scheme.warning};
    --color-error: {color_scheme.error};
    --color-info: {color_scheme.info};
    --color-background: {color_scheme.background};
    --color-surface: {color_scheme.surface};
    --color-text-primary: {color_scheme.text_primary};
    --color-text-secondary: {color_scheme.text_secondary};

    /* Typography */
    --font-family: {typography.font_family};
    --font-size-base: {typography.font_size_base}px;
    --font-size-h1: {typography.font_size_h1}px;
    --font-size-h2: {typography.font_size_h2}px;
    --font-size-h3: {typography.font_size_h3}px;
    --font-size-h4: {typography.font_size_h4}px;
    --font-size-h5: {typography.font_size_h5}px;
    --font-size-h6: {typography.font_size_h6}px;
    --line-height: {typography.line_height};
    --letter-spacing: {typography.letter_spacing};
}}

body {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    line-height: var(--line-height);
    color: var(--color-text-primary);
    background-color: var(--color-background);
}}

.btn-primary {{
    background-color: var(--color-primary);
    border-color: var(--color-primary);
}}

.btn-secondary {{
    background-color: var(--color-secondary);
    border-color: var(--color-secondary);
}}

h1 {{ font-size: var(--font-size-h1); }}
h2 {{ font-size: var(--font-size-h2); }}
h3 {{ font-size: var(--font-size-h3); }}
h4 {{ font-size: var(--font-size-h4); }}
h5 {{ font-size: var(--font-size-h5); }}
h6 {{ font-size: var(--font-size-h6); }}
"""

        return css

    def generate_theme_bundle(self, config: WhiteLabelConfig) -> Dict[str, str]:
        """Generate complete theme bundle"""
        return {
            "light_css": self.generate_css(config.color_scheme_light, config.typography, ThemeMode.LIGHT),
            "dark_css": (
                self.generate_css(
                    config.color_scheme_dark or config.color_scheme_light, config.typography, ThemeMode.DARK
                )
                if config.color_scheme_dark
                else None
            ),
            "custom_css": config.custom_css,
            "custom_js": config.custom_js,
        }


class EmailTemplateEngine:
    """Manages email templates"""

    def __init__(self):
        self.templates: Dict[str, EmailTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default email templates"""
        self.templates["welcome"] = EmailTemplate(
            id="welcome",
            name="Welcome Email",
            subject="Welcome to {{company_name}}",
            html_body="""
                <html>
                <head><style>body { font-family: Arial, sans-serif; }</style></head>
                <body>
                    <img src="{{logo_url}}" alt="Logo" style="max-width: 200px;"/>
                    <h1 style="color: {{primary_color}};">Welcome!</h1>
                    <p>Hello {{user_name}},</p>
                    <p>Welcome to {{company_name}}. We're excited to have you on board.</p>
                    <p><a href="{{login_url}}" style="background-color: {{primary_color}}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a></p>
                    <p>Best regards,<br/>The {{company_name}} Team</p>
                </body>
                </html>
            """,
            text_body="Welcome to {{company_name}}! Visit {{login_url}} to get started.",
            variables=["company_name", "user_name", "login_url", "logo_url", "primary_color"],
        )

        self.templates["password_reset"] = EmailTemplate(
            id="password_reset",
            name="Password Reset",
            subject="Reset your password",
            html_body="""
                <html>
                <body>
                    <h1>Password Reset</h1>
                    <p>Hello {{user_name}},</p>
                    <p>You requested to reset your password. Click the button below:</p>
                    <p><a href="{{reset_url}}">Reset Password</a></p>
                    <p>This link expires in 24 hours.</p>
                </body>
                </html>
            """,
            text_body="Reset your password: {{reset_url}}",
            variables=["user_name", "reset_url"],
        )

        self.templates["invoice"] = EmailTemplate(
            id="invoice",
            name="Invoice",
            subject="Invoice #{{invoice_number}}",
            html_body="""
                <html>
                <body>
                    <h1>Invoice #{{invoice_number}}</h1>
                    <p>Amount: {{amount}}</p>
                    <p>Due Date: {{due_date}}</p>
                    <p><a href="{{invoice_url}}">View Invoice</a></p>
                </body>
                </html>
            """,
            text_body="Invoice #{{invoice_number}}: {{amount}} due {{due_date}}",
            variables=["invoice_number", "amount", "due_date", "invoice_url"],
        )

    def customize_template(self, tenant_id: str, template_id: str, customizations: Dict[str, str]) -> EmailTemplate:
        """Customize email template for tenant"""
        base_template = self.templates.get(template_id)

        if not base_template:
            raise ValueError(f"Template {template_id} not found")

        # Create customized copy
        custom_template = EmailTemplate(
            id=f"{tenant_id}_{template_id}",
            name=customizations.get("name", base_template.name),
            subject=customizations.get("subject", base_template.subject),
            html_body=customizations.get("html_body", base_template.html_body),
            text_body=customizations.get("text_body", base_template.text_body),
            variables=base_template.variables,
        )

        return custom_template

    def render_template(self, template: EmailTemplate, variables: Dict[str, Any]) -> Dict[str, str]:
        """Render email template with variables"""
        html_body = template.html_body
        text_body = template.text_body
        subject = template.subject

        # Simple variable substitution
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            html_body = html_body.replace(placeholder, str(var_value))
            text_body = text_body.replace(placeholder, str(var_value))
            subject = subject.replace(placeholder, str(var_value))

        return {"subject": subject, "html_body": html_body, "text_body": text_body}


class LocalizationManager:
    """Manages multi-language support"""

    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_default_translations()

    def _load_default_translations(self):
        """Load default translations"""
        self.translations["en"] = {
            "app.title": "Document Management System",
            "app.welcome": "Welcome",
            "login.title": "Sign In",
            "login.email": "Email",
            "login.password": "Password",
            "login.submit": "Sign In",
            "dashboard.title": "Dashboard",
            "documents.title": "Documents",
            "upload.title": "Upload Document",
        }

        self.translations["de"] = {
            "app.title": "Dokumentenverwaltungssystem",
            "app.welcome": "Willkommen",
            "login.title": "Anmelden",
            "login.email": "E-Mail",
            "login.password": "Passwort",
            "login.submit": "Anmelden",
            "dashboard.title": "Dashboard",
            "documents.title": "Dokumente",
            "upload.title": "Dokument hochladen",
        }

        self.translations["fr"] = {
            "app.title": "Système de gestion documentaire",
            "app.welcome": "Bienvenue",
            "login.title": "Se connecter",
            "login.email": "E-mail",
            "login.password": "Mot de passe",
            "login.submit": "Se connecter",
            "dashboard.title": "Tableau de bord",
            "documents.title": "Documents",
            "upload.title": "Télécharger un document",
        }

    def add_translation(self, language: str, key: str, value: str):
        """Add translation"""
        if language not in self.translations:
            self.translations[language] = {}

        self.translations[language][key] = value

    def get_translation(self, language: str, key: str, default: Optional[str] = None) -> str:
        """Get translation"""
        return self.translations.get(language, {}).get(key, default or key)

    def get_all_translations(self, language: str) -> Dict[str, str]:
        """Get all translations for language"""
        return self.translations.get(language, {})


class DomainManager:
    """Manages custom domains"""

    def __init__(self):
        self.domain_mappings: Dict[str, str] = {}  # domain -> tenant_id

    def register_domain(self, tenant_id: str, domain: str) -> bool:
        """Register custom domain for tenant"""
        # Check if domain is already registered
        if domain in self.domain_mappings:
            return False

        self.domain_mappings[domain] = tenant_id
        print(f"[Domain] Registered {domain} for tenant {tenant_id}")

        # In production, would:
        # 1. Validate domain ownership (DNS TXT record)
        # 2. Configure SSL certificate (Let's Encrypt)
        # 3. Update CDN/load balancer routing

        return True

    def unregister_domain(self, domain: str) -> bool:
        """Unregister domain"""
        if domain in self.domain_mappings:
            tenant_id = self.domain_mappings.pop(domain)
            print(f"[Domain] Unregistered {domain} from tenant {tenant_id}")
            return True
        return False

    def get_tenant_by_domain(self, domain: str) -> Optional[str]:
        """Get tenant ID by domain"""
        return self.domain_mappings.get(domain)

    def verify_domain_ownership(self, domain: str, verification_token: str) -> bool:
        """Verify domain ownership via DNS TXT record"""
        # In production, query DNS for TXT record
        # dns.resolver.query(f"_dms-verify.{domain}", 'TXT')
        print(f"[Domain] Verifying ownership of {domain}")
        return True


class WhiteLabelManager:
    """Main white-label management"""

    def __init__(self):
        self.configs: Dict[str, WhiteLabelConfig] = {}
        self.branding_manager = BrandingManager()
        self.theme_engine = ThemeEngine()
        self.email_engine = EmailTemplateEngine()
        self.localization_manager = LocalizationManager()
        self.domain_manager = DomainManager()

    def create_config(self, tenant_id: str, company_name: str, domain: Optional[str] = None) -> WhiteLabelConfig:
        """Create white-label configuration"""
        config = WhiteLabelConfig(tenant_id=tenant_id, company_name=company_name, domain=domain)

        self.configs[tenant_id] = config

        print(f"[WhiteLabel] Created config for {company_name}")
        return config

    def update_branding(
        self,
        tenant_id: str,
        color_scheme: Optional[ColorScheme] = None,
        typography: Optional[Typography] = None,
        theme_mode: Optional[ThemeMode] = None,
    ) -> bool:
        """Update branding configuration"""
        config = self.configs.get(tenant_id)
        if not config:
            return False

        if color_scheme:
            config.color_scheme_light = color_scheme
        if typography:
            config.typography = typography
        if theme_mode:
            config.theme_mode = theme_mode

        config.updated_at = datetime.now()

        print(f"[WhiteLabel] Updated branding for tenant {tenant_id}")
        return True

    def upload_branding_asset(
        self, tenant_id: str, asset_type: BrandingElement, file_data: bytes, filename: str
    ) -> str:
        """Upload branding asset"""
        asset_url = self.branding_manager.upload_asset(tenant_id, asset_type, file_data, filename)

        config = self.configs.get(tenant_id)
        if config:
            # Update config with asset URL
            if asset_type == BrandingElement.PRIMARY_LOGO:
                config.brand_assets.primary_logo_url = asset_url
            elif asset_type == BrandingElement.FAVICON:
                config.brand_assets.favicon_url = asset_url
            # ... etc

        return asset_url

    def customize_email_template(
        self, tenant_id: str, template_id: str, customizations: Dict[str, str]
    ) -> EmailTemplate:
        """Customize email template"""
        template = self.email_engine.customize_template(tenant_id, template_id, customizations)

        config = self.configs.get(tenant_id)
        if config:
            config.email_templates[template_id] = template

        return template

    def register_custom_domain(self, tenant_id: str, domain: str) -> bool:
        """Register custom domain"""
        success = self.domain_manager.register_domain(tenant_id, domain)

        if success:
            config = self.configs.get(tenant_id)
            if config:
                config.domain = domain

        return success

    def get_config(self, tenant_id: str) -> Optional[WhiteLabelConfig]:
        """Get white-label configuration"""
        return self.configs.get(tenant_id)

    def get_theme_bundle(self, tenant_id: str) -> Dict[str, str]:
        """Get complete theme bundle for tenant"""
        config = self.configs.get(tenant_id)
        if not config:
            return {}

        return self.theme_engine.generate_theme_bundle(config)

    def render_email(self, tenant_id: str, template_id: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """Render email with tenant branding"""
        config = self.configs.get(tenant_id)
        if not config:
            return {}

        # Get template (custom or default)
        template = config.email_templates.get(template_id, self.email_engine.templates.get(template_id))

        if not template:
            return {}

        # Add branding variables
        variables.update(
            {
                "company_name": config.company_name,
                "logo_url": config.brand_assets.primary_logo_url or "",
                "primary_color": config.color_scheme_light.primary,
            }
        )

        return self.email_engine.render_template(template, variables)


# Global instance
_whitelabel_manager: Optional[WhiteLabelManager] = None


def get_whitelabel_manager() -> WhiteLabelManager:
    """Get global white-label manager instance"""
    global _whitelabel_manager

    if _whitelabel_manager is None:
        _whitelabel_manager = WhiteLabelManager()

    return _whitelabel_manager
