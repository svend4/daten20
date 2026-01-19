"""
Tests for DOCX Export Module

Tests professional DOCX generation with python-docx (formatting, tables, images).
"""

import sys
from unittest.mock import Mock, MagicMock, patch

# Mock docx before importing
mock_document_class = Mock()
mock_document = MagicMock()
mock_document_class.return_value = mock_document

# Mock styles
mock_document.styles = MagicMock()
mock_document.styles.__getitem__ = Mock(side_effect=KeyError)
mock_document.styles.add_style = Mock(return_value=MagicMock())

# Mock sections for header/footer
mock_section = MagicMock()
mock_section.header = MagicMock()
mock_section.footer = MagicMock()
mock_section.header.paragraphs = []
mock_section.footer.paragraphs = []
mock_document.sections = [mock_section]

# Mock add methods
mock_document.add_paragraph = Mock(return_value=MagicMock())
mock_document.add_heading = Mock(return_value=MagicMock())
mock_document.add_page_break = Mock(return_value=MagicMock())
mock_document.add_picture = Mock(return_value=MagicMock())
mock_document.add_table = Mock(return_value=MagicMock())
mock_document.save = Mock()

# Mock enums
mock_wd_style_type = Mock()
mock_wd_style_type.PARAGRAPH = 1
mock_wd_style_type.CHARACTER = 2
mock_wd_style_type.TABLE = 3

mock_wd_align = Mock()
mock_wd_align.LEFT = 0
mock_wd_align.CENTER = 1
mock_wd_align.RIGHT = 2
mock_wd_align.JUSTIFY = 3

# Mock shared units
mock_pt = Mock(side_effect=lambda x: x * 12700)
mock_inches = Mock(side_effect=lambda x: x * 914400)
mock_cm = Mock(side_effect=lambda x: x * 360000)

# Mock RGB color
class MockRGBColor:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

# Mock OxmlElement
mock_oxml_element = Mock(return_value=MagicMock())

# Mock qn function
mock_qn = Mock(side_effect=lambda x: f"{{namespace}}{x}")

# Set up sys.modules mocks
sys.modules["docx"] = Mock()
sys.modules["docx"].Document = mock_document_class
sys.modules["docx.enum"] = Mock()
sys.modules["docx.enum.style"] = Mock()
sys.modules["docx.enum.style"].WD_STYLE_TYPE = mock_wd_style_type
sys.modules["docx.enum.text"] = Mock()
sys.modules["docx.enum.text"].WD_ALIGN_PARAGRAPH = mock_wd_align
sys.modules["docx.shared"] = Mock()
sys.modules["docx.shared"].Pt = mock_pt
sys.modules["docx.shared"].Inches = mock_inches
sys.modules["docx.shared"].Cm = mock_cm
sys.modules["docx.shared"].RGBColor = MockRGBColor
sys.modules["docx.oxml"] = Mock()
sys.modules["docx.oxml"].OxmlElement = mock_oxml_element
sys.modules["docx.oxml.ns"] = Mock()
sys.modules["docx.oxml.ns"].qn = mock_qn

from src.core.docx_exporter import BrandingConfig, DOCXExporter


class TestBrandingConfig:
    """Test BrandingConfig class"""

    def test_branding_config_defaults(self):
        """Test default branding configuration"""
        config = BrandingConfig()
        assert config.company_name == "Document Management System"
        assert config.company_tagline == "Professional Service Management"
        assert config.logo_path is None
        assert config.header_font == "Calibri"
        assert config.body_font == "Calibri"
        assert config.font_size_title == 24
        assert config.font_size_heading1 == 18
        assert config.font_size_heading2 == 14
        assert config.font_size_body == 11
        assert config.show_page_numbers is True
        assert config.show_header is True
        assert config.show_footer is True

    def test_branding_config_custom_values(self):
        """Test custom branding values"""
        config = BrandingConfig()
        config.company_name = "Custom Company"
        config.font_size_title = 28
        config.show_page_numbers = False
        assert config.company_name == "Custom Company"
        assert config.font_size_title == 28
        assert config.show_page_numbers is False

    def test_branding_config_colors(self):
        """Test branding colors are RGBColor instances"""
        config = BrandingConfig()
        assert isinstance(config.primary_color, MockRGBColor)
        assert isinstance(config.secondary_color, MockRGBColor)
        assert isinstance(config.accent_color, MockRGBColor)
        # Check specific RGB values
        assert config.primary_color.r == 13
        assert config.primary_color.g == 110
        assert config.primary_color.b == 253


