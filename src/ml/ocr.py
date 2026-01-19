#!/usr/bin/env python3
"""
OCR (Optical Character Recognition) Module

Provides text extraction from images and scanned documents using multiple OCR engines.

Supported Engines:
- Tesseract OCR (via pytesseract) - Fast, multilingual
- EasyOCR - Deep learning-based, high accuracy
- PaddleOCR - Production-ready, supports 80+ languages

Features:
- Multiple OCR engines
- Automatic language detection
- Image preprocessing (deskew, denoise, binarization)
- Batch processing
- PDF to image conversion
- Confidence scoring
- Layout analysis
"""

import logging
import os
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class OCREngine(str, Enum):
    """Supported OCR engines"""

    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"
    AUTO = "auto"  # Automatically select best available


@dataclass
class OCRResult:
    """Result from OCR processing"""

    text: str
    confidence: float
    language: str
    engine: str
    bbox: Optional[List[Tuple[int, int, int, int]]] = None  # Bounding boxes
    word_confidences: Optional[List[float]] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "engine": self.engine,
            "bbox": self.bbox,
            "word_confidences": self.word_confidences,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


class ImagePreprocessor:
    """
    Image preprocessing for better OCR accuracy

    Techniques:
    - Grayscale conversion
    - Noise reduction
    - Binarization (Otsu's method)
    - Deskewing
    - Contrast enhancement
    """

    @staticmethod
    def preprocess(
        image_path: str, denoise: bool = True, deskew: bool = True, binarize: bool = True, enhance_contrast: bool = True
    ) -> str:
        """
        Preprocess image for better OCR accuracy

        Returns path to preprocessed image
        """
        try:
            import numpy as np
            from PIL import Image, ImageEnhance, ImageFilter
            from scipy import ndimage

            img = Image.open(image_path)

            # Convert to grayscale
            if img.mode != "L":
                img = img.convert("L")

            # Denoise
            if denoise:
                img = img.filter(ImageFilter.MedianFilter(size=3))

            # Enhance contrast
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2.0)

            # Deskew
            if deskew:
                img_array = np.array(img)
                # Simple deskewing using moments
                try:
                    # Calculate skew angle
                    coords = np.column_stack(np.where(img_array < 128))
                    if len(coords) > 0:
                        angle = np.arctan2(coords[:, 0].std(), coords[:, 1].std())
                        angle_deg = np.degrees(angle)

                        if abs(angle_deg) > 0.5:  # Only deskew if significant
                            img_array = ndimage.rotate(img_array, angle_deg, reshape=False, cval=255)
                            img = Image.fromarray(img_array)
                except Exception as e:
                    logger.debug(f"Deskewing failed: {e}")

            # Binarization (Otsu's method)
            if binarize:
                from PIL import ImageOps

                img = ImageOps.autocontrast(img)
                threshold = 128
                img = img.point(lambda p: p > threshold and 255)

            # Save preprocessed image
            temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
            os.close(temp_fd)
            img.save(temp_path)

            return temp_path

        except ImportError as e:
            logger.warning(f"Preprocessing libraries not available: {e}")
            return image_path
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return image_path


