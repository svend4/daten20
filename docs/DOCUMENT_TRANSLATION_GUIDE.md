# Document Translation Guide

**Version:** 1.0
**Last Updated:** 2026-01-16
**Status:** Production Ready ✅

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Concepts](#core-concepts)
6. [Translation Backends](#translation-backends)
7. [API Reference](#api-reference)
8. [REST API Endpoints](#rest-api-endpoints)
9. [Examples](#examples)
10. [Performance](#performance)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Document Translation module provides comprehensive multi-language translation capabilities for the Document Management System. It supports multiple translation backends, automatic language detection, and intelligent caching for optimal performance.

### Key Capabilities

- **Multi-Backend Support**: Google Translate, DeepL, Argos Translate, LibreTranslate
- **100+ Languages**: Support for over 100 languages
- **Automatic Language Detection**: Detect source language automatically
- **Intelligent Caching**: Cache translations for better performance
- **Batch Processing**: Translate multiple texts efficiently
- **Document Translation**: Translate entire documents with format preservation
- **REST API**: Full REST API support for integration

### Use Cases

- Multi-language document management
- Real-time content translation
- International collaboration
- Compliance with multi-language requirements
- Customer support in multiple languages
- Content localization

---

## Features

### Translation Backends

| Backend | Type | Quality | Speed | Cost | Offline |
|---------|------|---------|-------|------|---------|
| **Google Translate** | Cloud | High | Fast | Free* | No |
| **DeepL** | Cloud | Excellent | Fast | Paid | No |
| **Argos Translate** | Local | Good | Medium | Free | Yes |
| **LibreTranslate** | Self-hosted | Good | Medium | Free | Yes |

\* Google Translate is free but rate-limited

### Core Features

#### 1. **Text Translation**
- Translate any text to 100+ languages
- Automatic source language detection
- Translation confidence scores
- Multiple backend support

#### 2. **Batch Translation**
- Translate multiple texts at once
- Progress tracking
- Error handling for failed translations
- Performance metrics

#### 3. **Document Translation**
- Translate entire documents
- Preserve formatting (paragraphs, line breaks)
- Support for TXT, Markdown, and more
- Metadata tracking

#### 4. **Language Detection**
- Automatic language detection
- Confidence scores
- Alternative language suggestions
- Support for mixed-language content

#### 5. **Translation Cache**
- In-memory caching
- TTL-based expiration
- Cache statistics
- Manual cache management

#### 6. **Quality Metrics**
- Translation confidence scores
- Backend quality ratings
- Performance tracking
- Error reporting

---

## Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Basic Installation

```bash
# Install core package
pip install -r requirements.txt
```

### Backend-Specific Dependencies

#### Google Translate (Free)
```bash
pip install googletrans==4.0.0rc1
```

#### DeepL (Paid - High Quality)
```bash
pip install deepl
# Requires API key from https://www.deepl.com/pro-api
```

#### Argos Translate (Free - Offline)
```bash
pip install argostranslate
# Install language packages
argospm install en es  # English to Spanish
argospm install en fr  # English to French
```

#### Language Detection
```bash
pip install langdetect
```

### Verify Installation

```python
from src.ml.document_translator import DocumentTranslator

translator = DocumentTranslator()
print(f"Available backends: {translator.available_backends}")
```

---

## Quick Start

### Basic Translation

```python
from src.ml.document_translator import quick_translate

# Simple translation
result = quick_translate("Hello, world!", target_language="es")
print(result)  # "¡Hola, mundo!"
```

### Using DocumentTranslator

```python
from src.ml.document_translator import DocumentTranslator

# Create translator
translator = DocumentTranslator()

# Translate text
result = translator.translate(
    text="Hello, world!",
    target_language="es"
)

print(f"Translated: {result.translated_text}")
print(f"Confidence: {result.confidence}")
print(f"Backend: {result.backend}")
```

### Language Detection

```python
# Detect language
detection = translator.detect_language("Bonjour le monde")

print(f"Language: {detection.language}")  # "fr"
print(f"Confidence: {detection.confidence}")  # 0.99
```

### Batch Translation

```python
# Translate multiple texts
texts = [
    "Hello",
    "Good morning",
    "How are you?"
]

batch_result = translator.translate_batch(
    texts=texts,
    target_language="es"
)

print(f"Successful: {batch_result.successful}/{batch_result.total_texts}")
for result in batch_result.results:
    print(f"{result.source_text} → {result.translated_text}")
```

---

## Core Concepts

### Translation Backends

The module supports multiple translation backends, each with different characteristics:

#### Backend Selection Strategy

```python
from src.ml.document_translator import DocumentTranslator, TranslationBackend

# Automatic backend selection (recommended)
translator = DocumentTranslator(backend=TranslationBackend.AUTO)

# Specific backend
translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

# With API key (for DeepL)
translator = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key="your-deepl-api-key"
)
```

#### Fallback Mechanism

If a specific backend is unavailable, the system automatically falls back to other available backends in priority order:

1. **DeepL** (highest quality)
2. **Google Translate** (good quality, free)
3. **Argos Translate** (offline support)

### Translation Cache

The translation cache stores results to avoid redundant API calls:

```python
# Enable caching (default)
translator = DocumentTranslator(cache_enabled=True)

# First translation (cache miss)
result1 = translator.translate("Hello", "es")

# Second translation (cache hit - instant)
result2 = translator.translate("Hello", "es")

# Check cache statistics
stats = translator.get_statistics()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
```

#### Cache Configuration

```python
from src.ml.document_translator import TranslationCache

# Custom cache settings
cache = TranslationCache(
    max_entries=10000,  # Maximum cached entries
    ttl_hours=24        # Time-to-live in hours
)
```

### Language Codes

The module uses ISO 639-1 language codes:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English | `es` | Spanish |
| `fr` | French | `de` | German |
| `it` | Italian | `pt` | Portuguese |
| `ru` | Russian | `zh-cn` | Chinese (Simplified) |
| `ja` | Japanese | `ko` | Korean |
| `ar` | Arabic | `hi` | Hindi |

See full list in `DocumentTranslator.SUPPORTED_LANGUAGES`

---

## Translation Backends

### Google Translate

**Pros:**
- Free (rate-limited)
- 100+ languages
- Fast
- High quality
- No setup required

**Cons:**
- Rate limits
- Requires internet
- Terms of service restrictions

**Setup:**
```python
from src.ml.document_translator import DocumentTranslator, TranslationBackend

translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)
```

### DeepL

**Pros:**
- Highest quality translations
- Natural-sounding results
- Professional use allowed
- Fast

**Cons:**
- Paid (API key required)
- Fewer languages (~30)
- Requires internet

**Setup:**
```python
translator = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key="your-deepl-api-key"
)

# Get API key from: https://www.deepl.com/pro-api
```

**Supported Languages:**
- EN, DE, FR, ES, IT, PT, NL, PL, RU, JA, ZH

### Argos Translate

**Pros:**
- 100% free
- Offline support
- Privacy-friendly
- Open source

**Cons:**
- Lower quality
- Slower
- Requires language package installation

**Setup:**
```bash
# Install Argos Translate
pip install argostranslate

# Install language packages
argospm update
argospm install en es  # English to Spanish
argospm install es en  # Spanish to English

# List available packages
argospm list
```

```python
translator = DocumentTranslator(backend=TranslationBackend.ARGOS)
```

### LibreTranslate

**Pros:**
- Free
- Self-hosted
- Privacy-friendly
- API compatible

**Cons:**
- Requires setup
- Server resources needed
- Variable quality

**Setup:**
```bash
# Using Docker
docker run -p 5000:5000 libretranslate/libretranslate
```

---

## API Reference

### DocumentTranslator

Main translation class.

#### Constructor

```python
DocumentTranslator(
    backend: TranslationBackend = TranslationBackend.AUTO,
    api_key: Optional[str] = None,
    cache_enabled: bool = True,
    quality: TranslationQuality = TranslationQuality.BALANCED
)
```

**Parameters:**
- `backend`: Translation backend to use
- `api_key`: API key for paid services (DeepL)
- `cache_enabled`: Enable translation caching
- `quality`: Translation quality level

#### Methods

##### translate()

Translate text to target language.

```python
translate(
    text: str,
    target_language: str,
    source_language: Optional[str] = None
) -> TranslationResult
```

**Parameters:**
- `text`: Text to translate
- `target_language`: Target language code (e.g., "es", "fr")
- `source_language`: Source language code (auto-detected if None)

**Returns:** `TranslationResult` with translated text and metadata

**Example:**
```python
result = translator.translate("Hello", target_language="es")
print(result.translated_text)  # "Hola"
```

##### translate_batch()

Translate multiple texts in batch.

```python
translate_batch(
    texts: List[str],
    target_language: str,
    source_language: Optional[str] = None
) -> BatchTranslationResult
```

**Parameters:**
- `texts`: List of texts to translate
- `target_language`: Target language code
- `source_language`: Source language code (auto-detected if None)

**Returns:** `BatchTranslationResult` with all results and statistics

**Example:**
```python
results = translator.translate_batch(
    texts=["Hello", "Goodbye"],
    target_language="es"
)
```

##### translate_document()

Translate entire document file.

```python
translate_document(
    document_path: Union[str, Path],
    target_language: str,
    source_language: Optional[str] = None,
    preserve_formatting: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `document_path`: Path to document file
- `target_language`: Target language code
- `source_language`: Source language code (auto-detected if None)
- `preserve_formatting`: Preserve document formatting

**Returns:** Dictionary with translation results

**Example:**
```python
result = translator.translate_document(
    document_path="document.txt",
    target_language="es"
)
```

##### detect_language()

Detect language of text.

```python
detect_language(text: str) -> LanguageDetectionResult
```

**Parameters:**
- `text`: Text to detect language for

**Returns:** `LanguageDetectionResult` with detected language and confidence

**Example:**
```python
detection = translator.detect_language("Bonjour")
print(detection.language)  # "fr"
print(detection.confidence)  # 0.99
```

##### get_statistics()

Get translator statistics.

```python
get_statistics() -> Dict[str, Any]
```

**Returns:** Dictionary with statistics (translations, cache hits, errors, etc.)

**Example:**
```python
stats = translator.get_statistics()
print(f"Total translations: {stats['translations']}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
```

##### clear_cache()

Clear translation cache.

```python
clear_cache() -> None
```

**Example:**
```python
translator.clear_cache()
```

---

## REST API Endpoints

The translation module provides REST API endpoints for integration.

### Base URL

```
http://localhost:5000/api/translate
```

### Endpoints

#### 1. Translate Text

**POST** `/api/translate/text`

Translate single text.

**Request:**
```json
{
  "text": "Hello, world!",
  "target_language": "es",
  "source_language": "en"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "source_text": "Hello, world!",
    "translated_text": "¡Hola, mundo!",
    "source_language": "en",
    "target_language": "es",
    "backend": "google",
    "confidence": 1.0,
    "translation_time_ms": 245
  }
}
```

#### 2. Translate Batch

**POST** `/api/translate/batch`

Translate multiple texts.

**Request:**
```json
{
  "texts": ["Hello", "Goodbye", "Thank you"],
  "target_language": "es",
  "source_language": "en"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "source_text": "Hello",
      "translated_text": "Hola",
      "source_language": "en",
      "target_language": "es"
    },
    ...
  ],
  "summary": {
    "total_texts": 3,
    "successful": 3,
    "failed": 0,
    "total_time_seconds": 1.2,
    "words_translated": 12,
    "success_rate": 1.0
  }
}
```

#### 3. Translate Document

**POST** `/api/translate/document`

Translate entire document.

**Request:**
```json
{
  "document_path": "/path/to/document.txt",
  "target_language": "es",
  "source_language": "en",  // optional
  "preserve_formatting": true  // optional
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "source_file": "/path/to/document.txt",
    "source_language": "en",
    "target_language": "es",
    "translated_content": "...",
    "word_count": 1234,
    "backend": "google",
    "timestamp": "2026-01-16T12:34:56"
  }
}
```

#### 4. Detect Language

**POST** `/api/translate/detect`

Detect language of text.

**Request:**
```json
{
  "text": "Bonjour le monde"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "language": "fr",
    "confidence": 0.99,
    "alternatives": [
      ["en", 0.01]
    ]
  }
}
```

#### 5. Get Supported Languages

**GET** `/api/translate/languages`

Get list of supported languages.

**Response:**
```json
{
  "success": true,
  "languages": ["af", "ar", "bg", "bn", ...],
  "total_languages": 100
}
```

#### 6. Get Statistics

**GET** `/api/translate/stats`

Get translation statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "translations": 1234,
    "cache_hits": 567,
    "cache_misses": 667,
    "errors": 12,
    "total_words": 45678,
    "cache_hit_rate": 0.46,
    "cache_size": 890
  }
}
```

#### 7. Clear Cache

**DELETE** `/api/translate/cache`

Clear translation cache.

**Response:**
```json
{
  "success": true,
  "message": "Translation cache cleared successfully"
}
```

#### 8. Health Check

**GET** `/api/translate/health`

Check API health and available backends.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "backends_available": ["google", "deepl"]
}
```

### API Usage Example

```bash
# Translate text
curl -X POST http://localhost:5000/api/translate/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "target_language": "es"
  }'

