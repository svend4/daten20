# 📄 DOCX Export Guide

## Professional DOCX Document Generation

Comprehensive guide for using the DOCX exporter to create professional Word documents with custom branding, tables, images, and multi-level formatting.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Branding Configuration](#branding-configuration)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The DOCX exporter provides professional document generation capabilities:

### Features

✅ **Professional Formatting**
- Custom branding with logo and colors
- Headers and footers with page numbers
- Multiple heading levels
- Paragraph styles

✅ **Rich Content**
- Tables with custom styling
- Bullet and numbered lists
- Images with sizing control
- Info boxes and highlights

✅ **Document Types**
- Simple text documents
- Structured data reports
- Professional business reports
- Invoices and quotes
- Technical documentation

✅ **Customization**
- Custom branding configuration
- Font and color control
- Page layout options
- Style customization

---

## 📦 Installation

### 1. Install Dependencies

```bash
# Install python-docx
pip install python-docx>=0.8.11

# Or install from requirements.txt
pip install -r requirements.txt
```

### 2. Verify Installation

```python
from docx import Document
print("python-docx installed successfully!")
```

---

## 🚀 Quick Start

### Simple Export

```python
from src.core.docx_exporter import export_to_docx

# Export text content
content = """
# My Document

This is a simple document with **bold** text.

## Section 1
Some content here.
"""

export_to_docx(content, "output.docx", title="My Document")
```

### Structured Data Export

```python
from src.core.docx_exporter import export_to_docx

data = {
    "company": "Acme Corp",
    "employees": [
        {"name": "John Doe", "role": "CEO"},
        {"name": "Jane Smith", "role": "CTO"}
    ]
}

export_to_docx(data, "company_info.docx", title="Company Information")
```

### Professional Report

```python
from src.core.docx_exporter import DOCXExporter

exporter = DOCXExporter()
exporter.create_document("Quarterly Report")
exporter.add_title("Q4 2025 Report")
exporter.add_heading("Financial Results", level=1)
exporter.add_paragraph("Revenue increased by 25%...")
exporter.doc.save("report.docx")
```

---

## 📚 API Reference

### DOCXExporter Class

Main class for DOCX document generation.

#### Constructor

```python
exporter = DOCXExporter(branding: Optional[BrandingConfig] = None)
```

**Parameters:**
- `branding` (Optional[BrandingConfig]): Custom branding configuration

#### Methods

##### `create_document(title: str) -> Document`

Create a new document with branding.

```python
doc = exporter.create_document("My Document")
```

##### `add_title(text: str)`

Add document title (centered, large, colored).

```python
exporter.add_title("Annual Report 2025")
```

##### `add_heading(text: str, level: int = 1)`

Add heading (level 1 or 2).

```python
exporter.add_heading("Introduction", level=1)
exporter.add_heading("Background", level=2)
```

##### `add_paragraph(text: str, style: str = 'Custom Body')`

Add paragraph with specified style.

```python
exporter.add_paragraph("This is a paragraph of text.")
```

##### `add_bullet_list(items: List[str])`

Add bullet list.

```python
exporter.add_bullet_list([
    "First item",
    "Second item",
    "Third item"
])
```

##### `add_numbered_list(items: List[str])`

Add numbered list.

```python
exporter.add_numbered_list([
    "Step 1: Preparation",
    "Step 2: Execution",
    "Step 3: Review"
])
```

##### `add_table(data: List[List[str]], headers: Optional[List[str]] = None, style: str = 'Light Grid Accent 1')`

Add table with optional headers.

```python
exporter.add_table(
    data=[
        ["John", "Developer", "$80k"],
        ["Jane", "Designer", "$75k"]
    ],
    headers=["Name", "Role", "Salary"]
)
```

##### `add_image(image_path: str, width: Optional[float] = None)`

Add image (centered).

```python
exporter.add_image("logo.png", width=3.0)  # 3 inches wide
```

##### `add_page_break()`

Add page break.

```python
exporter.add_page_break()
```

##### `add_info_box(title: str, content: str)`

Add highlighted info box.

```python
exporter.add_info_box(
    "Important Notice",
    "Please read this carefully before proceeding."
)
```

##### `export_simple(content: str, output_path: str, title: str = "Document") -> bool`

Export simple text content.

```python
success = exporter.export_simple(
    content="# Hello\nThis is content",
    output_path="output.docx",
    title="My Doc"
)
```

##### `export_structured(data: Dict[str, Any], output_path: str, title: str = "Document") -> bool`

Export structured dictionary data.

```python
success = exporter.export_structured(
    data={"section1": "content", "items": ["a", "b"]},
    output_path="output.docx",
    title="Structured Doc"
)
```

##### `export_report(report_data: Dict[str, Any], output_path: str) -> bool`

Export professional report.

```python
report = {
    "title": "Annual Report",
    "summary": "Executive summary here",
    "sections": [
        {
            "title": "Section 1",
            "content": "Content here",
            "subsections": [...]
        }
    ],
    "conclusion": "Conclusion here"
}
success = exporter.export_report(report, "report.docx")
```

---

### BrandingConfig Class

Configuration for document branding.

```python
from src.core.docx_exporter import BrandingConfig
from docx.shared import RGBColor

branding = BrandingConfig()

# Company information
branding.company_name = "My Company"
branding.company_tagline = "Excellence in Service"
branding.logo_path = "path/to/logo.png"  # Optional

# Colors (RGB)
branding.primary_color = RGBColor(13, 110, 253)  # Blue
branding.secondary_color = RGBColor(108, 117, 125)  # Gray
branding.accent_color = RGBColor(25, 135, 84)  # Green

# Fonts
branding.header_font = 'Calibri'
branding.body_font = 'Calibri'
branding.font_size_title = 24
branding.font_size_heading1 = 18
branding.font_size_heading2 = 14
branding.font_size_body = 11

# Footer
branding.footer_text = "Generated by My System"
branding.show_page_numbers = True
branding.show_header = True
branding.show_footer = True
```

---

### Convenience Function

```python
from src.core.docx_exporter import export_to_docx

# Simple usage
success = export_to_docx(
    content="text or dict",
    output_path="output.docx",
    title="Document Title",
    branding=None  # Optional custom branding
)
```

---

## 💡 Examples

### Example 1: Simple Document

```python
from src.core.docx_exporter import DOCXExporter

exporter = DOCXExporter()
exporter.create_document("Simple Doc")

exporter.add_title("My First Document")
exporter.add_heading("Introduction", level=1)
exporter.add_paragraph("This is the introduction.")

exporter.add_heading("Main Content", level=1)
exporter.add_paragraph("This is the main content.")

exporter.doc.save("simple.docx")
```

### Example 2: Document with Table

```python
exporter = DOCXExporter()
exporter.create_document("Employee List")

exporter.add_title("Employee Directory")
exporter.add_heading("Active Employees", level=1)

exporter.add_table(
    data=[
        ["001", "Alice", "Engineering", "alice@company.com"],
        ["002", "Bob", "Sales", "bob@company.com"],
        ["003", "Carol", "HR", "carol@company.com"]
    ],
    headers=["ID", "Name", "Department", "Email"]
)

exporter.doc.save("employees.docx")
```

### Example 3: Invoice

```python
from datetime import datetime

exporter = DOCXExporter()
exporter.create_document("Invoice")

exporter.add_title("INVOICE")
exporter.add_paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
exporter.add_paragraph("Invoice #: INV-2025-001")

exporter.add_heading("Bill To", level=1)
exporter.add_paragraph("Customer Name")
exporter.add_paragraph("123 Customer Street")

exporter.add_heading("Items", level=1)
exporter.add_table(
    data=[
        ["Consulting Services", "10", "$150", "$1,500"],
        ["Software License", "1", "$500", "$500"]
    ],
    headers=["Description", "Qty", "Price", "Total"]
)

exporter.add_paragraph("Total: $2,000")
exporter.doc.save("invoice.docx")
```

### Example 4: Multi-Section Report

```python
exporter = DOCXExporter()
exporter.create_document("Technical Report")

# Section 1
exporter.add_title("Technical Documentation")
exporter.add_heading("1. Overview", level=1)
exporter.add_paragraph("This document describes the system architecture.")

exporter.add_page_break()

# Section 2
exporter.add_heading("2. Architecture", level=1)
exporter.add_paragraph("The system consists of multiple components:")
exporter.add_bullet_list([
    "Web Frontend",
    "API Backend",
    "Database Layer",
    "Cache Layer"
])

exporter.add_page_break()

# Section 3
exporter.add_heading("3. Installation", level=1)
exporter.add_numbered_list([
    "Download the package",
    "Extract files",
    "Run installer",
    "Configure settings",
    "Start application"
])

exporter.doc.save("technical_doc.docx")
```

### Example 5: Custom Branding

```python
from src.core.docx_exporter import BrandingConfig
from docx.shared import RGBColor

# Custom branding
branding = BrandingConfig()
branding.company_name = "TechCorp"
branding.primary_color = RGBColor(220, 38, 38)  # Red
branding.footer_text = "© 2025 TechCorp - Confidential"

# Create document with custom branding
exporter = DOCXExporter(branding)
exporter.create_document("Branded Document")
exporter.add_title("TechCorp Quarterly Report")
exporter.add_paragraph("This document uses custom branding.")

exporter.doc.save("branded.docx")
```

---

## 🎨 Branding Configuration

### Colors

Use RGB values for colors:

```python
from docx.shared import RGBColor

branding.primary_color = RGBColor(13, 110, 253)  # Blue #0d6efd
branding.secondary_color = RGBColor(108, 117, 125)  # Gray #6c757d
branding.accent_color = RGBColor(25, 135, 84)  # Green #198754
```

### Fonts

Recommended fonts:
- Calibri (default)
- Arial
- Times New Roman
- Georgia
- Verdana

```python
branding.header_font = 'Calibri'
branding.body_font = 'Calibri'
```

### Logo

Add your company logo:

```python
branding.logo_path = "path/to/logo.png"
```

Logo requirements:
- Format: PNG, JPG
- Recommended size: 300x150 pixels
- Will be displayed in header

---

## 🚀 Advanced Features

### Custom Styles

Create custom paragraph styles:

```python
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

para = exporter.add_paragraph("Custom styled text")
para.alignment = WD_ALIGN_PARAGRAPH.CENTER

for run in para.runs:
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 0, 0)
```

### Table Styling

Available table styles:
- Light Grid Accent 1 (default)
- Medium Grid 1
- Medium Grid 2
- Dark List Accent 1
- Colorful Grid
- And more...

```python
exporter.add_table(data, headers, style='Medium Grid 1')
```

### Page Setup

Modify page settings:

```python
from docx.shared import Inches

section = exporter.doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(1.0)
section.bottom_margin = Inches(1.0)
section.left_margin = Inches(1.0)
section.right_margin = Inches(1.0)
```

---

## ✅ Best Practices

### 1. Document Structure

Always follow this structure:
1. Title
2. Table of contents (if needed)
3. Sections with headings
4. Conclusion
5. Appendices (if needed)

### 2. Formatting

- Use heading levels consistently
- Don't skip heading levels (1 → 2, not 1 → 3)
- Keep paragraphs concise
- Use lists for multiple items
- Add page breaks between major sections

### 3. Tables

- Always include headers
- Keep columns to 5-6 maximum
- Use appropriate column widths
- Align numbers to the right
- Use consistent formatting

### 4. Branding

- Use consistent colors throughout
- Match company brand guidelines
- Include logo on first page
- Add footer with date and page numbers

### 5. Performance

- Process large documents in chunks
- Reuse exporter instance for multiple exports
- Close documents after saving
- Use appropriate image sizes

---

## 🔧 Troubleshooting

### Issue: ImportError for python-docx

**Problem:** Cannot import docx module

**Solution:**
```bash
pip install python-docx
```

### Issue: Logo not displaying

**Problem:** Logo path is incorrect or file doesn't exist

**Solution:**
```python
from pathlib import Path

logo_path = "path/to/logo.png"
if Path(logo_path).exists():
    branding.logo_path = logo_path
else:
    print(f"Logo not found: {logo_path}")
```

### Issue: Table formatting issues

**Problem:** Table doesn't look right

**Solution:** Try different table styles:
```python
# Try these styles
styles = [
    'Light Grid Accent 1',
    'Medium Grid 1',
    'Medium Grid 2',
    'Dark List Accent 1'
]

for style in styles:
    exporter.add_table(data, headers, style=style)
```

### Issue: Text encoding problems

**Problem:** Special characters not displaying

**Solution:** Ensure UTF-8 encoding:
```python
content = "Special chars: é, ñ, ü, ß"
exporter.add_paragraph(content)  # UTF-8 handled automatically
```

### Issue: Memory issues with large documents

**Problem:** Out of memory with huge documents

**Solution:** Process in batches:
```python
# Don't do this for large data
exporter.add_table(huge_data)

# Do this instead
BATCH_SIZE = 100
for i in range(0, len(huge_data), BATCH_SIZE):
    batch = huge_data[i:i+BATCH_SIZE]
    exporter.add_table(batch, headers if i == 0 else None)
```

---

## 📖 Additional Resources

### Documentation

- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Office Open XML Format](https://en.wikipedia.org/wiki/Office_Open_XML)
- [Word Document Specification](https://docs.microsoft.com/en-us/openspecs/)

### Related Modules

- `src/core/exporter.py` - Base exporter class
- `src/core/pdf_exporter.py` - PDF export functionality
- `src/core/excel_export.py` - Excel export functionality

### Examples

See `examples/docx_export_examples.py` for 8 complete examples:
1. Simple text export
2. Structured data export
3. Professional report
4. Custom branding
5. Tables and lists
6. Info boxes
7. Invoice document
8. Multi-section document

---

## 🎓 Learning Path

### Beginner

1. Start with `export_to_docx()` convenience function
2. Try simple text and dict exports
3. Experiment with basic formatting

### Intermediate

1. Use `DOCXExporter` class directly
2. Add tables and lists
3. Customize branding
4. Create multi-page documents

### Advanced

1. Custom paragraph styles
2. Complex table layouts
3. Conditional formatting
4. Template-based generation
5. Batch processing

---

## 📝 License

Part of Document Management System (DMS)

---

**Version:** 1.0.0
**Last Updated:** 2026-01-12
**Author:** Document Management System Team
