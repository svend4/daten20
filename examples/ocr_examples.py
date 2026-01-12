#!/usr/bin/env python3
"""
OCR (Optical Character Recognition) Examples

Demonstrates text extraction from images and scanned documents.

Features:
- Tesseract OCR and EasyOCR engines
- Image preprocessing for better accuracy
- PDF to text conversion
- Batch processing
- Confidence scoring
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.ml.ocr import (
    OCRManager,
    OCREngine,
    OCRResult,
    ImagePreprocessor,
    extract_text_from_image
)
from pathlib import Path
import tempfile


def create_sample_image_with_text(text: str = "Hello World") -> str:
    """Create a sample image with text for testing"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create white image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)

        # Draw text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()

        draw.text((20, 30), text, fill='black', font=font)

        # Save to temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(temp_fd)
        img.save(temp_path)

        return temp_path

    except ImportError:
        print("❌ PIL/Pillow not available")
        return None


def example_1_basic_ocr():
    """Example 1: Basic OCR with automatic engine selection"""
    print("\n" + "="*70)
    print("Example 1: Basic OCR")
    print("="*70 + "\n")

    # Create sample image
    image_path = create_sample_image_with_text("Hello OCR World!")

    if not image_path:
        print("⚠️  Could not create sample image")
        return

    try:
        # Quick extraction
        text = extract_text_from_image(image_path)
        print(f"Extracted Text: {text}")

    finally:
        # Cleanup
        try:
            os.unlink(image_path)
        except:
            pass


def example_2_ocr_with_details():
    """Example 2: OCR with detailed results"""
    print("\n" + "="*70)
    print("Example 2: OCR with Detailed Results")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("Document Management System")

    if not image_path:
        return

    try:
        # Initialize OCR manager
        ocr = OCRManager(engine=OCREngine.AUTO, preprocess=True)

        # Extract with details
        result = ocr.extract_text(image_path)

        print(f"📄 Extracted Text:")
        print(f"   {result.text}\n")
        print(f"📊 Details:")
        print(f"   Engine: {result.engine}")
        print(f"   Confidence: {result.confidence:.2f}%")
        print(f"   Language: {result.language}")
        print(f"   Processing Time: {result.processing_time:.3f}s")

        if result.word_confidences:
            print(f"   Words Detected: {len(result.word_confidences)}")
            print(f"   Avg Word Confidence: {sum(result.word_confidences)/len(result.word_confidences):.2f}%")

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def example_3_tesseract_specific():
    """Example 3: Using Tesseract specifically"""
    print("\n" + "="*70)
    print("Example 3: Tesseract OCR")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("Tesseract OCR Engine")

    if not image_path:
        return

    try:
        # Use Tesseract specifically
        from src.ml.ocr import TesseractOCR

        try:
            tesseract = TesseractOCR(lang="eng")
            result = tesseract.extract_text(image_path, preprocess=True)

            print(f"✅ Tesseract Result:")
            print(f"   Text: {result.text}")
            print(f"   Confidence: {result.confidence:.2f}%")
            print(f"   Bounding Boxes: {len(result.bbox) if result.bbox else 0}")

        except Exception as e:
            print(f"❌ Tesseract not available: {e}")
            print("💡 Install: sudo apt-get install tesseract-ocr")

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def example_4_image_preprocessing():
    """Example 4: Image preprocessing effects"""
    print("\n" + "="*70)
    print("Example 4: Image Preprocessing")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("Preprocessing Test")

    if not image_path:
        return

    try:
        ocr = OCRManager(engine=OCREngine.AUTO)

        # Without preprocessing
        print("🔹 Without Preprocessing:")
        ocr.preprocess = False
        result1 = ocr.extract_text(image_path)
        print(f"   Text: {result1.text}")
        print(f"   Confidence: {result1.confidence:.2f}%")
        print(f"   Time: {result1.processing_time:.3f}s")

        # With preprocessing
        print("\n🔸 With Preprocessing:")
        ocr.preprocess = True
        result2 = ocr.extract_text(image_path)
        print(f"   Text: {result2.text}")
        print(f"   Confidence: {result2.confidence:.2f}%")
        print(f"   Time: {result2.processing_time:.3f}s")

        print(f"\n📊 Improvement:")
        conf_diff = result2.confidence - result1.confidence
        print(f"   Confidence: {conf_diff:+.2f}%")

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def example_5_batch_processing():
    """Example 5: Batch OCR processing"""
    print("\n" + "="*70)
    print("Example 5: Batch Processing")
    print("="*70 + "\n")

    # Create multiple test images
    texts = ["Page 1", "Page 2", "Page 3", "Page 4"]
    image_paths = []

    for text in texts:
        path = create_sample_image_with_text(text)
        if path:
            image_paths.append(path)

    if not image_paths:
        return

    try:
        ocr = OCRManager(engine=OCREngine.AUTO)

        print(f"📚 Processing {len(image_paths)} images...\n")

        # Batch process
        results = ocr.batch_extract(image_paths, max_workers=2)

        for i, result in enumerate(results):
            print(f"   {i+1}. {result.text.strip()} "
                  f"(confidence: {result.confidence:.1f}%, "
                  f"time: {result.processing_time:.3f}s)")

        # Statistics
        avg_confidence = sum(r.confidence for r in results) / len(results)
        total_time = sum(r.processing_time for r in results)

        print(f"\n📊 Batch Statistics:")
        print(f"   Images Processed: {len(results)}")
        print(f"   Average Confidence: {avg_confidence:.2f}%")
        print(f"   Total Time: {total_time:.3f}s")
        print(f"   Avg Time/Image: {total_time/len(results):.3f}s")

    finally:
        # Cleanup
        for path in image_paths:
            try:
                os.unlink(path)
            except:
                pass


