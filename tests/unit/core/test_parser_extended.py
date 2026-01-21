"""
Comprehensive tests for parser.py module

Tests cover:
- TemplateParser initialization (2 tests)
- File loading (4 tests)
- Generic document parsing (5 tests)
- Template parsing (10 tests)
- Block parsing (8 tests)
- Block header matching (6 tests)
- Section handling (5 tests)
- Metadata extraction (3 tests)
- Content retrieval (6 tests)
- Variable extraction (8 tests)
- Statistics (6 tests)
- Search functionality (5 tests)
- Edge cases and error handling (8 tests)

Total: 76+ comprehensive test methods
Coverage target: 18.2% → 80%+
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.core.parser import TemplateParser
from src.models.template import Block, Section, Variable, TemplateStructure, TemplateStats


# ============================================================================
# TemplateParser Initialization Tests (2 tests)
# ============================================================================


class TestTemplateParserInit:
    """Test TemplateParser initialization"""

    def test_init_without_path(self):
        """Test initialization without template path"""
        parser = TemplateParser()
        assert parser.template_path is None
        assert parser.lines == []
        assert parser.structure is None

    def test_init_with_path(self):
        """Test initialization with template path"""
        parser = TemplateParser(template_path="/path/to/template.txt")
        assert parser.template_path == "/path/to/template.txt"
        assert parser.lines == []
        assert parser.structure is None


# ============================================================================
# File Loading Tests (4 tests)
# ============================================================================


class TestTemplateParserLoad:
    """Test file loading functionality"""

    def test_load_success(self, tmp_path):
        """Test successful file loading"""
        # Create test template file
        test_file = tmp_path / "template.txt"
        test_content = "Line 1\nLine 2\nLine 3\n"
        test_file.write_text(test_content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()

        assert len(parser.lines) == 3
        assert parser.lines[0] == "Line 1\n"
        assert parser.lines[1] == "Line 2\n"
        assert parser.lines[2] == "Line 3\n"

    def test_load_empty_file(self, tmp_path):
        """Test loading empty file"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()

        assert len(parser.lines) == 0

    def test_load_without_path(self):
        """Test loading without template path set"""
        parser = TemplateParser()

        with pytest.raises(ValueError, match="no template_path"):
            parser.load()

    def test_load_nonexistent_file(self):
        """Test loading non-existent file"""
        parser = TemplateParser(template_path="/nonexistent/file.txt")

        with pytest.raises(FileNotFoundError):
            parser.load()


# ============================================================================
# Generic Document Parsing Tests (5 tests)
# ============================================================================


class TestTemplateParserGenericParsing:
    """Test generic document parsing"""

    def test_parse_generic_document(self, tmp_path):
        """Test parsing generic document"""
        test_file = tmp_path / "document.txt"
        test_content = "This is a test document.\nWith multiple lines."
        test_file.write_text(test_content, encoding="utf-8")

        parser = TemplateParser()
        result = parser.parse(file_path=str(test_file))

        assert isinstance(result, dict)
        assert "text" in result
        assert "file_path" in result
        assert result["text"] == test_content
        assert result["file_path"] == str(test_file)

    def test_parse_generic_empty_document(self, tmp_path):
        """Test parsing empty generic document"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        parser = TemplateParser()
        result = parser.parse(file_path=str(test_file))

        assert result["text"] == ""
        assert "error" not in result

    def test_parse_generic_nonexistent_file(self):
        """Test parsing non-existent generic document"""
        parser = TemplateParser()
        result = parser.parse(file_path="/nonexistent/file.txt")

        assert "error" in result
        assert result["text"] == ""

    def test_parse_generic_unicode(self, tmp_path):
        """Test parsing document with unicode characters"""
        test_file = tmp_path / "unicode.txt"
        test_content = "German: äöü ÄÖÜ ß\nRussian: Привет мир"
        test_file.write_text(test_content, encoding="utf-8")

        parser = TemplateParser()
        result = parser.parse(file_path=str(test_file))

        assert result["text"] == test_content

    def test_parse_generic_large_file(self, tmp_path):
        """Test parsing large generic document"""
        test_file = tmp_path / "large.txt"
        test_content = "Line\n" * 10000
        test_file.write_text(test_content, encoding="utf-8")

        parser = TemplateParser()
        result = parser.parse(file_path=str(test_file))

        assert "text" in result
        assert len(result["text"]) > 0


# ============================================================================
# Template Parsing Tests (10 tests)
# ============================================================================


class TestTemplateParserTemplateParsing:
    """Test template parsing functionality"""

    def create_simple_template(self, tmp_path):
        """Helper to create simple test template"""
        content = """MEGA-TEMPLATE für soziale Dienstleistungsplanung

