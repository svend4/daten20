"""
File Conversion Service

Document, image, and spreadsheet format conversion with PDF generation.

Part of v3.7 Advanced Integrations implementation.
"""

import asyncio
import base64
import io
import logging
import os
import zipfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False


class FileFormat(Enum):
    """File formats."""

    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "md"
    PNG = "png"
    JPG = "jpg"
    XLSX = "xlsx"
    CSV = "csv"
    ZIP = "zip"


@dataclass
class ConversionResult:
    """Conversion result."""

    output_path: str
    format: FileFormat
    size: int
    success: bool


class FileConverter:
    """Main file converter."""

    async def convert(self, input_path: str, output_format: str, **kwargs) -> ConversionResult:
        """Convert file to different format."""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Determine input format
        input_ext = Path(input_path).suffix.lstrip('.')
        output_path = input_path.rsplit(".", 1)[0] + f".{output_format}"

        # Markdown to HTML conversion
        if input_ext in ['md', 'markdown'] and output_format == 'html':
            if not HAS_MARKDOWN:
                raise ImportError("markdown library required for markdown conversion. Install: pip install markdown")

            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Converted Document</title></head>
<body>{html_content}</body>
</html>""")

            size = os.path.getsize(output_path)
            logger.info(f"Converted markdown to HTML: {input_path} -> {output_path}")
            return ConversionResult(output_path=output_path, format=FileFormat.HTML, size=size, success=True)

        # HTML to PDF conversion
        elif input_ext == 'html' and output_format == 'pdf':
            return await self.html_to_pdf_from_file(input_path, output_path)

        # Base64 encoding for images
        elif input_ext in ['png', 'jpg', 'jpeg'] and output_format == 'base64':
            with open(input_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')

            with open(output_path + '.txt', 'w') as f:
                f.write(encoded)

            size = os.path.getsize(output_path + '.txt')
            logger.info(f"Encoded image to base64: {input_path}")
            return ConversionResult(output_path=output_path + '.txt', format=FileFormat.PNG, size=size, success=True)

        else:
            raise NotImplementedError(
                f"Conversion from {input_ext} to {output_format} not implemented. "
                f"Supported: markdown->html, html->pdf (requires weasyprint), images->base64"
            )

    async def html_to_pdf_from_file(self, html_path: str, output_path: str) -> ConversionResult:
        """Convert HTML file to PDF."""
        if not HAS_WEASYPRINT:
            raise ImportError(
                "weasyprint library required for PDF generation. Install: pip install weasyprint"
            )

        HTML(filename=html_path).write_pdf(output_path)
        size = os.path.getsize(output_path)

        logger.info(f"Generated PDF from HTML file: {html_path} -> {output_path}")
        return ConversionResult(output_path=output_path, format=FileFormat.PDF, size=size, success=True)

    async def html_to_pdf(self, html_content: str, output_path: str, **kwargs) -> ConversionResult:
        """Convert HTML content to PDF."""
        if not HAS_WEASYPRINT:
            # Fallback: save HTML content to file
            html_file = output_path.replace('.pdf', '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            size = os.path.getsize(html_file)
            logger.warning(
                f"weasyprint not available - saved as HTML instead. "
                f"Install weasyprint for PDF conversion: pip install weasyprint"
            )
            return ConversionResult(output_path=html_file, format=FileFormat.HTML, size=size, success=False)

        # Generate PDF using weasyprint
        HTML(string=html_content, base_url=kwargs.get('base_url', '')).write_pdf(output_path)
        size = os.path.getsize(output_path)

        logger.info(f"Generated PDF from HTML content: {output_path}")
        return ConversionResult(output_path=output_path, format=FileFormat.PDF, size=size, success=True)

    async def create_archive(self, files: List[str], output_path: str, format: str = "zip") -> ConversionResult:
        """Create archive from files."""
        if format != "zip":
            raise NotImplementedError(f"Archive format '{format}' not supported. Currently supports: zip")

        # Verify all input files exist
        missing_files = [f for f in files if not os.path.exists(f)]
        if missing_files:
            raise FileNotFoundError(f"Files not found: {missing_files}")

        # Create ZIP archive
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                # Add file with relative path
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)
                logger.debug(f"Added to archive: {file_path} as {arcname}")

        size = os.path.getsize(output_path)
        logger.info(f"Created ZIP archive with {len(files)} files: {output_path} ({size} bytes)")

        return ConversionResult(output_path=output_path, format=FileFormat.ZIP, size=size, success=True)

    async def markdown_to_html(self, md_content: str, output_path: str) -> ConversionResult:
        """Convert Markdown content to HTML."""
        if not HAS_MARKDOWN:
            raise ImportError("markdown library required. Install: pip install markdown")

        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Converted Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        size = os.path.getsize(output_path)
        logger.info(f"Converted markdown content to HTML: {output_path}")

        return ConversionResult(output_path=output_path, format=FileFormat.HTML, size=size, success=True)


_file_converter: Optional[FileConverter] = None


def get_file_converter() -> FileConverter:
    """Get file converter."""
    global _file_converter
    if _file_converter is None:
        _file_converter = FileConverter()
    return _file_converter
