"""
Tests for PowerPoint Export Module

Tests professional PowerPoint generation with python-pptx (slides, charts, tables, images).
"""

import sys
from unittest.mock import Mock, MagicMock, patch

# Mock python-pptx before importing
mock_presentation_class = Mock()
mock_presentation = MagicMock()
mock_presentation_class.return_value = mock_presentation

# Mock presentation attributes
mock_presentation.slide_width = 914400 * 10  # Inches(10)
mock_presentation.slide_height = 914400 * 5.625  # Inches(5.625)
mock_presentation.slides = MagicMock()
mock_presentation.slide_layouts = [MagicMock() for _ in range(10)]
mock_presentation.save = Mock()

# Mock slide and shapes
mock_slide = MagicMock()
mock_slide.shapes = MagicMock()
mock_slide.shapes.title = MagicMock()
mock_slide.shapes.add_textbox = Mock(return_value=MagicMock())
mock_slide.shapes.add_table = Mock(return_value=MagicMock())
mock_slide.shapes.add_chart = Mock(return_value=MagicMock())
mock_slide.shapes.add_picture = Mock(return_value=MagicMock())
mock_slide.placeholders = {0: MagicMock(), 1: MagicMock(), 2: MagicMock()}
mock_slide.notes_slide = MagicMock()
mock_slide.notes_slide.notes_text_frame = MagicMock()

mock_presentation.slides.add_slide = Mock(return_value=mock_slide)

# Mock chart enums
mock_xl_chart_type = Mock()
mock_xl_chart_type.BAR_CLUSTERED = 57
mock_xl_chart_type.COLUMN_CLUSTERED = 51
mock_xl_chart_type.LINE = 4
mock_xl_chart_type.PIE = 5

mock_xl_legend_position = Mock()
mock_xl_legend_position.BOTTOM = 3
mock_xl_legend_position.TOP = 2
mock_xl_legend_position.LEFT = 4
mock_xl_legend_position.RIGHT = 1

# Mock shape enums
mock_mso_shape = Mock()
mock_mso_shape.RECTANGLE = 1
mock_mso_shape.ROUNDED_RECTANGLE = 5

# Mock text enums
mock_mso_anchor = Mock()
mock_mso_anchor.TOP = 1
mock_mso_anchor.MIDDLE = 3
mock_mso_anchor.BOTTOM = 4

mock_pp_align = Mock()
mock_pp_align.LEFT = 1
mock_pp_align.CENTER = 2
mock_pp_align.RIGHT = 3
mock_pp_align.JUSTIFY = 4

# Mock utility functions
mock_inches = Mock(side_effect=lambda x: int(x * 914400))
mock_pt = Mock(side_effect=lambda x: int(x * 12700))

# Mock RGBColor
class MockRGBColor:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

# Mock CategoryChartData
class MockCategoryChartData:
    def __init__(self):
        self.categories = []
        self._series = []

    def add_series(self, name, values):
        self._series.append({"name": name, "values": values})

# Set up sys.modules mocks
sys.modules["pptx"] = Mock()
sys.modules["pptx"].Presentation = mock_presentation_class
sys.modules["pptx.chart"] = Mock()
sys.modules["pptx.chart.data"] = Mock()
sys.modules["pptx.chart.data"].CategoryChartData = MockCategoryChartData
sys.modules["pptx.dml"] = Mock()
sys.modules["pptx.dml.color"] = Mock()
sys.modules["pptx.dml.color"].RGBColor = MockRGBColor
sys.modules["pptx.enum"] = Mock()
sys.modules["pptx.enum.chart"] = Mock()
sys.modules["pptx.enum.chart"].XL_CHART_TYPE = mock_xl_chart_type
sys.modules["pptx.enum.chart"].XL_LEGEND_POSITION = mock_xl_legend_position
sys.modules["pptx.enum.shapes"] = Mock()
sys.modules["pptx.enum.shapes"].MSO_SHAPE = mock_mso_shape
sys.modules["pptx.enum.text"] = Mock()
sys.modules["pptx.enum.text"].MSO_ANCHOR = mock_mso_anchor
sys.modules["pptx.enum.text"].PP_ALIGN = mock_pp_align
sys.modules["pptx.util"] = Mock()
sys.modules["pptx.util"].Inches = mock_inches
sys.modules["pptx.util"].Pt = mock_pt

from src.core.powerpoint_export import PPTTheme, PowerPointExporter, create_presentation


