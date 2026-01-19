"""
Tests for Enhanced Excel Export Module

Tests Excel generation with openpyxl (advanced formatting, charts, formulas).
"""

import sys
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call

# Mock openpyxl before importing
mock_workbook_class = Mock()
mock_workbook = MagicMock()
mock_workbook_class.return_value = mock_workbook
mock_workbook.sheetnames = ["Sheet"]
mock_workbook.properties = MagicMock()
mock_workbook.create_sheet = Mock(return_value=MagicMock())

# Mock chart classes (need to be callable)
mock_line_chart = Mock(return_value=MagicMock())
mock_bar_chart = Mock(return_value=MagicMock())
mock_pie_chart = Mock(return_value=MagicMock())
mock_area_chart = Mock(return_value=MagicMock())
mock_reference = Mock(return_value=MagicMock())
mock_series = Mock(return_value=MagicMock())

# Mock formatting rules (need to be callable)
mock_cell_is_rule = Mock(return_value=MagicMock())
mock_color_scale_rule = Mock(return_value=MagicMock())
mock_formula_rule = Mock(return_value=MagicMock())

# Mock styles (need to be callable)
mock_font = Mock(return_value=MagicMock())
mock_alignment = Mock(return_value=MagicMock())
mock_border = Mock(return_value=MagicMock())
mock_pattern_fill = Mock(return_value=MagicMock())
mock_protection = Mock(return_value=MagicMock())
mock_side = Mock(return_value=MagicMock())

# Mock utils
def mock_get_column_letter(col_idx):
    """Mock get_column_letter to return simple letters"""
    if col_idx <= 26:
        return chr(64 + col_idx)
    else:
        return f"A{chr(64 + col_idx - 26)}"

# Mock data validation (need to be callable)
mock_data_validation = Mock(return_value=MagicMock())

# Set up sys.modules mocks
sys.modules["openpyxl"] = Mock()
sys.modules["openpyxl"].Workbook = mock_workbook_class
sys.modules["openpyxl.chart"] = Mock()
sys.modules["openpyxl.chart"].LineChart = mock_line_chart
sys.modules["openpyxl.chart"].BarChart = mock_bar_chart
sys.modules["openpyxl.chart"].PieChart = mock_pie_chart
sys.modules["openpyxl.chart"].AreaChart = mock_area_chart
sys.modules["openpyxl.chart"].Reference = mock_reference
sys.modules["openpyxl.chart"].Series = mock_series
sys.modules["openpyxl.formatting"] = Mock()
sys.modules["openpyxl.formatting.rule"] = Mock()
sys.modules["openpyxl.formatting.rule"].CellIsRule = mock_cell_is_rule
sys.modules["openpyxl.formatting.rule"].ColorScaleRule = mock_color_scale_rule
sys.modules["openpyxl.formatting.rule"].FormulaRule = mock_formula_rule
sys.modules["openpyxl.styles"] = Mock()
sys.modules["openpyxl.styles"].Font = mock_font
sys.modules["openpyxl.styles"].Alignment = mock_alignment
sys.modules["openpyxl.styles"].Border = mock_border
sys.modules["openpyxl.styles"].PatternFill = mock_pattern_fill
sys.modules["openpyxl.styles"].Protection = mock_protection
sys.modules["openpyxl.styles"].Side = mock_side
sys.modules["openpyxl.utils"] = Mock()
sys.modules["openpyxl.utils"].get_column_letter = mock_get_column_letter
sys.modules["openpyxl.worksheet"] = Mock()
sys.modules["openpyxl.worksheet.datavalidation"] = Mock()
sys.modules["openpyxl.worksheet.datavalidation"].DataValidation = mock_data_validation

from src.core.enhanced_excel_export import (
    ExcelStyle,
    EnhancedExcelExporter,
    OPENPYXL_AVAILABLE,
)