# Batch translation
curl -X POST http://localhost:5000/api/translate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello", "Goodbye"],
    "target_language": "es"
  }'

# Language detection
curl -X POST http://localhost:5000/api/translate/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour"}'
```

---

## Examples

### Example 1: Basic Translation

```python
from src.ml.document_translator import DocumentTranslator

# Create translator
translator = DocumentTranslator()

# Translate text
result = translator.translate(
    text="The document management system is excellent.",
    target_language="es"
)

print(f"Original: {result.source_text}")
print(f"Translated: {result.translated_text}")
print(f"Language: {result.source_language} → {result.target_language}")
print(f"Backend: {result.backend}")
print(f"Confidence: {result.confidence:.2%}")

# Output:
# Original: The document management system is excellent.
# Translated: El sistema de gestión de documentos es excelente.
# Language: en → es
# Backend: google
# Confidence: 100%
```

### Example 2: Multi-Language Translation

```python
# Translate to multiple languages
text = "Hello, welcome to our document management system"
target_languages = ["es", "fr", "de", "it", "pt"]

for lang in target_languages:
    result = translator.translate(text, target_language=lang)
    print(f"{lang}: {result.translated_text}")

# Output:
# es: Hola, bienvenido a nuestro sistema de gestión de documentos
# fr: Bonjour, bienvenue dans notre système de gestion de documents
# de: Hallo, willkommen in unserem Dokumentenverwaltungssystem
# it: Ciao, benvenuto nel nostro sistema di gestione dei documenti
# pt: Olá, bem-vindo ao nosso sistema de gerenciamento de documentos
```

### Example 3: Batch Translation with Progress

```python
# Translate multiple documents
documents = [
    "Invoice #1234 - Total: $500",
    "Contract signed on 2026-01-15",
    "Meeting scheduled for tomorrow at 10 AM",
    "Please review the attached proposal",
    "Thank you for your business"
]

