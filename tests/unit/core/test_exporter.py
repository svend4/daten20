"""
Comprehensive tests for core.exporter module
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.unit


class TestDocumentExporter:
    """Tests for DocumentExporter class"""

    @pytest.fixture
    def exporter(self):
        """Fixture providing DocumentExporter instance"""
        from src.core.exporter import DocumentExporter

        return DocumentExporter()

    def test_exporter_initialization(self, exporter):
        """Test DocumentExporter can be initialized"""
        assert exporter is not None

    def test_export_text_format(self, exporter, tmp_path):
        """Test exporting to text format"""
        content = "Sample document content"
        output_path = tmp_path / "output.txt"

        result = exporter.export(content, str(output_path), format="txt")

        assert result is True
        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == content

    def test_export_markdown_format(self, exporter, tmp_path):
        """Test exporting to markdown format"""
        content = "# Markdown Content\n\nParagraph text"
        output_path = tmp_path / "output.md"

        result = exporter.export(content, str(output_path), format="md")

        assert result is True
        assert output_path.exists()

    def test_export_markdown_with_metadata(self, exporter, tmp_path):
        """Test exporting markdown with frontmatter"""
        content = "Content"
        output_path = tmp_path / "output.md"
        metadata = {"title": "Test Document", "author": "Test Author"}

        result = exporter.export(content, str(output_path), format="md", metadata=metadata)

        assert result is True
        text = output_path.read_text(encoding="utf-8")
        assert "---" in text
        assert "title: Test Document" in text
        assert "author: Test Author" in text

    def test_export_html_format(self, exporter, tmp_path):
        """Test exporting to HTML format"""
        content = "HTML content"
        output_path = tmp_path / "output.html"

        result = exporter.export(content, str(output_path), format="html", title="Test Page")

        assert result is True
        assert output_path.exists()
        html = output_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html
        assert "<title>Test Page</title>" in html

    @patch("src.core.exporter.DocumentExporter.export_to_pdf")
    def test_export_pdf_format(self, mock_export_pdf, exporter, tmp_path):
        """Test exporting to PDF format"""
        content = "PDF content"
        output_path = tmp_path / "output.pdf"
        mock_export_pdf.return_value = True

        result = exporter.export(content, str(output_path), format="pdf", title="PDF Doc")

        assert result is True
        mock_export_pdf.assert_called_once_with(content, str(output_path), "PDF Doc")

    @patch("src.core.exporter.DocumentExporter.export_to_docx")
    def test_export_docx_format(self, mock_export_docx, exporter, tmp_path):
        """Test exporting to DOCX format"""
        content = "DOCX content"
        output_path = tmp_path / "output.docx"
        mock_export_docx.return_value = True

        result = exporter.export(content, str(output_path), format="docx", title="DOCX Doc")

        assert result is True
        mock_export_docx.assert_called_once_with(content, str(output_path), "DOCX Doc")

    def test_export_unsupported_format(self, exporter, tmp_path):
        """Test exporting with unsupported format returns False"""
        content = "Content"
        output_path = tmp_path / "output.xyz"

        result = exporter.export(content, str(output_path), format="xyz")

        assert result is False

    def test_export_to_text_creates_parent_dir(self, exporter, tmp_path):
        """Test export_to_text creates parent directories"""
        content = "Content"
        output_path = tmp_path / "nested" / "dirs" / "file.txt"

        exporter.export_to_text(content, str(output_path))

        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == content

    def test_export_to_markdown_without_metadata(self, exporter, tmp_path):
        """Test export_to_markdown without metadata"""
        content = "# Heading\n\nContent"
        output_path = tmp_path / "output.md"

        exporter.export_to_markdown(content, str(output_path))

        assert output_path.exists()
        text = output_path.read_text(encoding="utf-8")
        assert text == content
        assert "---" not in text

    def test_export_to_html_includes_styling(self, exporter, tmp_path):
        """Test export_to_html includes CSS styling"""
        content = "Content"
        output_path = tmp_path / "output.html"

        exporter.export_to_html(content, str(output_path), title="Styled Doc")

        html = output_path.read_text(encoding="utf-8")
        assert "<style>" in html
        assert "font-family" in html
        assert "Styled Doc" in html

    def test_export_case_insensitive_format(self, exporter, tmp_path):
        """Test export format is case-insensitive"""
        content = "Content"
        output_path1 = tmp_path / "output1.txt"
        output_path2 = tmp_path / "output2.txt"

        result1 = exporter.export(content, str(output_path1), format="TXT")
        result2 = exporter.export(content, str(output_path2), format="Txt")

        assert result1 is True
        assert result2 is True

    def test_export_format_aliases(self, exporter, tmp_path):
        """Test format aliases (text=txt, markdown=md)"""
        content = "Content"
        output_path1 = tmp_path / "output1.txt"
        output_path2 = tmp_path / "output2.md"

        result1 = exporter.export(content, str(output_path1), format="text")
        result2 = exporter.export(content, str(output_path2), format="markdown")

        assert result1 is True
        assert result2 is True


class TestDocumentExporterEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.fixture
    def exporter(self):
        """Fixture providing DocumentExporter instance"""
        from src.core.exporter import DocumentExporter

        return DocumentExporter()

    def test_export_empty_content(self, exporter, tmp_path):
        """Test exporting empty content"""
        content = ""
        output_path = tmp_path / "empty.txt"

        result = exporter.export(content, str(output_path), format="txt")

        assert result is True
        assert output_path.read_text(encoding="utf-8") == ""

    def test_export_unicode_content(self, exporter, tmp_path):
        """Test exporting Unicode content"""
        content = "Тест с кириллицей и эмодзи 🎉"
        output_path = tmp_path / "unicode.txt"

        result = exporter.export(content, str(output_path), format="txt")

        assert result is True
        assert output_path.read_text(encoding="utf-8") == content

    def test_export_large_content(self, exporter, tmp_path):
        """Test exporting large content"""
        content = "A" * 100000  # 100KB
        output_path = tmp_path / "large.txt"

        result = exporter.export(content, str(output_path), format="txt")

        assert result is True
        assert len(output_path.read_text(encoding="utf-8")) == 100000

    def test_export_multiline_content(self, exporter, tmp_path):
        """Test exporting multiline content"""
        content = "Line 1\nLine 2\nLine 3\n"
        output_path = tmp_path / "multiline.txt"

        exporter.export_to_text(content, str(output_path))

        assert output_path.read_text(encoding="utf-8") == content

    def test_export_with_special_characters(self, exporter, tmp_path):
        """Test exporting content with special characters"""
        content = "Special chars: <>&\"'\n\t"
        output_path = tmp_path / "special.txt"

        result = exporter.export(content, str(output_path), format="txt")

        assert result is True

    @patch("src.core.exporter.DocumentExporter.export_to_text")
    def test_export_handles_exceptions(self, mock_export, exporter, tmp_path):
        """Test export handles exceptions gracefully"""
        mock_export.side_effect = Exception("Export error")
        output_path = tmp_path / "error.txt"

        result = exporter.export("Content", str(output_path), format="txt")

        assert result is False