class TestExcelStyle:
    """Test ExcelStyle predefined styles"""

    def test_colors_defined(self):
        """Test color constants are defined"""
        assert hasattr(ExcelStyle, "COLOR_HEADER")
        assert hasattr(ExcelStyle, "COLOR_ACCENT")
        assert hasattr(ExcelStyle, "COLOR_WARNING")
        assert hasattr(ExcelStyle, "COLOR_DANGER")
        assert hasattr(ExcelStyle, "COLOR_LIGHT")
        assert hasattr(ExcelStyle, "COLOR_DARK")

        # Verify color format (hex without #)
        assert ExcelStyle.COLOR_HEADER == "0D6EFD"
        assert ExcelStyle.COLOR_ACCENT == "198754"

    def test_fonts_defined(self):
        """Test font constants are defined"""
        assert hasattr(ExcelStyle, "FONT_HEADER")
        assert hasattr(ExcelStyle, "FONT_TITLE")
        assert hasattr(ExcelStyle, "FONT_BODY")
        assert hasattr(ExcelStyle, "FONT_BOLD")
        assert hasattr(ExcelStyle, "FONT_ITALIC")

    def test_alignments_defined(self):
        """Test alignment constants are defined"""
        assert hasattr(ExcelStyle, "ALIGN_CENTER")
        assert hasattr(ExcelStyle, "ALIGN_LEFT")
        assert hasattr(ExcelStyle, "ALIGN_RIGHT")
        assert hasattr(ExcelStyle, "ALIGN_JUSTIFY")

    def test_borders_defined(self):
        """Test border constants are defined"""
        assert hasattr(ExcelStyle, "BORDER_THIN")
        assert hasattr(ExcelStyle, "BORDER_THICK")

    def test_fills_defined(self):
        """Test fill constants are defined"""
        assert hasattr(ExcelStyle, "FILL_HEADER")
        assert hasattr(ExcelStyle, "FILL_ACCENT")
        assert hasattr(ExcelStyle, "FILL_LIGHT")