# Translate batch
batch_result = translator.translate_batch(
    texts=documents,
    target_language="es"
)

# Display results
print(f"Translation Summary:")
print(f"  Total: {batch_result.total_texts}")
print(f"  Successful: {batch_result.successful}")
print(f"  Failed: {batch_result.failed}")
print(f"  Success Rate: {batch_result.success_rate:.1%}")
print(f"  Time: {batch_result.total_time_seconds:.2f}s")
print(f"  Words: {batch_result.words_translated}")
print()

# Display translations
for result in batch_result.results:
    print(f"EN: {result.source_text}")
    print(f"ES: {result.translated_text}")
    print()
```

### Example 4: Document Translation with Format Preservation

```python
from pathlib import Path

# Create a sample document
doc_content = """# Project Report

## Executive Summary

This document contains important information about our project.

## Key Points

1. Timeline: Q1 2026
2. Budget: $100,000
3. Team: 5 members

## Conclusion

The project is on track and within budget.
"""

# Save document
doc_path = Path("report.txt")
doc_path.write_text(doc_content)

# Translate document
result = translator.translate_document(
    document_path=doc_path,
    target_language="es",
    preserve_formatting=True
)

print(f"Source: {result['source_file']}")
print(f"Language: {result['source_language']} → {result['target_language']}")
print(f"Words: {result['word_count']}")
print(f"Backend: {result['backend']}")
print()
print("Translated Content:")
print(result['translated_content'])

