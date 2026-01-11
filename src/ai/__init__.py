"""
AI/ML Module - v3.5

Advanced AI and Machine Learning services with LLM integration.

Modules:
- ai_services: Unified AI/ML services

Components:
- LLM Integration: Multi-provider LLM support (OpenAI, Anthropic, local)
- Document Intelligence: AI-powered document analysis and summarization
- Recommendations: ML recommendation engine with collaborative filtering
- Text Analysis: Sentiment analysis, NER, keyword extraction

Version: 3.5.0
"""

__version__ = '3.5.0'

from .ai_services import (
    # LLM Integration
    LLMClient,
    LLMProvider,
    LLMResponse,
    PromptTemplate,
    get_llm_client,
    # Document Intelligence
    DocumentIntelligence,
    DocumentAnalysis,
    Entity,
    EntityType,
    get_document_intelligence,
    # Recommendations
    RecommendationEngine,
    Recommendation,
    get_recommendation_engine,
)

__all__ = [
    # LLM Integration
    'LLMClient',
    'LLMProvider',
    'LLMResponse',
    'PromptTemplate',
    'get_llm_client',
    # Document Intelligence
    'DocumentIntelligence',
    'DocumentAnalysis',
    'Entity',
    'EntityType',
    'get_document_intelligence',
    # Recommendations
    'RecommendationEngine',
    'Recommendation',
    'get_recommendation_engine',
]
