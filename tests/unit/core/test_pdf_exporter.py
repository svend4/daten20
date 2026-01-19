"""
Tests for PDF Export Module with Branding

Tests PDF generation with reportlab (programmatic).
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

# Mock reportlab before importing
mock_colors = Mock()
mock_colors.HexColor = Mock(side_effect=lambda x: f"Color({x})")
mock_colors.white = "white"
mock_colors.black = "black"
mock_colors.beige = "beige"
mock_colors.lightgrey = "lightgrey"
mock_colors.grey = "grey"

mock_enums = Mock()
mock_enums.TA_CENTER = "center"
mock_enums.TA_JUSTIFY = "justify"
mock_enums.TA_LEFT = "left"
mock_enums.TA_RIGHT = "right"

mock_pagesizes = Mock()
mock_pagesizes.A4 = (595, 842)
mock_pagesizes.letter = (612, 792)

# Create a mock stylesheet that behaves like dict but has add method
class MockStyleSheet:
    def __init__(self):
        self._styles = {}

    def __getitem__(self, key):
        if key not in self._styles:
            self._styles[key] = Mock()
        return self._styles[key]

    def __setitem__(self, key, value):
        self._styles[key] = value

    def add(self, style, **kwargs):
        """Add a style to the stylesheet"""
        if hasattr(style, 'name'):
            self._styles[style.name] = style

mock_stylesheet_class = MockStyleSheet
mock_stylesheet = mock_stylesheet_class()

# Create a ParagraphStyle mock that captures the name parameter
def mock_paragraph_style(**kwargs):
    style_mock = Mock()
    if 'name' in kwargs:
        style_mock.name = kwargs['name']
    return style_mock

mock_styles = Mock()
mock_styles.ParagraphStyle = mock_paragraph_style
mock_styles.getSampleStyleSheet = Mock(return_value=mock_stylesheet)

mock_units = Mock()
mock_units.cm = 28.35
mock_units.mm = 2.835

mock_canvas = Mock()
mock_platypus = Mock()
mock_platypus.Image = Mock
mock_platypus.KeepTogether = Mock
mock_platypus.PageBreak = Mock
mock_platypus.Paragraph = Mock
# SimpleDocTemplate needs to be a Mock that returns a mock with build method
_simple_doc_mock = Mock()
_simple_doc_mock.return_value = MagicMock()
mock_platypus.SimpleDocTemplate = _simple_doc_mock
mock_platypus.Spacer = Mock
# Table needs to return a mock with setStyle method
mock_platypus.Table = lambda *args, **kwargs: MagicMock()
mock_platypus.TableStyle = Mock

sys.modules["reportlab"] = Mock()
sys.modules["reportlab.lib"] = Mock()
sys.modules["reportlab.lib.colors"] = mock_colors
sys.modules["reportlab.lib.enums"] = mock_enums
sys.modules["reportlab.lib.pagesizes"] = mock_pagesizes
sys.modules["reportlab.lib.styles"] = mock_styles
sys.modules["reportlab.lib.units"] = mock_units
sys.modules["reportlab.pdfgen"] = Mock()
sys.modules["reportlab.pdfgen.canvas"] = mock_canvas
sys.modules["reportlab.platypus"] = mock_platypus

# Mock weasyprint
mock_weasyprint = Mock()
mock_weasyprint.HTML = Mock
mock_weasyprint.CSS = Mock
sys.modules["weasyprint"] = mock_weasyprint

from src.core.pdf_exporter import (
    BrandingConfig,
    PDFExporter,
    export_html_to_pdf,
    PDFReportExporter,
)


class TestBrandingConfig:
    """Test BrandingConfig class"""

    def test_branding_config_defaults(self):
        """Test default branding configuration"""
        config = BrandingConfig()
        assert config.company_name == "Document Management System"
        assert config.company_tagline == "Professional Service Management"
        assert config.logo_path is None
        assert config.header_font == "Helvetica-Bold"
        assert config.body_font == "Helvetica"
        assert config.font_size_title == 18
        assert config.font_size_heading == 14
        assert config.font_size_body == 10
        assert config.show_page_numbers is True
        assert config.show_watermark is False
        assert config.watermark_text == "CONFIDENTIAL"

    def test_branding_config_custom_values(self):
        """Test custom branding values"""
        config = BrandingConfig()
        config.company_name = "Custom Company"
        config.font_size_title = 20
        config.show_watermark = True
        assert config.company_name == "Custom Company"
        assert config.font_size_title == 20
        assert config.show_watermark is True


class TestPDFExporter:
    """Test PDFExporter class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mock to use proper stylesheet with add method
        mock_styles.getSampleStyleSheet.return_value = MockStyleSheet()
        self.exporter = PDFExporter()

    def test_exporter_initialization_default_branding(self):
        """Test exporter initialization with default branding"""
        exporter = PDFExporter()
        assert isinstance(exporter.branding, BrandingConfig)
        assert exporter.styles is not None

    def test_exporter_initialization_custom_branding(self):
        """Test exporter initialization with custom branding"""
        custom_branding = BrandingConfig()
        custom_branding.company_name = "Custom Corp"
        exporter = PDFExporter(branding=custom_branding)
        assert exporter.branding.company_name == "Custom Corp"

    def test_setup_custom_styles_called(self):
        """Test custom styles setup is called"""
        # Create exporter and verify styles were set up
        exporter = PDFExporter()
        # Styles should be set up and have custom styles
        assert exporter.styles is not None
        # Verify custom styles exist (CustomTitle, CustomHeading are created by PDFExporter)
        assert "CustomTitle" in exporter.styles._styles or "CustomHeading" in exporter.styles._styles

    def test_create_header_footer_without_logo(self):
        """Test header/footer creation without logo"""
        mock_canvas_obj = Mock()
        mock_doc = Mock()
        mock_doc.leftMargin = 50
        mock_doc.rightMargin = 50
        mock_doc.topMargin = 50
        mock_doc.bottomMargin = 50
        mock_doc.width = 500
        mock_doc.height = 700
        mock_doc.page = 1

        self.exporter._create_header_footer(mock_canvas_obj, mock_doc)

        # Check canvas methods were called
        mock_canvas_obj.saveState.assert_called()
        mock_canvas_obj.setFont.assert_called()
        mock_canvas_obj.restoreState.assert_called()

    def test_create_header_footer_with_page_numbers(self):
        """Test header/footer with page numbers"""
        mock_canvas_obj = Mock()
        mock_doc = Mock()
        mock_doc.leftMargin = 50
        mock_doc.topMargin = 50
        mock_doc.width = 500
        mock_doc.height = 700
        mock_doc.page = 5

        self.exporter.branding.show_page_numbers = True

        self.exporter._create_header_footer(mock_canvas_obj, mock_doc)

        # Check page number was drawn
        assert mock_canvas_obj.drawRightString.call_count >= 1

    def test_create_header_footer_with_watermark(self):
        """Test header/footer with watermark"""
        mock_canvas_obj = Mock()
        mock_doc = Mock()
        mock_doc.leftMargin = 50
        mock_doc.topMargin = 50
        mock_doc.width = 500
        mock_doc.height = 700
        mock_doc.page = 1

        self.exporter.branding.show_watermark = True
        self.exporter.branding.watermark_text = "CONFIDENTIAL"

        self.exporter._create_header_footer(mock_canvas_obj, mock_doc)

        # Check watermark methods were called
        assert mock_canvas_obj.saveState.call_count >= 2  # Initial and for watermark
        mock_canvas_obj.rotate.assert_called()

    def test_export_service_to_pdf(self):
        """Test exporting service to PDF"""
        # Create mock service
        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "Test Service"
        mock_service.basic_info.region = "North"
        mock_service.basic_info.target_group = "Adults"
        mock_service.basic_info.service_type = "Consultation"
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 45.50
        mock_service.financial.netto_rate = 38.25
        mock_service.financial.base_salary = 3500.00

        # Mock SimpleDocTemplate
        mock_doc = Mock()
        mock_doc.build = Mock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        output_path = "/tmp/test_service.pdf"
        result = self.exporter.export_service_to_pdf(mock_service, output_path)

        assert result == output_path
        mock_platypus.SimpleDocTemplate.assert_called_once()
        mock_doc.build.assert_called_once()

    def test_export_service_to_pdf_without_cost_breakdown(self):
        """Test exporting service without cost breakdown"""
        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "Test Service"
        mock_service.basic_info.region = "North"
        mock_service.basic_info.target_group = "Adults"
        mock_service.basic_info.service_type = "Consultation"
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 45.50
        mock_service.financial.netto_rate = 38.25
        mock_service.financial.base_salary = 3500.00

        mock_doc = Mock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        result = self.exporter.export_service_to_pdf(
            mock_service,
            "/tmp/test.pdf",
            include_cost_breakdown=False,
        )

        assert result == "/tmp/test.pdf"

    def test_export_service_list_to_pdf(self):
        """Test exporting service list to PDF"""
        # Create mock services
        mock_service1 = Mock()
        mock_service1.basic_info = Mock()
        mock_service1.basic_info.service_name = "Service 1"
        mock_service1.basic_info.region = "North"
        mock_service1.basic_info.target_group = "Adults"
        mock_service1.financial = Mock()
        mock_service1.financial.brutto_rate = 45.50

        mock_service2 = Mock()
        mock_service2.basic_info = Mock()
        mock_service2.basic_info.service_name = "Service 2"
        mock_service2.basic_info.region = "South"
        mock_service2.basic_info.target_group = "Children"
        mock_service2.financial = Mock()
        mock_service2.financial.brutto_rate = 52.00

        services = [mock_service1, mock_service2]

        mock_doc = MagicMock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        output_path = "/tmp/services_list.pdf"
        result = self.exporter.export_service_list_to_pdf(services, output_path)

        assert result == output_path
        # Verify SimpleDocTemplate was called with the output path
        assert any(output_path in str(call) for call in mock_platypus.SimpleDocTemplate.call_args_list)
        mock_doc.build.assert_called_once()

    def test_export_service_list_custom_title(self):
        """Test exporting service list with custom title"""
        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "Test Service"
        mock_service.basic_info.region = "North"
        mock_service.basic_info.target_group = "Adults"
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 45.50

        mock_doc = Mock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        result = self.exporter.export_service_list_to_pdf(
            [mock_service],
            "/tmp/test.pdf",
            title="Custom Report Title",
        )

        assert result == "/tmp/test.pdf"

    def test_export_empty_service_list(self):
        """Test exporting empty service list"""
        mock_doc = MagicMock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        result = self.exporter.export_service_list_to_pdf([], "/tmp/empty.pdf")

        assert result == "/tmp/empty.pdf"
        mock_doc.build.assert_called_once()

    def test_export_service_long_names_truncated(self):
        """Test service names are truncated in list"""
        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "A" * 100  # Very long name
        mock_service.basic_info.region = "North"
        mock_service.basic_info.target_group = "B" * 50  # Very long target group
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 45.50

        mock_doc = Mock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        result = self.exporter.export_service_list_to_pdf([mock_service], "/tmp/test.pdf")

        assert result == "/tmp/test.pdf"