class TestPPTTheme:
    """Test PPTTheme class"""

    def test_theme_defaults(self):
        """Test default theme configuration"""
        theme = PPTTheme()
        assert theme.company_name == "Document Management System"
        assert theme.company_tagline == "Professional Service Management"
        assert theme.logo_path is None
        assert theme.font_title == "Calibri"
        assert theme.font_body == "Calibri"

    def test_theme_colors(self):
        """Test theme colors are RGBColor instances"""
        theme = PPTTheme()
        assert isinstance(theme.color_primary, MockRGBColor)
        assert isinstance(theme.color_secondary, MockRGBColor)
        assert isinstance(theme.color_accent, MockRGBColor)
        assert isinstance(theme.color_warning, MockRGBColor)
        assert isinstance(theme.color_danger, MockRGBColor)
        assert isinstance(theme.color_text, MockRGBColor)
        assert isinstance(theme.color_bg, MockRGBColor)

    def test_theme_primary_color_values(self):
        """Test primary color RGB values"""
        theme = PPTTheme()
        assert theme.color_primary.r == 13
        assert theme.color_primary.g == 110
        assert theme.color_primary.b == 253

    def test_theme_font_sizes(self):
        """Test font sizes use Pt"""
        theme = PPTTheme()
        # Pt is mocked to return value * 12700
        assert theme.font_size_title == 44 * 12700
        assert theme.font_size_heading == 32 * 12700
        assert theme.font_size_body == 18 * 12700
        assert theme.font_size_small == 14 * 12700

    def test_theme_custom_values(self):
        """Test custom theme values"""
        theme = PPTTheme()
        theme.company_name = "Custom Corp"
        theme.font_title = "Arial"
        theme.logo_path = "/path/to/logo.png"
        assert theme.company_name == "Custom Corp"
        assert theme.font_title == "Arial"
        assert theme.logo_path == "/path/to/logo.png"


