"""
Tests for Enhanced Export Modules (v4.2)

Tests for PDF, Excel, and PowerPoint enhanced exporters.
"""

import pytest
import os
import tempfile
from datetime import datetime


class TestEnhancedPDFExporter:
    """Test Enhanced PDF Exporter (v4.2)"""

    def test_import_pdf_exporter(self):
        """Test importing EnhancedPDFExporter"""
        from core.pdf_enhanced import EnhancedPDFExporter, PDFQuality, PDFStandard
        assert EnhancedPDFExporter is not None
        assert PDFQuality.HIGH is not None
        assert PDFStandard.PDF_A_2B is not None

    def test_create_pdf_exporter(self):
        """Test creating PDF exporter instance"""
        from core.pdf_enhanced import EnhancedPDFExporter, PDFConfig, PDFQuality

        config = PDFConfig(
            quality=PDFQuality.HIGH,
            compress=True,
            optimize_for_web=True
        )
        exporter = EnhancedPDFExporter(config)
        assert exporter is not None
        assert exporter.config.quality == PDFQuality.HIGH

    def test_pdf_metadata(self):
        """Test PDF metadata creation"""
        from core.pdf_enhanced import PDFMetadata

        metadata = PDFMetadata(
            title="Test Document",
            author="Test Author",
            subject="Testing",
            keywords=["test", "pdf", "export"],
            creator="EnhancedPDFExporter"
        )
        assert metadata.title == "Test Document"
        assert "test" in metadata.keywords

    def test_export_simple_document(self):
        """Test exporting simple document"""
        from core.pdf_enhanced import EnhancedPDFExporter, PDFConfig, PDFMetadata

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_output.pdf")

            config = PDFConfig()
            exporter = EnhancedPDFExporter(config)

            metadata = PDFMetadata(
                title="Test Document",
                author="Test Author"
            )

            content = {
                'title': 'Test Document',
                'sections': [
                    {'heading': 'Section 1', 'content': 'This is test content.'}
                ],
                'metadata': metadata
            }

            # Test export (simulation mode - no actual file creation)
            result = exporter.export_document(content, output_path)
            assert result is True


class TestEnhancedExcelExporter:
    """Test Enhanced Excel Exporter (v4.2)"""

    def test_import_excel_exporter(self):
        """Test importing EnhancedExcelExporter"""
        from core.excel_enhanced import EnhancedExcelExporter, ExcelFormat, ChartType
        assert EnhancedExcelExporter is not None
        assert ExcelFormat.XLSX is not None
        assert ChartType.BAR is not None

    def test_create_excel_exporter(self):
        """Test creating Excel exporter instance"""
        from core.excel_enhanced import EnhancedExcelExporter

        exporter = EnhancedExcelExporter()
        assert exporter is not None
        assert len(exporter.workbooks) == 0

    def test_create_workbook(self):
        """Test creating workbook"""
        from core.excel_enhanced import EnhancedExcelExporter, ExcelFormat

        exporter = EnhancedExcelExporter()
        workbook_id = exporter.create_workbook("Test Workbook", ExcelFormat.XLSX)

        assert workbook_id is not None
        assert workbook_id in exporter.workbooks

    def test_add_worksheet(self):
        """Test adding worksheet"""
        from core.excel_enhanced import EnhancedExcelExporter

        exporter = EnhancedExcelExporter()
        workbook_id = exporter.create_workbook("Test Workbook")

        result = exporter.add_worksheet(workbook_id, "Sheet1")
        assert result is True

    def test_write_cell_data(self):
        """Test writing cell data"""
        from core.excel_enhanced import EnhancedExcelExporter

        exporter = EnhancedExcelExporter()
        workbook_id = exporter.create_workbook("Test")
        exporter.add_worksheet(workbook_id, "Sheet1")

        result = exporter.write_cell(workbook_id, "Sheet1", "A1", "Test Value")
        assert result is True

    def test_write_formula(self):
        """Test writing formula"""
        from core.excel_enhanced import EnhancedExcelExporter

        exporter = EnhancedExcelExporter()
        workbook_id = exporter.create_workbook("Test")
        exporter.add_worksheet(workbook_id, "Sheet1")

        result = exporter.write_formula(workbook_id, "Sheet1", "B1", "=SUM(A1:A10)")
        assert result is True


class TestEnhancedPowerPointExporter:
    """Test Enhanced PowerPoint Exporter (v4.2)"""

    def test_import_powerpoint_exporter(self):
        """Test importing EnhancedPowerPointExporter"""
        from core.pptx_enhanced import (
            EnhancedPowerPointExporter,
            SlideLayout,
            TransitionType
        )
        assert EnhancedPowerPointExporter is not None
        assert SlideLayout.TITLE is not None
        assert TransitionType.FADE is not None

    def test_create_powerpoint_exporter(self):
        """Test creating PowerPoint exporter instance"""
        from core.pptx_enhanced import EnhancedPowerPointExporter, PresentationConfig

        config = PresentationConfig(
            slide_width=1920,
            slide_height=1080,
            theme="modern"
        )
        exporter = EnhancedPowerPointExporter(config)
        assert exporter is not None

    def test_create_presentation(self):
        """Test creating presentation"""
        from core.pptx_enhanced import EnhancedPowerPointExporter

        exporter = EnhancedPowerPointExporter()
        pres_id = exporter.create_presentation("Test Presentation")

        assert pres_id is not None
        assert pres_id in exporter.presentations

    def test_add_title_slide(self):
        """Test adding title slide"""
        from core.pptx_enhanced import EnhancedPowerPointExporter

        exporter = EnhancedPowerPointExporter()
        pres_id = exporter.create_presentation("Test")

        slide_idx = exporter.add_title_slide(
            pres_id,
            "Test Presentation",
            "Subtitle Here"
        )
        assert slide_idx == 0

    def test_add_content_slide(self):
        """Test adding content slide"""
        from core.pptx_enhanced import EnhancedPowerPointExporter

        exporter = EnhancedPowerPointExporter()
        pres_id = exporter.create_presentation("Test")

        slide_idx = exporter.add_content_slide(
            pres_id,
            "Content Title",
            ["Point 1", "Point 2", "Point 3"],
            bullet_points=True
        )
        assert slide_idx == 0

    def test_set_slide_transition(self):
        """Test setting slide transition"""
        from core.pptx_enhanced import (
            EnhancedPowerPointExporter,
            TransitionConfig,
            TransitionType
        )

        exporter = EnhancedPowerPointExporter()
        pres_id = exporter.create_presentation("Test")
        exporter.add_title_slide(pres_id, "Title", "Subtitle")

        transition = TransitionConfig(
            transition_type=TransitionType.FADE,
            duration=1.0,
            auto_advance=False
        )

        result = exporter.set_slide_transition(pres_id, 0, transition)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
