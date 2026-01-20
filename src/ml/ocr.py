#!/usr/bin/env python3
"""
OCR Module (Pure Python - Simplified)

Mock OCR without tesseract/numpy dependencies.
"""

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class OCRResult:
    """OCR result"""
    text: str
    confidence: float
    bounding_boxes: List[Dict[str, Any]] = None

@dataclass
class TextRegion:
    """Text region"""
    text: str
    bbox: Dict[str, int]
    confidence: float

class OCREngine:
    """OCR engine (Pure Python - Mock)"""
    
    def __init__(self, language: str = "eng"):
        self.language = language
    
    def extract_text(self, image_path: str, confidence_threshold: float = 0.5) -> OCRResult:
        """Extract text from image (mock)"""
        # Mock OCR result
        mock_text = "This is mock OCR text extracted from the image."
        confidence = random.uniform(0.7, 0.95)
        
        bounding_boxes = [
            {"x": 10, "y": 10, "w": 100, "h": 20, "text": "This is", "confidence": 0.92},
            {"x": 10, "y": 35, "w": 150, "h": 20, "text": "mock OCR text", "confidence": 0.88},
        ]
        
        return OCRResult(
            text=mock_text,
            confidence=confidence,
            bounding_boxes=bounding_boxes
        )
    
    def extract_regions(self, image_path: str) -> List[TextRegion]:
        """Extract text regions (mock)"""
        regions = [
            TextRegion(
                text=f"Region {i}",
                bbox={"x": i*50, "y": i*30, "w": 100, "h": 25},
                confidence=random.uniform(0.7, 0.95)
            )
            for i in range(3)
        ]
        return regions
    
    def extract_table(self, image_path: str) -> List[List[str]]:
        """Extract table from image (mock)"""
        return [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
        ]

def get_ocr_engine(language: str = "eng") -> OCREngine:
    """Get OCR engine singleton"""
    return OCREngine(language=language)
