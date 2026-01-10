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

from .classifier import (
    DocumentClassifier,
    get_document_classifier,
    configure_document_classifier,
    DocumentCategory,
    ModelType
)

from .tagging import (
    AutoTagger,
    get_auto_tagger,
    configure_auto_tagger,
    TagType
)

from .anomaly import (
    AnomalyDetectionEngine,
    get_anomaly_detector,
    AnomalyType
)

from .ner import (
    NEREngine,
    get_ner_engine,
    EntityType
)

from .recommendations import (
    RecommendationEngine,
    get_recommendation_engine
)

from .predictive import (
    PredictiveAnalyticsEngine,
    get_predictive_engine
)

__all__ = [
    'DocumentClassifier',
    'get_document_classifier',
    'configure_document_classifier',
    'AutoTagger',
    'get_auto_tagger',
    'configure_auto_tagger',
    'AnomalyDetectionEngine',
    'get_anomaly_detector',
    'NEREngine',
    'get_ner_engine',
    'RecommendationEngine',
    'get_recommendation_engine',
    'PredictiveAnalyticsEngine',
    'get_predictive_engine',
    'DocumentCategory',
    'ModelType',
    'TagType',
    'AnomalyType',
    'EntityType'
]
