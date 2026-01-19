"""
Machine Learning Module

Provides ML capabilities:
- Document classification
- Auto-tagging
- Anomaly detection
- Named Entity Recognition (NER)
- Recommendations
- Predictive analytics
"""

from .anomaly import AnomalyDetectionEngine, AnomalyType, get_anomaly_detector
from .classifier import (
    DocumentCategory,
    DocumentClassifier,
    ModelType,
    configure_document_classifier,
    get_document_classifier,
)
from .ner import EntityType, NEREngine, get_ner_engine
from .predictive import PredictiveAnalyticsEngine, get_predictive_engine
from .recommendations import RecommendationEngine, get_recommendation_engine
from .tagging import AutoTagger, TagType, configure_auto_tagger, get_auto_tagger

__all__ = [
    "DocumentClassifier",
    "get_document_classifier",
    "configure_document_classifier",
    "AutoTagger",
    "get_auto_tagger",
    "configure_auto_tagger",
    "AnomalyDetectionEngine",
    "get_anomaly_detector",
    "NEREngine",
    "get_ner_engine",
    "RecommendationEngine",
    "get_recommendation_engine",
    "PredictiveAnalyticsEngine",
    "get_predictive_engine",
    "DocumentCategory",
    "ModelType",
    "TagType",
    "AnomalyType",
    "EntityType",
]