Beschreibung

0. ПАСПОРТ УСЛУГИ

Dienst Name: {{service_name}}
Region: {{region}}

---

БЛОК I: GRUNDLEGENDE INFORMATION

Zielgruppe: {{target_group}}
Servicetyp: {{service_type}}

---

БЛОК II: FINANZIELLE PARAMETER

Brutto-Rate: {{brutto_rate}}
"""
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")
        return str(test_file)

    def test_parse_template_structure(self, tmp_path):
        """Test parsing template returns TemplateStructure"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert isinstance(result, TemplateStructure)
        assert result.total_lines > 0
        assert result.total_blocks > 0

    def test_parse_template_loads_file(self, tmp_path):
        """Test parsing template loads file automatically"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)

        # Don't call load() explicitly
        result = parser.parse()

        assert len(parser.lines) > 0
        assert isinstance(result, TemplateStructure)

    def test_parse_template_counts_lines(self, tmp_path):
        """Test parsing counts total lines"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert result.total_lines == len(parser.lines)

    def test_parse_template_extracts_blocks(self, tmp_path):
        """Test parsing extracts blocks"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert len(result.blocks) >= 2
        assert result.total_blocks == len(result.blocks)

    def test_parse_template_extracts_variables(self, tmp_path):
        """Test parsing extracts variables"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert result.total_variables > 0
        assert len(result.all_variables) == result.total_variables

    def test_parse_template_extracts_sections(self, tmp_path):
        """Test parsing extracts sections"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert result.total_sections > 0
        # Each block should have at least one section
        for block in result.blocks:
            assert len(block.sections) > 0

    def test_parse_template_metadata(self, tmp_path):
        """Test parsing extracts metadata"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert result.metadata is not None
        assert isinstance(result.metadata, dict)

    def test_parse_empty_template(self, tmp_path):
        """Test parsing empty template"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert result.total_lines == 0
        assert result.total_blocks == 0
        assert result.total_variables == 0

    def test_parse_template_stores_structure(self, tmp_path):
        """Test parsing stores structure in parser"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)

        assert parser.structure is None
        parser.parse()
        assert parser.structure is not None

    def test_parse_template_twice(self, tmp_path):
        """Test parsing same template twice"""
        template_path = self.create_simple_template(tmp_path)
        parser = TemplateParser(template_path=template_path)

        result1 = parser.parse()
        result2 = parser.parse()

        assert result1.total_lines == result2.total_lines
        assert result1.total_blocks == result2.total_blocks


# ============================================================================
# Block Parsing Tests (8 tests)
# ============================================================================