class TestPowerPointExporter:
    """Test PowerPointExporter class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mocks
        mock_presentation.reset_mock()
        mock_presentation.slide_width = 914400 * 10
        mock_presentation.slide_height = 914400 * 5.625
        mock_presentation.slides = MagicMock()
        mock_presentation.slide_layouts = [MagicMock() for _ in range(10)]
        mock_presentation.save = Mock()

        mock_slide.reset_mock()
        mock_slide.shapes = MagicMock()
        mock_slide.shapes.title = MagicMock()
        mock_slide.shapes.add_textbox = Mock(return_value=MagicMock())
        mock_slide.shapes.add_table = Mock(return_value=MagicMock())
        mock_slide.shapes.add_chart = Mock(return_value=MagicMock())
        mock_slide.shapes.add_picture = Mock(return_value=MagicMock())
        mock_slide.placeholders = {0: MagicMock(), 1: MagicMock(), 2: MagicMock()}
        mock_slide.notes_slide = MagicMock()
        mock_slide.notes_slide.notes_text_frame = MagicMock()

        mock_presentation.slides.add_slide = Mock(return_value=mock_slide)
        mock_presentation_class.reset_mock()
        mock_presentation_class.return_value = mock_presentation

    def test_initialization_default_theme(self):
        """Test exporter initialization with default theme"""
        exporter = PowerPointExporter()
        assert isinstance(exporter.theme, PPTTheme)
        assert exporter.presentation is not None
        mock_presentation_class.assert_called_once()

    def test_initialization_custom_theme(self):
        """Test exporter initialization with custom theme"""
        custom_theme = PPTTheme()
        custom_theme.company_name = "Custom Corp"
        exporter = PowerPointExporter(theme=custom_theme)
        assert exporter.theme.company_name == "Custom Corp"

    def test_initialization_sets_slide_size(self):
        """Test initialization sets 16:9 slide dimensions"""
        exporter = PowerPointExporter()
        # Verify slide dimensions were set (Inches(10) x Inches(5.625))
        assert exporter.presentation.slide_width == 914400 * 10
        assert exporter.presentation.slide_height == 914400 * 5.625

    def test_add_title_slide_basic(self):
        """Test adding title slide without subtitle"""
        exporter = PowerPointExporter()
        slide = exporter.add_title_slide("Test Presentation")

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_title_slide_with_subtitle(self):
        """Test adding title slide with subtitle"""
        exporter = PowerPointExporter()
        slide = exporter.add_title_slide("Test Presentation", "Subtitle Text")

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_content_slide_string_content(self):
        """Test adding content slide with string content"""
        exporter = PowerPointExporter()
        slide = exporter.add_content_slide("Content Title", "Single paragraph text")

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_content_slide_list_content(self):
        """Test adding content slide with list content"""
        exporter = PowerPointExporter()
        content = ["Point 1", "Point 2", "Point 3"]
        slide = exporter.add_content_slide("Content Title", content)

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_content_slide_bullet_points(self):
        """Test adding content slide with bullet points enabled"""
        exporter = PowerPointExporter()
        content = ["Bullet 1", "Bullet 2"]
        slide = exporter.add_content_slide("Title", content, bullet_points=True)

        assert slide is not None

    def test_add_content_slide_no_bullets(self):
        """Test adding content slide with bullet points disabled"""
        exporter = PowerPointExporter()
        content = ["Line 1", "Line 2"]
        slide = exporter.add_content_slide("Title", content, bullet_points=False)

        assert slide is not None

    def test_add_comparison_slide(self):
        """Test adding comparison slide"""
        exporter = PowerPointExporter()
        left_content = ["Old feature 1", "Old feature 2"]
        right_content = ["New feature 1", "New feature 2"]
        slide = exporter.add_comparison_slide(
            "Comparison", left_content, right_content, "Before", "After"
        )

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_comparison_slide_custom_titles(self):
        """Test comparison slide with custom column titles"""
        exporter = PowerPointExporter()
        left = ["Option A details"]
        right = ["Option B details"]
        slide = exporter.add_comparison_slide(
            "Options", left, right, "Option A", "Option B"
        )

        assert slide is not None

    def test_add_table_slide_without_headers(self):
        """Test adding table slide without headers"""
        exporter = PowerPointExporter()
        data = [["A", "B"], ["C", "D"]]
        slide = exporter.add_table_slide("Table", data)

        assert slide is not None
        mock_slide.shapes.add_table.assert_called()

    def test_add_table_slide_with_headers(self):
        """Test adding table slide with headers"""
        exporter = PowerPointExporter()
        headers = ["Column 1", "Column 2"]
        data = [["A", "B"], ["C", "D"]]
        slide = exporter.add_table_slide("Table", data, headers=headers)

        assert slide is not None
        mock_slide.shapes.add_table.assert_called()

    def test_add_chart_slide_column_chart(self):
        """Test adding column chart slide"""
        exporter = PowerPointExporter()
        categories = ["Q1", "Q2", "Q3"]
        series_data = {"Sales": [100, 150, 200]}
        slide = exporter.add_chart_slide("Sales Chart", "column", categories, series_data)

        assert slide is not None
        mock_slide.shapes.add_chart.assert_called()

    def test_add_chart_slide_bar_chart(self):
        """Test adding bar chart slide"""
        exporter = PowerPointExporter()
        categories = ["Product A", "Product B"]
        series_data = {"Revenue": [500, 750]}
        slide = exporter.add_chart_slide("Revenue", "bar", categories, series_data)

        assert slide is not None

    def test_add_chart_slide_line_chart(self):
        """Test adding line chart slide"""
        exporter = PowerPointExporter()
        categories = ["Jan", "Feb", "Mar"]
        series_data = {"Trend": [10, 20, 30]}
        slide = exporter.add_chart_slide("Trend", "line", categories, series_data)

        assert slide is not None

    def test_add_chart_slide_pie_chart(self):
        """Test adding pie chart slide"""
        exporter = PowerPointExporter()
        categories = ["Category A", "Category B"]
        series_data = {"Distribution": [60, 40]}
        slide = exporter.add_chart_slide("Distribution", "pie", categories, series_data)

        assert slide is not None

    def test_add_chart_slide_with_title(self):
        """Test adding chart slide with chart title"""
        exporter = PowerPointExporter()
        categories = ["A", "B"]
        series_data = {"Data": [1, 2]}
        slide = exporter.add_chart_slide(
            "Slide Title", "column", categories, series_data, chart_title="Chart Title"
        )

        assert slide is not None

    def test_add_chart_slide_multiple_series(self):
        """Test adding chart with multiple data series"""
        exporter = PowerPointExporter()
        categories = ["Q1", "Q2"]
        series_data = {"Product A": [100, 120], "Product B": [150, 180]}
        slide = exporter.add_chart_slide("Comparison", "column", categories, series_data)

        assert slide is not None

    def test_add_image_slide_basic(self):
        """Test adding image slide without caption"""
        exporter = PowerPointExporter()
        slide = exporter.add_image_slide("Image Title", "/tmp/test.png")

        assert slide is not None
        mock_slide.shapes.add_picture.assert_called()

    def test_add_image_slide_with_caption(self):
        """Test adding image slide with caption"""
        exporter = PowerPointExporter()
        slide = exporter.add_image_slide("Image", "/tmp/test.png", caption="Test Caption")

        assert slide is not None
        mock_slide.shapes.add_picture.assert_called()
        # Caption textbox should be added
        assert mock_slide.shapes.add_textbox.call_count >= 2  # Title + caption

    def test_add_image_slide_exception_handling(self):
        """Test image slide handles exceptions gracefully"""
        exporter = PowerPointExporter()
        mock_slide.shapes.add_picture.side_effect = Exception("Image error")

        slide = exporter.add_image_slide("Image", "/bad/path.png")

        # Should return slide even on error
        assert slide is not None

    def test_add_section_divider_basic(self):
        """Test adding section divider without subtitle"""
        exporter = PowerPointExporter()
        slide = exporter.add_section_divider("New Section")

        assert slide is not None
        mock_presentation.slides.add_slide.assert_called()

    def test_add_section_divider_with_subtitle(self):
        """Test adding section divider with subtitle"""
        exporter = PowerPointExporter()
        slide = exporter.add_section_divider("Section", "Subtitle text")

        assert slide is not None

    def test_add_notes(self):
        """Test adding speaker notes to slide"""
        exporter = PowerPointExporter()
        slide = exporter.add_title_slide("Test")
        exporter.add_notes(slide, "These are speaker notes")

        # Verify notes were set
        assert slide.notes_slide.notes_text_frame.text == "These are speaker notes"

    def test_save_success(self):
        """Test saving presentation successfully"""
        exporter = PowerPointExporter()
        exporter.add_title_slide("Test")

        result = exporter.save("/tmp/test.pptx")

        assert result is True
        mock_presentation.save.assert_called_once()

    @patch("src.core.powerpoint_export.Path")
    def test_save_creates_parent_directory(self, mock_path):
        """Test save creates parent directory if needed"""
        exporter = PowerPointExporter()

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent.mkdir = Mock()

        result = exporter.save("/tmp/subdir/test.pptx")

        assert result is True
        mock_path_instance.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_save_exception_handling(self):
        """Test save handles exceptions"""
        exporter = PowerPointExporter()
        mock_presentation.save.side_effect = Exception("Save failed")

        result = exporter.save("/tmp/test.pptx")

        assert result is False

    def test_export_services_presentation_empty(self):
        """Test exporting services presentation with empty list"""
        exporter = PowerPointExporter()

        result = exporter.export_services_presentation([], "/tmp/services.pptx")

        assert result is True
        mock_presentation.save.assert_called()

    def test_export_services_presentation_with_data(self):
        """Test exporting services presentation with service data"""
        exporter = PowerPointExporter()
        services = [
            {"name": "Service 1", "region": "North"},
            {"name": "Service 2", "region": "South"},
            {"name": "Service 3", "region": "North"},
        ]

        result = exporter.export_services_presentation(services, "/tmp/services.pptx")

        assert result is True
        # Should add title, overview, chart, and summary slides
        assert mock_presentation.slides.add_slide.call_count >= 4

    def test_export_services_presentation_without_regions(self):
        """Test exporting services without region data"""
        exporter = PowerPointExporter()
        services = [{"name": "Service 1"}, {"name": "Service 2"}]

        result = exporter.export_services_presentation(services, "/tmp/services.pptx")

        assert result is True

    def test_export_services_presentation_exception(self):
        """Test export_services_presentation handles exceptions"""
        exporter = PowerPointExporter()
        mock_presentation.save.side_effect = Exception("Export failed")

        result = exporter.export_services_presentation([{"name": "Test"}], "/tmp/test.pptx")

        assert result is False


class TestConvenienceFunctions:
    """Test convenience functions"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mocks
        mock_presentation.reset_mock()
        mock_presentation.slides = MagicMock()
        mock_presentation.slide_layouts = [MagicMock() for _ in range(10)]
        mock_presentation.save = Mock()

        mock_slide.reset_mock()
        mock_slide.shapes = MagicMock()
        mock_slide.shapes.add_textbox = Mock(return_value=MagicMock())
        mock_slide.shapes.add_table = Mock(return_value=MagicMock())
        mock_slide.shapes.add_chart = Mock(return_value=MagicMock())

        mock_presentation.slides.add_slide = Mock(return_value=mock_slide)
        mock_presentation_class.reset_mock()
        mock_presentation_class.return_value = mock_presentation

    def test_create_presentation_basic(self):
        """Test create_presentation with content slides"""
        slides_data = [
            {"type": "content", "title": "Slide 1", "content": ["Point 1", "Point 2"]},
            {"type": "content", "title": "Slide 2", "content": ["Point 3"]},
        ]

        result = create_presentation("Test Presentation", slides_data, "/tmp/test.pptx")

        assert result is True
        mock_presentation.save.assert_called()

    def test_create_presentation_with_table(self):
        """Test create_presentation with table slide"""
        slides_data = [
            {
                "type": "table",
                "title": "Data Table",
                "content": [["A", "B"], ["C", "D"]],
                "headers": ["Col1", "Col2"],
            }
        ]

        result = create_presentation("Presentation", slides_data, "/tmp/table.pptx")

        assert result is True
        mock_slide.shapes.add_table.assert_called()

    def test_create_presentation_with_chart(self):
        """Test create_presentation with chart slide"""
        slides_data = [
            {
                "type": "chart",
                "title": "Chart Slide",
                "content": [],
                "chart_type": "bar",
                "categories": ["A", "B"],
                "series": {"Data": [10, 20]},
            }
        ]

        result = create_presentation("Presentation", slides_data, "/tmp/chart.pptx")

        assert result is True
        mock_slide.shapes.add_chart.assert_called()

    def test_create_presentation_mixed_slides(self):
        """Test create_presentation with mixed slide types"""
        slides_data = [
            {"type": "content", "title": "Intro", "content": ["Welcome"]},
            {"type": "table", "title": "Data", "content": [["1", "2"]]},
            {"type": "chart", "title": "Chart", "chart_type": "line", "categories": ["X"], "series": {"Y": [5]}},
        ]

        result = create_presentation("Mixed", slides_data, "/tmp/mixed.pptx")

        assert result is True
        # Should have title slide + 3 content slides
        assert mock_presentation.slides.add_slide.call_count >= 4


