# OCR (Optical Character Recognition) Guide

Complete guide to extracting text from images and scanned documents.

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The OCR module provides text extraction from images and scanned documents using multiple OCR engines:

- **Tesseract OCR**: Fast, open-source, supports 100+ languages
- **EasyOCR**: Deep learning-based, high accuracy, 80+ languages
- **Automatic Selection**: Chooses best available engine

### Key Features

✅ **Multiple OCR Engines**: Tesseract, EasyOCR
✅ **Image Preprocessing**: Denoise, deskew, binarization
✅ **Multilingual Support**: 100+ languages
✅ **Confidence Scoring**: Quality assessment
✅ **Batch Processing**: Process multiple images
✅ **PDF Support**: Extract text from PDF pages
✅ **Bounding Boxes**: Word-level location data

---

## Installation

### 1. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Additional languages
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-spa  # Spanish
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Install Python Packages

```bash
pip install pytesseract easyocr pdf2image Pillow scipy
```

### 3. Verify Installation

```python
from src.ml.ocr import OCRManager

ocr = OCRManager()
print("✅ OCR ready!")
```

---

## Quick Start

### Basic Text Extraction

```python
from src.ml.ocr import extract_text_from_image

# Extract text from image
text = extract_text_from_image("document.png")
print(text)
```

### With OCR Manager

```python
from src.ml.ocr import OCRManager, OCREngine

# Initialize OCR
ocr = OCRManager(
    engine=OCREngine.AUTO,  # Automatic engine selection
    language="eng",         # English
    preprocess=True         # Enable preprocessing
)

# Extract text
result = ocr.extract_text("document.png")

print(f"Text: {result.text}")
print(f"Confidence: {result.confidence:.2f}%")
print(f"Engine: {result.engine}")
print(f"Time: {result.processing_time:.3f}s")
```

---

## Features

### 1. Automatic Engine Selection

```python
from src.ml.ocr import OCRManager, OCREngine

# Auto-detect and use best available engine
ocr = OCRManager(engine=OCREngine.AUTO)
```

### 2. Specific Engine

```python
# Use Tesseract specifically
ocr = OCRManager(engine=OCREngine.TESSERACT)

# Use EasyOCR specifically
ocr = OCRManager(engine=OCREngine.EASYOCR)
```

### 3. Image Preprocessing