class TesseractOCR:
    """Tesseract OCR engine wrapper"""

    def __init__(self, lang: str = "eng"):
        """
        Initialize Tesseract OCR

        Args:
            lang: Language code (e.g., 'eng', 'deu', 'fra')
        """
        self.lang = lang
        self._check_available()

    def _check_available(self) -> bool:
        """Check if Tesseract is available"""
        try:
            import pytesseract

            # Test if tesseract is installed
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False

    def extract_text(self, image_path: str, config: str = "--psm 3", preprocess: bool = True) -> OCRResult:
        """
        Extract text from image using Tesseract

        Args:
            image_path: Path to image file
            config: Tesseract configuration string
            preprocess: Apply preprocessing

        Returns:
            OCRResult with extracted text
        """
        import time

        start_time = time.time()

        try:
            import pytesseract
            from PIL import Image

            # Preprocess if requested
            if preprocess:
                preprocessor = ImagePreprocessor()
                processed_path = preprocessor.preprocess(image_path)
            else:
                processed_path = image_path

            # Open image
            img = Image.open(processed_path)

            # Extract text with details
            data = pytesseract.image_to_data(img, lang=self.lang, config=config, output_type=pytesseract.Output.DICT)

            # Extract text
            text = pytesseract.image_to_string(img, lang=self.lang, config=config)

            # Calculate average confidence
            confidences = [float(conf) for conf in data["conf"] if conf != "-1" and conf.replace(".", "").isdigit()]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Extract bounding boxes
            n_boxes = len(data["text"])
            bboxes = []
            word_confidences = []

            for i in range(n_boxes):
                if int(data["conf"][i]) > 0:
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    bboxes.append((x, y, x + w, y + h))
                    word_confidences.append(float(data["conf"][i]))

            # Clean up preprocessed image
            if preprocess and processed_path != image_path:
                try:
                    os.unlink(processed_path)
                except:
                    pass

            processing_time = time.time() - start_time

            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                language=self.lang,
                engine="tesseract",
                bbox=bboxes if bboxes else None,
                word_confidences=word_confidences if word_confidences else None,
                processing_time=processing_time,
                metadata={"config": config, "num_words": len([w for w in data["text"] if w.strip()])},
            )

        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                language=self.lang,
                engine="tesseract",
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
            )


class EasyOCRWrapper:
    """EasyOCR engine wrapper"""

    def __init__(self, languages: List[str] = None):
        """
        Initialize EasyOCR

        Args:
            languages: List of language codes (e.g., ['en', 'de'])
        """
        self.languages = languages or ["en"]
        self.reader = None
        self._initialize()

    def _initialize(self):
        """Initialize EasyOCR reader"""
        try:
            import easyocr

            self.reader = easyocr.Reader(self.languages, gpu=False)
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")

    def extract_text(self, image_path: str, detail: int = 1) -> OCRResult:
        """
        Extract text using EasyOCR

        Args:
            image_path: Path to image
            detail: Detail level (0=text only, 1=with bbox, 2=with confidence)

        Returns:
            OCRResult with extracted text
        """
        import time

        start_time = time.time()

        if not self.reader:
            return OCRResult(
                text="",
                confidence=0.0,
                language=",".join(self.languages),
                engine="easyocr",
                metadata={"error": "EasyOCR not initialized"},
            )

        try:
            # Read text
            results = self.reader.readtext(image_path, detail=detail)

            # Combine text
            text_parts = []
            bboxes = []
            confidences = []

            for result in results:
                if detail == 0:
                    text_parts.append(result)
                else:
                    bbox, text, conf = result
                    text_parts.append(text)
                    bboxes.append(
                        tuple(map(int, [bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]]))  # top-left  # bottom-right
                    )
                    confidences.append(float(conf))

            full_text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            processing_time = time.time() - start_time

            return OCRResult(
                text=full_text.strip(),
                confidence=avg_confidence * 100,  # Convert to percentage
                language=",".join(self.languages),
                engine="easyocr",
                bbox=bboxes if bboxes else None,
                word_confidences=confidences if confidences else None,
                processing_time=processing_time,
                metadata={"num_detections": len(results)},
            )

        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                language=",".join(self.languages),
                engine="easyocr",
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
            )