def example_6_multilingual():
    """Example 6: Multilingual OCR"""
    print("\n" + "="*70)
    print("Example 6: Multilingual OCR")
    print("="*70 + "\n")

    # English text
    en_path = create_sample_image_with_text("Hello World")

    # German text (if available)
    de_path = create_sample_image_with_text("Hallo Welt")

    paths = [p for p in [en_path, de_path] if p]

    if not paths:
        return

    try:
        # English
        print("🇬🇧 English:")
        ocr_en = OCRManager(engine=OCREngine.AUTO, language="eng")
        result_en = ocr_en.extract_text(en_path)
        print(f"   Text: {result_en.text}")
        print(f"   Confidence: {result_en.confidence:.2f}%")

        # German (if Tesseract has German trained data)
        print("\n🇩🇪 German:")
        try:
            ocr_de = OCRManager(engine=OCREngine.AUTO, language="deu")
            result_de = ocr_de.extract_text(de_path)
            print(f"   Text: {result_de.text}")
            print(f"   Confidence: {result_de.confidence:.2f}%")
        except Exception as e:
            print(f"   ⚠️  German language not available: {e}")
            print("   💡 Install: sudo apt-get install tesseract-ocr-deu")

    finally:
        for path in paths:
            try:
                os.unlink(path)
            except:
                pass


def example_7_confidence_threshold():
    """Example 7: Filter by confidence threshold"""
    print("\n" + "="*70)
    print("Example 7: Confidence Threshold Filtering")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("Quality Control Test")

    if not image_path:
        return

    try:
        ocr = OCRManager(engine=OCREngine.AUTO)
        result = ocr.extract_text(image_path)

        threshold = 70.0  # 70% confidence threshold

        print(f"📊 OCR Result:")
        print(f"   Text: {result.text}")
        print(f"   Overall Confidence: {result.confidence:.2f}%")
        print(f"   Threshold: {threshold}%")

        if result.confidence >= threshold:
            print(f"\n✅ PASSED - Confidence above threshold")
            print(f"   Text accepted: {result.text}")
        else:
            print(f"\n❌ FAILED - Confidence below threshold")
            print(f"   Consider manual review or re-scanning")

        # Word-level filtering
        if result.word_confidences:
            print(f"\n📝 Word-Level Analysis:")
            high_conf = sum(1 for c in result.word_confidences if c >= threshold)
            low_conf = len(result.word_confidences) - high_conf

            print(f"   High confidence words: {high_conf}")
            print(f"   Low confidence words: {low_conf}")

            if low_conf > 0:
                print(f"   ⚠️  {low_conf} words need review")

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def example_8_ocr_result_to_dict():
    """Example 8: Export OCR results to dictionary/JSON"""
    print("\n" + "="*70)
    print("Example 8: Export Results to Dictionary")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("JSON Export Test")

    if not image_path:
        return

    try:
        ocr = OCRManager(engine=OCREngine.AUTO)
        result = ocr.extract_text(image_path)

        # Convert to dictionary
        result_dict = result.to_dict()

        import json
        print("📄 OCR Result as JSON:")
        print(json.dumps(result_dict, indent=2, default=str))

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def example_9_available_engines():
    """Example 9: Check available OCR engines"""
    print("\n" + "="*70)
    print("Example 9: Check Available OCR Engines")
    print("="*70 + "\n")

    print("🔍 Checking OCR Engine Availability:\n")

    # Check Tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR")
        print(f"   Version: {version}")
        print(f"   Languages: {pytesseract.get_languages()}")
    except Exception as e:
        print(f"❌ Tesseract OCR - Not available")
        print(f"   Error: {e}")
        print(f"   Install: sudo apt-get install tesseract-ocr")

    print()

    # Check EasyOCR
    try:
        import easyocr
        print(f"✅ EasyOCR")
        print(f"   Version: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'}")
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print(f"   Languages: Supports 80+ languages")
        del reader
    except Exception as e:
        print(f"❌ EasyOCR - Not available")
        print(f"   Error: {e}")
        print(f"   Install: pip install easyocr")

    print()

    # Check preprocessing libraries
    try:
        from PIL import Image
        from scipy import ndimage
        print(f"✅ Image Preprocessing")
        print(f"   PIL/Pillow: Available")
        print(f"   SciPy: Available")
    except Exception as e:
        print(f"❌ Image Preprocessing - Not fully available")
        print(f"   Error: {e}")