# Clean up
doc_path.unlink()
```

### Example 5: Custom Backend Configuration

```python
from src.ml.document_translator import (
    DocumentTranslator,
    TranslationBackend,
    TranslationQuality
)

# High-quality translation with DeepL
translator_hq = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key="your-deepl-api-key",
    quality=TranslationQuality.HIGH,
    cache_enabled=True
)

# Fast translation with Google
translator_fast = DocumentTranslator(
    backend=TranslationBackend.GOOGLE,
    quality=TranslationQuality.FAST,
    cache_enabled=True
)

# Offline translation with Argos
translator_offline = DocumentTranslator(
    backend=TranslationBackend.ARGOS,
    cache_enabled=False
)

# Use appropriate translator based on requirements
text = "Important business proposal"

# High quality for important content
hq_result = translator_hq.translate(text, "de")

# Fast for user interface
fast_result = translator_fast.translate(text, "es")

# Offline for secure content
offline_result = translator_offline.translate(text, "fr")
```

---

## Performance

### Benchmarks

| Operation | Time | Throughput |
|-----------|------|------------|
| Single translation (cached) | <1ms | 1000+ trans/sec |
| Single translation (Google) | 200-500ms | 2-5 trans/sec |
| Single translation (DeepL) | 150-300ms | 3-7 trans/sec |
| Batch translation (10 texts) | 1-2s | 5-10 texts/sec |
| Document translation (1000 words) | 2-5s | 200-500 words/sec |
| Language detection | 10-50ms | 20-100 detections/sec |

### Optimization Tips

#### 1. Enable Caching

```python
# Enable caching for better performance
translator = DocumentTranslator(cache_enabled=True)

