"""Unit tests for Template Analyzer"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.core.parser import TemplateParser
from src.template_analyzer import TemplateAnalyzer


class TestTemplateParser:
    """Test Template Parser"""

    def setup_method(self):
        """Setup before each test"""
        self.parser = TemplateParser('mSchablone')

    def test_load_template(self):
        """Test template loading"""
        self.parser.load()

        assert len(self.parser.lines) > 0
        assert len(self.parser.lines) == 4360  # Expected line count

    def test_parse_structure(self):
        """Test structure parsing"""
        structure = self.parser.parse()

        assert structure is not None
        assert structure.total_lines > 0
        assert structure.total_blocks > 0
        assert len(structure.blocks) == 11  # 0 + I-X

    def test_extract_variables(self):
        """Test variable extraction"""
        structure = self.parser.parse()

        assert len(structure.all_variables) > 0
        # Should find variables like {Название_услуги}

    def test_get_block_content(self):
        """Test block content retrieval"""
        self.parser.parse()
        content = self.parser.get_block_content(0)

        assert len(content) > 0
        assert "ПАСПОРТ" in content

    def test_search_content(self):
        """Test content search"""
        self.parser.load()
        results = self.parser.search_content("услуга")

        assert len(results) > 0
        # Results should be tuples of (line_number, line_content)

    def test_statistics(self):
        """Test statistics generation"""
        structure = self.parser.parse()
        stats = self.parser.get_statistics()

        assert stats.total_lines > 0
        assert stats.total_blocks > 0
        assert stats.total_variables > 0


class TestTemplateAnalyzer:
    """Test Template Analyzer"""

    def setup_method(self):
        """Setup before each test"""
        self.analyzer = TemplateAnalyzer('mSchablone')

    def test_analyze(self):
        """Test analysis execution"""
        self.analyzer.analyze()

        assert self.analyzer.structure is not None
        assert self.analyzer.structure.total_lines > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