def example_10_performance_comparison():
    """Example 10: Compare OCR engine performance"""
    print("\n" + "="*70)
    print("Example 10: OCR Engine Performance Comparison")
    print("="*70 + "\n")

    image_path = create_sample_image_with_text("Performance Test 12345")

    if not image_path:
        return

    try:
        engines = []

        # Try Tesseract
        try:
            ocr_tess = OCRManager(engine=OCREngine.TESSERACT)
            result_tess = ocr_tess.extract_text(image_path)
            engines.append(("Tesseract", result_tess))
        except:
            pass

        # Try EasyOCR
        try:
            ocr_easy = OCRManager(engine=OCREngine.EASYOCR)
            result_easy = ocr_easy.extract_text(image_path)
            engines.append(("EasyOCR", result_easy))
        except:
            pass

        if not engines:
            print("❌ No OCR engines available")
            return

        print("📊 Performance Comparison:\n")
        print(f"{'Engine':<15} {'Time (s)':<12} {'Confidence':<12} {'Text'}")
        print("-" * 70)

        for engine_name, result in engines:
            print(f"{engine_name:<15} "
                  f"{result.processing_time:<12.3f} "
                  f"{result.confidence:<12.2f} "
                  f"{result.text[:30]}")

        # Find best
        best = max(engines, key=lambda x: x[1].confidence)
        fastest = min(engines, key=lambda x: x[1].processing_time)

        print(f"\n🏆 Best Confidence: {best[0]} ({best[1].confidence:.2f}%)")
        print(f"⚡ Fastest: {fastest[0]} ({fastest[1].processing_time:.3f}s)")

    finally:
        try:
            os.unlink(image_path)
        except:
            pass


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("OCR (OPTICAL CHARACTER RECOGNITION) EXAMPLES")
    print("="*70)

    examples = [
        ("1", "Basic OCR", example_1_basic_ocr),
        ("2", "OCR with Details", example_2_ocr_with_details),
        ("3", "Tesseract Specific", example_3_tesseract_specific),
        ("4", "Image Preprocessing", example_4_image_preprocessing),
        ("5", "Batch Processing", example_5_batch_processing),
        ("6", "Multilingual OCR", example_6_multilingual),
        ("7", "Confidence Threshold", example_7_confidence_threshold),
        ("8", "Export to JSON", example_8_ocr_result_to_dict),
        ("9", "Available Engines", example_9_available_engines),
        ("10", "Performance Comparison", example_10_performance_comparison),
    ]

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        for num, name, func in examples:
            if num == example_num:
                func()
                return
        print(f"❌ Example {example_num} not found")
        print("\nAvailable examples:")
        for num, name, _ in examples:
            print(f"   {num}. {name}")
    else:
        # Run all examples
        for _, _, func in examples:
            try:
                func()
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("="*70 + "\n")

        print("💡 TIP: Run specific example with:")
        print("   python examples/ocr_examples.py <number>")
        print("\nAvailable examples:")
        for num, name, _ in examples:
            print(f"   {num}. {name}")


if __name__ == "__main__":
    main()
