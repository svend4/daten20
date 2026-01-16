"""
Advanced PDF Features Module

Additional PDF generation features:
- Password protection
- Watermarks
- Metadata embedding
- Table of Contents
- Async generation
- Template caching
- Batch processing
- Progress tracking
"""

import asyncio
import hashlib
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

try:
    from PyPDF2 import PdfReader, PdfWriter

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available. Password protection and advanced features disabled.")

logger = logging.getLogger("dms.pdf_advanced")


class PDFProtectionConfig:
    """Configuration for PDF security and protection."""

    def __init__(self):
        self.user_password: Optional[str] = None  # Password to open PDF
        self.owner_password: Optional[str] = None  # Password for full access
        self.allow_printing: bool = True
        self.allow_modification: bool = False
        self.allow_copying: bool = False
        self.allow_annotations: bool = True


class PDFMetadata:
    """PDF metadata configuration."""

    def __init__(self):
        self.title: str = "Document"
        self.author: str = "Document Management System"
        self.subject: str = "Generated Report"
        self.keywords: List[str] = []
        self.creator: str = "DMS PDF Exporter v3.0"
        self.producer: str = "ReportLab PDF Library"
        self.creation_date: datetime = datetime.now()
        self.modification_date: datetime = datetime.now()
        self.custom_properties: Dict[str, str] = {}


class WatermarkConfig:
    """Configuration for PDF watermark."""

    def __init__(self):
        self.text: str = "CONFIDENTIAL"
        self.font_name: str = "Helvetica-Bold"
        self.font_size: int = 60
        self.color: colors.Color = colors.Color(0.9, 0.9, 0.9, alpha=0.3)
        self.rotation: int = 45  # degrees
        self.position: str = "center"  # 'center', 'diagonal'


