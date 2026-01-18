"""
Comprehensive tests for core.parser module
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestTemplateParserInitialization:
    """Tests for TemplateParser initialization"""

    def test_parser_initialization_without_path(self):
        """Test parser can be initialized without template path"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        assert parser is not None
        assert parser.template_path is None
        assert parser.lines == []
        assert parser.structure is None

    def test_parser_initialization_with_path(self):
        """Test parser initialization with template path"""
        from src.core.parser import TemplateParser

        parser = TemplateParser(template_path="/path/to/template.txt")
        assert parser.template_path == "/path/to/template.txt"
        assert parser.lines == []


class TestTemplateParserLoad:
    """Tests for template loading"""

    @pytest.fixture
    def sample_template_file(self, tmp_path):
        """Create a sample template file"""
        template_path = tmp_path / "template.txt"
        content = """MEGA-TEMPLATE TEST

0. ПАСПОРТ услуги

Service Name: {{service_name}}
Region: {{region}}

---

БЛОК I: Основная информация

Description: {{description}}
Target Group: {{target_group}}
"""
        template_path.write_text(content, encoding="utf-8")
        return str(template_path)

    def test_load_template(self, sample_template_file):
        """Test loading template file"""
        from src.core.parser import TemplateParser

        parser = TemplateParser(template_path=sample_template_file)
        parser.load()

        assert len(parser.lines) > 0
        assert "MEGA-TEMPLATE" in parser.lines[0]

    def test_load_without_path_raises_error(self):
        """Test loading without template path raises error"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()

        with pytest.raises(ValueError, match="no template_path"):
            parser.load()


class TestTemplateParserParse:
    """Tests for template parsing"""

    @pytest.fixture
    def template_with_blocks(self, tmp_path):
        """Create template with multiple blocks"""
        template_path = tmp_path / "blocks_template.txt"
        content = """MEGA-TEMPLATE

0. ПАСПОРТ услуги

Service: {{service_name}}

---

БЛОК I: Базовая информация

Name: {{name}}
Email: {{email}}

---

БЛОК II: Финансовые данные

Rate: {{brutto_rate}}
Currency: {{currency}}
"""
        template_path.write_text(content, encoding="utf-8")
        return str(template_path)

    def test_parse_generic_document(self, tmp_path):
        """Test parsing generic document (not a template)"""
        from src.core.parser import TemplateParser

        # Create a generic document
        doc_path = tmp_path / "document.txt"
        doc_path.write_text("This is a test document.\nWith multiple lines.", encoding="utf-8")

        parser = TemplateParser()
        result = parser.parse(file_path=str(doc_path))

        assert isinstance(result, dict)
        assert "text" in result
        assert "This is a test document" in result["text"]
        assert result["file_path"] == str(doc_path)

    def test_parse_generic_document_error(self, tmp_path):
        """Test parsing non-existent document returns error"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser.parse(file_path="/nonexistent/file.txt")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["text"] == ""

    def test_parse_template_structure(self, template_with_blocks):
        """Test parsing template and extracting structure"""
        from src.core.parser import TemplateParser

        parser = TemplateParser(template_path=template_with_blocks)
        structure = parser.parse()

        assert structure is not None
        assert structure.total_lines > 0
        assert structure.total_blocks > 0
        assert len(structure.blocks) >= 2  # At least blocks 0 and I

    def test_parse_extracts_blocks(self, template_with_blocks):
        """Test parsing extracts all blocks"""
        from src.core.parser import TemplateParser

        parser = TemplateParser(template_path=template_with_blocks)
        structure = parser.parse()

        # Should have blocks 0 (ПАСПОРТ), I, and II
        assert len(structure.blocks) == 3

        block_ids = [b.id for b in structure.blocks]
        assert 0 in block_ids  # ПАСПОРТ
        assert 1 in block_ids  # Block I
        assert 2 in block_ids  # Block II

    def test_parse_extracts_variables(self, template_with_blocks):
        """Test parsing extracts variables from blocks"""
        from src.core.parser import TemplateParser

        parser = TemplateParser(template_path=template_with_blocks)
        structure = parser.parse()

        # Should have multiple variables
        assert structure.total_variables > 0
        assert len(structure.all_variables) > 0

        # Check for specific variables
        var_names = [v.name for v in structure.all_variables]
        assert "service_name" in var_names
        assert "brutto_rate" in var_names