class TestTemplateParserBlockParsing:
    """Test block parsing"""

    def create_block_template(self, tmp_path):
        """Helper to create template with multiple blocks"""
        content = """0. ПАСПОРТ УСЛУГИ
Section content
---
БЛОК I: FIRST BLOCK
Content 1
---
БЛОК II: SECOND BLOCK
Content 2
---
БЛОК III: THIRD BLOCK
Content 3
"""
        test_file = tmp_path / "blocks.txt"
        test_file.write_text(content, encoding="utf-8")
        return str(test_file)

    def test_parse_blocks_multiple(self, tmp_path):
        """Test parsing multiple blocks"""
        template_path = self.create_block_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        assert len(result.blocks) == 4  # 0, I, II, III

    def test_parse_blocks_ids(self, tmp_path):
        """Test block IDs are assigned correctly"""
        template_path = self.create_block_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        block_ids = [block.id for block in result.blocks]
        assert 0 in block_ids  # ПАСПОРТ
        assert 1 in block_ids  # БЛОК I
        assert 2 in block_ids  # БЛОК II
        assert 3 in block_ids  # БЛОК III

    def test_parse_blocks_titles(self, tmp_path):
        """Test block titles are extracted"""
        template_path = self.create_block_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        for block in result.blocks:
            assert block.title is not None
            assert len(block.title) > 0

    def test_parse_blocks_sections(self, tmp_path):
        """Test blocks contain sections"""
        template_path = self.create_block_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        result = parser.parse()

        for block in result.blocks:
            assert len(block.sections) > 0

    def test_parse_blocks_variables(self, tmp_path):
        """Test blocks can have variables"""
        content = """БЛОК I: TEST BLOCK
Name: {{var1}}
Value: {{var2}}
"""
        test_file = tmp_path / "vars.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) == 1
        assert len(result.blocks[0].variables) >= 2

    def test_parse_blocks_empty_sections(self, tmp_path):
        """Test blocks with empty sections"""
        content = """БЛОК I: EMPTY BLOCK
---
---
"""
        test_file = tmp_path / "empty_sections.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) >= 1

    def test_parse_blocks_no_sections(self, tmp_path):
        """Test block without section separators"""
        content = """БЛОК I: SINGLE BLOCK
All content in one section
No separator lines
"""
        test_file = tmp_path / "no_sep.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) >= 1
        assert len(result.blocks[0].sections) > 0

    def test_parse_blocks_consecutive(self, tmp_path):
        """Test consecutive blocks without content between"""
        content = """БЛОК I: BLOCK 1
БЛОК II: BLOCK 2
БЛОК III: BLOCK 3
"""
        test_file = tmp_path / "consecutive.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) == 3


# ============================================================================
# Block Header Matching Tests (6 tests)
# ============================================================================


class TestTemplateParserBlockHeaderMatching:
    """Test block header matching"""

    def test_match_passport_block(self):
        """Test matching ПАСПОРТ block (block 0)"""
        parser = TemplateParser()
        result = parser._match_block_header("0. ПАСПОРТ УСЛУГИ")

        assert result is not None
        assert result[0] == 0
        assert "ПАСПОРТ" in result[1]

    def test_match_roman_numeral_blocks(self):
        """Test matching blocks with Roman numerals"""
        parser = TemplateParser()

        test_cases = [
            ("БЛОК I: FIRST BLOCK", 1),
            ("БЛОК II: SECOND BLOCK", 2),
            ("БЛОК III: THIRD BLOCK", 3),
            ("БЛОК IV: FOURTH BLOCK", 4),
            ("БЛОК V: FIFTH BLOCK", 5),
        ]

        for line, expected_id in test_cases:
            result = parser._match_block_header(line)
            assert result is not None
            assert result[0] == expected_id

    def test_match_all_roman_numerals(self):
        """Test matching all Roman numerals I-X"""
        parser = TemplateParser()

        for i in range(1, 11):
            roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
            line = f"БЛОК {roman_numerals[i-1]}: BLOCK {i}"
            result = parser._match_block_header(line)
            assert result is not None
            assert result[0] == i

    def test_match_no_match(self):
        """Test non-matching lines"""
        parser = TemplateParser()

        non_matching = ["Regular text", "Not a header", "BLOCK I: Missing БЛОК", ""]

        for line in non_matching:
            result = parser._match_block_header(line)
            assert result is None

    def test_match_extracts_title(self):
        """Test title extraction from headers"""
        parser = TemplateParser()

        result = parser._match_block_header("БЛОК I: This is the title")
        assert result is not None
        assert result[1] == "This is the title"

    def test_match_case_sensitivity(self):
        """Test header matching is case-sensitive where needed"""
        parser = TemplateParser()

        # Should match (correct case)
        assert parser._match_block_header("БЛОК I: TEST") is not None

        # Should not match (wrong case)
        assert parser._match_block_header("блок I: TEST") is None


