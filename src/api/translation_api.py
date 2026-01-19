#!/usr/bin/env python3
"""
Translation API Endpoints

Provides REST API endpoints for document translation functionality.

Endpoints:
- POST /api/translate/text - Translate text
- POST /api/translate/batch - Translate multiple texts
- POST /api/translate/document - Translate entire document
- POST /api/translate/detect - Detect language
- GET /api/translate/languages - Get supported languages
- GET /api/translate/stats - Get translation statistics
- DELETE /api/translate/cache - Clear translation cache
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from time import time

from flask import Blueprint, jsonify, request

from src.ml.document_translator import (
    DocumentTranslator,
    TranslationBackend,
    create_translator
)

logger = logging.getLogger("dms.translation_api")

# Create Blueprint
translation_bp = Blueprint("translation", __name__, url_prefix="/api/translate")

# Global translator instance
_translator: Optional[DocumentTranslator] = None


def get_translator() -> DocumentTranslator:
    """Get or create document translator"""
    global _translator
    if _translator is None:
        # Can be configured via environment variables
        backend = TranslationBackend.AUTO
        _translator = DocumentTranslator(backend=backend, cache_enabled=True)
        logger.info(f"Initialized document translator with backend: {backend.value}")
    return _translator


@translation_bp.route("/text", methods=["POST"])
def translate_text():
    """
    Translate text to target language

    Request JSON:
    {
        "text": "Hello, world!",
        "target_language": "es",
        "source_language": "en"  # optional, auto-detected if not provided
    }

    Response:
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
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or "text" not in data or "target_language" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: 'text' and 'target_language'"
            }), 400

        text = data["text"]
        target_language = data["target_language"]
        source_language = data.get("source_language")

        # Validate inputs
        if not text or not isinstance(text, str):
            return jsonify({"success": False, "error": "Text must be a non-empty string"}), 400

        # Translate
        start_time = time()
        translator = get_translator()
        result = translator.translate(text, target_language, source_language)
        elapsed_ms = (time() - start_time) * 1000

        return jsonify({
            "success": True,
            "result": {
                "source_text": result.source_text,
                "translated_text": result.translated_text,
                "source_language": result.source_language,
                "target_language": result.target_language,
                "backend": result.backend,
                "confidence": result.confidence,
                "translation_time_ms": round(elapsed_ms, 2)
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"success": False, "error": f"Translation failed: {str(e)}"}), 500


@translation_bp.route("/batch", methods=["POST"])
def translate_batch():
    """
    Translate multiple texts in batch

    Request JSON:
    {
        "texts": ["Hello", "Good morning", "How are you?"],
        "target_language": "es",
        "source_language": "en"  # optional
    }

    Response:
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
            "total_time_seconds": 1.23,
            "words_translated": 12,
            "success_rate": 1.0
        }
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or "texts" not in data or "target_language" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: 'texts' and 'target_language'"
            }), 400

        texts = data["texts"]
        target_language = data["target_language"]
        source_language = data.get("source_language")

        # Validate inputs
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({"success": False, "error": "Texts must be a non-empty list"}), 400

        # Translate batch
        translator = get_translator()
        batch_result = translator.translate_batch(texts, target_language, source_language)

        # Format results
        results = [
            {
                "source_text": r.source_text,
                "translated_text": r.translated_text,
                "source_language": r.source_language,
                "target_language": r.target_language,
                "backend": r.backend,
                "confidence": r.confidence
            }
            for r in batch_result.results
        ]

        return jsonify({
            "success": True,
            "results": results,
            "summary": {
                "total_texts": batch_result.total_texts,
                "successful": batch_result.successful,
                "failed": batch_result.failed,
                "total_time_seconds": round(batch_result.total_time_seconds, 2),
                "words_translated": batch_result.words_translated,
                "success_rate": batch_result.success_rate
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        return jsonify({"success": False, "error": f"Batch translation failed: {str(e)}"}), 500


@translation_bp.route("/document", methods=["POST"])
def translate_document():
    """
    Translate entire document file

    Request JSON:
    {
        "document_path": "/path/to/document.txt",
        "target_language": "es",
        "source_language": "en",  # optional
        "preserve_formatting": true  # optional, default: true
    }

    Response:
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
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or "document_path" not in data or "target_language" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: 'document_path' and 'target_language'"
            }), 400

        document_path = data["document_path"]
        target_language = data["target_language"]
        source_language = data.get("source_language")
        preserve_formatting = data.get("preserve_formatting", True)

        # Translate document
        translator = get_translator()
        result = translator.translate_document(
            document_path,
            target_language,
            source_language,
            preserve_formatting
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Document translation error: {e}")
        return jsonify({"success": False, "error": f"Document translation failed: {str(e)}"}), 500


@translation_bp.route("/detect", methods=["POST"])
def detect_language():
    """
    Detect language of text

    Request JSON:
    {
        "text": "Bonjour le monde"
    }

    Response:
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
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Missing required field: 'text'"}), 400

        text = data["text"]

        if not text or not isinstance(text, str):
            return jsonify({"success": False, "error": "Text must be a non-empty string"}), 400

        # Detect language
        translator = get_translator()
        detection = translator.detect_language(text)

        return jsonify({
            "success": True,
            "result": {
                "language": detection.language,
                "confidence": detection.confidence,
                "alternatives": detection.alternatives
            }
        })

    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return jsonify({"success": False, "error": f"Language detection failed: {str(e)}"}), 500


@translation_bp.route("/languages", methods=["GET"])
def get_supported_languages():
    """
    Get list of supported languages

    Response:
    {
        "success": true,
        "languages": ["en", "es", "fr", "de", ...],
        "total_languages": 100
    }
    """
    try:
        languages = sorted(list(DocumentTranslator.SUPPORTED_LANGUAGES))

        return jsonify({
            "success": True,
            "languages": languages,
            "total_languages": len(languages)
        })

    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@translation_bp.route("/stats", methods=["GET"])
def get_statistics():
    """
    Get translation statistics

    Response:
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
    """
    try:
        translator = get_translator()
        stats = translator.get_statistics()

        return jsonify({
            "success": True,
            "stats": stats
        })

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@translation_bp.route("/cache", methods=["DELETE"])
def clear_cache():
    """
    Clear translation cache

    Response:
    {
        "success": true,
        "message": "Translation cache cleared successfully"
    }
    """
    try:
        translator = get_translator()
        translator.clear_cache()

        return jsonify({
            "success": True,
            "message": "Translation cache cleared successfully"
        })

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@translation_bp.route("/backends", methods=["GET"])
def get_available_backends():
    """
    Get available translation backends

    Response:
    {
        "success": true,
        "backends": {
            "available": ["google", "deepl"],
            "current": "google"
        }
    }
    """
    try:
        translator = get_translator()
        available = [backend.value for backend in translator.available_backends]
        current = translator._get_backend().value

        return jsonify({
            "success": True,
            "backends": {
                "available": available,
                "current": current
            }
        })

    except Exception as e:
        logger.error(f"Error getting backends: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Health check endpoint
@translation_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint

    Response:
    {
        "success": true,
        "status": "healthy",
        "backends_available": ["google", "deepl"]
    }
    """
    try:
        translator = get_translator()
        backends = [backend.value for backend in translator.available_backends]

        return jsonify({
            "success": True,
            "status": "healthy",
            "backends_available": backends
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }), 503


# Error handlers
@translation_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@translation_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"success": False, "error": "Internal server error"}), 500
