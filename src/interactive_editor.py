#!/usr/bin/env python3
"""
Interactive Editor - Интерактивный редактор

Пошаговое заполнение шаблона с валидацией и подсказками.
"""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.validator import TemplateValidator
from src.document_generator import DocumentGenerator
from src.financial_calculator import FinancialCalculator
from src.models.financial import FinancialParameters
from src.models.service import BasicInfo, Funding, Service, SystemSettings
from src.utils.constants import (
    DEFAULT_INSURANCE_RATES,
    DEFAULT_SURCHARGES,
    DEFAULT_UMLAGES,
    FUNDING_SOURCES,
    REGIONAL_COEFFICIENTS,
    SERVICE_TYPES,
)
from src.utils.formatting import (
    bold,
    colored,
    divider,
    error,
    header,
    info,
    key_value,
    progress_bar,
    section,
    success,
    title_box,
    warning,
)
from src.utils.helpers import get_date_string, parse_number, save_config, validate_date, validate_email, validate_phone


class InteractiveEditor:
    """Interactive template editor"""

    def __init__(self):
        """Initialize editor"""
        self.service = Service()
        self.validator = TemplateValidator()
        self.calculator = FinancialCalculator()
        self.generator = DocumentGenerator()
        self.current_section = 0
        self.total_sections = 5

    def start(self) -> Service:
        """
        Start interactive session

        Returns:
            Filled Service object
        """
        print(title_box("ИНТЕРАКТИВНЫЙ РЕДАКТОР ШАБЛОНА"))
        print()
        print(info("Пошаговое заполнение шаблона документа"))
        print(info("Нажмите Ctrl+C для выхода в любой момент"))
        print()

        try:
            # Section 1: Basic Information
            self._edit_basic_info()

            # Section 2: Financial Parameters
            self._edit_financial_parameters()

            # Section 3: System Settings
            self._edit_system_settings()

            # Section 4: Funding Information
            self._edit_funding()

            # Section 5: Additional Fields
            self._edit_additional_fields()

            # Summary and confirmation
            self._show_summary()

            return self.service

        except KeyboardInterrupt:
            print()
            print(warning("\nРедактирование прервано"))
            return None

    def _edit_basic_info(self) -> None:
        """Edit basic service information"""
        self.current_section = 1
        print(section(f"[{self.current_section}/{self.total_sections}] БАЗОВАЯ ИНФОРМАЦИЯ"))
        print()

        self.service.basic_info.service_name = self._prompt(
            "Название услуги", "Например: Сопровождение в магазин", required=True
        )

        self.service.basic_info.target_group = self._prompt(
            "Целевая группа", "Например: Люди с ограниченной мобильностью", required=True
        )

        self.service.basic_info.region = self._prompt_choice(
            "Регион/земля", list(REGIONAL_COEFFICIENTS.keys()), required=True
        )

        self.service.basic_info.provider_type = self._prompt(
            "Тип исполнителя/квалификация", "Например: Квалифицированный ассистент"
        )

        self.service.basic_info.document_date = self._prompt(
            "Дата создания карточки",
            f"Формат: ДД.ММ.ГГГГ (по умолчанию: {get_date_string()})",
            default=get_date_string(),
            validator=validate_date,
        )

        self.service.basic_info.document_version = self._prompt("Версия документа", "По умолчанию: 1.0", default="1.0")

        self.service.basic_info.responsible_person = self._prompt("Ответственный за актуализацию", "ФИО и должность")

        print(success("✓ Базовая информация заполнена"))
        print()

    def _edit_financial_parameters(self) -> None:
        """Edit financial parameters"""
        self.current_section = 2
        print(section(f"[{self.current_section}/{self.total_sections}] ФИНАНСОВЫЕ ПАРАМЕТРЫ"))
        print()

        # Brutto rate
        brutto = self._prompt_number(
            "Ставка брутто €/ч", "Почасовая ставка до отчислений", required=True, min_value=0.0
        )
        self.service.financial.brutto_rate = Decimal(str(brutto))

        # Insurance rates
        print()
        print(bold("Социальные отчисления работодателя (в процентах):"))
        use_defaults = self._prompt_yes_no("Использовать значения по умолчанию?", default=True)

        if not use_defaults:
            rates = self.service.financial.insurance_rates
            rates.kv_er = Decimal(str(self._prompt_number("KV (Krankenversicherung)", default=7.3)))
            rates.kv_zusatz_er = Decimal(str(self._prompt_number("½ Zusatz", default=0.8)))

            is_saxony = self.service.basic_info.region == "Sachsen"
            if is_saxony:
                rates.pv_er_sn = Decimal(str(self._prompt_number("PV для Саксонии", default=2.025)))
            else:
                rates.pv_er = Decimal(str(self._prompt_number("PV (Pflegeversicherung)", default=1.525)))

            rates.rv_er = Decimal(str(self._prompt_number("RV (Rentenversicherung)", default=9.3)))
            rates.av_er = Decimal(str(self._prompt_number("AV (Arbeitslosenversicherung)", default=1.2)))
            rates.uv_er = Decimal(str(self._prompt_number("UV (Unfallversicherung)", default=1.3)))

        # Umlages
        print()
        print(bold("Умлаги (Umlages) в процентах:"))
        use_default_umlages = self._prompt_yes_no("Использовать значения по умолчанию?", default=True)

        if not use_default_umlages:
            uml = self.service.financial.umlages
            uml.u1 = Decimal(str(self._prompt_number("U1 (Krankheit)", default=0.9)))
            uml.u2 = Decimal(str(self._prompt_number("U2 (Mutterschaft)", default=0.4)))
            uml.u3 = Decimal(str(self._prompt_number("U3 (Insolvenz)", default=0.09)))

        # Surcharges
        print()
        print(bold("Надбавки (в процентах):"))
        edit_surcharges = self._prompt_yes_no("Изменить надбавки?", default=False)

        if edit_surcharges:
            sur = self.service.financial.surcharges
            sur.night = Decimal(str(self._prompt_number("Ночная работа %", default=25)))
            sur.weekend = Decimal(str(self._prompt_number("Выходные дни %", default=50)))
            sur.holiday = Decimal(str(self._prompt_number("Праздничные дни %", default=100)))
            sur.urgent = Decimal(str(self._prompt_number("Срочность %", default=15)))

        # Materials and admin
        print()
        print(bold("Материалы и административные расходы:"))

        materials_month = self._prompt_number("Материалы/проезд/связь €/месяц", default=0.0)
        self.service.financial.materials_per_month = Decimal(str(materials_month))

        admin_pct = self._prompt_number("Административные затраты %", "Процент от фонда оплаты", default=5.0)
        self.service.financial.admin_percent = Decimal(str(admin_pct))

        # Regional coefficient
        print()
        region_coef = REGIONAL_COEFFICIENTS.get(self.service.basic_info.region, 1.0)
        print(info(f"Региональный коэффициент для {self.service.basic_info.region}: {region_coef}"))

        custom_coef = self._prompt_yes_no("Использовать другой коэффициент?", default=False)

        if custom_coef:
            region_coef = self._prompt_number(
                "Региональный коэффициент", default=region_coef, min_value=0.5, max_value=3.0
            )

        self.service.financial.region_coefficient = Decimal(str(region_coef))
        self.service.financial.is_saxony = self.service.basic_info.region == "Sachsen"

        print(success("✓ Финансовые параметры заполнены"))
        print()

        # Show quick calculation
        print(info("Предварительный расчет стоимости часа:"))
        breakdown = self.calculator.calculate_hourly_rate(self.service.financial)
        print(key_value("  Итоговая ставка", f"{float(breakdown.final_hourly_rate):.2f} €/ч"))
        print()

    def _edit_system_settings(self) -> None:
        """Edit system settings"""
        self.current_section = 3
        print(section(f"[{self.current_section}/{self.total_sections}] СИСТЕМНЫЕ НАСТРОЙКИ"))
        print()

        # Calculation mode
        print(bold("Режим социальных выплат:"))
        use_umlages = self._prompt_yes_no(
            "Использовать U-умлаги (U1/U2/U3)?", info_text="Альтернатива: резерв на отпуск/больничные", default=True
        )

        self.service.system_settings.use_umlages = use_umlages
        self.service.system_settings.use_vacation_reserve = not use_umlages
        self.service.financial.use_umlages = use_umlages
        self.service.financial.use_vacation_reserve = not use_umlages

        # Surcharge base
        print()
        print(bold("База применения надбавок:"))
        print("1. К полной стоимости часа (включая накладные)")
        print("2. К ставке брутто (без материалов/админа)")

        surcharge_base_choice = self._prompt_choice("Выберите базу", ["1", "2"], default="1")

        self.service.system_settings.surcharge_base = "full_cost" if surcharge_base_choice == "1" else "brutto_only"
        self.service.financial.surcharge_base = self.service.system_settings.surcharge_base

        # Service type
        print()
        print(bold("Тип услуги:"))
        for i, (key, desc) in enumerate(SERVICE_TYPES.items(), 1):
            print(f"{i}. {desc}")

        service_type_idx = self._prompt_choice(
            "Выберите тип услуги", [str(i) for i in range(1, len(SERVICE_TYPES) + 1)], default="2"
        )

        service_types_list = list(SERVICE_TYPES.keys())
        self.service.system_settings.service_type = service_types_list[int(service_type_idx) - 1]

        print(success("✓ Системные настройки заполнены"))
        print()

    def _edit_funding(self) -> None:
        """Edit funding information"""
        self.current_section = 4
        print(section(f"[{self.current_section}/{self.total_sections}] ИСТОЧНИКИ ФИНАНСИРОВАНИЯ"))
        print()

        print(bold("Доступные источники:"))
        for i, source in enumerate(FUNDING_SOURCES, 1):
            print(f"{i}. {source}")

        payer_idx = self._prompt_choice("Плательщик", [str(i) for i in range(1, len(FUNDING_SOURCES) + 1)], default="1")

        self.service.funding.payer = FUNDING_SOURCES[int(payer_idx) - 1]

        # Documents
        print()
        print(info("Документы-основания (введите по одному, пустая строка для завершения):"))

        documents = []
        while True:
            doc = input(f"  Документ {len(documents) + 1}: ").strip()
            if not doc:
                break
            documents.append(doc)

        self.service.funding.documents = documents

        print(success("✓ Информация о финансировании заполнена"))
        print()

    def _edit_additional_fields(self) -> None:
        """Edit additional custom fields"""
        self.current_section = 5
        print(section(f"[{self.current_section}/{self.total_sections}] ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ"))
        print()

        add_custom = self._prompt_yes_no("Добавить дополнительные поля?", default=False)

        if add_custom:
            print(info("Введите пары ключ=значение (пустая строка для завершения):"))
            while True:
                field = input("  Поле: ").strip()
                if not field:
                    break

                if "=" in field:
                    key, value = field.split("=", 1)
                    self.service.custom_fields[key.strip()] = value.strip()
                else:
                    value = input(f"  Значение для '{field}': ").strip()
                    self.service.custom_fields[field] = value

        print(success("✓ Все разделы заполнены"))
        print()

    def _show_summary(self) -> None:
        """Show summary and save options"""
        print(divider("="))
        print(section("ИТОГОВАЯ ИНФОРМАЦИЯ"))

        print(bold("Услуга:"))
        print(key_value("  Название", self.service.basic_info.service_name))
        print(key_value("  Целевая группа", self.service.basic_info.target_group))
        print(key_value("  Регион", self.service.basic_info.region))
        print()

        print(bold("Финансы:"))
        print(key_value("  Ставка брутто", f"{float(self.service.financial.brutto_rate):.2f} €/ч"))

        # Calculate final rate
        breakdown = self.calculator.calculate_hourly_rate(self.service.financial)
        print(key_value("  Итоговая ставка", f"{float(breakdown.final_hourly_rate):.2f} €/ч", 25))
        print()

        # Validation
        print(info("Проверка данных..."))
        validation = self.validator.validate_config(self.service.to_dict())

        if validation.is_valid:
            print(success("✓ Все данные корректны"))
        else:
            print(warning("⚠ Обнаружены предупреждения:"))
            for warn in validation.warnings:
                print(f"  - {warn}")

        print()

        # Save options
        save_config_ask = self._prompt_yes_no("Сохранить конфигурацию?", default=True)

        if save_config_ask:
            default_filename = f"config/service_{self.service.basic_info.service_name.replace(' ', '_')}.yaml"
            filename = self._prompt("Имя файла", default=default_filename)

            try:
                save_config(self.service.to_dict(), filename)
                print(success(f"✓ Конфигурация сохранена: {filename}"))
            except Exception as e:
                print(error(f"Ошибка при сохранении: {e}"))

        # Generate document
        print()
        generate_doc = self._prompt_yes_no("Сгенерировать документ сейчас?", default=True)

        if generate_doc:
            self._generate_document()

    def _generate_document(self) -> None:
        """Generate document from current service"""
        print()
        print(info("Генерация документа..."))

        format_choice = self._prompt_choice("Формат выходного файла", ["txt", "html", "md"], default="html")

        default_filename = f"data/exports/{self.service.basic_info.service_name.replace(' ', '_')}.{format_choice}"
        filename = self._prompt("Имя файла", default=default_filename)

        try:
            # Generate
            if not self.generator.load_template():
                return

            filled_content = self.generator.fill_from_service(self.service)

            if format_choice == "txt":
                self.generator.exporter.export_to_text(filled_content, filename)
            elif format_choice == "html":
                self.generator.exporter.export_to_html(filled_content, filename, self.service.basic_info.service_name)
            elif format_choice == "md":
                self.generator.exporter.export_to_markdown(filled_content, filename)

            print(success(f"✓ Документ создан: {filename}"))

        except Exception as e:
            print(error(f"Ошибка при генерации: {e}"))

    def _prompt(
        self, field_name: str, hint: str = "", default: str = "", required: bool = False, validator=None
    ) -> str:
        """
        Prompt for text input

        Args:
            field_name: Name of field
            hint: Help text
            default: Default value
            required: Is required
            validator: Validation function

        Returns:
            User input
        """
        while True:
            if hint:
                print(colored(f"  {hint}", "cyan"))

            prompt_text = f"{bold(field_name)}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "

            value = input(prompt_text).strip()

            if not value and default:
                value = default

            if required and not value:
                print(error("  ✗ Это поле обязательно"))
                continue

            if validator and value:
                if not validator(value):
                    print(error("  ✗ Неверный формат"))
                    continue

            return value

    def _prompt_number(
        self,
        field_name: str,
        hint: str = "",
        default: float = None,
        required: bool = False,
        min_value: float = None,
        max_value: float = None,
    ) -> float:
        """Prompt for number input"""
        while True:
            default_str = f"{default:.2f}" if default is not None else ""
            value_str = self._prompt(field_name, hint, default_str, required)

            if not value_str and not required:
                return default if default is not None else 0.0

            num = parse_number(value_str)
            if num is None:
                print(error("  ✗ Введите корректное число"))
                continue

            if min_value is not None and num < min_value:
                print(error(f"  ✗ Значение должно быть >= {min_value}"))
                continue

            if max_value is not None and num > max_value:
                print(error(f"  ✗ Значение должно быть <= {max_value}"))
                continue

            return num

    def _prompt_yes_no(self, question: str, default: bool = True, info_text: str = "") -> bool:
        """Prompt for yes/no"""
        if info_text:
            print(colored(f"  {info_text}", "cyan"))

        default_str = "Y/n" if default else "y/N"
        response = input(f"{bold(question)} [{default_str}]: ").strip().lower()

        if not response:
            return default

        return response in ["y", "yes", "да", "д"]

    def _prompt_choice(self, field_name: str, choices: List[str], default: str = None, required: bool = False) -> str:
        """Prompt for choice from list"""
        while True:
            value = self._prompt(field_name, "", default or "", required)

            if value in choices:
                return value

            print(error(f"  ✗ Выберите один из: {', '.join(choices)}"))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Интерактивный редактор шаблонов", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    args = parser.parse_args()

    # Create and start editor
    editor = InteractiveEditor()
    service = editor.start()

    if service:
        print()
        print(success("Редактирование завершено успешно!"))
    else:
        print()
        print(warning("Редактирование не завершено"))


if __name__ == "__main__":
    main()