# ============================================================================
# Section Handling Tests (5 tests)
# ============================================================================


class TestTemplateParserSectionHandling:
    """Test section handling"""

    def test_add_section_to_block(self):
        """Test adding section to block"""
        parser = TemplateParser()
        block = Block(id=1, title="Test Block", description="")

        section_lines = ["Section Title\n", "Content line 1\n", "Content line 2\n"]
        parser._add_section_to_block(block, section_lines)

        assert len(block.sections) == 1
        assert block.sections[0].title == "Section Title"

    def test_add_section_extracts_content(self):
        """Test section content extraction"""
        parser = TemplateParser()
        block = Block(id=1, title="Test Block", description="")

        section_lines = ["Title\n", "Line 1\n", "Line 2\n"]
        parser._add_section_to_block(block, section_lines)

        section = block.sections[0]
        assert "Line 1" in section.content
        assert "Line 2" in section.content

    def test_add_section_with_variables(self):
        """Test section with variables"""
        parser = TemplateParser()
        block = Block(id=1, title="Test Block", description="")

        section_lines = ["Section with variables\n", "Name: {{name}}\n", "Age: {{age}}\n"]
        parser._add_section_to_block(block, section_lines)

        assert len(block.variables) >= 2
        var_names = [var.name for var in block.variables]
        assert "name" in var_names
        assert "age" in var_names

    def test_add_section_id_assignment(self):
        """Test section ID assignment"""
        parser = TemplateParser()
        block = Block(id=1, title="Test Block", description="")

        # Add first section
        parser._add_section_to_block(block, ["Section 1\n"])
        # Add second section
        parser._add_section_to_block(block, ["Section 2\n"])

        assert block.sections[0].id == "1.1"
        assert block.sections[1].id == "1.2"

    def test_add_section_empty_lines(self):
        """Test adding section with empty lines"""
        parser = TemplateParser()
        block = Block(id=1, title="Test Block", description="")

        section_lines = ["\n", "\n", "Title\n", "\n"]
        parser._add_section_to_block(block, section_lines)

        # Should skip empty lines for title
        assert block.sections[0].title == "Title"


# ============================================================================
# Metadata Extraction Tests (3 tests)
# ============================================================================


class TestTemplateParserMetadata:
    """Test metadata extraction"""

    def test_extract_metadata_title(self, tmp_path):
        """Test extracting title from first line"""
        content = "TEMPLATE TITLE\nSome content\nMore content"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()
        metadata = parser._extract_metadata()

        assert "title" in metadata
        assert metadata["title"] == "TEMPLATE TITLE"

    def test_extract_metadata_description(self, tmp_path):
        """Test extracting description"""
        content = "Title\nLine 2\nDescription line"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()
        metadata = parser._extract_metadata()

        assert "description" in metadata
        assert metadata["description"] == "Description line"

    def test_extract_metadata_empty(self):
        """Test extracting metadata from empty template"""
        parser = TemplateParser()
        parser.lines = []
        metadata = parser._extract_metadata()

        assert isinstance(metadata, dict)


# ============================================================================
# Content Retrieval Tests (6 tests)
# ============================================================================


