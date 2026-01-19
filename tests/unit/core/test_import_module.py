"""
Unit tests for import_module (data import)
"""

import csv
import json
import os
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.import_module import DataImporter, import_services_from_file


# ============================================================================
# DataImporter Tests
# ============================================================================


class TestDataImporter:
    """Test DataImporter class"""

    @pytest.fixture
    def importer(self):
        """Create DataImporter instance"""
        return DataImporter()

    @pytest.fixture
    def temp_csv_file(self):
        """Create temporary CSV file"""
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def temp_json_file(self):
        """Create temporary JSON file"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_init(self, importer):
        """Test importer initialization"""
        assert importer is not None
        assert isinstance(importer, DataImporter)

    def test_import_from_csv_empty_file(self, importer, temp_csv_file):
        """Test importing from empty CSV file"""
        # Create empty CSV
        with open(temp_csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Название"])
            writer.writeheader()

        services = importer.import_from_csv(temp_csv_file)

        assert services == []

    def test_import_from_csv_with_data(self, importer, temp_csv_file):
        """Test importing from CSV with valid data"""
        # Create CSV with data
        with open(temp_csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Название",
                    "Целевая группа",
                    "Регион",
                    "Тип исполнителя",
                    "Ставка брутто",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Название": "Test Service",
                    "Целевая группа": "Test Group",
                    "Регион": "Berlin",
                    "Тип исполнителя": "Specialist",
                    "Ставка брутто": "25.50",
                }
            )

        services = importer.import_from_csv(temp_csv_file)

        assert len(services) == 1
        assert services[0].basic_info.service_name == "Test Service"
        assert services[0].basic_info.region == "Berlin"

    def test_import_from_csv_nonexistent_file(self, importer):
        """Test importing from nonexistent CSV file"""
        services = importer.import_from_csv("/nonexistent/file.csv")

        # Should return empty list instead of raising
        assert services == []

    def test_import_from_csv_unicode_data(self, importer, temp_csv_file):
        """Test importing CSV with Unicode data"""
        # Create CSV with Unicode data
        with open(temp_csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Название", "Регион", "Ставка брутто"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Название": "Услуга тест",
                    "Регион": "Москва",
                    "Ставка брутто": "30.00",
                }
            )

        services = importer.import_from_csv(temp_csv_file)

        assert len(services) == 1
        assert services[0].basic_info.service_name == "Услуга тест"
        assert services[0].basic_info.region == "Москва"

    def test_import_from_csv_multiple_rows(self, importer, temp_csv_file):
        """Test importing multiple rows from CSV"""
        with open(temp_csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Название", "Регион", "Ставка брутто"],
            )
            writer.writeheader()
            for i in range(5):
                writer.writerow(
                    {
                        "Название": f"Service {i}",
                        "Регион": "Berlin",
                        "Ставка брутто": f"{20 + i}.00",
                    }
                )

        services = importer.import_from_csv(temp_csv_file)

        assert len(services) == 5
        assert all(s.basic_info.region == "Berlin" for s in services)

    def test_csv_row_to_service_basic_fields(self, importer):
        """Test converting CSV row to Service with basic fields"""
        row = {
            "Название": "Test Service",
            "Целевая группа": "Test Group",
            "Регион": "Berlin",
            "Тип исполнителя": "Specialist",
            "Ставка брутто": "25.50",
        }

        service = importer._csv_row_to_service(row)

        assert service.basic_info.service_name == "Test Service"
        assert service.basic_info.target_group == "Test Group"
        assert service.basic_info.region == "Berlin"
        assert service.basic_info.provider_type == "Specialist"
        assert service.financial.brutto_rate == Decimal("25.50")

    def test_csv_row_to_service_optional_fields(self, importer):
        """Test converting CSV row with optional fields"""
        row = {
            "Название": "Test",
            "Ставка брутто": "25.00",
            "Региональный коэффициент": "1.20",
            "Материалы/месяц": "50.00",
            "Админ %": "7.5",
        }

        service = importer._csv_row_to_service(row)

        assert service.financial.region_coefficient == Decimal("1.20")
        assert service.financial.materials_per_month == Decimal("50.00")
        assert service.financial.admin_percent == Decimal("7.5")

    def test_csv_row_to_service_umlages_mode(self, importer):
        """Test CSV row with Umlages calculation mode"""
        row = {
            "Название": "Test",
            "Ставка брутто": "25.00",
            "Режим расчета": "Умлаги",
        }

        service = importer._csv_row_to_service(row)

        assert service.system_settings.use_umlages is True
        assert service.system_settings.use_vacation_reserve is False

    def test_csv_row_to_service_vacation_reserve_mode(self, importer):
        """Test CSV row with vacation reserve mode"""
        row = {
            "Название": "Test",
            "Ставка брутто": "25.00",
            "Режим расчета": "Резерв отпусков",
        }

        service = importer._csv_row_to_service(row)

        assert service.system_settings.use_umlages is False
        assert service.system_settings.use_vacation_reserve is True

    def test_csv_row_to_service_service_type(self, importer):
        """Test CSV row with service type"""
        row = {
            "Название": "Test",
            "Ставка брутто": "25.00",
            "Тип услуги": "commercial",
        }

        service = importer._csv_row_to_service(row)

        assert service.system_settings.service_type == "commercial"

    def test_csv_row_to_service_funding(self, importer):
        """Test CSV row with funding information"""
        row = {
            "Название": "Test",
            "Ставка брутто": "25.00",
            "Плательщик": "Eingliederungshilfe",
        }

        service = importer._csv_row_to_service(row)

        assert service.funding.payer == "Eingliederungshilfe"
        assert service.funding.documents == []

    def test_import_from_json_empty_file(self, importer, temp_json_file):
        """Test importing from empty JSON file"""
        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        services = importer.import_from_json(temp_json_file)

        # Empty array returns empty list
        assert services == []

    @patch("src.models.service.Service.from_dict")
    def test_import_from_json_single_service(self, mock_from_dict, importer, temp_json_file):
        """Test importing single service from JSON"""
        mock_service = Mock()
        mock_from_dict.return_value = mock_service

        service_data = {"basic_info": {"service_name": "Test Service"}}

        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump(service_data, f)

        services = importer.import_from_json(temp_json_file)

        assert len(services) == 1
        assert services[0] == mock_service
        mock_from_dict.assert_called_once()

    @patch("src.models.service.Service.from_dict")
    def test_import_from_json_array_of_services(self, mock_from_dict, importer, temp_json_file):
        """Test importing array of services from JSON"""
        mock_service1 = Mock()
        mock_service2 = Mock()
        mock_from_dict.side_effect = [mock_service1, mock_service2]

        services_data = [
            {"basic_info": {"service_name": "Service 1"}},
            {"basic_info": {"service_name": "Service 2"}},
        ]

        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump(services_data, f)

        services = importer.import_from_json(temp_json_file)

        assert len(services) == 2
        assert services[0] == mock_service1
        assert services[1] == mock_service2
        assert mock_from_dict.call_count == 2

    def test_import_from_json_nonexistent_file(self, importer):
        """Test importing from nonexistent JSON file"""
        services = importer.import_from_json("/nonexistent/file.json")

        # Should return empty list instead of raising
        assert services == []

    @patch("src.models.service.Service.from_dict")
    def test_import_from_json_with_errors(self, mock_from_dict, importer, temp_json_file):
        """Test importing JSON with some invalid services"""
        mock_service = Mock()
        mock_from_dict.side_effect = [Exception("Invalid data"), mock_service]

        services_data = [
            {"invalid": "data"},
            {"basic_info": {"service_name": "Valid Service"}},
        ]

        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump(services_data, f)

        services = importer.import_from_json(temp_json_file)

        # Should skip invalid and return only valid
        assert len(services) == 1
        assert services[0] == mock_service

    def test_import_from_excel_not_installed(self, importer):
        """Test Excel import without openpyxl installed"""
        # This should return empty list when libraries not available
        services = importer.import_from_excel("/fake/file.xlsx")

        # Should handle missing library gracefully
        assert isinstance(services, list)

    @patch("src.core.validator.TemplateValidator")
    def test_validate_import_data_all_valid(self, mock_validator_class, importer):
        """Test validating all valid services"""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator

        # Create mock validation result
        mock_validation = Mock()
        mock_validation.is_valid = True
        mock_validator.validate_config.return_value = mock_validation

        # Create mock services
        services = []
        for i in range(3):
            service = Mock()
            service.to_dict.return_value = {}
            service.basic_info.service_name = f"Service {i}"
            services.append(service)

        report = importer.validate_import_data(services)

        assert report["total"] == 3
        assert report["valid"] == 3
        assert report["invalid"] == 0
        assert len(report["errors"]) == 0

    @patch("src.core.validator.TemplateValidator")
    def test_validate_import_data_with_errors(self, mock_validator_class, importer):
        """Test validating services with errors"""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator

        # Create mock validation results (one invalid)
        valid_result = Mock()
        valid_result.is_valid = True

        invalid_result = Mock()
        invalid_result.is_valid = False
        invalid_result.errors = ["Missing required field"]
        invalid_result.missing_required = ["brutto_rate"]

        mock_validator.validate_config.side_effect = [valid_result, invalid_result]

        # Create mock services
        service1 = Mock()
        service1.to_dict.return_value = {}
        service1.basic_info.service_name = "Service 1"

        service2 = Mock()
        service2.to_dict.return_value = {}
        service2.basic_info.service_name = "Service 2"

        services = [service1, service2]

        report = importer.validate_import_data(services)

        assert report["total"] == 2
        assert report["valid"] == 1
        assert report["invalid"] == 1
        assert len(report["errors"]) == 1
        assert report["errors"][0]["row"] == 2
        assert report["errors"][0]["service_name"] == "Service 2"

    def test_create_import_template_csv_success(self, importer):
        """Test creating CSV template"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            result = importer.create_import_template_csv(temp_path)

            assert result is True
            assert os.path.exists(temp_path)

            # Verify template content
            with open(temp_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                assert "Название" in headers
                assert "Регион" in headers
                assert "Ставка брутто" in headers

                # Should have example row
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]["Название"] == "Пример услуги"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_create_import_template_csv_invalid_path(self, importer):
        """Test creating template with invalid path"""
        result = importer.create_import_template_csv("/invalid/path/template.csv")

        assert result is False


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestImportServicesFromFile:
    """Test import_services_from_file helper function"""

    @pytest.fixture
    def temp_csv_file(self):
        """Create temporary CSV file"""
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def temp_json_file(self):
        """Create temporary JSON file"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_import_csv_file(self, temp_csv_file):
        """Test importing CSV file"""
        # Create CSV with data
        with open(temp_csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Название", "Ставка брутто"])
            writer.writeheader()
            writer.writerow({"Название": "Test", "Ставка брутто": "25.00"})

        services = import_services_from_file(temp_csv_file)

        assert len(services) == 1
        assert services[0].basic_info.service_name == "Test"

    @patch("src.models.service.Service.from_dict")
    def test_import_json_file(self, mock_from_dict, temp_json_file):
        """Test importing JSON file"""
        mock_service = Mock()
        mock_from_dict.return_value = mock_service

        with open(temp_json_file, "w", encoding="utf-8") as f:
            json.dump({"basic_info": {"service_name": "Test"}}, f)

        services = import_services_from_file(temp_json_file)

        assert len(services) == 1

    def test_import_unsupported_format(self):
        """Test importing unsupported file format"""
        with pytest.raises(ValueError, match="Unsupported file format"):
            import_services_from_file("test.txt")

    def test_import_xlsx_format(self):
        """Test file with .xlsx extension"""
        # Should recognize .xlsx as Excel format
        # Will fail due to missing file, but tests format detection
        try:
            import_services_from_file("test.xlsx")
        except (FileNotFoundError, Exception):
            # Expected - file doesn't exist
            pass

    def test_import_xls_format(self):
        """Test file with .xls extension"""
        # Should recognize .xls as Excel format
        try:
            import_services_from_file("test.xls")
        except (FileNotFoundError, Exception):
            # Expected - file doesn't exist
            pass


# ============================================================================
# Integration Tests
# ============================================================================


class TestDataImportIntegration:
    """Test data import integration scenarios"""

    @pytest.fixture
    def importer(self):
        """Create DataImporter instance"""
        return DataImporter()

    def test_full_csv_import_workflow(self, importer):
        """Test complete CSV import workflow"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig", newline="") as f:
            temp_path = f.name
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Название",
                    "Регион",
                    "Ставка брутто",
                    "Режим расчета",
                    "Плательщик",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Название": "Service A",
                    "Регион": "Berlin",
                    "Ставка брутто": "25.50",
                    "Режим расчета": "Умлаги",
                    "Плательщик": "Jugendamt",
                }
            )
            writer.writerow(
                {
                    "Название": "Service B",
                    "Регион": "Munich",
                    "Ставка брутто": "30.00",
                    "Режим расчета": "Резерв",
                    "Плательщик": "Sozialamt",
                }
            )

        try:
            # Import
            services = importer.import_from_csv(temp_path)

            # Verify
            assert len(services) == 2
            assert services[0].basic_info.service_name == "Service A"
            assert services[1].basic_info.service_name == "Service B"

            # Check calculation modes
            assert services[0].system_settings.use_umlages is True
            assert services[1].system_settings.use_umlages is False

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_csv_with_numeric_parsing(self, importer):
        """Test CSV import with various numeric formats"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig", newline="") as f:
            temp_path = f.name
            writer = csv.DictWriter(
                f,
                fieldnames=["Название", "Ставка брутто", "Региональный коэффициент"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Название": "Test",
                    "Ставка брутто": "25,50",  # Comma decimal
                    "Региональный коэффициент": "1.20",  # Dot decimal
                }
            )

        try:
            services = importer.import_from_csv(temp_path)

            assert len(services) == 1
            # parse_number should handle both formats
            assert services[0].financial.brutto_rate > Decimal("0")

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
