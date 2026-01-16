#!/usr/bin/env python3
"""
Unit Tests for OCR Module

Tests text extraction from images using multiple OCR engines.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.ml.ocr import ImagePreprocessor, OCREngine, OCRManager, OCRResult, TesseractOCR, extract_text_from_image


def create_test_image(text: str = "Test") -> str:
    """Create a simple test image with text"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (200, 50), color="white")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()

        draw.text((10, 15), text, fill="black", font=font)

        temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
        os.close(temp_fd)
        img.save(temp_path)

        return temp_path
    except ImportError:
        return None


class TestOCRResult(unittest.TestCase):
    """Test OCRResult dataclass"""

    def test_ocr_result_creation(self):
        """Test creating OCR result"""
        result = OCRResult(text="Hello World", confidence=95.5, language="eng", engine="tesseract")

        self.assertEqual(result.text, "Hello World")
        self.assertEqual(result.confidence, 95.5)
        self.assertEqual(result.language, "eng")
        self.assertEqual(result.engine, "tesseract")

    def test_ocr_result_to_dict(self):
        """Test converting result to dictionary"""
        result = OCRResult(
            text="Test",
            confidence=90.0,
            language="eng",
            engine="tesseract",
            bbox=[(0, 0, 10, 10)],
            word_confidences=[90.0],
        )

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["text"], "Test")
        self.assertEqual(result_dict["confidence"], 90.0)
        self.assertIn("bbox", result_dict)
        self.assertIn("word_confidences", result_dict)


class TestImagePreprocessor(unittest.TestCase):
    """Test image preprocessing"""

    def test_preprocessor_returns_path(self):
        """Test that preprocessor returns a path"""
        image_path = create_test_image()

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            preprocessor = ImagePreprocessor()
            result_path = preprocessor.preprocess(image_path)

            self.assertIsNotNone(result_path)
            self.assertTrue(os.path.exists(result_path))

            # Clean up
            if result_path != image_path:
                try:
                    os.unlink(result_path)
                except:
                    pass
        finally:
            try:
                os.unlink(image_path)
            except:
                pass

    def test_preprocessor_with_options(self):
        """Test preprocessing with different options"""
        image_path = create_test_image()

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            preprocessor = ImagePreprocessor()

            # Test with all options disabled
            result = preprocessor.preprocess(
                image_path, denoise=False, deskew=False, binarize=False, enhance_contrast=False
            )

            self.assertIsNotNone(result)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass


class TestTesseractOCR(unittest.TestCase):
    """Test Tesseract OCR engine"""

    def setUp(self):
        """Check if Tesseract is available"""
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except:
            self.tesseract_available = False

    def test_tesseract_initialization(self):
        """Test Tesseract initialization"""
        if not self.tesseract_available:
            self.skipTest("Tesseract not available")

        ocr = TesseractOCR(lang="eng")
        self.assertEqual(ocr.lang, "eng")

    def test_tesseract_extract_text(self):
        """Test text extraction with Tesseract"""
        if not self.tesseract_available:
            self.skipTest("Tesseract not available")

        image_path = create_test_image("Hello")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            ocr = TesseractOCR(lang="eng")
            result = ocr.extract_text(image_path)

            self.assertIsInstance(result, OCRResult)
            self.assertIsInstance(result.text, str)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 100.0)
            self.assertEqual(result.engine, "tesseract")

        finally:
            try:
                os.unlink(image_path)
            except:
                pass

    def test_tesseract_handles_errors(self):
        """Test Tesseract error handling"""
        if not self.tesseract_available:
            self.skipTest("Tesseract not available")

        ocr = TesseractOCR(lang="eng")

        # Test with non-existent file
        result = ocr.extract_text("/nonexistent/file.png")

        self.assertIsInstance(result, OCRResult)
        self.assertEqual(result.text, "")
        self.assertEqual(result.confidence, 0.0)
        self.assertIn("error", result.metadata)


