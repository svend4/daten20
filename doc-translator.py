#!/usr/bin/env python3
"""
Document Translator CLI Tool

Translate documents between 100+ languages using multiple backends.

Features:
- Multiple translation backends (Google Translate, DeepL, Argos, LibreTranslate)
- Automatic language detection
- Batch translation
- Translation caching for performance
- Document format preservation
- Quality scoring

Usage:
    python doc-translator.py document.txt --target es --output translated.txt
    python doc-translator.py text.pdf --source en --target de --backend deepl
    python doc-translator.py batch_dir/ --target fr --output-dir translated/
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from src.core.logging_config import setup_logging
from src.ml.document_translator import (
    DocumentTranslator,
    TranslationBackend,
    TranslationResult,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Common language codes
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "ro": "Romanian",
    "el": "Greek",
    "he": "Hebrew",
    "id": "Indonesian",
    "ms": "Malay",
    "uk": "Ukrainian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sr": "Serbian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "et": "Estonian",
}


class TranslatorCLITool:
    """CLI tool for document translation"""

    def __init__(self):
        self.translator: Optional[DocumentTranslator] = None

    def initialize_translator(self, backend: str, api_key: Optional[str] = None) -> None:
        """Initialize translator with specified backend"""
        try:
            backend_enum = TranslationBackend[backend.upper()]
            self.translator = DocumentTranslator(backend=backend_enum, api_key=api_key)
            logger.info(f"Initialized translator with {backend} backend")
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            sys.exit(1)

    def detect_language(self, text: str) -> None:
        """Detect language of text"""
        try:
            result = self.translator.detect_language(text)

            print("\n" + "=" * 80)
            print("Language Detection")
            print("=" * 80)
            print(f"\nDetected Language: {result.language} ({LANGUAGE_NAMES.get(result.language, 'Unknown')})")
            print(f"Confidence: {result.confidence:.2%}")

            if result.alternatives:
                print("\nAlternative Languages:")
                for lang, conf in result.alternatives[:5]:
                    print(f"  {lang} ({LANGUAGE_NAMES.get(lang, 'Unknown')}): {conf:.2%}")

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise

    def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        output_path: Optional[str] = None,
        show_details: bool = False,
    ) -> TranslationResult:
        """Translate text"""
        logger.info(f"Translating to {target_lang}")

        start_time = time.time()

        try:
            # Translate
            result = self.translator.translate(text=text, target_language=target_lang, source_language=source_lang)

            processing_time = time.time() - start_time

            # Display results
            print("\n" + "=" * 80)
            print("Translation Results")
            print("=" * 80)
            print(f"\nSource Language: {result.source_language} ({LANGUAGE_NAMES.get(result.source_language, 'Unknown')})")
            print(f"Target Language: {result.target_language} ({LANGUAGE_NAMES.get(result.target_language, 'Unknown')})")
            print(f"Backend: {result.backend}")
            print(f"Confidence: {result.confidence:.2%}")
            print(f"Processing Time: {processing_time:.2f}s")

            if show_details and result.quality_score > 0:
                print(f"Quality Score: {result.quality_score:.2f}")

            print("\n" + "-" * 80)
            print("Original Text:")
            print("-" * 80)
            print(text[:500] + ("..." if len(text) > 500 else ""))
            print("\n" + "-" * 80)
            print("Translated Text:")
            print("-" * 80)
            print(result.translated_text)
            print("-" * 80)

            # Save to output file if specified
            if output_path:
                output_format = Path(output_path).suffix.lower()

                if output_format == ".json":
                    self._save_json(result, output_path)
                elif output_format == ".txt":
                    self._save_text(result.translated_text, output_path)
                else:
                    # Default to text
                    self._save_text(result.translated_text, output_path)

                logger.info(f"Translation saved to: {output_path}")

            return result

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def translate_file(
        self,
        input_path: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        output_path: Optional[str] = None,
        show_details: bool = False,
    ) -> TranslationResult:
        """Translate document file"""
        logger.info(f"Translating file: {input_path}")

        # Read file
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            logger.error(f"Unable to read file as UTF-8: {input_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            sys.exit(1)

        # Translate
        result = self.translate_text(text, target_lang, source_lang, output_path, show_details)

        return result

    def translate_batch(
        self,
        input_dir: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        output_dir: Optional[str] = None,
        recursive: bool = False,
    ) -> List[TranslationResult]:
        """Translate multiple documents"""
        input_path = Path(input_dir)

        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            sys.exit(1)

        # Find all text files
        patterns = ["*.txt", "*.md", "*.rst", "*.text"]
        text_files = []

        for pattern in patterns:
            if recursive:
                text_files.extend(input_path.rglob(pattern))
            else:
                text_files.extend(input_path.glob(pattern))

        if not text_files:
            logger.warning(f"No text files found in {input_dir}")
            return []

        logger.info(f"Found {len(text_files)} files to translate")

        results = []
        output_path_obj = Path(output_dir) if output_dir else None

        if output_path_obj:
            output_path_obj.mkdir(parents=True, exist_ok=True)

        # Process each file
        for idx, text_file in enumerate(text_files, 1):
            print(f"\n[{idx}/{len(text_files)}] Translating: {text_file.name}")

            try:
                # Read file
                with open(text_file, "r", encoding="utf-8") as f:
                    text = f.read()

                # Translate
                result = self.translator.translate(text=text, target_language=target_lang, source_language=source_lang)

                results.append(result)

                # Save individual result
                if output_path_obj:
                    output_file = output_path_obj / f"{text_file.stem}_{target_lang}{text_file.suffix}"
                    self._save_text(result.translated_text, str(output_file))

                print(f"  ✓ Success - Confidence: {result.confidence:.2%}")

            except Exception as e:
                logger.error(f"Failed to translate {text_file.name}: {e}")
                print(f"  ✗ Failed: {e}")

        # Save batch summary
        if output_path_obj:
            summary_file = output_path_obj / "translation_summary.json"
            self._save_batch_summary(results, target_lang, str(summary_file))

        print(f"\n{'=' * 80}")
        print(f"Batch Translation Complete")
        print(f"{'=' * 80}")
        print(f"Total Files: {len(text_files)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(text_files) - len(results)}")
        print(f"Average Confidence: {sum(r.confidence for r in results) / len(results):.2%}" if results else "N/A")

        return results

    def _save_text(self, text: str, output_path: str) -> None:
        """Save text to file"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

    def _save_json(self, result: TranslationResult, output_path: str) -> None:
        """Save translation result as JSON"""
        data = {
            "source_text": result.source_text,
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
            "backend": result.backend,
            "confidence": result.confidence,
            "quality_score": result.quality_score,
            "metadata": result.metadata,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_batch_summary(self, results: List[TranslationResult], target_lang: str, output_path: str) -> None:
        """Save batch translation summary"""
        summary = {
            "total_files": len(results),
            "target_language": target_lang,
            "average_confidence": sum(r.confidence for r in results) / len(results) if results else 0,
            "total_characters_translated": sum(len(r.translated_text) for r in results),
            "results": [
                {
                    "source_language": r.source_language,
                    "target_language": r.target_language,
                    "backend": r.backend,
                    "confidence": r.confidence,
                    "quality_score": r.quality_score,
                }
                for r in results
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Document Translator CLI Tool - Translate documents between 100+ languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate text file to Spanish
  python doc-translator.py document.txt --target es --output translated_es.txt

  # Translate with specific source language
  python doc-translator.py text.txt --source en --target de --output german.txt

  # Use DeepL for higher quality
  python doc-translator.py document.txt --target fr --backend deepl --api-key YOUR_KEY

  # Detect language of text
  python doc-translator.py text.txt --detect

  # Batch translate directory
  python doc-translator.py docs/ --target es --output-dir translated/ --batch

  # Show translation details
  python doc-translator.py file.txt --target ja --show-details

Common Languages:
  en (English), es (Spanish), fr (French), de (German), it (Italian)
  pt (Portuguese), ru (Russian), zh (Chinese), ja (Japanese), ko (Korean)
  ar (Arabic), hi (Hindi), nl (Dutch), pl (Polish), tr (Turkish)
        """,
    )

    parser.add_argument("input", help="Input text file or directory for batch translation")

    parser.add_argument("-t", "--target", help="Target language code (e.g., es, fr, de)")

    parser.add_argument("-s", "--source", help="Source language code (optional, auto-detect if not specified)")

    parser.add_argument("-o", "--output", help="Output file path (default: print to console)")

    parser.add_argument(
        "-b",
        "--backend",
        choices=["google", "deepl", "argos", "libretranslate", "auto"],
        default="auto",
        help="Translation backend (default: auto)",
    )

    parser.add_argument("--api-key", help="API key for paid backends (DeepL, etc.)")

    parser.add_argument("--detect", action="store_true", help="Detect language instead of translating")

    parser.add_argument("--show-details", action="store_true", help="Show detailed translation information")

    parser.add_argument("--batch", action="store_true", help="Process directory in batch mode")

    parser.add_argument("--output-dir", help="Output directory for batch translation")

    parser.add_argument("--recursive", action="store_true", help="Recursively process subdirectories")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Validate arguments
    if not args.detect and not args.target:
        parser.error("--target is required unless using --detect")

    # Initialize tool
    tool = TranslatorCLITool()

    # Initialize translator
    tool.initialize_translator(args.backend, api_key=args.api_key)

    # Process input
    input_path = Path(args.input)

    try:
        if args.detect:
            # Language detection mode
            if not input_path.exists():
                logger.error(f"Input file not found: {args.input}")
                sys.exit(1)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            tool.detect_language(text)

        elif args.batch or (input_path.is_dir() and not args.output):
            # Batch mode
            if not input_path.is_dir():
                logger.error(f"Batch mode requires directory input: {args.input}")
                sys.exit(1)

            tool.translate_batch(
                args.input, target_lang=args.target, source_lang=args.source, output_dir=args.output_dir, recursive=args.recursive
            )

        else:
            # Single file mode
            if not input_path.exists():
                logger.error(f"Input file not found: {args.input}")
                sys.exit(1)

            tool.translate_file(
                args.input,
                target_lang=args.target,
                source_lang=args.source,
                output_path=args.output,
                show_details=args.show_details,
            )

        logger.info("Translation completed successfully")

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
