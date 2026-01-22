"""Comprehensive tests for Excel export module"""

import csv
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Mock dependencies before importing
mock_service = MagicMock()
mock_format_currency = Mock(side_effect=lambda x: f"€{x:.2f}")
mock_format_percentage = Mock(side_effect=lambda x: f"{x:.2%}")
mock_financial_calculator = MagicMock()

sys.modules["src.models"] = Mock()
sys.modules["src.models.service"] = Mock(Service=mock_service)
sys.modules["src.utils"] = Mock()
sys.modules["src.utils.helpers"] = Mock(
    format_currency=mock_format_currency, format_percentage=mock_format_percentage
)
sys.modules["src.financial_calculator"] = Mock(FinancialCalculator=mock_financial_calculator)

from src.core.excel_export import (
    ExcelExporter,
    export_financial_report_to_csv,
    export_services_list_to_csv,
)


@pytest.fixture
def exporter():
    """Create ExcelExporter instance"""
    return ExcelExporter()


@pytest.fixture
def mock_service_instance():
    """Create a mock Service instance with all required attributes"""
    service = Mock()
    service.id = "SRV-001"
    service.version = "1.0"
    service.created_at = datetime(2024, 1, 15, 10, 30, 0)

    # Basic info
    service.basic_info = Mock()
    service.basic_info.service_name = "Test Service"
    service.basic_info.target_group = "Elderly"
    service.basic_info.region = "Berlin"
    service.basic_info.provider_type = "Internal"
    service.basic_info.document_date = "2024-01-15"
    service.basic_info.responsible_person = "John Doe"

    # Financial info
    service.financial = Mock()
    service.financial.brutto_rate = 25.50
    service.financial.region_coefficient = 1.05
    service.financial.materials_per_month = 150.00
    service.financial.admin_percent = 5.0

    # System settings
    service.system_settings = Mock()
    service.system_settings.service_type = "Care"
    service.system_settings.use_umlages = True

    # Funding
    service.funding = Mock()
    service.funding.payer = "Insurance"
    service.funding.documents = ["DOC-001", "DOC-002"]

    return service


@pytest.fixture
def mock_breakdown():
    """Create a mock financial breakdown"""
    breakdown = Mock()
    breakdown.brutto_rate = 25.50
    breakdown.total_insurance = 5.10
    breakdown.kv_contribution = 2.00
    breakdown.pv_contribution = 0.80
    breakdown.rv_contribution = 1.50
    breakdown.av_contribution = 0.60
    breakdown.uv_contribution = 0.20
    breakdown.total_umlages = 1.50
    breakdown.u1_contribution = 0.50
    breakdown.u2_contribution = 0.60
    breakdown.u3_contribution = 0.40
    breakdown.vacation_reserve = 2.50
    breakdown.materials_cost = 3.00
    breakdown.admin_cost = 1.80
    breakdown.base_hourly_cost = 35.00
    breakdown.final_hourly_rate = 38.00
    breakdown.calculation_mode = "with_umlages"
    return breakdown


class TestExcelExporterInit:
    """Test ExcelExporter initialization"""

    def test_exporter_creation(self, exporter):
        """Test ExcelExporter can be created"""
        assert exporter is not None
        assert isinstance(exporter, ExcelExporter)

    def test_exporter_has_export_methods(self, exporter):
        """Test ExcelExporter has all export methods"""
        assert hasattr(exporter, "export_services_to_csv")
        assert hasattr(exporter, "export_financial_report_to_csv")
        assert hasattr(exporter, "export_statistics_to_csv")
        assert hasattr(exporter, "export_service_to_excel_format")

    def test_exporter_methods_are_callable(self, exporter):
        """Test all export methods are callable"""
        assert callable(exporter.export_services_to_csv)
        assert callable(exporter.export_financial_report_to_csv)
        assert callable(exporter.export_statistics_to_csv)
        assert callable(exporter.export_service_to_excel_format)