class TestOCRManager(unittest.TestCase):
    """Test OCR Manager"""

    def setUp(self):
        """Check available engines"""
        self.engines_available = False

        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self.engines_available = True
        except:
            pass

        try:
            import easyocr

            self.engines_available = True
        except:
            pass

    def test_manager_initialization(self):
        """Test OCR manager initialization"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        ocr = OCRManager(engine=OCREngine.AUTO)
        self.assertIsNotNone(ocr)

    def test_manager_extract_text(self):
        """Test text extraction through manager"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        image_path = create_test_image("Test")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            ocr = OCRManager(engine=OCREngine.AUTO)
            result = ocr.extract_text(image_path)

            self.assertIsInstance(result, OCRResult)
            self.assertIsInstance(result.text, str)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass

    def test_manager_batch_extract(self):
        """Test batch text extraction"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        # Create multiple test images
        images = []
        for i in range(3):
            img_path = create_test_image(f"Page{i}")
            if img_path:
                images.append(img_path)

        if not images:
            self.skipTest("Cannot create test images")

        try:
            ocr = OCRManager(engine=OCREngine.AUTO)
            results = ocr.batch_extract(images, max_workers=2)

            self.assertEqual(len(results), len(images))

            for result in results:
                self.assertIsInstance(result, OCRResult)

        finally:
            for img in images:
                try:
                    os.unlink(img)
                except:
                    pass

    def test_manager_preprocessing_option(self):
        """Test preprocessing option"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        image_path = create_test_image("Preprocess")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            # Without preprocessing
            ocr_no_prep = OCRManager(engine=OCREngine.AUTO, preprocess=False)
            result1 = ocr_no_prep.extract_text(image_path)

            # With preprocessing
            ocr_prep = OCRManager(engine=OCREngine.AUTO, preprocess=True)
            result2 = ocr_prep.extract_text(image_path)

            # Both should return results
            self.assertIsInstance(result1, OCRResult)
            self.assertIsInstance(result2, OCRResult)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        """Check if OCR engines available"""
        self.engines_available = False

        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self.engines_available = True
        except:
            pass

    def test_extract_text_from_image_function(self):
        """Test quick extraction function"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        image_path = create_test_image("Quick")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            text = extract_text_from_image(image_path)

            self.assertIsInstance(text, str)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass


class TestOCRIntegration(unittest.TestCase):
    """Integration tests for OCR"""

    def setUp(self):
        """Check engines"""
        self.engines_available = False

        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self.engines_available = True
        except:
            pass

    def test_end_to_end_ocr(self):
        """Test complete OCR workflow"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        # 1. Create test image
        image_path = create_test_image("Integration Test")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            # 2. Initialize OCR
            ocr = OCRManager(engine=OCREngine.AUTO, preprocess=True)

            # 3. Extract text
            result = ocr.extract_text(image_path)

            # 4. Verify result
            self.assertIsNotNone(result)
            self.assertIsInstance(result.text, str)
            self.assertGreater(len(result.text), 0)
            self.assertGreaterEqual(result.confidence, 0.0)

            # 5. Convert to dict
            result_dict = result.to_dict()
            self.assertIsInstance(result_dict, dict)
            self.assertIn("text", result_dict)
            self.assertIn("confidence", result_dict)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass

    def test_confidence_filtering(self):
        """Test filtering results by confidence"""
        if not self.engines_available:
            self.skipTest("No OCR engines available")

        image_path = create_test_image("Confidence")

        if not image_path:
            self.skipTest("Cannot create test image")

        try:
            ocr = OCRManager(engine=OCREngine.AUTO)
            result = ocr.extract_text(image_path)

            # Test confidence thresholding
            threshold = 50.0

            if result.confidence >= threshold:
                # High confidence - accept
                self.assertIsInstance(result.text, str)
            else:
                # Low confidence - might need review
                self.assertGreaterEqual(result.confidence, 0.0)

        finally:
            try:
                os.unlink(image_path)
            except:
                pass


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOCRResult))
    suite.addTests(loader.loadTestsFromTestCase(TestImagePreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestTesseractOCR))
    suite.addTests(loader.loadTestsFromTestCase(TestOCRManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestOCRIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
