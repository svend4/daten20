#!/usr/bin/env python3
"""
Document OCR CLI Tool

Extract text from images and scanned documents using OCR.

Features:
- Multiple OCR engines (Tesseract, EasyOCR, PaddleOCR)
- Image preprocessing for better accuracy
- Batch processing
- PDF to image conversion
- Multiple output formats
- Confidence scoring

Usage:
    python doc-ocr.py image.png --output text.txt
    python doc-ocr.py scan.pdf --engine easyocr --language en
    python doc-ocr.py batch_dir/ --output-dir results/
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from src.core.logging_config import setup_logging
from src.ml.ocr import OCREngine, OCRManager, OCRResult

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class OCRCLITool:
    """CLI tool for OCR processing"""

    def __init__(self):
        self.processor: Optional[OCRManager] = None

    def initialize_processor(self, engine: str, languages: List[str]) -> None:
        """Initialize OCR processor with specified engine"""
        try:
            engine_enum = OCREngine[engine.upper()]
            self.processor = OCRManager(engine=engine_enum, languages=languages)
            logger.info(f"Initialized OCR processor with {engine} engine")
        except Exception as e:
            logger.error(f"Failed to initialize OCR processor: {e}")
            sys.exit(1)

    def process_single(
        self, input_path: str, output_path: Optional[str] = None, preprocess: bool = True, show_confidence: bool = False
    ) -> OCRResult:
        """Process single image/document"""
        logger.info(f"Processing: {input_path}")

        start_time = time.time()

        try:
            # Process with OCR
            result = self.processor.process_image(input_path, preprocess=preprocess)

            processing_time = time.time() - start_time
            result.processing_time = processing_time

            # Display results
            print("\n" + "=" * 80)
            print(f"OCR Results - {Path(input_path).name}")
            print("=" * 80)
            print(f"\nEngine: {result.engine}")
            print(f"Language: {result.language}")
            print(f"Confidence: {result.confidence:.2%}")
            print(f"Processing Time: {processing_time:.2f}s")
            print("\n" + "-" * 80)
            print("Extracted Text:")
            print("-" * 80)
            print(result.text)
            print("-" * 80)

            if show_confidence and result.word_confidences:
                print("\nWord Confidences:")
                words = result.text.split()
                for word, conf in zip(words, result.word_confidences):
                    print(f"  {word}: {conf:.2%}")

            # Save to output file if specified
            if output_path:
                output_format = Path(output_path).suffix.lower()

                if output_format == ".json":
                    self._save_json(result, output_path)
                elif output_format == ".txt":
                    self._save_text(result, output_path)
                else:
                    # Default to text
                    self._save_text(result, output_path)

                logger.info(f"Results saved to: {output_path}")

            return result

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise

    def process_batch(
        self, input_dir: str, output_dir: Optional[str] = None, preprocess: bool = True, recursive: bool = False
    ) -> List[OCRResult]:
        """Process multiple images/documents"""
        input_path = Path(input_dir)

        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            sys.exit(1)

        # Find all image files
        patterns = ["*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff", "*.bmp", "*.pdf"]
        image_files = []

        for pattern in patterns:
            if recursive:
                image_files.extend(input_path.rglob(pattern))
            else:
                image_files.extend(input_path.glob(pattern))

        if not image_files:
            logger.warning(f"No image files found in {input_dir}")
            return []

        logger.info(f"Found {len(image_files)} files to process")

        results = []
        output_path_obj = Path(output_dir) if output_dir else None

        if output_path_obj:
            output_path_obj.mkdir(parents=True, exist_ok=True)

        # Process each file
        for idx, image_file in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}] Processing: {image_file.name}")

            try:
                result = self.processor.process_image(str(image_file), preprocess=preprocess)
                results.append(result)

                # Save individual result
                if output_path_obj:
                    output_file = output_path_obj / f"{image_file.stem}.txt"
                    self._save_text(result, str(output_file))

                print(f"  ✓ Success - Confidence: {result.confidence:.2%}")

            except Exception as e:
                logger.error(f"Failed to process {image_file.name}: {e}")
                print(f"  ✗ Failed: {e}")

        # Save batch summary
        if output_path_obj:
            summary_file = output_path_obj / "ocr_summary.json"
            self._save_batch_summary(results, str(summary_file))

        print(f"\n{'=' * 80}")
        print(f"Batch Processing Complete")
        print(f"{'=' * 80}")
        print(f"Total Files: {len(image_files)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(image_files) - len(results)}")
        print(f"Average Confidence: {sum(r.confidence for r in results) / len(results):.2%}" if results else "N/A")

        return results

    def _save_text(self, result: OCRResult, output_path: str) -> None:
        """Save OCR result as plain text"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text)

    def _save_json(self, result: OCRResult, output_path: str) -> None:
        """Save OCR result as JSON"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    def _save_batch_summary(self, results: List[OCRResult], output_path: str) -> None:
        """Save batch processing summary"""
        summary = {
            "total_files": len(results),
            "average_confidence": sum(r.confidence for r in results) / len(results) if results else 0,
            "total_text_length": sum(len(r.text) for r in results),
            "results": [r.to_dict() for r in results],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Document OCR CLI Tool - Extract text from images and scanned documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract text from single image
  python doc-ocr.py image.png --output text.txt

  # Use specific OCR engine
  python doc-ocr.py scan.pdf --engine easyocr --language en

  # Process with preprocessing
  python doc-ocr.py photo.jpg --preprocess --show-confidence

  # Batch process directory
  python doc-ocr.py batch_dir/ --output-dir results/ --recursive

  # Use PaddleOCR for better accuracy
  python doc-ocr.py document.pdf --engine paddleocr --languages en,de

  # Show word-level confidence scores
  python doc-ocr.py image.png --show-confidence
        """,
    )

    parser.add_argument("input", help="Input image/document file or directory for batch processing")

    parser.add_argument("-o", "--output", help="Output file path (default: print to console)")

    parser.add_argument(
        "-e",
        "--engine",
        choices=["tesseract", "easyocr", "paddleocr", "auto"],
        default="auto",
        help="OCR engine to use (default: auto)",
    )

    parser.add_argument(
        "-l",
        "--languages",
        default="en",
        help="Languages for OCR (comma-separated, default: en). Examples: en, en,de, en,ru",
    )

    parser.add_argument("--no-preprocess", action="store_true", help="Disable image preprocessing")

    parser.add_argument("--show-confidence", action="store_true", help="Show word-level confidence scores")

    parser.add_argument("--batch", action="store_true", help="Process directory in batch mode")

    parser.add_argument("--output-dir", help="Output directory for batch processing")

    parser.add_argument("--recursive", action="store_true", help="Recursively process subdirectories")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Initialize tool
    tool = OCRCLITool()

    # Parse languages
    languages = [lang.strip() for lang in args.languages.split(",")]

    # Initialize processor
    tool.initialize_processor(args.engine, languages)

    # Process input
    input_path = Path(args.input)

    try:
        if args.batch or (input_path.is_dir() and not args.output):
            # Batch mode
            if not input_path.is_dir():
                logger.error(f"Batch mode requires directory input: {args.input}")
                sys.exit(1)

            tool.process_batch(
                args.input, output_dir=args.output_dir, preprocess=not args.no_preprocess, recursive=args.recursive
            )
        else:
            # Single file mode
            if not input_path.exists():
                logger.error(f"Input file not found: {args.input}")
                sys.exit(1)

            tool.process_single(
                args.input, output_path=args.output, preprocess=not args.no_preprocess, show_confidence=args.show_confidence
            )

        logger.info("OCR processing completed successfully")

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