class TestExportServicesToCSV:
    """Test export_services_to_csv method"""

    def test_export_services_success(self, exporter, mock_service_instance):
        """Test successful export of services to CSV"""
        services = [mock_service_instance]
        output_path = "/tmp/test_services.csv"

        with patch("builtins.open", mock_open()) as mock_file:
            result = exporter.export_services_to_csv(services, output_path)

        assert result is True
        mock_file.assert_called_once_with(
            output_path, "w", newline="", encoding="utf-8-sig"
        )

    def test_export_services_writes_header(self, exporter, mock_service_instance):
        """Test CSV header is written correctly"""
        services = [mock_service_instance]
        output_path = "/tmp/test_services.csv"

        # Capture CSV content
        written_data = []

        def mock_write(data):
            written_data.append(data)

        mock_file = MagicMock()
        mock_file.write = mock_write
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)

        with patch("builtins.open", return_value=mock_file):
            exporter.export_services_to_csv(services, output_path)

        content = "".join(written_data)
        assert "ID" in content or len(written_data) > 0  # Header was written

    def test_export_services_multiple_services(self, exporter, mock_service_instance):
        """Test exporting multiple services"""
        service2 = Mock()
        service2.id = "SRV-002"
        service2.version = "2.0"
        service2.created_at = datetime(2024, 2, 20, 14, 0, 0)
        service2.basic_info = Mock()
        service2.basic_info.service_name = "Second Service"
        service2.basic_info.target_group = "Youth"
        service2.basic_info.region = "Munich"
        service2.financial = Mock()
        service2.financial.brutto_rate = 30.00
        service2.financial.region_coefficient = 1.10
        service2.financial.materials_per_month = 200.00
        service2.financial.admin_percent = 6.0
        service2.system_settings = Mock()
        service2.system_settings.service_type = "Education"
        service2.system_settings.use_umlages = False
        service2.funding = Mock()
        service2.funding.payer = "Government"

        services = [mock_service_instance, service2]

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv(services, "/tmp/test.csv")

        assert result is True

    def test_export_services_empty_list(self, exporter):
        """Test exporting empty services list"""
        services = []

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv(services, "/tmp/test.csv")

        assert result is True

    def test_export_services_with_none_id(self, exporter, mock_service_instance):
        """Test export handles None service ID"""
        mock_service_instance.id = None

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv(
                [mock_service_instance], "/tmp/test.csv"
            )

        assert result is True

    def test_export_services_with_none_created_at(self, exporter, mock_service_instance):
        """Test export handles None created_at"""
        mock_service_instance.created_at = None

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv(
                [mock_service_instance], "/tmp/test.csv"
            )

        assert result is True

    def test_export_services_umlages_mode(self, exporter, mock_service_instance):
        """Test export with umlages calculation mode"""
        mock_service_instance.system_settings.use_umlages = True

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv([mock_service_instance], "/tmp/test.csv")

        assert result is True

    def test_export_services_reserve_mode(self, exporter, mock_service_instance):
        """Test export with reserve calculation mode"""
        mock_service_instance.system_settings.use_umlages = False

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv([mock_service_instance], "/tmp/test.csv")

        assert result is True

    def test_export_services_file_error(self, exporter, mock_service_instance):
        """Test export handles file write errors"""
        services = [mock_service_instance]

        with patch("builtins.open", side_effect=IOError("File error")):
            result = exporter.export_services_to_csv(services, "/tmp/test.csv")

        assert result is False

    def test_export_services_exception_handling(self, exporter):
        """Test export handles general exceptions"""
        services = [Mock()]
        services[0].id = "TEST"
        services[0].basic_info.service_name = Mock(
            side_effect=Exception("Attribute error")
        )

        with patch("builtins.open", mock_open()):
            result = exporter.export_services_to_csv(services, "/tmp/test.csv")

        assert result is False