class TestIntegration:
    """Integration tests"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mocks
        mock_presentation.reset_mock()
        mock_presentation.slide_width = 914400 * 10
        mock_presentation.slide_height = 914400 * 5.625
        mock_presentation.slides = MagicMock()
        mock_presentation.slide_layouts = [MagicMock() for _ in range(10)]
        mock_presentation.save = Mock()

        mock_slide.reset_mock()
        mock_slide.shapes = MagicMock()
        mock_slide.shapes.title = MagicMock()
        mock_slide.shapes.add_textbox = Mock(return_value=MagicMock())
        mock_slide.shapes.add_table = Mock(return_value=MagicMock())
        mock_slide.shapes.add_chart = Mock(return_value=MagicMock())
        mock_slide.shapes.add_picture = Mock(return_value=MagicMock())

        mock_presentation.slides.add_slide = Mock(return_value=mock_slide)
        mock_presentation_class.reset_mock()
        mock_presentation_class.return_value = mock_presentation

    def test_full_presentation_workflow(self):
        """Test complete presentation creation workflow"""
        exporter = PowerPointExporter()

        # Add various slide types
        exporter.add_title_slide("Complete Presentation", "2024 Report")
        exporter.add_content_slide("Overview", ["Point 1", "Point 2"])
        exporter.add_section_divider("Section 1")
        exporter.add_table_slide("Data", [["A", "B"]], headers=["Col1", "Col2"])
        exporter.add_chart_slide("Chart", "column", ["Q1", "Q2"], {"Sales": [100, 150]})
        exporter.add_comparison_slide("Compare", ["Old"], ["New"])

        # Save
        result = exporter.save("/tmp/full.pptx")

        assert result is True
        assert mock_presentation.slides.add_slide.call_count >= 6

    def test_custom_theme_workflow(self):
        """Test workflow with custom theme"""
        custom_theme = PPTTheme()
        custom_theme.company_name = "Custom Corp"
        custom_theme.color_primary = MockRGBColor(255, 0, 0)

        exporter = PowerPointExporter(theme=custom_theme)
        exporter.add_title_slide("Custom Theme")

        assert exporter.theme.company_name == "Custom Corp"
        assert exporter.theme.color_primary.r == 255

    def test_multiple_exports_same_exporter(self):
        """Test multiple exports with same exporter instance"""
        exporter = PowerPointExporter()

        # First export
        exporter.add_title_slide("Presentation 1")
        result1 = exporter.save("/tmp/pres1.pptx")
        assert result1 is True

        # Second export (new presentation created)
        exporter.presentation = mock_presentation_class()
        exporter.add_title_slide("Presentation 2")
        result2 = exporter.save("/tmp/pres2.pptx")
        assert result2 is True