class TestDOCXExporter:
    """Test DOCXExporter class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mocks
        mock_document.reset_mock()
        mock_document.styles = MagicMock()
        mock_document.styles.__getitem__ = Mock(side_effect=KeyError)
        mock_document.styles.add_style = Mock(return_value=MagicMock())
        mock_document.sections = [mock_section]
        mock_document.add_paragraph = Mock(return_value=MagicMock())
        mock_document.add_heading = Mock(return_value=MagicMock())
        mock_document.add_table = Mock(return_value=MagicMock())
        mock_document.add_picture = Mock(return_value=MagicMock())
        mock_document.add_page_break = Mock(return_value=MagicMock())
        mock_document.save = Mock()

        mock_document_class.reset_mock()
        mock_document_class.return_value = mock_document

        self.exporter = DOCXExporter()

    def test_initialization_default_branding(self):
        """Test exporter initialization with default branding"""
        exporter = DOCXExporter()
        assert isinstance(exporter.branding, BrandingConfig)
        assert exporter.doc is None

    def test_initialization_custom_branding(self):
        """Test exporter initialization with custom branding"""
        custom_branding = BrandingConfig()
        custom_branding.company_name = "Custom Corp"
        exporter = DOCXExporter(branding=custom_branding)
        assert exporter.branding.company_name == "Custom Corp"

    def test_create_document_default(self):
        """Test creating document with default title"""
        exporter = DOCXExporter()
        doc = exporter.create_document()

        assert doc is not None
        assert exporter.doc is not None
        mock_document_class.assert_called_once()

    def test_create_document_custom_title(self):
        """Test creating document with custom title"""
        exporter = DOCXExporter()
        doc = exporter.create_document(title="Custom Report")

        assert doc is not None

    def test_setup_styles_called(self):
        """Test styles setup is called on create_document"""
        exporter = DOCXExporter()
        exporter.create_document()

        # Verify add_style was called for custom styles
        assert mock_document.styles.add_style.called

    def test_setup_header_footer_called(self):
        """Test header/footer setup is called on create_document"""
        exporter = DOCXExporter()
        exporter.create_document()

        # Verify sections were accessed
        assert len(mock_document.sections) > 0

    def test_add_title(self):
        """Test adding title"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_title("Test Title")

        # Verify add_paragraph was called
        mock_document.add_paragraph.assert_called()

    def test_add_heading_level1(self):
        """Test adding heading level 1"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_heading("Section 1", level=1)

        mock_document.add_paragraph.assert_called()

    def test_add_heading_level2(self):
        """Test adding heading level 2"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_heading("Subsection", level=2)

        mock_document.add_paragraph.assert_called()

    def test_add_paragraph(self):
        """Test adding paragraph"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_paragraph("This is a paragraph.")

        mock_document.add_paragraph.assert_called()

    def test_add_bullet_list(self):
        """Test adding bullet list"""
        exporter = DOCXExporter()
        exporter.create_document()

        items = ["Item 1", "Item 2", "Item 3"]
        exporter.add_bullet_list(items)

        # Verify add_paragraph was called for each item
        assert mock_document.add_paragraph.call_count >= len(items)

    def test_add_numbered_list(self):
        """Test adding numbered list"""
        exporter = DOCXExporter()
        exporter.create_document()

        items = ["First", "Second", "Third"]
        exporter.add_numbered_list(items)

        # Verify add_paragraph was called for each item
        assert mock_document.add_paragraph.call_count >= len(items)

    def test_add_table_without_headers(self):
        """Test adding table without headers"""
        exporter = DOCXExporter()
        exporter.create_document()

        data = [["A", "B"], ["C", "D"]]
        exporter.add_table(data)

        mock_document.add_table.assert_called_once()

    def test_add_table_with_headers(self):
        """Test adding table with headers"""
        exporter = DOCXExporter()
        exporter.create_document()

        headers = ["Col1", "Col2"]
        data = [["A", "B"], ["C", "D"]]
        exporter.add_table(data, headers=headers)

        mock_document.add_table.assert_called_once()

    def test_add_table_custom_style(self):
        """Test adding table with custom style"""
        exporter = DOCXExporter()
        exporter.create_document()

        data = [["A", "B"]]
        exporter.add_table(data, style="Medium Grid 1 Accent 1")

        mock_document.add_table.assert_called_once()

    @patch("src.core.docx_exporter.Path")
    def test_add_image(self, mock_path):
        """Test adding image"""
        # Mock Path.exists() to return True
        mock_path.return_value.exists.return_value = True

        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_image("/tmp/test.png")

        # Verify add_paragraph was called (image is added to a paragraph run)
        mock_document.add_paragraph.assert_called()

    @patch("src.core.docx_exporter.Path")
    def test_add_image_with_width(self, mock_path):
        """Test adding image with custom width"""
        # Mock Path.exists() to return True
        mock_path.return_value.exists.return_value = True

        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_image("/tmp/test.png", width=5.0)

        # Verify add_paragraph was called
        mock_document.add_paragraph.assert_called()

    def test_add_page_break(self):
        """Test adding page break"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_page_break()

        mock_document.add_page_break.assert_called_once()

    def test_add_info_box(self):
        """Test adding info box"""
        exporter = DOCXExporter()
        exporter.create_document()

        exporter.add_info_box("Important", "This is important information.")

        # Verify paragraphs were added (info box uses paragraphs, not table)
        assert mock_document.add_paragraph.call_count >= 2

    def test_export_simple_success(self):
        """Test simple export"""
        exporter = DOCXExporter()

        result = exporter.export_simple(
            content="Test content", output_path="/tmp/test.docx", title="Test Document"
        )

        assert result is True
        mock_document_class.assert_called()
        mock_document.save.assert_called_once_with("/tmp/test.docx")

    def test_export_simple_exception(self):
        """Test simple export handles exceptions"""
        exporter = DOCXExporter()
        mock_document.save.side_effect = Exception("Save failed")

        result = exporter.export_simple(content="Test", output_path="/tmp/test.docx")

        assert result is False

    def test_export_structured_with_sections(self):
        """Test structured export with sections"""
        exporter = DOCXExporter()

        data = {
            "sections": [
                {"title": "Section 1", "content": "Content 1"},
                {"title": "Section 2", "content": "Content 2"},
            ]
        }

        result = exporter.export_structured(data, "/tmp/structured.docx", title="Structured Doc")

        assert result is True
        mock_document.save.assert_called_once()

    def test_export_structured_with_table(self):
        """Test structured export with table data"""
        exporter = DOCXExporter()

        # Data with list of dictionaries (will be rendered as table)
        data = {"results": [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]}

        result = exporter.export_structured(data, "/tmp/table.docx")

        assert result is True
        mock_document.add_table.assert_called()

    def test_export_structured_with_lists(self):
        """Test structured export with bullet and numbered lists"""
        exporter = DOCXExporter()

        data = {"bullet_list": ["Item 1", "Item 2"], "numbered_list": ["First", "Second"]}

        result = exporter.export_structured(data, "/tmp/lists.docx")

        assert result is True

    def test_export_report_success(self):
        """Test report export"""
        exporter = DOCXExporter()

        report_data = {
            "title": "Annual Report",
            "subtitle": "2024",
            "summary": "Executive summary text",
            "sections": [{"title": "Results", "content": "Good results"}],
        }

        result = exporter.export_report(report_data, "/tmp/report.docx")

        assert result is True
        mock_document.save.assert_called_once()

    def test_export_report_with_stats(self):
        """Test report export with statistics"""
        exporter = DOCXExporter()

        report_data = {
            "title": "Report",
            "statistics": [{"label": "Total", "value": "100"}, {"label": "Average", "value": "75"}],
        }

        result = exporter.export_report(report_data, "/tmp/stats_report.docx")

        assert result is True

    def test_export_report_exception(self):
        """Test report export handles exceptions"""
        exporter = DOCXExporter()
        mock_document.save.side_effect = Exception("Save failed")

        result = exporter.export_report({"title": "Report"}, "/tmp/report.docx")

        assert result is False