# Cache is especially effective for:
# - Repeated content
# - Common phrases
# - User interface strings
```

#### 2. Use Batch Translation

```python
# Bad: Translate one by one
for text in texts:
    result = translator.translate(text, "es")

# Good: Use batch translation
batch_result = translator.translate_batch(texts, "es")
```

#### 3. Choose Appropriate Backend

```python
# For high-volume, low-cost: Google Translate
translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

# For high-quality, important content: DeepL
translator = DocumentTranslator(backend=TranslationBackend.DEEPL, api_key=key)

# For offline, privacy-sensitive: Argos
translator = DocumentTranslator(backend=TranslationBackend.ARGOS)
```

#### 4. Specify Source Language

```python
# Slower: Auto-detect language
result = translator.translate(text, target_language="es")

# Faster: Specify source language
result = translator.translate(
    text,
    target_language="es",
    source_language="en"
)
```

### Memory Usage

- **Cache Memory**: ~1KB per cached translation
- **Model Memory**: Negligible (backends handle models)
- **Document Processing**: ~2x document size

### Scaling Recommendations

- **Small scale** (<1000 trans/day): Google Translate
- **Medium scale** (1K-100K trans/day): DeepL with caching
- **Large scale** (>100K trans/day): Self-hosted LibreTranslate cluster
- **Enterprise**: Multi-backend with load balancing

---

## Best Practices

### 1. Backend Selection

```python
# Development: Use free Google Translate
dev_translator = DocumentTranslator(backend=TranslationBackend.GOOGLE)