class TestTemplateParserContentRetrieval:
    """Test content retrieval methods"""

    def create_test_template(self, tmp_path):
        """Helper to create test template"""
        content = """БЛОК I: FIRST BLOCK
Section 1 content
---
Section 2 content
---
БЛОК II: SECOND BLOCK
Section 1 of block 2
"""
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")
        return str(test_file)

    def test_get_block_content(self, tmp_path):
        """Test getting block content"""
        template_path = self.create_test_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.parse()

        content = parser.get_block_content(1)
        assert len(content) > 0
        assert "FIRST BLOCK" in content

    def test_get_block_content_nonexistent(self, tmp_path):
        """Test getting non-existent block"""
        template_path = self.create_test_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.parse()

        content = parser.get_block_content(999)
        assert content == ""

    def test_get_block_content_auto_parse(self, tmp_path):
        """Test get_block_content parses automatically"""
        template_path = self.create_test_template(tmp_path)
        parser = TemplateParser(template_path=template_path)

        # Don't call parse() explicitly
        content = parser.get_block_content(1)
        assert len(content) > 0

    def test_get_all_variables(self, tmp_path):
        """Test getting all variables"""
        content = "БЛОК I: TEST\nName: {{var1}}\nAge: {{var2}}"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        variables = parser.get_all_variables()

        assert len(variables) >= 2

    def test_get_variables_by_block(self, tmp_path):
        """Test getting variables by block"""
        content = """БЛОК I: BLOCK 1
{{var1}}
{{var2}}
---
БЛОК II: BLOCK 2
{{var3}}
"""
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.parse()

        vars_block_1 = parser.get_variables_by_block(1)
        vars_block_2 = parser.get_variables_by_block(2)

        assert len(vars_block_1) >= 2
        assert len(vars_block_2) >= 1

    def test_get_variables_nonexistent_block(self, tmp_path):
        """Test getting variables from non-existent block"""
        template_path = self.create_test_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.parse()

        variables = parser.get_variables_by_block(999)
        assert variables == []


# ============================================================================
# Statistics Tests (6 tests)
# ============================================================================


class TestTemplateParserStatistics:
    """Test statistics generation"""

    def create_stats_template(self, tmp_path):
        """Helper to create template for statistics"""
        content = """TEMPLATE TITLE

БЛОК I: BLOCK 1
Section 1: {{var1}}
---
Section 2: {{var2}}
---
БЛОК II: BLOCK 2
Section 1: {{var3}}
{{var4}}
"""
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")
        return str(test_file)

    def test_get_statistics(self, tmp_path):
        """Test getting statistics"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert isinstance(stats, TemplateStats)

    def test_statistics_counts(self, tmp_path):
        """Test statistics contain correct counts"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert stats.total_lines > 0
        assert stats.total_blocks > 0
        assert stats.total_sections > 0
        assert stats.total_variables > 0

    def test_statistics_unique_variables(self, tmp_path):
        """Test unique variables count"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert stats.unique_variables > 0
        assert stats.unique_variables <= stats.total_variables

    def test_statistics_blocks_summary(self, tmp_path):
        """Test blocks summary in statistics"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert isinstance(stats.blocks_summary, dict)
        assert len(stats.blocks_summary) > 0

    def test_statistics_variables_by_block(self, tmp_path):
        """Test variables by block in statistics"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert isinstance(stats.variables_by_block, dict)
        assert len(stats.variables_by_block) > 0

    def test_statistics_total_characters(self, tmp_path):
        """Test total characters count"""
        template_path = self.create_stats_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        stats = parser.get_statistics()

        assert stats.total_characters > 0


# ============================================================================
# Search Functionality Tests (5 tests)
# ============================================================================


class TestTemplateParserSearch:
    """Test search functionality"""

    def create_search_template(self, tmp_path):
        """Helper to create template for search tests"""
        content = """Line 1: This is a test
