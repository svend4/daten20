#!/usr/bin/env python3
"""
Document Generator - Генератор документов

Заполнение шаблона данными и экспорт в различные форматы.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.exporter import DocumentExporter
from src.core.parser import TemplateParser
from src.core.validator import TemplateValidator
from src.models.service import Service
from src.utils.constants import EXPORT_FORMATS
from src.utils.formatting import error, header, info, section, success, warning
from src.utils.helpers import get_date_string, load_config, sanitize_filename


class DocumentGenerator:
    """Main Document Generator class"""

    def __init__(self, template_path: str = "mSchablone"):
        """
        Initialize generator

        Args:
            template_path: Path to template file
        """
        self.template_path = template_path
        self.parser = TemplateParser(template_path)
        self.validator = TemplateValidator()
        self.exporter = DocumentExporter()
        self.template_content = ""

    def load_template(self) -> bool:
        """
        Load template content

        Returns:
            True if successful
        """
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                self.template_content = f.read()
            return True
        except Exception as e:
            print(error(f"Ошибка при загрузке шаблона: {e}"))
            return False

    def fill_template(self, data: Dict[str, Any]) -> str:
        """
        Fill template with data

        Args:
            data: Dictionary with variable values

        Returns:
            Filled template content
        """
        content = self.template_content

        # Replace all {Variable} occurrences with values from data
        def replace_variable(match):
            var_name = match.group(1)
            # Navigate nested dictionary using dot notation
            value = self._get_nested_value(data, var_name)
            return str(value) if value is not None else match.group(0)

        filled_content = re.sub(r"\{([^}]+)\}", replace_variable, content)

        return filled_content

    def fill_from_service(self, service: Service) -> str:
        """
        Fill template from Service object

        Args:
            service: Service object with all data

        Returns:
            Filled template content
        """
        # Build data dictionary from service
        data = {
            # Basic info
            "Название_услуги": service.basic_info.service_name,
            "Категории_получателей": service.basic_info.target_group,
            "Регион": service.basic_info.region,
            "Уровень_квалификации": service.basic_info.provider_type,
            "Дата": service.basic_info.document_date or get_date_string(),
            "Версия": service.basic_info.document_version,
            "ФИО_должность": service.basic_info.responsible_person,
            # Financial parameters
            "Rate_Brut": f"{float(service.financial.brutto_rate):.2f}",
            "KV_ER": f"{float(service.financial.insurance_rates.kv_er):.2f}",
            "KV_Zusatz_ER": f"{float(service.financial.insurance_rates.kv_zusatz_er):.2f}",
            "PV_ER": f"{float(service.financial.insurance_rates.pv_er):.2f}",
            "PV_ER_SN": f"{float(service.financial.insurance_rates.pv_er_sn):.2f}",
            "RV_ER": f"{float(service.financial.insurance_rates.rv_er):.2f}",
            "AV_ER": f"{float(service.financial.insurance_rates.av_er):.2f}",
            "UV_ER": f"{float(service.financial.insurance_rates.uv_er):.2f}",
            "U1": f"{float(service.financial.umlages.u1):.2f}",
            "U2": f"{float(service.financial.umlages.u2):.2f}",
            "U3": f"{float(service.financial.umlages.u3):.2f}",
            # Surcharges
            "Night_Add": f"{float(service.financial.surcharges.night):.0f}",
            "WE_Add": f"{float(service.financial.surcharges.weekend):.0f}",
            "Holiday_Add": f"{float(service.financial.surcharges.holiday):.0f}",
            "Urgent_Add": f"{float(service.financial.surcharges.urgent):.0f}",
            # Materials and admin
            "Materials_pm": f"{float(service.financial.materials_per_month):.2f}",
            "Materials_ph": f"{float(service.financial.materials_per_hour):.2f}",
            "Admin_pct": f"{float(service.financial.admin_percent):.1f}",
            "Admin_ph": f"{float(service.financial.admin_per_hour):.2f}",
            "Region_K": f"{float(service.financial.region_coefficient):.2f}",
            # Funding
            "Eingliederungshilfe": service.funding.payer,
            "Перечень": ", ".join(service.funding.documents) if service.funding.documents else "N/A",
        }

        # Add custom fields
        data.update(service.custom_fields)

        return self.fill_template(data)

    def fill_from_config(self, config_path: str) -> Optional[str]:
        """
        Fill template from configuration file

        Args:
            config_path: Path to YAML/JSON config file

        Returns:
            Filled template content or None if error
        """
        try:
            config = load_config(config_path)

            # Validate config
            validation_result = self.validator.validate_config(config)
            if not validation_result.is_valid:
                print(error("Ошибки в конфигурации:"))
                for err in validation_result.errors:
                    print(f"  - {err}")
                for missing in validation_result.missing_required:
                    print(f"  - Отсутствует обязательное поле: {missing}")
                return None

            # Create service from config
            service = Service.from_dict(config)

            # Fill template
            return self.fill_from_service(service)

        except Exception as e:
            print(error(f"Ошибка при заполнении шаблона: {e}"))
            return None

    def generate_document(self, config_path: str, output_path: str, output_format: str = "txt") -> bool:
        """
        Generate filled document

        Args:
            config_path: Path to configuration file
            output_path: Output file path
            output_format: Output format (txt, html, pdf, docx, md)

        Returns:
            True if successful
        """
        print(header("ГЕНЕРАЦИЯ ДОКУМЕНТА"))

        # Load template
        print(info("Загрузка шаблона..."))
        if not self.load_template():
            return False

        # Fill template
        print(info("Заполнение шаблона из конфигурации..."))
        filled_content = self.fill_from_config(config_path)

        if filled_content is None:
            return False

        print(success("Шаблон успешно заполнен"))

        # Check for unfilled variables
        unfilled = re.findall(r"\{([^}]+)\}", filled_content)
        if unfilled:
            print(warning(f"Обнаружены незаполненные переменные ({len(set(unfilled))}):"))
            for var in list(set(unfilled))[:10]:  # Show first 10
                print(f"  - {var}")
            if len(set(unfilled)) > 10:
                print(f"  ... и еще {len(set(unfilled)) - 10}")

        # Export
        print(info(f"Экспорт в формат {output_format.upper()}..."))

        try:
            if output_format == "txt":
                self.exporter.export_to_text(filled_content, output_path)
            elif output_format == "md" or output_format == "markdown":
                self.exporter.export_to_markdown(filled_content, output_path)
            elif output_format == "html":
                self.exporter.export_to_html(filled_content, output_path)
            elif output_format == "pdf":
                if not self.exporter.export_to_pdf(filled_content, output_path):
                    print(warning("PDF экспорт недоступен (требуется weasyprint). Создан HTML вместо этого."))
                    html_path = output_path.replace(".pdf", ".html")
                    self.exporter.export_to_html(filled_content, html_path)
                    output_path = html_path
            elif output_format == "docx":
                if not self.exporter.export_to_docx(filled_content, output_path):
                    print(warning("DOCX экспорт недоступен (требуется python-docx). Создан TXT вместо этого."))
                    txt_path = output_path.replace(".docx", ".txt")
                    self.exporter.export_to_text(filled_content, txt_path)
                    output_path = txt_path
            else:
                print(error(f"Неподдерживаемый формат: {output_format}"))
                return False

            print(success(f"Документ создан: {output_path}"))
            return True

        except Exception as e:
            print(error(f"Ошибка при экспорте: {e}"))
            return False

    def batch_generate(self, config_dir: str, output_dir: str, output_format: str = "txt") -> int:
        """
        Generate multiple documents from directory of configs

        Args:
            config_dir: Directory with config files
            output_dir: Output directory
            output_format: Output format

        Returns:
            Number of successfully generated documents
        """
        import os

        print(header("ПАКЕТНАЯ ГЕНЕРАЦИЯ ДОКУМЕНТОВ"))

        config_files = []
        for ext in [".yaml", ".yml", ".json"]:
            config_files.extend(Path(config_dir).glob(f"*{ext}"))

        if not config_files:
            print(warning(f"Конфигурационные файлы не найдены в {config_dir}"))
            return 0

        print(info(f"Найдено конфигураций: {len(config_files)}"))

        success_count = 0
        for config_file in config_files:
            print(f"\n{info(f'Обработка: {config_file.name}')}")

            # Generate output filename
            base_name = config_file.stem
            output_file = Path(output_dir) / f"{base_name}.{output_format}"

            if self.generate_document(str(config_file), str(output_file), output_format):
                success_count += 1

        print(f"\n{success(f'Успешно создано документов: {success_count} из {len(config_files)}')}")

        return success_count

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """
        Get value from nested dictionary using dot notation or direct key

        Args:
            data: Dictionary
            key: Key (can contain dots for nesting)

        Returns:
            Value or None
        """
        # Try direct key first
        if key in data:
            return data[key]

        # Try nested with dots
        parts = key.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Генератор документов из шаблонов", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("config", nargs="?", help="Путь к файлу конфигурации (YAML или JSON)")

    parser.add_argument("-o", "--output", help="Путь к выходному файлу")

    parser.add_argument(
        "-f",
        "--format",
        choices=["txt", "md", "html", "pdf", "docx"],
        default="txt",
        help="Формат выходного файла (по умолчанию: txt)",
    )

    parser.add_argument(
        "-t", "--template", default="mSchablone", help="Путь к файлу шаблона (по умолчанию: mSchablone)"
    )

    parser.add_argument("--batch", metavar="DIR", help="Пакетная генерация из директории с конфигурациями")

    parser.add_argument(
        "--output-dir", default="data/exports", help="Директория для выходных файлов при пакетной генерации"
    )

    args = parser.parse_args()

    # Create generator
    generator = DocumentGenerator(args.template)

    if args.batch:
        # Batch mode
        generator.batch_generate(args.batch, args.output_dir, args.format)
    elif args.config:
        # Single file mode
        if not args.output:
            # Auto-generate output filename
            config_name = Path(args.config).stem
            args.output = f"data/exports/{config_name}.{args.format}"

        generator.generate_document(args.config, args.output, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