# Production: Use high-quality DeepL
prod_translator = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key=os.environ["DEEPL_API_KEY"]
)

# Offline/Secure: Use Argos Translate
secure_translator = DocumentTranslator(backend=TranslationBackend.ARGOS)
```

### 2. Error Handling

```python
from src.ml.document_translator import DocumentTranslator

translator = DocumentTranslator()

try:
    result = translator.translate(text, target_language="es")
except ValueError as e:
    # Handle invalid language code
    print(f"Invalid language: {e}")
except RuntimeError as e:
    # Handle translation backend errors
    print(f"Translation failed: {e}")
except Exception as e:
    # Handle other errors
    print(f"Unexpected error: {e}")
```

### 3. Cache Management

```python
# Monitor cache performance
stats = translator.get_statistics()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")

# Clear cache periodically
if stats['cache_size'] > 10000:
    translator.clear_cache()

# Disable cache for one-time translations
translator_no_cache = DocumentTranslator(cache_enabled=False)
```

### 4. Quality Assurance

```python
# Check translation confidence
result = translator.translate(text, target_language="es")

if result.confidence < 0.8:
    print("Warning: Low confidence translation")
    # Consider manual review or alternative backend

# Use quality metrics
if result.backend == "google":
    quality_rating = 0.85
elif result.backend == "deepl":
    quality_rating = 0.95
else:
    quality_rating = 0.75
```

### 5. Production Deployment

```python
import os
from src.ml.document_translator import DocumentTranslator, TranslationBackend

# Load configuration from environment
backend = os.getenv("TRANSLATION_BACKEND", "auto")
api_key = os.getenv("DEEPL_API_KEY")
cache_enabled = os.getenv("TRANSLATION_CACHE", "true").lower() == "true"

# Create production translator
translator = DocumentTranslator(
    backend=TranslationBackend(backend),
    api_key=api_key,
    cache_enabled=cache_enabled
)

# Log backend information
print(f"Translation backend: {translator._get_backend().value}")
print(f"Available backends: {[b.value for b in translator.available_backends]}")
```

---

## Troubleshooting

### Common Issues

#### 1. No Translation Backend Available

**Error:**
```
RuntimeError: No translation backend available
```

**Solution:**
```bash
# Install at least one backend
pip install googletrans==4.0.0rc1
# OR
pip install deepl
# OR
pip install argostranslate
```

#### 2. Language Detection Failed

**Error:**
```
RuntimeError: Language detection not available
```

**Solution:**
```bash
# Install langdetect
pip install langdetect
```

#### 3. Unsupported Language

**Error:**
```
ValueError: Unsupported target language: xyz
```

**Solution:**
```python
# Check supported languages
from src.ml.document_translator import DocumentTranslator

translator = DocumentTranslator()
print(sorted(translator.SUPPORTED_LANGUAGES))

# Use valid language code
result = translator.translate(text, target_language="es")  # ✓
```

#### 4. DeepL API Key Invalid

**Error:**
```
RuntimeError: DeepL error: Authorization failed
```

**Solution:**
```python
# Get valid API key from https://www.deepl.com/pro-api
translator = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key="your-valid-api-key"
)
```

#### 5. Rate Limiting

**Error:**
```
Too many requests
```

**Solution:**
```python
import time

# Add delays between requests
for text in texts:
    result = translator.translate(text, "es")
    time.sleep(0.5)  # 500ms delay