class TestTemplateParserBlockMatching:
    """Tests for block header matching"""

    def test_match_passport_block(self):
        """Test matching ПАСПОРТ block (block 0)"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header("0. ПАСПОРТ услуги")

        assert result is not None
        block_id, title = result
        assert block_id == 0
        assert "ПАСПОРТ" in title

    def test_match_block_i(self):
        """Test matching БЛОК I"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header("БЛОК I: Основная информация")

        assert result is not None
        block_id, title = result
        assert block_id == 1
        assert title == "Основная информация"

    def test_match_block_ii(self):
        """Test matching БЛОК II"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header("БЛОК II: Финансы")

        assert result is not None
        block_id, title = result
        assert block_id == 2
        assert title == "Финансы"

    def test_match_block_x(self):
        """Test matching БЛОК X (block 10)"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header("БЛОК X: Заключение")

        assert result is not None
        block_id, title = result
        assert block_id == 10
        assert title == "Заключение"

    def test_match_invalid_header(self):
        """Test non-matching header returns None"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header("This is not a block header")

        assert result is None

    @pytest.mark.parametrize(
        "header,expected_id",
        [
            ("БЛОК I: Test", 1),
            ("БЛОК II: Test", 2),
            ("БЛОК III: Test", 3),
            ("БЛОК IV: Test", 4),
            ("БЛОК V: Test", 5),
            ("БЛОК VI: Test", 6),
            ("БЛОК VII: Test", 7),
            ("БЛОК VIII: Test", 8),
            ("БЛОК IX: Test", 9),
            ("БЛОК X: Test", 10),
        ],
    )
    def test_match_all_roman_numerals(self, header, expected_id):
        """Test matching all supported Roman numerals"""
        from src.core.parser import TemplateParser

        parser = TemplateParser()
        result = parser._match_block_header(header)

        assert result is not None
        block_id, title = result
        assert block_id == expected_id


class TestTemplateParserGetters:
    """Tests for getter methods"""

    @pytest.fixture
    def parsed_template(self, tmp_path):
        """Fixture with parsed template"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "template.txt"
        content = """MEGA-TEMPLATE

0. ПАСПОРТ услуги

{{service_name}}

---

БЛОК I: Info

{{description}}
{{email}}
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        parser.parse()
        return parser

    def test_get_block_content(self, parsed_template):
        """Test getting content of specific block"""
        content = parsed_template.get_block_content(0)

        assert content is not None
        assert "БЛОК 0" in content or "service_name" in content

    def test_get_nonexistent_block_content(self, parsed_template):
        """Test getting content of non-existent block returns empty string"""
        content = parsed_template.get_block_content(999)
        assert content == ""

    def test_get_all_variables(self, parsed_template):
        """Test getting all variables"""
        variables = parsed_template.get_all_variables()

        assert len(variables) > 0
        var_names = [v.name for v in variables]
        assert "service_name" in var_names

    def test_get_variables_by_block(self, parsed_template):
        """Test getting variables for specific block"""
        # Get variables from block 1 (БЛОК I)
        variables = parsed_template.get_variables_by_block(1)

        assert len(variables) > 0
        var_names = [v.name for v in variables]
        assert "description" in var_names or "email" in var_names

    def test_get_variables_for_nonexistent_block(self, parsed_template):
        """Test getting variables for non-existent block returns empty list"""
        variables = parsed_template.get_variables_by_block(999)
        assert variables == []


class TestTemplateParserStatistics:
    """Tests for template statistics"""

    @pytest.fixture
    def template_for_stats(self, tmp_path):
        """Create template for statistics testing"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "stats_template.txt"
        content = """MEGA-TEMPLATE TEST

0. ПАСПОРТ услуги

Service: {{service_name}}
Region: {{region}}

---

БЛОК I: Section 1

Field 1: {{field1}}
Field 2: {{field2}}

---

БЛОК II: Section 2

Field 3: {{field3}}
Field 1: {{field1}}
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        parser.parse()
        return parser

    def test_get_statistics(self, template_for_stats):
        """Test getting template statistics"""
        stats = template_for_stats.get_statistics()

        assert stats is not None
        assert stats.total_lines > 0
        assert stats.total_blocks > 0
        assert stats.total_sections > 0
        assert stats.total_variables > 0

    def test_statistics_counts_unique_variables(self, template_for_stats):
        """Test statistics correctly counts unique variables"""
        stats = template_for_stats.get_statistics()

        # field1 appears twice, so total_variables > unique_variables
        assert stats.unique_variables > 0
        assert stats.total_variables >= stats.unique_variables

    def test_statistics_blocks_summary(self, template_for_stats):
        """Test statistics includes blocks summary"""
        stats = template_for_stats.get_statistics()

        assert isinstance(stats.blocks_summary, dict)
        assert len(stats.blocks_summary) > 0

    def test_statistics_variables_by_block(self, template_for_stats):
        """Test statistics includes variables count by block"""
        stats = template_for_stats.get_statistics()

        assert isinstance(stats.variables_by_block, dict)
        assert len(stats.variables_by_block) > 0

        # Each block should have some variables
        for block_id, var_count in stats.variables_by_block.items():
            assert var_count >= 0

    def test_statistics_total_characters(self, template_for_stats):
        """Test statistics includes total character count"""
        stats = template_for_stats.get_statistics()

        assert stats.total_characters > 0


class TestTemplateParserSearch:
    """Tests for content search functionality"""

    @pytest.fixture
    def searchable_template(self, tmp_path):
        """Create template for search testing"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "search_template.txt"
        content = """Line 1: MEGA-TEMPLATE
Line 2: This is a test template
Line 3: With searchable content
Line 4: TEMPLATE keywords everywhere
Line 5: Case sensitive TEST
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        parser.load()
        return parser

    def test_search_content_case_insensitive(self, searchable_template):
        """Test case-insensitive search"""
        results = searchable_template.search_content("template", case_sensitive=False)

        assert len(results) >= 2  # Should find "TEMPLATE" and "template"

        # Results should be tuples of (line_number, line_content)
        for line_num, line_content in results:
            assert isinstance(line_num, int)
            assert isinstance(line_content, str)
            assert "template" in line_content.lower()

    def test_search_content_case_sensitive(self, searchable_template):
        """Test case-sensitive search"""
        # Search for "TEMPLATE" (uppercase)
        results = searchable_template.search_content("TEMPLATE", case_sensitive=True)

        assert len(results) >= 2

        # All results should contain exact match
        for line_num, line_content in results:
            assert "TEMPLATE" in line_content

    def test_search_content_no_matches(self, searchable_template):
        """Test search with no matches returns empty list"""
        results = searchable_template.search_content("NONEXISTENT")
        assert results == []

    def test_search_content_returns_line_numbers(self, searchable_template):
        """Test search returns correct line numbers"""
        results = searchable_template.search_content("Line", case_sensitive=True)

        # Should find lines 1-5
        line_numbers = [line_num for line_num, _ in results]
        assert len(line_numbers) == 5
        assert min(line_numbers) == 1
        assert max(line_numbers) == 5


class TestTemplateParserEdgeCases:
    """Tests for edge cases and error handling"""

    def test_parse_empty_template(self, tmp_path):
        """Test parsing empty template"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "empty.txt"
        template_path.write_text("", encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        structure = parser.parse()

        assert structure is not None
        assert structure.total_lines == 0
        assert structure.total_blocks == 0

    def test_parse_template_no_variables(self, tmp_path):
        """Test parsing template without variables"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "no_vars.txt"
        content = """MEGA-TEMPLATE

0. ПАСПОРТ услуги

This template has no variables.
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        structure = parser.parse()

        assert structure.total_blocks >= 1
        assert structure.total_variables == 0

    def test_parse_template_only_blocks_no_sections(self, tmp_path):
        """Test parsing template with block headers but no content"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "headers_only.txt"
        content = """MEGA-TEMPLATE

0. ПАСПОРТ услуги
БЛОК I: Info
БЛОК II: Data
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        structure = parser.parse()

        assert structure.total_blocks == 3
        # Blocks may have 0 or minimal sections

    def test_metadata_extraction(self, tmp_path):
        """Test extracting metadata from template"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "metadata.txt"
        content = """MEGA-TEMPLATE TITLE
Some other line
Template Description Here

Content...
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        structure = parser.parse()

        assert "title" in structure.metadata
        assert "MEGA-TEMPLATE TITLE" in structure.metadata["title"]

    def test_parse_unicode_content(self, tmp_path):
        """Test parsing template with Unicode characters"""
        from src.core.parser import TemplateParser

        template_path = tmp_path / "unicode.txt"
        content = """MEGA-TEMPLATE

0. ПАСПОРТ услуги

Имя: {{name}}
Описание: {{description}}
Специальные символы: ©®™€
"""
        template_path.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(template_path))
        structure = parser.parse()

        assert structure is not None
        assert structure.total_blocks > 0


class TestTemplateParserAliases:
    """Tests for backward compatibility aliases"""

    def test_document_parser_alias(self):
        """Test DocumentParser is an alias for TemplateParser"""
        from src.core.parser import DocumentParser, TemplateParser

        assert DocumentParser is TemplateParser

    def test_document_parser_works_same_as_template_parser(self):
        """Test DocumentParser has same functionality"""
        from src.core.parser import DocumentParser

        parser = DocumentParser()
        assert parser is not None
        assert hasattr(parser, "parse")
        assert hasattr(parser, "load")