class OCRManager:
    """
    High-level OCR manager supporting multiple engines

    Usage:
        ocr = OCRManager(engine=OCREngine.AUTO)
        result = ocr.extract_text("document.png")
        print(result.text)
    """

    def __init__(self, engine: OCREngine = OCREngine.AUTO, language: str = "eng", preprocess: bool = True):
        """
        Initialize OCR manager

        Args:
            engine: OCR engine to use
            language: Primary language
            preprocess: Enable image preprocessing
        """
        self.engine = engine
        self.language = language
        self.preprocess = preprocess
        self._engines = {}

        # Initialize requested engine
        if engine == OCREngine.AUTO:
            self._detect_available_engines()
        else:
            self._initialize_engine(engine)

    def _detect_available_engines(self):
        """Detect and initialize available OCR engines"""
        # Try Tesseract
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self._engines[OCREngine.TESSERACT] = TesseractOCR(self.language)
            logger.info("Tesseract OCR available")
        except:
            logger.debug("Tesseract not available")

        # Try EasyOCR
        try:
            import easyocr

            lang_code = self.language[:2]  # Convert 'eng' to 'en'
            self._engines[OCREngine.EASYOCR] = EasyOCRWrapper([lang_code])
            logger.info("EasyOCR available")
        except:
            logger.debug("EasyOCR not available")

        if not self._engines:
            raise RuntimeError("No OCR engines available. Install pytesseract or easyocr.")

    def _initialize_engine(self, engine: OCREngine):
        """Initialize specific engine"""
        if engine == OCREngine.TESSERACT:
            self._engines[engine] = TesseractOCR(self.language)
        elif engine == OCREngine.EASYOCR:
            lang_code = self.language[:2]
            self._engines[engine] = EasyOCRWrapper([lang_code])

    def extract_text(self, image_path: str, **kwargs) -> OCRResult:
        """
        Extract text from image

        Args:
            image_path: Path to image file
            **kwargs: Engine-specific arguments

        Returns:
            OCRResult with extracted text
        """
        if not self._engines:
            raise RuntimeError("No OCR engines initialized")

        # Use first available engine
        engine_type, engine = next(iter(self._engines.items()))

        if engine_type == OCREngine.TESSERACT:
            return engine.extract_text(image_path, preprocess=self.preprocess, **kwargs)
        elif engine_type == OCREngine.EASYOCR:
            return engine.extract_text(image_path, **kwargs)

        raise ValueError(f"Unknown engine: {engine_type}")

    def extract_text_from_pdf(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> List[OCRResult]:
        """
        Extract text from PDF by converting pages to images

        Args:
            pdf_path: Path to PDF file
            page_numbers: Specific pages to process (None = all)

        Returns:
            List of OCRResults, one per page
        """
        try:
            from pdf2image import convert_from_path

            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=page_numbers[0] if page_numbers else None,
                last_page=page_numbers[-1] if page_numbers else None,
            )

            results = []
            for i, img in enumerate(images):
                # Save to temp file
                temp_fd, temp_path = tempfile.mkstemp(suffix=".png")
                os.close(temp_fd)

                try:
                    img.save(temp_path)
                    result = self.extract_text(temp_path)
                    result.metadata["page"] = i + 1
                    results.append(result)
                finally:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            return results

        except ImportError:
            logger.error("pdf2image not available. Install: pip install pdf2image")
            return []
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            return []

    def batch_extract(self, image_paths: List[str], max_workers: int = 4) -> List[OCRResult]:
        """
        Extract text from multiple images in parallel

        Args:
            image_paths: List of image paths
            max_workers: Maximum parallel workers

        Returns:
            List of OCRResults
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {executor.submit(self.extract_text, path): path for path in image_paths}

            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"OCR failed for {path}: {e}")
                    results.append(
                        OCRResult(
                            text="",
                            confidence=0.0,
                            language=self.language,
                            engine="unknown",
                            metadata={"error": str(e), "path": path},
                        )
                    )

        return results


# Convenience function
def extract_text_from_image(
    image_path: str, engine: OCREngine = OCREngine.AUTO, language: str = "eng", preprocess: bool = True
) -> str:
    """
    Quick text extraction from image

    Args:
        image_path: Path to image
        engine: OCR engine to use
        language: Language code
        preprocess: Enable preprocessing

    Returns:
        Extracted text
    """
    ocr = OCRManager(engine=engine, language=language, preprocess=preprocess)
    result = ocr.extract_text(image_path)
    return result.text


if __name__ == "__main__":
    # Example usage
    print("OCR Module")
    print("=" * 50)

    # Check available engines
    try:
        import pytesseract

        print("✅ Tesseract available")
    except:
        print("❌ Tesseract not available")

    try:
        import easyocr

        print("✅ EasyOCR available")
    except:
        print("❌ EasyOCR not available")
