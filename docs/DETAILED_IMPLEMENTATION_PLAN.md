# 📋 Детальный план реализации следующих версий (v4.2+)

**Дата создания:** 2026-01-14
**Автор:** Development Team
**Статус:** Active Implementation Plan
**Версии:** v4.2, v4.3, v4.4, v5.0

---

## 🎯 Оглавление

1. [Обзор текущего состояния](#обзор-текущего-состояния)
2. [Phase 1: v4.2 - Production Hardening](#phase-1-v42---production-hardening)
3. [Phase 2: v4.3 - Advanced Analytics & BI](#phase-2-v43---advanced-analytics--bi)
4. [Phase 3: v4.4 - Microservices Architecture](#phase-3-v44---microservices-architecture)
5. [Phase 4: v5.0 - AI/ML Enhancements](#phase-4-v50---aiml-enhancements)
6. [Code Templates & Examples](#code-templates--examples)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)

---

## 📊 Обзор текущего состояния

### Текущая версия: v4.1
- ✅ 172/172 тестов проходят
- ✅ 241 исходных файлов Python
- ✅ ~131,000+ строк кода
- ✅ Production-ready статус
- ✅ Phase 2 Security завершена

### Существующие модули
```
src/
├── analytics/          # Частично реализовано (7 модулей)
├── ai/                 # AI services
├── bi/                 # BI engine
├── blockchain/         # Blockchain core
├── collaboration/      # Teams & realtime
├── compliance/         # GDPR, HIPAA, SOC2
├── core/              # Database, HTTPS, CSRF, Auth
├── enterprise/        # Multi-tenancy, billing
├── integrations/      # ERP, CRM, payments
├── ml/                # ML models (NER, classifier, etc.)
├── microservices/     # API gateway, service mesh
├── security/          # Security modules
└── web/               # Web application
```

---

# Phase 1: v4.2 - Production Hardening

**Цель:** Подготовить систему к production deployment с улучшенными экспортами, валидацией, CI/CD и тестовым покрытием.

**Срок:** 3-4 недели
**Приоритет:** P0 (Critical)
**Зависимости:** Нет

---

## Week 1: Enhanced Export Formats

### Day 1-2: PDF Export Enhancement

#### Задача 1.1: Улучшение PDF экспорта
**Файл:** `src/core/pdf_enhanced.py` (новый, ~600 строк)

**Шаг 1: Создание базового класса**
```python
"""
Enhanced PDF export module with advanced features.

Features:
- Multi-page support
- Headers & footers
- Table of contents
- Bookmarks
- Watermarks
- Digital signatures
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class EnhancedPDFExporter:
    """Enhanced PDF export with professional features."""

    def __init__(
        self,
        title: str = "Document",
        author: str = "DMS System",
        subject: str = "",
        pagesize=A4,
        add_toc: bool = True,
        add_headers: bool = True,
        add_footers: bool = True,
        watermark: Optional[str] = None
    ):
        """
        Initialize PDF exporter.

        Args:
            title: Document title
            author: Document author
            subject: Document subject
            pagesize: Page size (A4, LETTER, etc.)
            add_toc: Add table of contents
            add_headers: Add page headers
            add_footers: Add page footers
            watermark: Watermark text (optional)
        """
        self.title = title
        self.author = author
        self.subject = subject
        self.pagesize = pagesize
        self.add_toc = add_toc
        self.add_headers = add_headers
        self.add_footers = add_footers
        self.watermark = watermark

        self.styles = getSampleStyleSheet()
        self.story = []
        self.toc_entries = []

        # Custom styles
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

    def add_cover_page(self, subtitle: str = "", date: Optional[datetime] = None):
        """Add professional cover page."""
        if date is None:
            date = datetime.now()

        # Title
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(self.title, self.styles['CustomTitle']))

        # Subtitle
        if subtitle:
            self.story.append(Spacer(1, 0.5*inch))
            self.story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))

        # Author and date
        self.story.append(Spacer(1, 1*inch))
        author_text = f"<para align=center><i>{self.author}</i></para>"
        self.story.append(Paragraph(author_text, self.styles['Normal']))

        date_text = f"<para align=center>{date.strftime('%B %d, %Y')}</para>"
        self.story.append(Paragraph(date_text, self.styles['Normal']))

        self.story.append(PageBreak())

    def add_section(self, heading: str, content: str, level: int = 2):
        """
        Add a section with heading and content.

        Args:
            heading: Section heading
            content: Section content (can include HTML)
            level: Heading level (1-3)
        """
        # Add to TOC
        if self.add_toc and level <= 2:
            self.toc_entries.append((heading, level))

        # Add heading
        style_name = f'Heading{level}'
        if level == 2:
            style_name = 'SectionHeading'

        self.story.append(Paragraph(heading, self.styles[style_name]))

        # Add content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                self.story.append(Paragraph(para, self.styles['Normal']))
                self.story.append(Spacer(1, 0.2*inch))

    def add_table(
        self,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        col_widths: Optional[List[float]] = None,
        style: str = 'default'
    ):
        """
        Add a formatted table.

        Args:
            data: Table data (2D list)
            headers: Column headers
            col_widths: Column widths in inches
            style: Table style ('default', 'striped', 'minimal')
        """
        # Prepare data
        table_data = []
        if headers:
            table_data.append(headers)
        table_data.extend(data)

        # Create table
        if col_widths:
            col_widths = [w*inch for w in col_widths]
        table = Table(table_data, colWidths=col_widths)

        # Apply style
        if style == 'default':
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
        elif style == 'striped':
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ])
        else:  # minimal
            table_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ])

        table.setStyle(table_style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))

    def export(self, output_path: str) -> str:
        """
        Export PDF to file.

        Args:
            output_path: Output file path

        Returns:
            Path to generated PDF
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.pagesize,
                title=self.title,
                author=self.author,
                subject=self.subject
            )

            # Add TOC if requested
            if self.add_toc and self.toc_entries:
                self._add_table_of_contents()

            # Build PDF
            doc.build(
                self.story,
                onFirstPage=self._create_page_template,
                onLaterPages=self._create_page_template
            )

            logger.info(f"PDF exported successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise

    def export_to_bytes(self) -> bytes:
        """Export PDF to bytes (for downloads)."""
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            title=self.title,
            author=self.author,
            subject=self.subject
        )

        if self.add_toc and self.toc_entries:
            self._add_table_of_contents()

        doc.build(
            self.story,
            onFirstPage=self._create_page_template,
            onLaterPages=self._create_page_template
        )

        return buffer.getvalue()

    def _add_table_of_contents(self):
        """Generate table of contents."""
        self.story.insert(1, Paragraph("Table of Contents", self.styles['CustomTitle']))
        self.story.insert(2, Spacer(1, 0.3*inch))

        for i, (entry, level) in enumerate(self.toc_entries, 1):
            indent = "  " * (level - 1)
            toc_text = f"{indent}{i}. {entry}"
            self.story.insert(2 + i, Paragraph(toc_text, self.styles['Normal']))

        self.story.insert(2 + len(self.toc_entries) + 1, PageBreak())

    def _create_page_template(self, canvas_obj, doc):
        """Create page template with headers/footers."""
        canvas_obj.saveState()

        # Add watermark
        if self.watermark:
            canvas_obj.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
            canvas_obj.setFont('Helvetica-Bold', 60)
            canvas_obj.saveState()
            canvas_obj.translate(self.pagesize[0]/2, self.pagesize[1]/2)
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, self.watermark)
            canvas_obj.restoreState()

        # Add header
        if self.add_headers:
            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.drawString(inch, self.pagesize[1] - 0.75*inch, self.title)

        # Add footer
        if self.add_footers:
            canvas_obj.setFont('Helvetica', 9)
            page_num = canvas_obj.getPageNumber()
            footer_text = f"Page {page_num}"
            canvas_obj.drawCentredString(
                self.pagesize[0]/2,
                0.75*inch,
                footer_text
            )

        canvas_obj.restoreState()


# Example usage
def example_usage():
    """Example of how to use EnhancedPDFExporter."""
    exporter = EnhancedPDFExporter(
        title="Financial Report Q4 2025",
        author="Finance Department",
        subject="Quarterly Financial Analysis",
        add_toc=True,
        watermark="CONFIDENTIAL"
    )

    # Add cover page
    exporter.add_cover_page(subtitle="Quarterly Analysis")

    # Add sections
    exporter.add_section(
        "Executive Summary",
        "This report provides a comprehensive overview of Q4 2025 financial performance..."
    )

    # Add table
    exporter.add_table(
        data=[
            ["Q1", "$1.2M", "15%"],
            ["Q2", "$1.5M", "18%"],
            ["Q3", "$1.8M", "22%"],
            ["Q4", "$2.1M", "25%"],
        ],
        headers=["Quarter", "Revenue", "Growth"],
        col_widths=[2, 2, 2],
        style='striped'
    )

    # Export
    exporter.export("output/financial_report.pdf")
```

**Шаг 2: Тестирование**
Создать файл `tests/test_pdf_enhanced.py`:

```python
"""Tests for enhanced PDF export."""
import pytest
from src.core.pdf_enhanced import EnhancedPDFExporter
import os


class TestEnhancedPDFExporter:
    """Test suite for PDF export."""

    def test_basic_export(self, tmp_path):
        """Test basic PDF export."""
        output_file = tmp_path / "test.pdf"

        exporter = EnhancedPDFExporter(title="Test Document")
        exporter.add_cover_page()
        exporter.add_section("Test Section", "Test content")

        result = exporter.export(str(output_file))

        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_table_export(self, tmp_path):
        """Test table in PDF."""
        output_file = tmp_path / "table_test.pdf"

        exporter = EnhancedPDFExporter(title="Table Test")
        exporter.add_table(
            data=[["A", "B"], ["C", "D"]],
            headers=["Col1", "Col2"]
        )

        result = exporter.export(str(output_file))
        assert os.path.exists(result)

    def test_export_to_bytes(self):
        """Test export to bytes."""
        exporter = EnhancedPDFExporter(title="Bytes Test")
        exporter.add_section("Test", "Content")

        pdf_bytes = exporter.export_to_bytes()

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
```

**Шаг 3: Интеграция в API**
Обновить `src/api_v1.py`:

```python
from src.core.pdf_enhanced import EnhancedPDFExporter

@app.route('/api/v1/export/pdf/enhanced', methods=['POST'])
def export_pdf_enhanced():
    """Enhanced PDF export endpoint."""
    data = request.get_json()

    exporter = EnhancedPDFExporter(
        title=data.get('title', 'Document'),
        author=data.get('author', 'DMS System'),
        add_toc=data.get('add_toc', True),
        watermark=data.get('watermark')
    )

    # Add content from request
    if 'cover' in data:
        exporter.add_cover_page(
            subtitle=data['cover'].get('subtitle', '')
        )

    for section in data.get('sections', []):
        exporter.add_section(
            section['heading'],
            section['content']
        )

    # Export to bytes
    pdf_bytes = exporter.export_to_bytes()

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{data.get('filename', 'document')}.pdf"
    )
```

---

### Day 3-4: Excel Export Enhancement

#### Задача 1.2: Улучшение Excel экспорта
**Файл:** `src/core/excel_enhanced.py` (новый, ~500 строк)

**Реализация:**

```python
"""
Enhanced Excel export with advanced formatting.

Features:
- Multiple sheets
- Charts and graphs
- Conditional formatting
- Data validation
- Formulas
- Pivot tables
"""

from typing import List, Dict, Any, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, Alignment, Border, Side, PatternFill
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class EnhancedExcelExporter:
    """Enhanced Excel export with professional features."""

    def __init__(self, filename: str = "export.xlsx"):
        """Initialize Excel exporter."""
        self.workbook = Workbook()
        self.filename = filename
        # Remove default sheet
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']

        # Define styles
        self.header_font = Font(bold=True, color="FFFFFF", size=12)
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.header_alignment = Alignment(horizontal="center", vertical="center")

        self.border_thin = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

    def add_sheet(
        self,
        name: str,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        auto_filter: bool = True,
        freeze_panes: bool = True
    ) -> None:
        """
        Add a worksheet with data.

        Args:
            name: Sheet name
            data: Data to write (2D list)
            headers: Column headers
            auto_filter: Enable auto-filter
            freeze_panes: Freeze header row
        """
        ws = self.workbook.create_sheet(title=name)

        # Write headers
        if headers:
            ws.append(headers)
            # Style header row
            for cell in ws[1]:
                cell.font = self.header_font
                cell.fill = self.header_fill
                cell.alignment = self.header_alignment
                cell.border = self.border_thin

        # Write data
        for row in data:
            ws.append(row)

        # Apply borders to all cells
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row,
                                min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.border = self.border_thin

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Enable auto-filter
        if auto_filter and headers:
            ws.auto_filter.ref = ws.dimensions

        # Freeze panes
        if freeze_panes and headers:
            ws.freeze_panes = 'A2'

    def add_dataframe_sheet(
        self,
        name: str,
        df: pd.DataFrame,
        index: bool = False
    ) -> None:
        """
        Add sheet from pandas DataFrame.

        Args:
            name: Sheet name
            df: Pandas DataFrame
            index: Include index in export
        """
        ws = self.workbook.create_sheet(title=name)

        # Write DataFrame
        for r in dataframe_to_rows(df, index=index, header=True):
            ws.append(r)

        # Style first row (headers)
        for cell in ws[1]:
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.header_alignment
            cell.border = self.border_thin

        # Auto-filter
        ws.auto_filter.ref = ws.dimensions
        ws.freeze_panes = 'A2'

    def add_chart(
        self,
        sheet_name: str,
        chart_type: str,
        data_range: str,
        title: str,
        position: str = "E2"
    ) -> None:
        """
        Add chart to worksheet.

        Args:
            sheet_name: Sheet to add chart to
            chart_type: 'bar', 'line', or 'pie'
            data_range: Data range (e.g., "A1:B10")
            title: Chart title
            position: Chart position (cell reference)
        """
        ws = self.workbook[sheet_name]

        # Create chart
        if chart_type == 'bar':
            chart = BarChart()
        elif chart_type == 'line':
            chart = LineChart()
        elif chart_type == 'pie':
            chart = PieChart()
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")

        chart.title = title

        # Add data
        data = Reference(ws, range_string=data_range)
        chart.add_data(data, titles_from_data=True)

        # Add to worksheet
        ws.add_chart(chart, position)

    def add_conditional_formatting(
        self,
        sheet_name: str,
        range_str: str,
        rule_type: str = "colorscale"
    ) -> None:
        """
        Add conditional formatting.

        Args:
            sheet_name: Sheet name
            range_str: Cell range (e.g., "B2:B100")
            rule_type: 'colorscale' or 'threshold'
        """
        ws = self.workbook[sheet_name]

        if rule_type == "colorscale":
            rule = ColorScaleRule(
                start_type="min",
                start_color="63BE7B",  # Green
                mid_type="percentile",
                mid_value=50,
                mid_color="FFEB84",  # Yellow
                end_type="max",
                end_color="F8696B"   # Red
            )
            ws.conditional_formatting.add(range_str, rule)
        elif rule_type == "threshold":
            # Highlight cells > 100
            rule = CellIsRule(
                operator='greaterThan',
                formula=['100'],
                fill=PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            )
            ws.conditional_formatting.add(range_str, rule)

    def add_formula(
        self,
        sheet_name: str,
        cell: str,
        formula: str
    ) -> None:
        """
        Add formula to cell.

        Args:
            sheet_name: Sheet name
            cell: Cell reference (e.g., "C2")
            formula: Excel formula (e.g., "=SUM(A2:B2)")
        """
        ws = self.workbook[sheet_name]
        ws[cell] = formula

    def export(self, output_path: Optional[str] = None) -> str:
        """
        Save workbook to file.

        Args:
            output_path: Output file path (uses self.filename if None)

        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = self.filename

        try:
            self.workbook.save(output_path)
            logger.info(f"Excel exported successfully: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            raise


# Example usage
def example_usage():
    """Example of enhanced Excel export."""
    exporter = EnhancedExcelExporter("financial_report.xlsx")

    # Add revenue data
    revenue_data = [
        ["2023-Q1", 120000, 15],
        ["2023-Q2", 150000, 18],
        ["2023-Q3", 180000, 22],
        ["2023-Q4", 210000, 25],
    ]
    exporter.add_sheet(
        "Revenue",
        revenue_data,
        headers=["Quarter", "Revenue", "Growth %"]
    )

    # Add chart
    exporter.add_chart(
        "Revenue",
        "bar",
        "A1:B5",
        "Quarterly Revenue",
        "E2"
    )

    # Add conditional formatting
    exporter.add_conditional_formatting("Revenue", "C2:C5", "colorscale")

    # Export
    exporter.export()
```

**Тесты:** `tests/test_excel_enhanced.py`

```python
"""Tests for enhanced Excel export."""
import pytest
from src.core.excel_enhanced import EnhancedExcelExporter
import os
import pandas as pd


class TestEnhancedExcelExporter:
    """Test suite for Excel export."""

    def test_basic_export(self, tmp_path):
        """Test basic export."""
        output_file = tmp_path / "test.xlsx"

        exporter = EnhancedExcelExporter(str(output_file))
        exporter.add_sheet(
            "Test",
            [["A", "B"], ["C", "D"]],
            headers=["Col1", "Col2"]
        )

        result = exporter.export()
        assert os.path.exists(result)

    def test_dataframe_export(self, tmp_path):
        """Test DataFrame export."""
        output_file = tmp_path / "df_test.xlsx"

        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })

        exporter = EnhancedExcelExporter(str(output_file))
        exporter.add_dataframe_sheet("Data", df)

        result = exporter.export()
        assert os.path.exists(result)
```

---

### Day 5-6: PowerPoint Export Enhancement

#### Задача 1.3: Улучшение PowerPoint экспорта
**Файл:** `src/core/pptx_enhanced.py` (новый, ~450 строк)

Полная реализация в следующем разделе...

---

### Day 7: Comprehensive Validators

#### Задача 1.4: Система валидаторов
**Файл:** `src/core/validators.py` (новый, ~800 строк)

```python
"""
Comprehensive validation system.

Validates:
- Input data
- Configuration
- API requests
- File uploads
- Business rules
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime
import re
from email.utils import parseaddr
import phonenumbers
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __bool__(self):
        return self.is_valid


class Validator:
    """Base validator class."""

    def validate(self, value: Any) -> ValidationResult:
        """Validate value."""
        raise NotImplementedError


class StringValidator(Validator):
    """Validate string values."""

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        required: bool = True
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allowed_values = allowed_values
        self.required = required

    def validate(self, value: Any) -> ValidationResult:
        """Validate string."""
        errors = []
        warnings = []

        # Check required
        if value is None or value == "":
            if self.required:
                errors.append("Value is required")
            return ValidationResult(len(errors) == 0, errors, warnings)

        # Check type
        if not isinstance(value, str):
            errors.append(f"Expected string, got {type(value).__name__}")
            return ValidationResult(False, errors, warnings)

        # Check length
        if self.min_length and len(value) < self.min_length:
            errors.append(f"Minimum length is {self.min_length}, got {len(value)}")

        if self.max_length and len(value) > self.max_length:
            errors.append(f"Maximum length is {self.max_length}, got {len(value)}")

        # Check pattern
        if self.pattern and not re.match(self.pattern, value):
            errors.append(f"Value does not match pattern: {self.pattern}")

        # Check allowed values
        if self.allowed_values and value not in self.allowed_values:
            errors.append(f"Value must be one of: {', '.join(self.allowed_values)}")

        return ValidationResult(len(errors) == 0, errors, warnings)


class EmailValidator(Validator):
    """Validate email addresses."""

    def validate(self, value: Any) -> ValidationResult:
        """Validate email."""
        errors = []
        warnings = []

        if not value:
            errors.append("Email is required")
            return ValidationResult(False, errors, warnings)

        if not isinstance(value, str):
            errors.append("Email must be a string")
            return ValidationResult(False, errors, warnings)

        # Basic email validation
        name, addr = parseaddr(value)

        if not addr or '@' not in addr:
            errors.append("Invalid email format")
            return ValidationResult(False, errors, warnings)

        # Check for common issues
        if addr.startswith('@') or addr.endswith('@'):
            errors.append("Email cannot start or end with @")

        if '..' in addr:
            errors.append("Email cannot contain consecutive dots")

        # Validate domain
        try:
            local, domain = addr.rsplit('@', 1)
            if not domain or '.' not in domain:
                errors.append("Invalid email domain")
        except ValueError:
            errors.append("Invalid email format")

        return ValidationResult(len(errors) == 0, errors, warnings)


class PhoneValidator(Validator):
    """Validate phone numbers."""

    def __init__(self, region: str = "US"):
        self.region = region

    def validate(self, value: Any) -> ValidationResult:
        """Validate phone number."""
        errors = []
        warnings = []

        if not value:
            errors.append("Phone number is required")
            return ValidationResult(False, errors, warnings)

        try:
            phone = phonenumbers.parse(value, self.region)
            if not phonenumbers.is_valid_number(phone):
                errors.append("Invalid phone number")
        except phonenumbers.NumberParseException as e:
            errors.append(f"Invalid phone number: {str(e)}")

        return ValidationResult(len(errors) == 0, errors, warnings)


class NumberValidator(Validator):
    """Validate numeric values."""

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        positive_only: bool = False
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.positive_only = positive_only

    def validate(self, value: Any) -> ValidationResult:
        """Validate number."""
        errors = []
        warnings = []

        # Check type
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                errors.append(f"Expected number, got {type(value).__name__}")
                return ValidationResult(False, errors, warnings)

        # Check integer
        if self.integer_only and not isinstance(value, int) and not value.is_integer():
            errors.append("Value must be an integer")

        # Check positive
        if self.positive_only and value < 0:
            errors.append("Value must be positive")

        # Check range
        if self.min_value is not None and value < self.min_value:
            errors.append(f"Value must be at least {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            errors.append(f"Value must be at most {self.max_value}")

        return ValidationResult(len(errors) == 0, errors, warnings)


class DateValidator(Validator):
    """Validate dates."""

    def __init__(
        self,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
        allow_future: bool = True,
        allow_past: bool = True
    ):
        self.min_date = min_date
        self.max_date = max_date
        self.allow_future = allow_future
        self.allow_past = allow_past

    def validate(self, value: Any) -> ValidationResult:
        """Validate date."""
        errors = []
        warnings = []

        # Convert to datetime
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                errors.append("Invalid date format. Use ISO format (YYYY-MM-DD)")
                return ValidationResult(False, errors, warnings)

        if not isinstance(value, datetime):
            errors.append(f"Expected datetime, got {type(value).__name__}")
            return ValidationResult(False, errors, warnings)

        # Check future/past
        now = datetime.now()
        if not self.allow_future and value > now:
            errors.append("Future dates are not allowed")

        if not self.allow_past and value < now:
            errors.append("Past dates are not allowed")

        # Check range
        if self.min_date and value < self.min_date:
            errors.append(f"Date must be after {self.min_date.isoformat()}")

        if self.max_date and value > self.max_date:
            errors.append(f"Date must be before {self.max_date.isoformat()}")

        return ValidationResult(len(errors) == 0, errors, warnings)


class SchemaValidator(Validator):
    """Validate complex schemas."""

    def __init__(self, schema: Dict[str, Validator]):
        self.schema = schema

    def validate(self, value: Any) -> ValidationResult:
        """Validate against schema."""
        all_errors = []
        all_warnings = []

        if not isinstance(value, dict):
            return ValidationResult(False, ["Expected dictionary"], [])

        # Validate each field
        for field, validator in self.schema.items():
            field_value = value.get(field)
            result = validator.validate(field_value)

            if not result.is_valid:
                for error in result.errors:
                    all_errors.append(f"{field}: {error}")

            all_warnings.extend([f"{field}: {w}" for w in result.warnings])

        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)


# Convenience validators
def validate_email(email: str) -> ValidationResult:
    """Quick email validation."""
    return EmailValidator().validate(email)


def validate_phone(phone: str, region: str = "US") -> ValidationResult:
    """Quick phone validation."""
    return PhoneValidator(region).validate(phone)


def validate_positive_number(value: Union[int, float]) -> ValidationResult:
    """Quick positive number validation."""
    return NumberValidator(min_value=0, positive_only=True).validate(value)


# Example usage and tests
def example_usage():
    """Example validator usage."""
    # String validation
    name_validator = StringValidator(min_length=2, max_length=50, required=True)
    result = name_validator.validate("John Doe")
    print(f"Valid: {result.is_valid}, Errors: {result.errors}")

    # Email validation
    result = validate_email("user@example.com")
    print(f"Email valid: {result.is_valid}")

    # Schema validation
    user_schema = SchemaValidator({
        'name': StringValidator(min_length=2, max_length=100),
        'email': EmailValidator(),
        'age': NumberValidator(min_value=0, max_value=150, integer_only=True),
    })

    user_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    }

    result = user_schema.validate(user_data)
    print(f"User data valid: {result.is_valid}")
```

Это только начало детального плана. Документ продолжается с Week 2-4 и последующими фазами. Создать полный документ?

---

## 📝 Следующие секции (будут добавлены):

- Week 2: CI/CD Pipeline Setup
- Week 3: Test Coverage Enhancement
- Week 4: Documentation & Performance
- Phase 2: v4.3 Analytics & BI (детальная реализация 7 модулей)
- Phase 3: v4.4 Microservices
- Phase 4: v5.0 AI/ML

**Статус:** Документ в процессе создания (50% готовности)
