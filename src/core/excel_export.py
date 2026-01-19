"""Excel export module for services and reports"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from ..models.service import Service
from ..utils.helpers import format_currency, format_percentage


class ExcelExporter:
    """Export services and reports to Excel/CSV"""

    def __init__(self):
        """Initialize exporter"""
        pass

    def export_services_to_csv(self, services: List[Service], output_path: str) -> bool:
        """
        Export services to CSV

        Args:
            services: List of services
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = [
                    "ID",
                    "Название",
                    "Целевая группа",
                    "Регион",
                    "Тип услуги",
                    "Ставка брутто",
                    "Региональный коэффициент",
                    "Материалы/месяц",
                    "Админ %",
                    "Режим расчета",
                    "Плательщик",
                    "Дата создания",
                    "Версия",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for service in services:
                    writer.writerow(
                        {
                            "ID": service.id or "",
                            "Название": service.basic_info.service_name,
                            "Целевая группа": service.basic_info.target_group,
                            "Регион": service.basic_info.region,
                            "Тип услуги": service.system_settings.service_type,
                            "Ставка брутто": float(service.financial.brutto_rate),
                            "Региональный коэффициент": float(service.financial.region_coefficient),
                            "Материалы/месяц": float(service.financial.materials_per_month),
                            "Админ %": float(service.financial.admin_percent),
                            "Режим расчета": "Умлаги" if service.system_settings.use_umlages else "Резерв",
                            "Плательщик": service.funding.payer,
                            "Дата создания": service.created_at.isoformat() if service.created_at else "",
                            "Версия": service.version,
                        }
                    )

            return True

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_financial_report_to_csv(self, services: List[Service], output_path: str) -> bool:
        """
        Export financial report to CSV

        Args:
            services: List of services
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            from ..financial_calculator import FinancialCalculator

            calculator = FinancialCalculator()

            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = [
                    "ID",
                    "Название",
                    "Регион",
                    "Ставка брутто",
                    "Социальные отчисления",
                    "Умлаги/Резерв",
                    "Материалы",
                    "Админ",
                    "Базовая стоимость",
                    "Итоговая ставка",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for service in services:
                    breakdown = calculator.calculate_hourly_rate(service.financial)

                    umlages_or_reserve = (
                        float(breakdown.total_umlages)
                        if breakdown.calculation_mode == "with_umlages"
                        else float(breakdown.vacation_reserve)
                    )

                    writer.writerow(
                        {
                            "ID": service.id or "",
                            "Название": service.basic_info.service_name,
                            "Регион": service.basic_info.region,
                            "Ставка брутто": float(breakdown.brutto_rate),
                            "Социальные отчисления": float(breakdown.total_insurance),
                            "Умлаги/Резерв": umlages_or_reserve,
                            "Материалы": float(breakdown.materials_cost),
                            "Админ": float(breakdown.admin_cost),
                            "Базовая стоимость": float(breakdown.base_hourly_cost),
                            "Итоговая ставка": float(breakdown.final_hourly_rate),
                        }
                    )

            return True

        except Exception as e:
            print(f"Error exporting financial report: {e}")
            return False

    def export_statistics_to_csv(self, stats: Dict[str, Any], output_path: str) -> bool:
        """
        Export statistics to CSV

        Args:
            stats: Statistics dictionary
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)

                # General statistics
                writer.writerow(["Общая статистика", ""])
                writer.writerow(["Всего услуг", stats.get("total_services", 0)])
                writer.writerow(["Средняя ставка брутто", stats.get("avg_brutto_rate", 0)])
                writer.writerow([])

                # By region
                if "by_region" in stats and stats["by_region"]:
                    writer.writerow(["Услуги по регионам", ""])
                    writer.writerow(["Регион", "Количество"])
                    for region, count in stats["by_region"].items():
                        writer.writerow([region or "Не указан", count])
                    writer.writerow([])

                # By type
                if "by_type" in stats and stats["by_type"]:
                    writer.writerow(["Услуги по типам", ""])
                    writer.writerow(["Тип", "Количество"])
                    for stype, count in stats["by_type"].items():
                        writer.writerow([stype, count])

            return True

        except Exception as e:
            print(f"Error exporting statistics: {e}")
            return False

    def export_service_to_excel_format(self, service: Service, output_path: str) -> bool:
        """
        Export single service to detailed Excel-compatible CSV

        Args:
            service: Service to export
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            from ..financial_calculator import FinancialCalculator

            calculator = FinancialCalculator()
            breakdown = calculator.calculate_hourly_rate(service.financial)

            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)

                # Header
                writer.writerow(["ОТЧЕТ ПО УСЛУГЕ"])
                writer.writerow([])

                # Basic info
                writer.writerow(["БАЗОВАЯ ИНФОРМАЦИЯ", ""])
                writer.writerow(["ID", service.id or ""])
                writer.writerow(["Название", service.basic_info.service_name])
                writer.writerow(["Целевая группа", service.basic_info.target_group])
                writer.writerow(["Регион", service.basic_info.region])
                writer.writerow(["Тип исполнителя", service.basic_info.provider_type])
                writer.writerow(["Дата документа", service.basic_info.document_date])
                writer.writerow(["Версия", service.version])
                writer.writerow(["Ответственный", service.basic_info.responsible_person])
                writer.writerow([])

                # Financial parameters
                writer.writerow(["ФИНАНСОВЫЕ ПАРАМЕТРЫ", ""])
                writer.writerow(["Ставка брутто", float(service.financial.brutto_rate)])
                writer.writerow(["Региональный коэффициент", float(service.financial.region_coefficient)])
                writer.writerow(["Материалы/месяц", float(service.financial.materials_per_month)])
                writer.writerow(["Админ расходы %", float(service.financial.admin_percent)])
                writer.writerow(["Режим расчета", "Умлаги" if service.system_settings.use_umlages else "Резерв"])
                writer.writerow(["Тип услуги", service.system_settings.service_type])
                writer.writerow([])

                # Cost breakdown
                writer.writerow(["РАСЧЕТ СТОИМОСТИ", ""])
                writer.writerow(["Компонент", "Сумма (€)"])
                writer.writerow(["Ставка брутто", float(breakdown.brutto_rate)])
                writer.writerow(["Социальные отчисления", float(breakdown.total_insurance)])
                writer.writerow(["  - KV", float(breakdown.kv_contribution)])
                writer.writerow(["  - PV", float(breakdown.pv_contribution)])
                writer.writerow(["  - RV", float(breakdown.rv_contribution)])
                writer.writerow(["  - AV", float(breakdown.av_contribution)])
                writer.writerow(["  - UV", float(breakdown.uv_contribution)])

                if breakdown.calculation_mode == "with_umlages":
                    writer.writerow(["Умлаги", float(breakdown.total_umlages)])
                    writer.writerow(["  - U1", float(breakdown.u1_contribution)])
                    writer.writerow(["  - U2", float(breakdown.u2_contribution)])
                    writer.writerow(["  - U3", float(breakdown.u3_contribution)])
                else:
                    writer.writerow(["Резерв отпуск/больничные", float(breakdown.vacation_reserve)])

                writer.writerow(["Материалы", float(breakdown.materials_cost)])
                writer.writerow(["Административные расходы", float(breakdown.admin_cost)])
                writer.writerow([])
                writer.writerow(["Базовая стоимость часа", float(breakdown.base_hourly_cost)])
                writer.writerow(["ИТОГОВАЯ СТАВКА", float(breakdown.final_hourly_rate)])
                writer.writerow([])

                # Examples
                writer.writerow(["ПРИМЕРЫ РАСЧЕТА", ""])
                writer.writerow(["Часов", "Стоимость (€)"])
                for hours in [1, 10, 40, 80, 160]:
                    cost = float(breakdown.final_hourly_rate) * hours
                    writer.writerow([hours, f"{cost:.2f}"])
                writer.writerow([])

                # Funding
                writer.writerow(["ФИНАНСИРОВАНИЕ", ""])
                writer.writerow(["Плательщик", service.funding.payer])
                if service.funding.documents:
                    writer.writerow(["Документы", ", ".join(service.funding.documents)])

            return True

        except Exception as e:
            print(f"Error exporting service to Excel format: {e}")
            return False


def export_services_list_to_csv(services: List[Service], filename: str = "services_export.csv") -> str:
    """
    Quick export services to CSV

    Args:
        services: List of services
        filename: Output filename

    Returns:
        Path to created file
    """
    output_path = f"data/exports/{filename}"
    exporter = ExcelExporter()

    Path("data/exports").mkdir(parents=True, exist_ok=True)

    if exporter.export_services_to_csv(services, output_path):
        return output_path
    else:
        raise Exception("Failed to export services")


def export_financial_report_to_csv(services: List[Service], filename: str = "financial_report.csv") -> str:
    """
    Quick export financial report to CSV

    Args:
        services: List of services
        filename: Output filename

    Returns:
        Path to created file
    """
    output_path = f"data/exports/{filename}"
    exporter = ExcelExporter()

    Path("data/exports").mkdir(parents=True, exist_ok=True)

    if exporter.export_financial_report_to_csv(services, output_path):
        return output_path
    else:
        raise Exception("Failed to export financial report")