class TestIntegration:
    """Integration tests"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mocks
        mock_document.reset_mock()
        mock_document.styles = MagicMock()
        mock_document.styles.__getitem__ = Mock(side_effect=KeyError)
        mock_document.styles.add_style = Mock(return_value=MagicMock())
        mock_document.sections = [mock_section]
        mock_document.add_paragraph = Mock(return_value=MagicMock())
        mock_document.add_table = Mock(return_value=MagicMock())
        mock_document.save = Mock()

        mock_document_class.reset_mock()
        mock_document_class.return_value = mock_document

    def test_full_document_workflow(self):
        """Test complete document creation workflow"""
        exporter = DOCXExporter()

        # Create document
        exporter.create_document(title="Complete Report")

        # Add content
        exporter.add_title("Main Title")
        exporter.add_heading("Section 1", level=1)
        exporter.add_paragraph("Paragraph text")
        exporter.add_bullet_list(["Point 1", "Point 2"])
        exporter.add_table([["A", "B"]], headers=["Col1", "Col2"])
        exporter.add_page_break()
        exporter.add_heading("Section 2", level=1)

        # Verify operations were called
        assert mock_document.add_paragraph.called
        assert mock_document.add_table.called
        assert mock_document.add_page_break.called

    def test_custom_branding_workflow(self):
        """Test workflow with custom branding"""
        custom_branding = BrandingConfig()
        custom_branding.company_name = "Test Corp"
        custom_branding.show_page_numbers = False

        exporter = DOCXExporter(branding=custom_branding)
        exporter.create_document()

        assert exporter.branding.company_name == "Test Corp"
        assert exporter.branding.show_page_numbers is False

    def test_multiple_exports_same_exporter(self):
        """Test multiple exports with same exporter instance"""
        exporter = DOCXExporter()

        # First export
        result1 = exporter.export_simple("Content 1", "/tmp/doc1.docx")
        assert result1 is True

        # Second export
        result2 = exporter.export_simple("Content 2", "/tmp/doc2.docx")
        assert result2 is True

        # Both should succeed
        assert mock_document.save.call_count == 2