Line 2: Another test line
Line 3: Different content
Line 4: TEST in uppercase
Line 5: Final line
"""
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")
        return str(test_file)

    def test_search_content_found(self, tmp_path):
        """Test search finds matching content"""
        template_path = self.create_search_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.load()

        results = parser.search_content("test")
        assert len(results) > 0

    def test_search_content_case_insensitive(self, tmp_path):
        """Test case-insensitive search"""
        template_path = self.create_search_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.load()

        results = parser.search_content("TEST", case_sensitive=False)
        assert len(results) >= 3  # "test", "test", "TEST"

    def test_search_content_case_sensitive(self, tmp_path):
        """Test case-sensitive search"""
        template_path = self.create_search_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.load()

        results = parser.search_content("TEST", case_sensitive=True)
        assert len(results) == 1  # Only "TEST" in uppercase

    def test_search_content_no_results(self, tmp_path):
        """Test search with no results"""
        template_path = self.create_search_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.load()

        results = parser.search_content("nonexistent_text")
        assert len(results) == 0

    def test_search_content_returns_line_numbers(self, tmp_path):
        """Test search returns line numbers"""
        template_path = self.create_search_template(tmp_path)
        parser = TemplateParser(template_path=template_path)
        parser.load()

        results = parser.search_content("Line")
        assert all(isinstance(line_num, int) for line_num, _ in results)
        assert all(line_num > 0 for line_num, _ in results)


# ============================================================================
# Edge Cases and Error Handling Tests (8 tests)
# ============================================================================


class TestParserEdgeCases:
    """Test edge cases and error handling"""

    def test_parse_file_with_special_chars(self, tmp_path):
        """Test parsing file with special characters"""
        content = "Special: !@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"
        test_file = tmp_path / "special.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert result.total_lines > 0

    def test_parse_file_with_long_lines(self, tmp_path):
        """Test parsing file with very long lines"""
        long_line = "x" * 10000
        test_file = tmp_path / "long.txt"
        test_file.write_text(long_line, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()

        assert len(parser.lines[0]) == 10000

    def test_parse_with_multiple_separators(self, tmp_path):
        """Test parsing with multiple consecutive separators"""
        content = "БЛОК I: TEST\n---\n---\n---\nContent"
        test_file = tmp_path / "multi_sep.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) > 0

    def test_parse_with_only_separators(self, tmp_path):
        """Test parsing file with only separators"""
        content = "---\n---\n---"
        test_file = tmp_path / "only_sep.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert result.total_lines == 3

    def test_get_block_before_parsing(self, tmp_path):
        """Test getting block triggers parsing"""
        content = "БЛОК I: TEST\nContent"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        # Don't parse explicitly
        content = parser.get_block_content(1)

        assert parser.structure is not None
        assert len(content) > 0

    def test_statistics_before_parsing(self, tmp_path):
        """Test getting statistics triggers parsing"""
        content = "БЛОК I: TEST"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        stats = parser.get_statistics()

        assert parser.structure is not None
        assert stats.total_lines > 0

    def test_search_empty_query(self, tmp_path):
        """Test search with empty query"""
        content = "Some content"
        test_file = tmp_path / "template.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        parser.load()
        results = parser.search_content("")

        # Empty query should match all lines
        assert len(results) == len(parser.lines)

    def test_unicode_in_block_headers(self, tmp_path):
        """Test Unicode characters in block headers"""
        content = "БЛОК I: Тестовый блок\nСодержание\n"
        test_file = tmp_path / "unicode.txt"
        test_file.write_text(content, encoding="utf-8")

        parser = TemplateParser(template_path=str(test_file))
        result = parser.parse()

        assert len(result.blocks) > 0
        assert "Тестовый" in result.blocks[0].title


# ============================================================================
# Alias Tests (1 test)
# ============================================================================


class TestParserAlias:
    """Test backward compatibility alias"""

    def test_document_parser_alias(self):
        """Test DocumentParser is alias for TemplateParser"""
        from src.core.parser import DocumentParser

        parser = DocumentParser()
        assert isinstance(parser, TemplateParser)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
