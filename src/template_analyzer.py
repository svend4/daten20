#!/usr/bin/env python3
"""
Template Analyzer - Анализатор структуры шаблонов

Парсинг, анализ и валидация мега-шаблона интегрированного
профессионального планирования услуг персонального бюджета.

Улучшения v1.0.1:
- Добавлено кэширование результатов парсинга
- Добавлена поддержка YAML/JSON шаблонов
- Улучшена производительность
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cache import cached, get_cache_manager
from src.core.parser import TemplateParser
from src.core.validator import TemplateValidator
from src.utils.formatting import (
    bold,
    colored,
    divider,
    error,
    header,
    info,
    key_value,
    section,
    success,
    table,
    warning,
)
from src.utils.helpers import format_currency, truncate_text

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class TemplateAnalyzer:
    """Main Template Analyzer class with caching support"""

    def __init__(self, template_path: str, enable_cache: bool = True):
        """
        Initialize analyzer

        Args:
            template_path: Path to template file
            enable_cache: Enable caching of results (default: True)
        """
        self.template_path = template_path
        self.parser = TemplateParser(template_path)
        self.validator = TemplateValidator()
        self.structure = None
        self.enable_cache = enable_cache

        # Initialize cache if enabled
        if enable_cache:
            self.cache = get_cache_manager()
        else:
            self.cache = None

    def _get_template_hash(self) -> str:
        """Generate hash of template file for cache key"""
        try:
            with open(self.template_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return hashlib.md5(self.template_path.encode()).hexdigest()

    def analyze(self) -> None:
        """Perform complete analysis with caching"""
        print(header("АНАЛИЗ ШАБЛОНА ДОКУМЕНТА"))

        # Check if template is YAML/JSON
        file_ext = Path(self.template_path).suffix.lower()
        if file_ext in ['.yaml', '.yml', '.json']:
            print(info(f"Обнаружен {file_ext} формат, загрузка..."))
            try:
                self.structure = self._load_structured_template()
                print(success(f"Шаблон успешно загружен из {file_ext}"))
                return
            except Exception as e:
                print(error(f"Ошибка при загрузке {file_ext}: {e}"))
                return

        # Try to get from cache
        cache_key = f"template_structure:{self._get_template_hash()}"
        if self.enable_cache and self.cache:
            cached_structure = self.cache.get(cache_key)
            if cached_structure is not None:
                self.structure = cached_structure
                print(success(f"Шаблон загружен из кэша ({self.structure.total_lines} строк) ⚡"))
                print()
                return

        print(info("Загрузка и парсинг шаблона..."))
        try:
            self.structure = self.parser.parse()

            # Cache the result
            if self.enable_cache and self.cache:
                self.cache.set(cache_key, self.structure, timeout=3600)  # 1 hour

            print(success(f"Шаблон успешно загружен ({self.structure.total_lines} строк)"))
        except Exception as e:
            print(error(f"Ошибка при загрузке шаблона: {e}"))
            return

        print()

    def _load_structured_template(self):
        """Load template from YAML or JSON file"""
        file_ext = Path(self.template_path).suffix.lower()

        with open(self.template_path, 'r', encoding='utf-8') as f:
            if file_ext == '.json':
                data = json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise RuntimeError("PyYAML not installed. Install with: pip install pyyaml")
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {file_ext}")

        # Convert to TemplateStructure
        from src.models.template import TemplateStructure, Block, Variable

        structure = TemplateStructure()
        structure.metadata = data.get('metadata', {})
        structure.total_lines = data.get('total_lines', 0)

        # Load blocks
        blocks = []
        for block_data in data.get('blocks', []):
            block = Block(
                id=block_data.get('id', 0),
                title=block_data.get('title', ''),
                description=block_data.get('description', '')
            )

            # Load variables
            for var_name in block_data.get('variables', []):
                var = Variable(name=var_name, block_id=block.id)
                block.variables.append(var)

            blocks.append(block)

        structure.blocks = blocks
        structure.total_blocks = len(blocks)
        structure.all_variables = [var for block in blocks for var in block.variables]
        structure.total_variables = len(structure.all_variables)

        return structure

    def show_summary(self) -> None:
        """Show template summary"""
        if self.structure is None:
            print(error("Шаблон не загружен. Сначала выполните analyze()"))
            return

        print(section("ОБЩАЯ ИНФОРМАЦИЯ"))

        print(key_value("Название", self.structure.metadata.get("title", "N/A")))
        print(key_value("Всего строк", str(self.structure.total_lines)))
        print(key_value("Всего блоков", str(self.structure.total_blocks)))
        print(key_value("Всего разделов", str(self.structure.total_sections)))
        print(key_value("Всего переменных", str(self.structure.total_variables)))

        unique_vars = len(set(var.name for var in self.structure.all_variables))
        print(key_value("Уникальных переменных", str(unique_vars)))

        print()

    def show_blocks(self) -> None:
        """Show all blocks"""
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        print(section("СТРУКТУРА БЛОКОВ"))

        rows = []
        for block in self.structure.blocks:
            block_title = f"Блок {block.id}" if block.id > 0 else "Блок 0"
            title_short = truncate_text(block.title, 60)
            sections = str(len(block.sections))
            variables = str(len(block.variables))

            rows.append([block_title, title_short, sections, variables])

        headers = ["ID", "Название", "Разделы", "Переменные"]
        print(table(headers, rows))
        print()

    def show_variables(self, block_id: Optional[int] = None, limit: int = 50) -> None:
        """
        Show variables

        Args:
            block_id: Show only variables from specific block (None for all)
            limit: Maximum number of variables to show
        """
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        if block_id is not None:
            print(section(f"ПЕРЕМЕННЫЕ БЛОКА {block_id}"))
            variables = self.parser.get_variables_by_block(block_id)
        else:
            print(section("ВСЕ ПЕРЕМЕННЫЕ"))
            variables = self.structure.all_variables

        if not variables:
            print(warning("Переменные не найдены"))
            return

        print(info(f"Найдено переменных: {len(variables)}"))

        if len(variables) > limit:
            print(warning(f"Показаны первые {limit} из {len(variables)}"))
            variables = variables[:limit]

        rows = []
        for var in variables:
            block = f"Блок {var.block_id}" if var.block_id is not None else "N/A"
            section_id = var.section if var.section else "N/A"
            rows.append([var.name, block, section_id])

        headers = ["Переменная", "Блок", "Раздел"]
        print(table(headers, rows))
        print()

    def show_statistics(self) -> None:
        """Show detailed statistics"""
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        stats = self.parser.get_statistics()

        print(section("ДЕТАЛЬНАЯ СТАТИСТИКА"))

        print(bold("Общие показатели:"))
        print(key_value("  Строк", f"{stats.total_lines:,}".replace(",", " ")))
        print(key_value("  Символов", f"{stats.total_characters:,}".replace(",", " ")))
        print(key_value("  Блоков", str(stats.total_blocks)))
        print(key_value("  Разделов", str(stats.total_sections)))
        print(key_value("  Переменных", str(stats.total_variables)))
        print(key_value("  Уникальных переменных", str(stats.unique_variables)))
        print()

        print(bold("Переменные по блокам:"))
        for block_id, count in stats.variables_by_block.items():
            block_name = f"Блок {block_id}"
            print(key_value(f"  {block_name}", str(count)))
        print()

    def show_block_content(self, block_id: int, lines: int = 50) -> None:
        """
        Show content of specific block

        Args:
            block_id: Block ID to show
            lines: Maximum number of lines to show
        """
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        block = self.structure.get_block(block_id)
        if block is None:
            print(error(f"Блок {block_id} не найден"))
            return

        print(section(f"БЛОК {block_id}: {block.title}"))

        content = self.parser.get_block_content(block_id)
        content_lines = content.split("\n")

        if len(content_lines) > lines:
            print(warning(f"Показаны первые {lines} строк из {len(content_lines)}"))
            content_lines = content_lines[:lines]

        for line in content_lines:
            print(line)

        print()

    def search(self, query: str, case_sensitive: bool = False) -> None:
        """
        Search in template with caching

        Args:
            query: Search query
            case_sensitive: Case-sensitive search
        """
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        print(section(f"ПОИСК: '{query}'"))

        # Try cache first
        cache_key = f"search:{self._get_template_hash()}:{query}:{case_sensitive}"
        if self.enable_cache and self.cache:
            results = self.cache.get(cache_key)
            if results is not None:
                print(info("(из кэша) ⚡"))
            else:
                results = self.parser.search_content(query, case_sensitive)
                self.cache.set(cache_key, results, timeout=1800)  # 30 minutes
        else:
            results = self.parser.search_content(query, case_sensitive)

        if not results:
            print(warning("Ничего не найдено"))
            return

        print(success(f"Найдено совпадений: {len(results)}"))
        print()

        for line_num, line_content in results[:100]:  # Limit to 100 results
            line_preview = truncate_text(line_content, 100)
            print(f"{colored(f'Строка {line_num}:', 'cyan')} {line_preview}")

        if len(results) > 100:
            print()
            print(warning(f"Показаны первые 100 результатов из {len(results)}"))

        print()

    def export_structure(self, output_file: str, format: str = 'auto') -> None:
        """
        Export structure to JSON or YAML file

        Args:
            output_file: Output file path
            format: Output format ('json', 'yaml', 'auto')
                   'auto' detects from file extension
        """
        if self.structure is None:
            print(error("Шаблон не загружен"))
            return

        # Auto-detect format from extension
        if format == 'auto':
            ext = Path(output_file).suffix.lower()
            if ext in ['.yaml', '.yml']:
                format = 'yaml'
            else:
                format = 'json'

        data = {
            "metadata": self.structure.metadata,
            "statistics": {
                "total_lines": self.structure.total_lines,
                "total_blocks": self.structure.total_blocks,
                "total_sections": self.structure.total_sections,
                "total_variables": self.structure.total_variables,
            },
            "blocks": [
                {
                    "id": block.id,
                    "title": block.title,
                    "sections_count": len(block.sections),
                    "variables_count": len(block.variables),
                    "variables": [var.name for var in block.variables],
                }
                for block in self.structure.blocks
            ],
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if format == 'yaml':
                    if not YAML_AVAILABLE:
                        print(error("PyYAML не установлен. Установите: pip install pyyaml"))
                        return
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            print(success(f"Структура экспортирована в {output_file} ({format.upper()})"))
        except Exception as e:
            print(error(f"Ошибка при экспорте: {e}"))

    def get_cache_stats(self) -> None:
        """Show cache statistics"""
        if not self.enable_cache or not self.cache:
            print(warning("Кэширование отключено"))
            return

        stats = self.cache.get_stats()
        print(section("СТАТИСТИКА КЭША"))
        print(key_value("Бэкенд", stats['backend']))
        print(key_value("Попаданий", str(stats['hits'])))
        print(key_value("Промахов", str(stats['misses'])))
        print(key_value("Всего запросов", str(stats['total_requests'])))
        print(key_value("Процент попаданий", f"{stats['hit_rate']}%"))
        print()

    def clear_cache(self) -> None:
        """Clear analyzer cache"""
        if not self.enable_cache or not self.cache:
            print(warning("Кэширование отключено"))
            return

        self.cache.clear()
        print(success("Кэш очищен"))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Анализатор структуры шаблона документов (v1.0.1 с кэшированием)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "template", nargs="?", default="mSchablone",
        help="Путь к файлу шаблона (поддержка: .txt, .json, .yaml, .yml)"
    )

    parser.add_argument("--blocks", action="store_true", help="Показать список всех блоков")

    parser.add_argument("--variables", action="store_true", help="Показать все переменные")

    parser.add_argument("--block", type=int, metavar="ID", help="Показать содержимое блока по ID")

    parser.add_argument("--block-vars", type=int, metavar="ID", help="Показать переменные конкретного блока")

    parser.add_argument("--stats", action="store_true", help="Показать детальную статистику")

    parser.add_argument("--search", metavar="QUERY", help="Поиск текста в шаблоне")

    parser.add_argument("--case-sensitive", action="store_true", help="Регистрозависимый поиск")

    parser.add_argument("--export", metavar="FILE", help="Экспортировать структуру в JSON/YAML")

    parser.add_argument("--export-format", choices=['json', 'yaml', 'auto'], default='auto',
                       help="Формат экспорта (по умолчанию: auto)")

    parser.add_argument("--all", action="store_true", help="Показать всю информацию")

    # Cache options
    parser.add_argument("--no-cache", action="store_true", help="Отключить кэширование")

    parser.add_argument("--cache-stats", action="store_true", help="Показать статистику кэша")

    parser.add_argument("--clear-cache", action="store_true", help="Очистить кэш")

    args = parser.parse_args()

    # Create analyzer
    analyzer = TemplateAnalyzer(args.template, enable_cache=not args.no_cache)

    # Handle cache-only commands
    if args.clear_cache:
        analyzer.clear_cache()
        return

    if args.cache_stats:
        analyzer.get_cache_stats()
        if not any([args.blocks, args.variables, args.block, args.block_vars,
                   args.stats, args.search, args.export, args.all]):
            return

    # Analyze template
    analyzer.analyze()

    # Show requested information
    if args.all or (
        not any([args.blocks, args.variables, args.block, args.block_vars,
                args.stats, args.search, args.export, args.cache_stats])
    ):
        analyzer.show_summary()
        analyzer.show_blocks()

    if args.blocks or args.all:
        analyzer.show_blocks()

    if args.variables or args.all:
        analyzer.show_variables()

    if args.stats or args.all:
        analyzer.show_statistics()

    if args.block is not None:
        analyzer.show_block_content(args.block)

    if args.block_vars is not None:
        analyzer.show_variables(block_id=args.block_vars)

    if args.search:
        analyzer.search(args.search, args.case_sensitive)

    if args.export:
        analyzer.export_structure(args.export, format=args.export_format)

    # Show cache stats at the end if requested
    if args.cache_stats and not args.clear_cache:
        analyzer.get_cache_stats()


if __name__ == "__main__":
    main()