Improves OCR accuracy by:
- Converting to grayscale
- Removing noise
- Binarization (Otsu's method)
- Deskewing rotated text
- Contrast enhancement

```python
ocr = OCRManager(preprocess=True)
result = ocr.extract_text("noisy_scan.png")
```

### 4. Multilingual Support

```python
# German text
ocr_de = OCRManager(language="deu")
result = ocr_de.extract_text("deutsche_dokument.png")

# French text
ocr_fr = OCRManager(language="fra")
result = ocr_fr.extract_text("document_francais.png")

# Multiple languages (EasyOCR)
from src.ml.ocr import EasyOCRWrapper
ocr_multi = EasyOCRWrapper(languages=['en', 'de', 'fr'])
```

### 5. Confidence Scoring

```python
result = ocr.extract_text("document.png")

if result.confidence >= 80.0:
    print("✅ High confidence - text accepted")
elif result.confidence >= 50.0:
    print("⚠️  Medium confidence - review recommended")
else:
    print("❌ Low confidence - manual review required")
```

### 6. Batch Processing

```python
image_paths = [
    "page1.png",
    "page2.png",
    "page3.png"
]

results = ocr.batch_extract(image_paths, max_workers=4)

for i, result in enumerate(results):
    print(f"Page {i+1}: {result.text[:50]}...")
```

### 7. PDF Text Extraction

```python
# Extract from all pages
results = ocr.extract_text_from_pdf("document.pdf")

# Extract specific pages
results = ocr.extract_text_from_pdf(
    "document.pdf",
    page_numbers=[1, 2, 3]  # Pages 1-3
)

for i, result in enumerate(results):
    print(f"Page {i+1}:")
    print(result.text)
    print(f"Confidence: {result.confidence:.2f}%")
    print()
```

### 8. Bounding Boxes

Get word locations for layout analysis:

```python
result = ocr.extract_text("document.png")

if result.bbox:
    print(f"Words detected: {len(result.bbox)}")

    for i, (x1, y1, x2, y2) in enumerate(result.bbox):
        print(f"Word {i+1}: ({x1}, {y1}) to ({x2}, {y2})")
        if result.word_confidences:
            print(f"  Confidence: {result.word_confidences[i]:.2f}%")
```

---

## API Reference

### OCRManager

Main OCR interface supporting multiple engines.

```python
class OCRManager:
    def __init__(
        self,
        engine: OCREngine = OCREngine.AUTO,
        language: str = "eng",
        preprocess: bool = True
    )
```

**Parameters:**
- `engine`: OCR engine (AUTO, TESSERACT, EASYOCR)
- `language`: Language code (e.g., 'eng', 'deu', 'fra')
- `preprocess`: Enable image preprocessing

**Methods:**

#### extract_text()

```python
def extract_text(self, image_path: str) -> OCRResult
```

Extract text from single image.

**Returns:** `OCRResult` with text and metadata

#### batch_extract()

```python
def batch_extract(
    self,
    image_paths: List[str],
    max_workers: int = 4
) -> List[OCRResult]
```

Extract text from multiple images in parallel.

#### extract_text_from_pdf()

```python
def extract_text_from_pdf(
    self,
    pdf_path: str,
    page_numbers: Optional[List[int]] = None
) -> List[OCRResult]
```

Extract text from PDF by converting to images.

### OCRResult

Result dataclass with extraction details.

```python
@dataclass
class OCRResult:
    text: str                              # Extracted text
    confidence: float                      # Overall confidence (0-100)
    language: str                          # Language
    engine: str                            # Engine used
    bbox: List[Tuple[int,int,int,int]]   # Bounding boxes
    word_confidences: List[float]         # Per-word confidence
    processing_time: float                # Time taken
    metadata: Dict[str, Any]              # Additional data
```

**Methods:**

```python
def to_dict(self) -> Dict[str, Any]
```

Convert result to dictionary for JSON export.

### TesseractOCR

Direct Tesseract interface.

```python
class TesseractOCR:
    def __init__(self, lang: str = "eng")
    def extract_text(self, image_path: str, config: str = "--psm 3") -> OCRResult
```

### EasyOCRWrapper

Direct EasyOCR interface.

```python
class EasyOCRWrapper:
    def __init__(self, languages: List[str] = None)
    def extract_text(self, image_path: str, detail: int = 1) -> OCRResult
```

### ImagePreprocessor

Image preprocessing utilities.

```python
class ImagePreprocessor:
    @staticmethod
    def preprocess(
        image_path: str,
        denoise: bool = True,
        deskew: bool = True,
        binarize: bool = True,
        enhance_contrast: bool = True
    ) -> str
```

---

## Examples

### Example 1: Receipt OCR

```python
from src.ml.ocr import OCRManager

ocr = OCRManager(preprocess=True)
result = ocr.extract_text("receipt.png")

# Extract structured data
lines = result.text.split('\n')
for line in lines:
    if '$' in line:
        print(f"Amount found: {line}")
```

### Example 2: Business Card Extraction

```python
ocr = OCRManager(preprocess=True)
result = ocr.extract_text("business_card.png")

# Parse contact info
lines = result.text.split('\n')
for line in lines:
    if '@' in line:  # Email
        print(f"Email: {line}")
    elif any(c.isdigit() for c in line):  # Phone
        print(f"Phone: {line}")
```

### Example 3: Multi-page Document

```python
# Process entire document
results = ocr.extract_text_from_pdf("report.pdf")

# Combine all text
full_text = "\n\n".join(r.text for r in results)

# Calculate average confidence
avg_conf = sum(r.confidence for r in results) / len(results)
print(f"Average confidence: {avg_conf:.2f}%")

# Save to file
with open("extracted_text.txt", "w") as f:
    f.write(full_text)
```

### Example 4: Quality Control

```python
def extract_with_validation(image_path: str, min_confidence: float = 70.0):
    """Extract text with quality validation"""
    ocr = OCRManager(preprocess=True)
    result = ocr.extract_text(image_path)

    if result.confidence < min_confidence:
        # Try with different preprocessing
        ocr.preprocess = False
        result_no_prep = ocr.extract_text(image_path)

        # Use better result
        if result_no_prep.confidence > result.confidence:
            result = result_no_prep

    return result if result.confidence >= min_confidence else None

# Use it
result = extract_with_validation("scan.png")
if result:
    print(f"✅ Text: {result.text}")
else:
    print("❌ Quality too low - manual review needed")
```

### Example 5: Language Detection

```python
def detect_and_extract(image_path: str):
    """Try multiple languages and use best result"""
    languages = ['eng', 'deu', 'fra', 'spa']
    best_result = None

    for lang in languages:
        ocr = OCRManager(language=lang)
        result = ocr.extract_text(image_path)

        if not best_result or result.confidence > best_result.confidence:
            best_result = result

    return best_result

result = detect_and_extract("multilingual.png")
print(f"Best language: {result.language}")
print(f"Confidence: {result.confidence:.2f}%")
```

---

## Best Practices

### 1. Image Quality

For best results:
- **Resolution**: 300 DPI minimum
- **Format**: PNG or TIFF (lossless)
- **Lighting**: Even, no shadows
- **Focus**: Sharp, not blurry
- **Orientation**: Straight, not rotated

### 2. Preprocessing

Enable preprocessing for:
- ✅ Scanned documents
- ✅ Phone camera photos
- ✅ Low quality images
- ✅ Noisy backgrounds

Disable preprocessing for:
- ❌ High quality screenshots
- ❌ Digital-born documents
- ❌ Already processed images

### 3. Engine Selection

**Use Tesseract when:**
- Speed is important
- Processing many documents
- Standard fonts/layouts
- Latin-based languages

**Use EasyOCR when:**
- Accuracy is critical
- Handwritten text
- Complex layouts
- Asian languages

### 4. Confidence Thresholds

Recommended thresholds:
- **>= 90%**: Excellent - fully automated
- **80-90%**: Good - automated with logging
- **70-80%**: Fair - spot check recommended
- **50-70%**: Poor - review recommended
- **< 50%**: Very poor - manual review required

### 5. Performance Optimization

```python
# Batch processing for speed
results = ocr.batch_extract(image_paths, max_workers=4)

# Process smaller images
from PIL import Image
img = Image.open("large.png")
if img.size[0] > 2000:
    img = img.resize((2000, int(2000 * img.size[1] / img.size[0])))
    img.save("resized.png")
```

---

## Troubleshooting

### Tesseract Not Found

**Problem**: `TesseractNotFoundError`

**Solution**:
```bash
# Ubuntu
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Language Not Available

**Problem**: `TesseractError: (1, 'Error opening data file')`

**Solution**:
```bash
# Install language data
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-fra  # French

# List available languages
tesseract --list-langs
```

### Low Confidence Results

**Problem**: Confidence < 50%

**Solutions**:
1. **Improve image quality**
   ```python
   # Increase resolution before OCR
   img = Image.open("low_res.png")
   img = img.resize((img.size[0]*2, img.size[1]*2))
   ```

2. **Try preprocessing**
   ```python
   ocr = OCRManager(preprocess=True)
   ```

3. **Try different engines**
   ```python
   # Try both engines
   result1 = OCRManager(engine=OCREngine.TESSERACT).extract_text(path)
   result2 = OCRManager(engine=OCREngine.EASYOCR).extract_text(path)
   # Use better result
   ```

### PDF Conversion Fails

**Problem**: `PDFInfoNotInstalledError`

**Solution**:
```bash
# Ubuntu
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Python
pip install pdf2image
```

### Memory Issues

**Problem**: Out of memory with EasyOCR

**Solution**:
```python
# Process images sequentially
for image_path in image_paths:
    result = ocr.extract_text(image_path)
    process_result(result)
    del result  # Free memory
```

---

## Integration Examples

### With doc-processor.py

```python
# Add OCR to document processor
from src.ml.ocr import OCRManager

def process_scanned_document(pdf_path: str):
    ocr = OCRManager(preprocess=True)

    # Extract text from PDF
    results = ocr.extract_text_from_pdf(pdf_path)

    # Combine text
    full_text = "\n".join(r.text for r in results)

    # Process with NER, classification, etc.
    # ...

    return full_text
```

### With Flask API

```python
from flask import Flask, request, jsonify
from src.ml.ocr import OCRManager

app = Flask(__name__)
ocr = OCRManager()

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    temp_path = f"/tmp/{image.filename}"
    image.save(temp_path)

    try:
        result = ocr.extract_text(temp_path)
        return jsonify(result.to_dict())
    finally:
        os.unlink(temp_path)
```

---

## Performance Benchmarks

Typical processing times (300 DPI, 1 page):

| Engine | Time | Accuracy | Best For |
|--------|------|----------|----------|
| Tesseract | 0.5-2s | 85-95% | Speed, volume |
| EasyOCR | 2-10s | 90-98% | Accuracy, quality |

## Summary

OCR module provides:
- ✅ Multiple OCR engines (Tesseract, EasyOCR)
- ✅ Image preprocessing
- ✅ Multilingual support (100+ languages)
- ✅ Batch processing
- ✅ PDF support
- ✅ Confidence scoring
- ✅ Production-ready implementation

For examples: `examples/ocr_examples.py`

For tests: `tests/unit/ml/test_ocr.py`

---

**Related Documentation:**
- [Document Processing Guide](./DOCUMENT_PROCESSING_GUIDE.md)
- [ML Models Guide](./ML_MODELS_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
