"""Import module for CSV/Excel and other formats"""

import csv
import json
from decimal import Decimal
from typing import Any, Dict, List

from ..models.financial import FinancialParameters
from ..models.service import BasicInfo, Funding, Service, SystemSettings
from ..utils.helpers import parse_number


class DataImporter:
    """Import services from various formats"""

    def __init__(self):
        """Initialize importer"""
        pass

    def import_from_csv(self, csv_path: str) -> List[Service]:
        """
        Import services from CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            List of imported services
        """
        services = []

        try:
            with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    try:
                        service = self._csv_row_to_service(row)
                        services.append(service)
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
                        continue

        except Exception as e:
            print(f"Error reading CSV file: {e}")

        return services

    def _csv_row_to_service(self, row: Dict[str, str]) -> Service:
        """
        Convert CSV row to Service object

        Args:
            row: CSV row as dictionary

        Returns:
            Service object
        """
        service = Service()

        # Basic info
        service.basic_info = BasicInfo(
            service_name=row.get("Название", ""),
            target_group=row.get("Целевая группа", ""),
            region=row.get("Регион", ""),
            provider_type=row.get("Тип исполнителя", ""),
            document_date=row.get("Дата документа", ""),
            document_version=row.get("Версия документа", "1.0"),
            responsible_person=row.get("Ответственный", ""),
        )

        # Financial
        service.financial = FinancialParameters(
            brutto_rate=Decimal(str(parse_number(row.get("Ставка брутто", "0")) or 0))
        )

        if "Региональный коэффициент" in row:
            service.financial.region_coefficient = Decimal(
                str(parse_number(row.get("Региональный коэффициент", "1")) or 1)
            )

        if "Материалы/месяц" in row:
            service.financial.materials_per_month = Decimal(str(parse_number(row.get("Материалы/месяц", "0")) or 0))

        if "Админ %" in row:
            service.financial.admin_percent = Decimal(str(parse_number(row.get("Админ %", "5")) or 5))

        # System settings
        service.system_settings = SystemSettings()

        if "Режим расчета" in row:
            mode = row.get("Режим расчета", "").lower()
            service.system_settings.use_umlages = "умлаг" in mode or "umlage" in mode
            service.system_settings.use_vacation_reserve = not service.system_settings.use_umlages

        if "Тип услуги" in row:
            service.system_settings.service_type = row.get("Тип услуги", "social")

        service.financial.use_umlages = service.system_settings.use_umlages
        service.financial.use_vacation_reserve = service.system_settings.use_vacation_reserve

        # Funding
        service.funding = Funding(payer=row.get("Плательщик", ""), documents=[])

        return service

    def import_from_json(self, json_path: str) -> List[Service]:
        """
        Import services from JSON file

        Args:
            json_path: Path to JSON file

        Returns:
            List of imported services
        """
        services = []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Handle both single service and array of services
                if isinstance(data, list):
                    for item in data:
                        try:
                            service = Service.from_dict(item)
                            services.append(service)
                        except Exception as e:
                            print(f"Skipping service due to error: {e}")
                            continue
                else:
                    service = Service.from_dict(data)
                    services.append(service)

        except Exception as e:
            print(f"Error reading JSON file: {e}")

        return services

    def import_from_excel(self, excel_path: str) -> List[Service]:
        """
        Import services from Excel file (requires openpyxl or xlrd)

        Args:
            excel_path: Path to Excel file

        Returns:
            List of imported services
        """
        services = []

        try:
            # Try openpyxl first (for .xlsx)
            try:
                import openpyxl

                workbook = openpyxl.load_workbook(excel_path, read_only=True)
                sheet = workbook.active

                # Get headers from first row
                headers = [cell.value for cell in sheet[1]]

                # Read data rows
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    row_dict = dict(zip(headers, row))
                    try:
                        service = self._csv_row_to_service(row_dict)
                        services.append(service)
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
                        continue

                workbook.close()

            except ImportError:
                # Fall back to xlrd for .xls
                import xlrd

                workbook = xlrd.open_workbook(excel_path)
                sheet = workbook.sheet_by_index(0)

                # Get headers
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]

                # Read data rows
                for row_idx in range(1, sheet.nrows):
                    row_values = [sheet.cell_value(row_idx, col) for col in range(sheet.ncols)]
                    row_dict = dict(zip(headers, row_values))

                    try:
                        service = self._csv_row_to_service(row_dict)
                        services.append(service)
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
                        continue

        except ImportError:
            print("Excel import requires openpyxl or xlrd library")
        except Exception as e:
            print(f"Error reading Excel file: {e}")

        return services

    def validate_import_data(self, services: List[Service]) -> Dict[str, Any]:
        """
        Validate imported services

        Args:
            services: List of services to validate

        Returns:
            Validation report
        """
        from ..core.validator import TemplateValidator

        validator = TemplateValidator()
        report = {"total": len(services), "valid": 0, "invalid": 0, "errors": []}

        for i, service in enumerate(services):
            validation = validator.validate_config(service.to_dict())

            if validation.is_valid:
                report["valid"] += 1
            else:
                report["invalid"] += 1
                report["errors"].append(
                    {
                        "row": i + 1,
                        "service_name": service.basic_info.service_name,
                        "errors": validation.errors,
                        "missing": validation.missing_required,
                    }
                )

        return report

    def create_import_template_csv(self, output_path: str) -> bool:
        """
        Create CSV template for import

        Args:
            output_path: Path to output template file

        Returns:
            True if successful
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = [
                    "Название",
                    "Целевая группа",
                    "Регион",
                    "Тип исполнителя",
                    "Дата документа",
                    "Версия документа",
                    "Ответственный",
                    "Ставка брутто",
                    "Региональный коэффициент",
                    "Материалы/месяц",
                    "Админ %",
                    "Режим расчета",
                    "Тип услуги",
                    "Плательщик",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                # Add example row
                writer.writerow(
                    {
                        "Название": "Пример услуги",
                        "Целевая группа": "Пример целевой группы",
                        "Регион": "Berlin",
                        "Тип исполнителя": "Квалифицированный специалист",
                        "Дата документа": "01.01.2026",
                        "Версия документа": "1.0",
                        "Ответственный": "Иван Иванов",
                        "Ставка брутто": "25.50",
                        "Региональный коэффициент": "1.20",
                        "Материалы/месяц": "50.00",
                        "Админ %": "5.0",
                        "Режим расчета": "Умлаги",
                        "Тип услуги": "social",
                        "Плательщик": "Eingliederungshilfe",
                    }
                )

            return True

        except Exception as e:
            print(f"Error creating template: {e}")
            return False


def import_services_from_file(file_path: str) -> List[Service]:
    """
    Quick import services from file (auto-detect format)

    Args:
        file_path: Path to import file

    Returns:
        List of imported services
    """
    importer = DataImporter()

    if file_path.endswith(".csv"):
        return importer.import_from_csv(file_path)
    elif file_path.endswith(".json"):
        return importer.import_from_json(file_path)
    elif file_path.endswith((".xlsx", ".xls")):
        return importer.import_from_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