class TestExportHTMLToPDF:
    """Test export_html_to_pdf function"""

    @patch("src.core.pdf_exporter.WEASYPRINT_AVAILABLE", False)
    def test_export_html_weasyprint_not_available(self):
        """Test HTML export when weasyprint not available"""
        try:
            export_html_to_pdf("<html><body>Test</body></html>", "/tmp/test.pdf")
            assert False, "Should raise RuntimeError"
        except RuntimeError as e:
            assert "WeasyPrint is not installed" in str(e)

    @patch("src.core.pdf_exporter.WEASYPRINT_AVAILABLE", True)
    @patch("weasyprint.HTML")
    @patch("weasyprint.CSS")
    def test_export_html_to_pdf_default_css(self, mock_css_class, mock_html_class):
        """Test HTML to PDF export with default CSS"""
        mock_html = Mock()
        mock_html.write_pdf = Mock()
        mock_html_class.return_value = mock_html

        # Ensure HTML is accessible from pdf_exporter module
        import src.core.pdf_exporter
        src.core.pdf_exporter.HTML = mock_html_class
        src.core.pdf_exporter.CSS = mock_css_class

        html_content = "<html><body><h1>Test</h1></body></html>"
        output_path = "/tmp/test.pdf"

        result = export_html_to_pdf(html_content, output_path)

        assert result == output_path
        mock_html_class.assert_called_once_with(string=html_content)
        mock_html.write_pdf.assert_called_once()

    @patch("src.core.pdf_exporter.WEASYPRINT_AVAILABLE", True)
    @patch("weasyprint.HTML")
    @patch("weasyprint.CSS")
    def test_export_html_to_pdf_custom_css(self, mock_css_class, mock_html_class):
        """Test HTML to PDF export with custom CSS"""
        mock_html = Mock()
        mock_html.write_pdf = Mock()
        mock_html_class.return_value = mock_html

        # Ensure HTML and CSS are accessible from pdf_exporter module
        import src.core.pdf_exporter
        src.core.pdf_exporter.HTML = mock_html_class
        src.core.pdf_exporter.CSS = mock_css_class

        html_content = "<html><body>Test</body></html>"
        custom_css = "body { font-size: 14pt; }"
        output_path = "/tmp/test.pdf"

        result = export_html_to_pdf(html_content, output_path, css=custom_css)

        assert result == output_path
        mock_html.write_pdf.assert_called_once()