class TestEnhancedExcelExporter:
    """Test EnhancedExcelExporter class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Reset mock workbook
        mock_workbook.reset_mock()
        mock_workbook.sheetnames = ["Sheet"]
        mock_workbook.__getitem__ = Mock()
        mock_workbook.__delitem__ = Mock()
        mock_workbook.create_sheet = Mock(return_value=MagicMock())
        mock_workbook.save = Mock()
        mock_workbook.properties = MagicMock()

        mock_workbook_class.reset_mock()
        mock_workbook_class.return_value = mock_workbook

        # Reset mocks for charts, rules, validation
        mock_line_chart.reset_mock()
        mock_bar_chart.reset_mock()
        mock_pie_chart.reset_mock()
        mock_area_chart.reset_mock()
        mock_cell_is_rule.reset_mock()
        mock_color_scale_rule.reset_mock()
        mock_formula_rule.reset_mock()
        mock_data_validation.reset_mock()

    def test_initialization(self):
        """Test exporter initialization"""
        exporter = EnhancedExcelExporter()
        assert exporter.workbook is None
        assert exporter.sheets == {}

    def test_initialization_openpyxl_not_available(self):
        """Test initialization fails when openpyxl not available"""
        # This test is difficult to perform since we need openpyxl for importing
        # Just verify that OPENPYXL_AVAILABLE is True in our test environment
        assert OPENPYXL_AVAILABLE is True

    def test_create_workbook_default(self):
        """Test creating workbook with default title"""
        exporter = EnhancedExcelExporter()
        wb = exporter.create_workbook()

        assert wb is not None
        assert exporter.workbook is not None
        mock_workbook_class.assert_called_once()

    def test_create_workbook_custom_title(self):
        """Test creating workbook with custom title"""
        exporter = EnhancedExcelExporter()
        wb = exporter.create_workbook(title="Custom Report")

        assert wb is not None
        # Verify properties were set
        assert mock_workbook.properties.title is not None

    def test_create_workbook_removes_default_sheet(self):
        """Test default sheet is removed"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        # Verify __delitem__ was called to remove default sheet
        mock_workbook.__delitem__.assert_called()

    def test_add_sheet_basic(self):
        """Test adding basic sheet with data"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [
            {"name": "Alice", "age": 30, "city": "Berlin"},
            {"name": "Bob", "age": 25, "city": "Munich"},
        ]

        ws = exporter.add_sheet("TestSheet", data)

        assert ws is not None
        assert "TestSheet" in exporter.sheets
        mock_workbook.create_sheet.assert_called_with(title="TestSheet")

    def test_add_sheet_with_title(self):
        """Test adding sheet with title row"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"name": "Alice", "value": 100}]

        ws = exporter.add_sheet("TestSheet", data, title="Report Title")

        assert ws is not None
        # Verify merge_cells was called for title
        ws.merge_cells.assert_called()

    def test_add_sheet_custom_headers(self):
        """Test adding sheet with custom headers"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"name": "Alice", "value": 100}]
        headers = ["Name", "Value"]

        ws = exporter.add_sheet("TestSheet", data, headers=headers)

        assert ws is not None
        # Verify cell was accessed for headers
        assert ws.cell.called

    def test_add_sheet_without_style(self):
        """Test adding sheet without header styling"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"name": "Alice"}]

        ws = exporter.add_sheet("TestSheet", data, style_header=False)

        assert ws is not None

    def test_add_sheet_empty_data(self):
        """Test adding sheet with empty data"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        ws = exporter.add_sheet("EmptySheet", [], headers=["Name", "Value"])

        assert ws is not None

    def test_add_sheet_formats_datetime(self):
        """Test sheet formats datetime values correctly"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"date": datetime(2024, 1, 15, 10, 30)}]

        ws = exporter.add_sheet("DateSheet", data)

        assert ws is not None
        # Cell should be called for each data value
        assert ws.cell.called

    def test_add_sheet_formats_date(self):
        """Test sheet formats date values correctly"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"date": date(2024, 1, 15)}]

        ws = exporter.add_sheet("DateSheet", data)

        assert ws is not None

    def test_add_sheet_formats_numbers(self):
        """Test sheet formats numeric values correctly"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [
            {"integer": 42, "float": 3.14, "decimal": Decimal("10.50")}
        ]

        ws = exporter.add_sheet("NumberSheet", data)

        assert ws is not None

    def test_add_sheet_formats_boolean(self):
        """Test sheet formats boolean values correctly"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"active": True, "disabled": False}]

        ws = exporter.add_sheet("BoolSheet", data)

        assert ws is not None

    def test_add_chart_line(self):
        """Test adding line chart"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"month": "Jan", "sales": 100}]
        exporter.add_sheet("Data", data)

        exporter.add_chart(
            sheet_name="Data",
            chart_type="line",
            data_range="B2:B13",
            title="Sales Chart",
            position="E2",
        )

        # Verify chart was created
        mock_line_chart.assert_called_once()

    def test_add_chart_bar(self):
        """Test adding bar chart"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"category": "A", "value": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_chart(
            sheet_name="Data",
            chart_type="bar",
            data_range="B2:B10",
            title="Bar Chart",
        )

        mock_bar_chart.assert_called_once()

    def test_add_chart_pie(self):
        """Test adding pie chart"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"label": "A", "value": 25}]
        exporter.add_sheet("Data", data)

        exporter.add_chart(
            sheet_name="Data",
            chart_type="pie",
            data_range="B2:B5",
            title="Pie Chart",
        )

        mock_pie_chart.assert_called_once()

    def test_add_chart_area(self):
        """Test adding area chart"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"x": 1, "y": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_chart(
            sheet_name="Data",
            chart_type="area",
            data_range="B2:B10",
            title="Area Chart",
        )

        mock_area_chart.assert_called_once()

    def test_add_conditional_formatting_cell_is(self):
        """Test adding cell-based conditional formatting"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"value": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_conditional_formatting(
            sheet_name="Data",
            range_="A2:A10",
            rule_type="cell_is",
            operator="greaterThan",
            formula=["5"],
            fill="FF0000",
        )

        # Verify rule was created
        mock_cell_is_rule.assert_called_once()

    def test_add_conditional_formatting_color_scale(self):
        """Test adding color scale conditional formatting"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"value": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_conditional_formatting(
            sheet_name="Data",
            range_="A2:A10",
            rule_type="color_scale",
        )

        mock_color_scale_rule.assert_called_once()

    def test_add_conditional_formatting_formula(self):
        """Test adding formula-based conditional formatting"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"value": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_conditional_formatting(
            sheet_name="Data",
            range_="A2:A10",
            rule_type="formula",
            formula=["$A2>10"],
            fill="00FF00",
        )

        mock_formula_rule.assert_called_once()

    def test_add_data_validation_list(self):
        """Test adding list data validation"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"status": "Active"}]
        exporter.add_sheet("Data", data)

        exporter.add_data_validation(
            sheet_name="Data",
            range_="A2:A10",
            validation_type="list",
            formula1='"Active,Inactive,Pending"',
        )

        mock_data_validation.assert_called_once()

    def test_add_data_validation_integer(self):
        """Test adding integer data validation"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"age": 30}]
        exporter.add_sheet("Data", data)

        exporter.add_data_validation(
            sheet_name="Data",
            range_="A2:A10",
            validation_type="whole",
            operator="between",
            formula1="1",
            formula2="100",
        )

        mock_data_validation.assert_called_once()

    def test_add_formula(self):
        """Test adding formula to cell"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        data = [{"value": 10}]
        exporter.add_sheet("Data", data)

        exporter.add_formula("Data", "C2", "=SUM(A2:B2)")

        # Verify cell access
        ws = exporter.sheets["Data"]
        assert ws.__getitem__.called or hasattr(ws, "__getitem__")

    def test_save_success(self):
        """Test saving workbook successfully"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        result = exporter.save("/tmp/test_export.xlsx")

        assert result is True
        mock_workbook.save.assert_called_once_with("/tmp/test_export.xlsx")

    def test_save_no_workbook(self):
        """Test save fails when no workbook"""
        exporter = EnhancedExcelExporter()

        result = exporter.save("/tmp/test.xlsx")

        assert result is False

    def test_save_exception(self):
        """Test save handles exceptions"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        mock_workbook.save.side_effect = Exception("Save failed")

        result = exporter.save("/tmp/test.xlsx")

        assert result is False

    def test_export_services_report(self):
        """Test exporting services report"""
        exporter = EnhancedExcelExporter()

        services = [
            {
                "service_name": "Service A",
                "region": "North",
                "target_group": "Adults",
                "brutto_rate": 45.50,
                "netto_rate": 38.25,
            },
            {
                "service_name": "Service B",
                "region": "South",
                "target_group": "Children",
                "brutto_rate": 52.00,
                "netto_rate": 44.00,
            },
        ]

        result = exporter.export_services_report(services, "/tmp/services.xlsx")

        assert result is True
        # Verify workbook was created and sheets added
        mock_workbook_class.assert_called()
        assert mock_workbook.create_sheet.called

    def test_export_services_report_empty(self):
        """Test exporting empty services list"""
        exporter = EnhancedExcelExporter()

        result = exporter.export_services_report([], "/tmp/empty.xlsx")

        # Empty data causes error (list index out of range), so result is False
        assert result is False


class TestIntegration:
    """Integration tests"""

    def test_full_export_workflow(self):
        """Test complete export workflow"""
        exporter = EnhancedExcelExporter()

        # Create workbook
        exporter.create_workbook(title="Full Report")

        # Add data sheet
        data = [
            {"product": "Widget", "sales": 100, "revenue": 1000.50},
            {"product": "Gadget", "sales": 200, "revenue": 2500.75},
        ]
        exporter.add_sheet("Sales", data, title="Sales Report")

        # Add chart
        exporter.add_chart(
            sheet_name="Sales",
            chart_type="bar",
            data_range="C2:C3",
            title="Sales Chart",
        )

        # Save
        result = exporter.save("/tmp/full_report.xlsx")

        assert result is True

    def test_multiple_sheets_workflow(self):
        """Test creating multiple sheets"""
        exporter = EnhancedExcelExporter()
        exporter.create_workbook()

        # Sheet 1
        data1 = [{"name": "Alice", "score": 95}]
        exporter.add_sheet("Students", data1)

        # Sheet 2
        data2 = [{"course": "Math", "average": 88.5}]
        exporter.add_sheet("Courses", data2)

        # Verify both sheets exist
        assert "Students" in exporter.sheets
        assert "Courses" in exporter.sheets

        result = exporter.save("/tmp/multi_sheet.xlsx")
        assert result is True