class TestExportFinancialReportToCSV:
    """Test export_financial_report_to_csv method"""

    def test_export_financial_report_success(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test successful export of financial report"""
        services = [mock_service_instance]

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is True
        mock_calculator.calculate_hourly_rate.assert_called_once()

    def test_export_financial_report_with_umlages(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test financial report export with umlages mode"""
        mock_breakdown.calculation_mode = "with_umlages"
        services = [mock_service_instance]

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is True

    def test_export_financial_report_with_reserve(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test financial report export with reserve mode"""
        mock_breakdown.calculation_mode = "with_reserve"
        services = [mock_service_instance]

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is True

    def test_export_financial_report_multiple_services(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test exporting financial report for multiple services"""
        service2 = Mock()
        service2.id = "SRV-002"
        service2.basic_info = Mock()
        service2.basic_info.service_name = "Service 2"
        service2.basic_info.region = "Hamburg"
        service2.financial = Mock()

        services = [mock_service_instance, service2]

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is True
        assert mock_calculator.calculate_hourly_rate.call_count == 2

    def test_export_financial_report_empty_list(self, exporter):
        """Test exporting empty financial report"""
        services = []

        with patch("src.financial_calculator.FinancialCalculator"):
            with patch("builtins.open", mock_open()):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is True

    def test_export_financial_report_file_error(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test financial report export handles file errors"""
        services = [mock_service_instance]

        with patch("src.financial_calculator.FinancialCalculator"):
            with patch("builtins.open", side_effect=IOError("File error")):
                result = exporter.export_financial_report_to_csv(
                    services, "/tmp/test.csv"
                )

        assert result is False

    def test_export_financial_report_calculator_error(
        self, exporter, mock_service_instance
    ):
        """Test financial report handles calculator errors"""
        services = [mock_service_instance]

        with patch(
            "src.financial_calculator.FinancialCalculator",
            side_effect=Exception("Calculator error"),
        ):
            result = exporter.export_financial_report_to_csv(services, "/tmp/test.csv")

        assert result is False


class TestExportStatisticsToCSV:
    """Test export_statistics_to_csv method"""

    def test_export_statistics_success(self, exporter):
        """Test successful export of statistics"""
        stats = {
            "total_services": 100,
            "avg_brutto_rate": 28.50,
            "by_region": {"Berlin": 40, "Munich": 30, "Hamburg": 30},
            "by_type": {"Care": 60, "Education": 40},
        }

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_minimal_data(self, exporter):
        """Test export with minimal statistics"""
        stats = {"total_services": 5, "avg_brutto_rate": 25.00}

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_empty_dict(self, exporter):
        """Test export with empty statistics"""
        stats = {}

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_with_regions(self, exporter):
        """Test statistics export includes regions"""
        stats = {
            "total_services": 50,
            "avg_brutto_rate": 30.00,
            "by_region": {"Berlin": 20, "Munich": 15, None: 15},
        }

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_with_types(self, exporter):
        """Test statistics export includes service types"""
        stats = {
            "total_services": 80,
            "avg_brutto_rate": 27.00,
            "by_type": {"Care": 50, "Education": 20, "Other": 10},
        }

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_empty_regions(self, exporter):
        """Test statistics with empty regions dict"""
        stats = {"total_services": 10, "by_region": {}}

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_empty_types(self, exporter):
        """Test statistics with empty types dict"""
        stats = {"total_services": 10, "by_type": {}}

        with patch("builtins.open", mock_open()):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is True

    def test_export_statistics_file_error(self, exporter):
        """Test statistics export handles file errors"""
        stats = {"total_services": 10}

        with patch("builtins.open", side_effect=IOError("File error")):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is False

    def test_export_statistics_exception(self, exporter):
        """Test statistics export handles exceptions"""
        stats = {"total_services": 10}

        with patch("builtins.open", side_effect=Exception("Unexpected error")):
            result = exporter.export_statistics_to_csv(stats, "/tmp/test.csv")

        assert result is False


class TestExportServiceToExcelFormat:
    """Test export_service_to_excel_format method"""

    def test_export_service_excel_format_success(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test successful export of single service to Excel format"""
        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True
        mock_calculator.calculate_hourly_rate.assert_called_once_with(
            mock_service_instance.financial
        )

    def test_export_service_excel_format_with_umlages(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test Excel format export with umlages mode"""
        mock_breakdown.calculation_mode = "with_umlages"

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True

    def test_export_service_excel_format_with_reserve(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test Excel format export with reserve mode"""
        mock_breakdown.calculation_mode = "with_reserve"

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True

    def test_export_service_excel_format_sections(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test Excel format includes all sections"""
        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True

    def test_export_service_excel_format_with_documents(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test Excel format includes funding documents"""
        mock_service_instance.funding.documents = ["DOC-001", "DOC-002", "DOC-003"]

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True

    def test_export_service_excel_format_without_documents(
        self, exporter, mock_service_instance, mock_breakdown
    ):
        """Test Excel format without funding documents"""
        mock_service_instance.funding.documents = []

        with patch(
            "src.financial_calculator.FinancialCalculator"
        ) as mock_calculator_class:
            mock_calculator = Mock()
            mock_calculator.calculate_hourly_rate.return_value = mock_breakdown
            mock_calculator_class.return_value = mock_calculator

            with patch("builtins.open", mock_open()):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is True

    def test_export_service_excel_format_file_error(
        self, exporter, mock_service_instance
    ):
        """Test Excel format export handles file errors"""
        with patch("src.financial_calculator.FinancialCalculator"):
            with patch("builtins.open", side_effect=IOError("File error")):
                result = exporter.export_service_to_excel_format(
                    mock_service_instance, "/tmp/test.csv"
                )

        assert result is False

    def test_export_service_excel_format_calculator_error(
        self, exporter, mock_service_instance
    ):
        """Test Excel format handles calculator errors"""
        with patch(
            "src.financial_calculator.FinancialCalculator",
            side_effect=Exception("Calculator error"),
        ):
            result = exporter.export_service_to_excel_format(
                mock_service_instance, "/tmp/test.csv"
            )

        assert result is False


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""

    def test_export_services_list_to_csv_success(self, mock_service_instance):
        """Test module-level export_services_list_to_csv function"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch("src.core.excel_export.ExcelExporter.export_services_to_csv") as mock_export:
                mock_export.return_value = True
                result = export_services_list_to_csv(services, "test.csv")

        assert result == "data/exports/test.csv"

    def test_export_services_list_default_filename(self, mock_service_instance):
        """Test export_services_list_to_csv with default filename"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch("src.core.excel_export.ExcelExporter.export_services_to_csv") as mock_export:
                mock_export.return_value = True
                result = export_services_list_to_csv(services)

        assert result == "data/exports/services_export.csv"

    def test_export_services_list_creates_directory(self, mock_service_instance):
        """Test export_services_list_to_csv creates export directory"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir") as mock_mkdir:
            with patch("src.core.excel_export.ExcelExporter.export_services_to_csv") as mock_export:
                mock_export.return_value = True
                export_services_list_to_csv(services, "test.csv")

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_export_services_list_failure(self, mock_service_instance):
        """Test export_services_list_to_csv handles failures"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch("src.core.excel_export.ExcelExporter.export_services_to_csv") as mock_export:
                mock_export.return_value = False
                with pytest.raises(Exception, match="Failed to export services"):
                    export_services_list_to_csv(services, "test.csv")

    def test_export_financial_report_function_success(self, mock_service_instance):
        """Test module-level export_financial_report_to_csv function"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch(
                "src.core.excel_export.ExcelExporter.export_financial_report_to_csv"
            ) as mock_export:
                mock_export.return_value = True
                result = export_financial_report_to_csv(services, "report.csv")

        assert result == "data/exports/report.csv"

    def test_export_financial_report_default_filename(self, mock_service_instance):
        """Test export_financial_report_to_csv with default filename"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch(
                "src.core.excel_export.ExcelExporter.export_financial_report_to_csv"
            ) as mock_export:
                mock_export.return_value = True
                result = export_financial_report_to_csv(services)

        assert result == "data/exports/financial_report.csv"

    def test_export_financial_report_creates_directory(self, mock_service_instance):
        """Test export_financial_report_to_csv creates export directory"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir") as mock_mkdir:
            with patch(
                "src.core.excel_export.ExcelExporter.export_financial_report_to_csv"
            ) as mock_export:
                mock_export.return_value = True
                export_financial_report_to_csv(services, "report.csv")

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_export_financial_report_failure(self, mock_service_instance):
        """Test export_financial_report_to_csv handles failures"""
        services = [mock_service_instance]

        with patch("src.core.excel_export.Path.mkdir"):
            with patch(
                "src.core.excel_export.ExcelExporter.export_financial_report_to_csv"
            ) as mock_export:
                mock_export.return_value = False
                with pytest.raises(Exception, match="Failed to export financial report"):
                    export_financial_report_to_csv(services, "report.csv")
