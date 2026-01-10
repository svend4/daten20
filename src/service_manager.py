#!/usr/bin/env python3
"""
Service Manager - Менеджер услуг

Управление базой данных услуг: создание, редактирование, поиск, статистика.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import Database
from src.models.service import Service
from src.utils.formatting import (
    header, section, success, error, warning, info,
    table, key_value, colored, bold, divider
)
from src.utils.helpers import load_config, truncate_text


class ServiceManager:
    """Service Manager for database operations"""

    def __init__(self, db_path: str = "data/services.db"):
        """
        Initialize manager

        Args:
            db_path: Path to database file
        """
        self.db = Database(db_path)

    def add_service(self, config_path: str) -> Optional[int]:
        """
        Add service from configuration file

        Args:
            config_path: Path to config file

        Returns:
            Service ID or None
        """
        print(info(f"Загрузка конфигурации: {config_path}"))

        try:
            config = load_config(config_path)
            service = Service.from_dict(config)

            service_id = self.db.create_service(service)

            print(success(f"✓ Услуга создана с ID: {service_id}"))
            return service_id

        except Exception as e:
            print(error(f"Ошибка при создании услуги: {e}"))
            return None

    def list_services(
        self,
        region: Optional[str] = None,
        service_type: Optional[str] = None,
        limit: int = 50
    ) -> None:
        """
        List all services

        Args:
            region: Filter by region
            service_type: Filter by service type
            limit: Maximum number of results
        """
        print(section("СПИСОК УСЛУГ"))

        services = self.db.list_services(limit=limit, region=region, service_type=service_type)

        if not services:
            print(warning("Услуги не найдены"))
            return

        print(info(f"Найдено услуг: {len(services)}"))
        print()

        rows = []
        for service in services:
            service_id = service.id or "N/A"
            name = truncate_text(service.basic_info.service_name, 40)
            target_group = truncate_text(service.basic_info.target_group, 30)
            region_name = service.basic_info.region or "N/A"
            brutto = f"{float(service.financial.brutto_rate):.2f} €"

            rows.append([service_id, name, target_group, region_name, brutto])

        headers = ["ID", "Название", "Целевая группа", "Регион", "Ставка"]
        print(table(headers, rows))
        print()

    def show_service(self, service_id: int, detailed: bool = False) -> None:
        """
        Show service details

        Args:
            service_id: Service ID
            detailed: Show detailed information
        """
        service = self.db.get_service(service_id)

        if not service:
            print(error(f"Услуга с ID {service_id} не найдена"))
            return

        print(section(f"УСЛУГА #{service_id}"))
        print()

        # Basic info
        print(bold("Базовая информация:"))
        print(key_value("  Название", service.basic_info.service_name))
        print(key_value("  Целевая группа", service.basic_info.target_group))
        print(key_value("  Регион", service.basic_info.region))
        print(key_value("  Тип исполнителя", service.basic_info.provider_type))
        print(key_value("  Дата документа", service.basic_info.document_date))
        print(key_value("  Версия", f"{service.version}"))
        print()

        # Financial
        print(bold("Финансовые параметры:"))
        print(key_value("  Ставка брутто", f"{float(service.financial.brutto_rate):.2f} €/ч"))
        print(key_value("  Региональный коэф.", f"{float(service.financial.region_coefficient):.2f}"))
        print(key_value("  Материалы/месяц", f"{float(service.financial.materials_per_month):.2f} €"))
        print(key_value("  Админ расходы", f"{float(service.financial.admin_percent):.1f}%"))
        print()

        # System settings
        print(bold("Системные настройки:"))
        calc_mode = "С умлагами (U1/U2/U3)" if service.system_settings.use_umlages else "С резервом отпуск/больничные"
        print(key_value("  Режим расчета", calc_mode))
        print(key_value("  Тип услуги", service.system_settings.service_type))
        print()

        # Funding
        print(bold("Финансирование:"))
        print(key_value("  Плательщик", service.funding.payer))
        if service.funding.documents:
            print(key_value("  Документы", ", ".join(service.funding.documents)))
        print()

        # Metadata
        if service.created_at:
            print(key_value("Создано", service.created_at.strftime("%d.%m.%Y %H:%M")))
        if service.updated_at:
            print(key_value("Обновлено", service.updated_at.strftime("%d.%m.%Y %H:%M")))
        print()

        # Show versions if requested
        if detailed:
            versions = self.db.get_service_versions(service_id)
            if versions:
                print(bold("История версий:"))
                for ver in versions:
                    print(f"  v{ver['version']} - {ver['created_at']} - {ver['notes']}")
                print()

    def search(self, query: str) -> None:
        """
        Search services

        Args:
            query: Search query
        """
        print(section(f"ПОИСК: '{query}'"))

        services = self.db.search_services(query)

        if not services:
            print(warning("Ничего не найдено"))
            return

        print(success(f"Найдено: {len(services)} услуг"))
        print()

        rows = []
        for service in services:
            service_id = service.id or "N/A"
            name = truncate_text(service.basic_info.service_name, 50)
            target_group = truncate_text(service.basic_info.target_group, 40)

            rows.append([service_id, name, target_group])

        headers = ["ID", "Название", "Целевая группа"]
        print(table(headers, rows))
        print()

    def delete_service(self, service_id: int, confirm: bool = True) -> bool:
        """
        Delete service

        Args:
            service_id: Service ID
            confirm: Ask for confirmation

        Returns:
            True if deleted
        """
        service = self.db.get_service(service_id)

        if not service:
            print(error(f"Услуга с ID {service_id} не найдена"))
            return False

        if confirm:
            print(warning(f"Удаление услуги: {service.basic_info.service_name}"))
            response = input("Вы уверены? (yes/no): ").strip().lower()

            if response not in ['yes', 'y', 'да', 'д']:
                print(info("Отменено"))
                return False

        if self.db.delete_service(service_id):
            print(success(f"✓ Услуга #{service_id} удалена"))
            return True
        else:
            print(error("Ошибка при удалении"))
            return False

    def show_statistics(self) -> None:
        """Show database statistics"""
        print(section("СТАТИСТИКА БАЗЫ ДАННЫХ"))

        stats = self.db.get_statistics()

        print(key_value("Всего услуг", str(stats['total_services'])))
        print(key_value("Средняя ставка брутто", f"{stats['avg_brutto_rate']:.2f} €/ч"))
        print()

        # By region
        if stats['by_region']:
            print(bold("Услуг по регионам:"))
            for region, count in sorted(stats['by_region'].items()):
                region_name = region if region else "Не указан"
                print(key_value(f"  {region_name}", str(count)))
            print()

        # By type
        if stats['by_type']:
            print(bold("Услуг по типам:"))
            type_names = {
                "domestic": "Домашние услуги",
                "social": "Социальные услуги",
                "medical": "Медицинские услуги",
                "professional": "Профессиональные услуги",
                "educational": "Образовательные услуги"
            }
            for stype, count in sorted(stats['by_type'].items()):
                type_name = type_names.get(stype, stype)
                print(key_value(f"  {type_name}", str(count)))
            print()

    def export_service(self, service_id: int, output_path: str) -> bool:
        """
        Export service configuration

        Args:
            service_id: Service ID
            output_path: Output file path

        Returns:
            True if successful
        """
        service = self.db.get_service(service_id)

        if not service:
            print(error(f"Услуга с ID {service_id} не найдена"))
            return False

        try:
            from src.utils.helpers import save_config
            save_config(service.to_dict(), output_path)
            print(success(f"✓ Конфигурация экспортирована: {output_path}"))
            return True
        except Exception as e:
            print(error(f"Ошибка при экспорте: {e}"))
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Менеджер услуг - управление базой данных",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--db",
        default="data/services.db",
        help="Путь к файлу базы данных"
    )

    subparsers = parser.add_subparsers(dest="command", help="Команда")

    # Add command
    add_parser = subparsers.add_parser("add", help="Добавить услугу")
    add_parser.add_argument("config", help="Путь к файлу конфигурации")

    # List command
    list_parser = subparsers.add_parser("list", help="Список услуг")
    list_parser.add_argument("--region", help="Фильтр по региону")
    list_parser.add_argument("--type", help="Фильтр по типу")
    list_parser.add_argument("--limit", type=int, default=50, help="Лимит результатов")

    # Show command
    show_parser = subparsers.add_parser("show", help="Показать услугу")
    show_parser.add_argument("id", type=int, help="ID услуги")
    show_parser.add_argument("--detailed", action="store_true", help="Подробная информация")

    # Search command
    search_parser = subparsers.add_parser("search", help="Поиск услуг")
    search_parser.add_argument("query", help="Поисковый запрос")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Удалить услугу")
    delete_parser.add_argument("id", type=int, help="ID услуги")
    delete_parser.add_argument("--force", action="store_true", help="Без подтверждения")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Статистика")

    # Export command
    export_parser = subparsers.add_parser("export", help="Экспорт конфигурации")
    export_parser.add_argument("id", type=int, help="ID услуги")
    export_parser.add_argument("output", help="Путь к выходному файлу")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create manager
    manager = ServiceManager(args.db)

    print(header("МЕНЕДЖЕР УСЛУГ"))

    # Execute command
    if args.command == "add":
        manager.add_service(args.config)

    elif args.command == "list":
        manager.list_services(region=args.region, service_type=args.type, limit=args.limit)

    elif args.command == "show":
        manager.show_service(args.id, args.detailed)

    elif args.command == "search":
        manager.search(args.query)

    elif args.command == "delete":
        manager.delete_service(args.id, confirm=not args.force)

    elif args.command == "stats":
        manager.show_statistics()

    elif args.command == "export":
        manager.export_service(args.id, args.output)


if __name__ == "__main__":
    main()