class TemplateCache:
    """Cache for PDF templates to improve performance."""

    def __init__(self, max_size: int = 100):
        """
        Initialize template cache.

        Args:
            max_size: Maximum number of cached templates
        """
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.access_count: Dict[str, int] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get template from cache.

        Args:
            key: Cache key

        Returns:
            Cached template or None
        """
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            logger.debug(f"Cache hit for {key}")
            return self.cache[key]

        logger.debug(f"Cache miss for {key}")
        return None

    def set(self, key: str, value: Any):
        """
        Store template in cache.

        Args:
            key: Cache key
            value: Template to cache
        """
        if len(self.cache) >= self.max_size:
            # Remove least accessed item
            least_used = min(self.access_count.items(), key=lambda x: x[1])[0]
            del self.cache[least_used]
            del self.access_count[least_used]
            logger.debug(f"Evicted {least_used} from cache")

        self.cache[key] = value
        self.access_count[key] = 0
        logger.debug(f"Cached {key}")

    def clear(self):
        """Clear all cached templates."""
        self.cache.clear()
        self.access_count.clear()
        logger.info("Template cache cleared")


class AdvancedPDFFeatures:
    """Advanced PDF features for enhanced PDF generation."""

    def __init__(self):
        """Initialize advanced features."""
        self.template_cache = TemplateCache()

    def add_password_protection(
        self, input_path: str, output_path: str, protection_config: PDFProtectionConfig
    ) -> bool:
        """
        Add password protection to existing PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path to output protected PDF
            protection_config: Protection configuration

        Returns:
            True if successful
        """
        if not PYPDF2_AVAILABLE:
            logger.error("PyPDF2 not available for password protection")
            return False

        try:
            # Read existing PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add encryption
            writer.encrypt(
                user_password=protection_config.user_password or "",
                owner_password=protection_config.owner_password or "",
                permissions_flag=(
                    (4 if protection_config.allow_printing else 0)
                    | (8 if protection_config.allow_modification else 0)
                    | (16 if protection_config.allow_copying else 0)
                    | (32 if protection_config.allow_annotations else 0)
                ),
            )

            # Write protected PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"Added password protection to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error adding password protection: {e}")
            return False

    def add_watermark(self, input_path: str, output_path: str, watermark_config: WatermarkConfig) -> bool:
        """
        Add watermark to existing PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF with watermark
            watermark_config: Watermark configuration

        Returns:
            True if successful
        """
        if not PYPDF2_AVAILABLE:
            logger.error("PyPDF2 not available for watermark")
            return False

        try:
            # Create watermark PDF
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=A4)

            # Set watermark properties
            c.setFont(watermark_config.font_name, watermark_config.font_size)
            c.setFillColor(watermark_config.color)

            # Calculate position
            width, height = A4

            if watermark_config.position == "center":
                x, y = width / 2, height / 2
            else:  # diagonal
                x, y = width / 2, height / 2

            # Add text with rotation
            c.saveState()
            c.translate(x, y)
            c.rotate(watermark_config.rotation)
            c.drawCentredString(0, 0, watermark_config.text)
            c.restoreState()

            c.save()
            watermark_buffer.seek(0)

            # Read PDFs
            reader = PdfReader(input_path)
            watermark_reader = PdfReader(watermark_buffer)
            watermark_page = watermark_reader.pages[0]

            writer = PdfWriter()

            # Apply watermark to all pages
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)

            # Write output
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"Added watermark to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
            return False

    def embed_metadata(self, input_path: str, output_path: str, metadata: PDFMetadata) -> bool:
        """
        Embed metadata in PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF with metadata
            metadata: Metadata to embed

        Returns:
            True if successful
        """
        if not PYPDF2_AVAILABLE:
            logger.error("PyPDF2 not available for metadata embedding")
            return False

        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add metadata
            writer.add_metadata(
                {
                    "/Title": metadata.title,
                    "/Author": metadata.author,
                    "/Subject": metadata.subject,
                    "/Keywords": ", ".join(metadata.keywords),
                    "/Creator": metadata.creator,
                    "/Producer": metadata.producer,
                    "/CreationDate": metadata.creation_date.strftime("D:%Y%m%d%H%M%S"),
                    "/ModDate": metadata.modification_date.strftime("D:%Y%m%d%H%M%S"),
                }
            )

            # Add custom properties
            for key, value in metadata.custom_properties.items():
                writer.add_metadata({f"/{key}": value})

            # Write output
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"Embedded metadata in {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error embedding metadata: {e}")
            return False

    async def generate_pdf_async(
        self, generator_func: Callable, output_path: str, *args, **kwargs
    ) -> bool:
        """
        Generate PDF asynchronously.

        Args:
            generator_func: Function to generate PDF
            output_path: Output file path
            *args: Arguments for generator function
            **kwargs: Keyword arguments for generator function

        Returns:
            True if successful
        """

        def sync_generator():
            return generator_func(output_path, *args, **kwargs)

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, sync_generator)

            logger.info(f"Async PDF generation completed: {output_path}")
            return result

        except Exception as e:
            logger.error(f"Error in async PDF generation: {e}")
            return False

    async def batch_process_pdfs(
        self, tasks: List[Dict[str, Any]], progress_callback: Optional[Callable] = None
    ) -> Dict[str, bool]:
        """
        Process multiple PDFs in batch asynchronously.

        Args:
            tasks: List of task dictionaries with 'func', 'output', and 'args'
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary of output_path -> success status
        """
        results = {}
        total = len(tasks)

        for i, task in enumerate(tasks):
            func = task["func"]
            output = task["output"]
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})

            try:
                success = await self.generate_pdf_async(func, output, *args, **kwargs)
                results[output] = success

                if progress_callback:
                    progress_callback(i + 1, total, output, success)

            except Exception as e:
                logger.error(f"Error processing {output}: {e}")
                results[output] = False

        logger.info(f"Batch processing completed: {sum(results.values())}/{total} successful")
        return results

    def generate_cache_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.

        Args:
            *args: Arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key hash
        """
        # Create string representation
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)

        # Generate hash
        return hashlib.md5(key_string.encode()).hexdigest()

    def create_toc_entry(self, text: str, level: int = 0) -> Paragraph:
        """
        Create table of contents entry.

        Args:
            text: Entry text
            level: Indentation level

        Returns:
            Formatted paragraph for TOC
        """
        from reportlab.lib.styles import getSampleStyleSheet

        styles = getSampleStyleSheet()

        # Indent based on level
        indent = level * 20

        style = styles["Normal"]
        style.leftIndent = indent

        return Paragraph(text, style)


# Convenience functions
def protect_pdf(input_path: str, output_path: str, user_password: str, owner_password: Optional[str] = None) -> bool:
    """
    Quick function to password-protect a PDF.

    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        user_password: User password (to open)
        owner_password: Owner password (optional)

    Returns:
        True if successful
    """
    features = AdvancedPDFFeatures()
    config = PDFProtectionConfig()
    config.user_password = user_password
    config.owner_password = owner_password or user_password

    return features.add_password_protection(input_path, output_path, config)


def watermark_pdf(input_path: str, output_path: str, watermark_text: str = "CONFIDENTIAL") -> bool:
    """
    Quick function to add watermark to PDF.

    Args:
        input_path: Input PDF path
        output_path: Output PDF path
        watermark_text: Watermark text

    Returns:
        True if successful
    """
    features = AdvancedPDFFeatures()
    config = WatermarkConfig()
    config.text = watermark_text

    return features.add_watermark(input_path, output_path, config)


async def generate_pdfs_batch(pdf_tasks: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Quick function to generate multiple PDFs in batch.

    Args:
        pdf_tasks: List of PDF generation tasks

    Returns:
        Dictionary of results
    """
    features = AdvancedPDFFeatures()

    def progress_callback(current, total, output, success):
        status = "✓" if success else "✗"
        logger.info(f"[{current}/{total}] {status} {output}")

    return await features.batch_process_pdfs(pdf_tasks, progress_callback)