class TestBackwardCompatibility:
    """Test backward compatibility"""

    def test_pdf_report_exporter_alias(self):
        """Test PDFReportExporter is alias for PDFExporter"""
        assert PDFReportExporter is PDFExporter


class TestIntegration:
    """Integration tests"""

    def test_full_pdf_generation_workflow(self):
        """Test complete PDF generation workflow"""
        # Create custom branding
        branding = BrandingConfig()
        branding.company_name = "Test Corp"
        branding.show_watermark = True

        # Create exporter
        exporter = PDFExporter(branding=branding)

        # Create mock service
        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "Integration Test Service"
        mock_service.basic_info.region = "West"
        mock_service.basic_info.target_group = "All"
        mock_service.basic_info.service_type = "Support"
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 60.00
        mock_service.financial.netto_rate = 50.00
        mock_service.financial.base_salary = 4000.00

        # Mock document
        mock_doc = Mock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        # Export service
        result = exporter.export_service_to_pdf(mock_service, "/tmp/integration_test.pdf")

        assert result == "/tmp/integration_test.pdf"
        assert exporter.branding.company_name == "Test Corp"

    def test_multiple_exports_same_exporter(self):
        """Test multiple exports with same exporter instance"""
        exporter = PDFExporter()

        mock_service = Mock()
        mock_service.basic_info = Mock()
        mock_service.basic_info.service_name = "Service"
        mock_service.basic_info.region = "North"
        mock_service.basic_info.target_group = "Adults"
        mock_service.basic_info.service_type = "Consultation"
        mock_service.financial = Mock()
        mock_service.financial.brutto_rate = 45.00
        mock_service.financial.netto_rate = 38.00
        mock_service.financial.base_salary = 3500.00

        mock_doc = MagicMock()
        mock_platypus.SimpleDocTemplate.return_value = mock_doc

        # First export
        result1 = exporter.export_service_to_pdf(mock_service, "/tmp/test1.pdf")
        assert result1 == "/tmp/test1.pdf"

        # Second export
        result2 = exporter.export_service_list_to_pdf([mock_service], "/tmp/test2.pdf")
        assert result2 == "/tmp/test2.pdf"

        # Both should succeed
        assert mock_doc.build.call_count == 2