# Or switch to paid API
translator = DocumentTranslator(
    backend=TranslationBackend.DEEPL,
    api_key="your-api-key"
)
```

### Performance Issues

#### Slow Translations

**Symptoms:** Translations taking >5 seconds

**Solutions:**
1. Enable caching
2. Specify source language
3. Use batch translation
4. Switch to faster backend

```python
# Optimize for speed
translator = DocumentTranslator(
    backend=TranslationBackend.GOOGLE,  # Fast backend
    cache_enabled=True  # Enable caching
)

# Specify source language
result = translator.translate(
    text,
    target_language="es",
    source_language="en"  # Don't auto-detect
)
```

#### High Memory Usage

**Symptoms:** Memory usage growing over time

**Solutions:**
1. Limit cache size
2. Clear cache periodically
3. Disable cache if not needed

```python
from src.ml.document_translator import TranslationCache

# Limit cache size
translator = DocumentTranslator(cache_enabled=True)
translator.cache = TranslationCache(
    max_entries=1000,  # Limit to 1000 entries
    ttl_hours=1        # Expire after 1 hour
)
```

### API Issues

#### Connection Errors

**Symptoms:** Network errors, timeouts

**Solutions:**
1. Check internet connection
2. Verify API endpoints
3. Use offline backend for unreliable networks

```python
# Use offline backend
translator = DocumentTranslator(backend=TranslationBackend.ARGOS)
```

---

## Advanced Usage

### Custom Translation Pipeline

```python
from src.ml.document_translator import DocumentTranslator, TranslationBackend

class CustomTranslator:
    def __init__(self):
        # Primary: DeepL for quality
        self.primary = DocumentTranslator(
            backend=TranslationBackend.DEEPL,
            api_key=os.getenv("DEEPL_API_KEY")
        )

        # Fallback: Google Translate
        self.fallback = DocumentTranslator(
            backend=TranslationBackend.GOOGLE
        )

    def translate(self, text, target_language):
        try:
            # Try primary backend
            return self.primary.translate(text, target_language)
        except Exception:
            # Fallback to Google
            return self.fallback.translate(text, target_language)
```

### Integration with Document Processing

```python
from src.ml.document_translator import DocumentTranslator
from src.core.document_parser import DocumentParser

def translate_parsed_document(doc_path, target_language):
    # Parse document
    parser = DocumentParser()
    doc = parser.parse(doc_path)

    # Translate content
    translator = DocumentTranslator()
    result = translator.translate(
        doc.text,
        target_language=target_language
    )

    # Create translated document
    translated_doc = {
        "title": doc.metadata.get("title", ""),
        "content": result.translated_text,
        "language": target_language,
        "source_language": result.source_language
    }

    return translated_doc
```

---

## FAQ

**Q: Which backend should I use?**

A:
- **DeepL**: Best quality, paid, professional use
- **Google**: Good quality, free (limited), general use
- **Argos**: Free, offline, privacy-sensitive

**Q: How accurate are the translations?**

A: Quality varies by backend:
- DeepL: 90-95% accuracy
- Google: 80-90% accuracy
- Argos: 70-80% accuracy

**Q: Can I translate documents offline?**

A: Yes, use Argos Translate backend for offline translation.

**Q: How many languages are supported?**

A: 100+ languages with Google/Argos, ~30 with DeepL.

**Q: Is there a cost?**

A:
- Google: Free (rate-limited)
- DeepL: Paid (€4.99/month+)
- Argos: Free
- LibreTranslate: Free (self-hosted)

**Q: How fast is translation?**

A:
- Cached: <1ms
- Google: 200-500ms
- DeepL: 150-300ms
- Argos: 500-1000ms

---

## Resources

### Documentation
- [Google Translate API](https://cloud.google.com/translate)
- [DeepL API](https://www.deepl.com/docs-api)
- [Argos Translate](https://github.com/argosopentech/argos-translate)
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)

### Related Guides
- [Semantic Search Guide](SEMANTIC_SEARCH_GUIDE.md)
- [API Documentation](API_DOCUMENTATION_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

**Document Translation Module v1.0** - Production Ready - 2026-01-16 ✅
