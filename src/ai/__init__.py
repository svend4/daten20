"""
AI/ML Module - v3.5

Advanced AI and Machine Learning services with LLM integration.

Modules:
- llm_integration: Multi-provider LLM client (OpenAI, Anthropic, local)
- document_intelligence: AI-powered document analysis and understanding
- recommendations: ML-powered recommendation engine
- text_analysis: Advanced NLP and text processing
- embeddings: Vector embeddings and semantic search
- content_generation: AI-powered content creation

Components:
- LLM Integration: Multi-provider LLM support (OpenAI, Anthropic, local)
- Document Intelligence: Summarization, entity extraction, classification
- Recommendations: Content-based, collaborative filtering, hybrid
- Text Analysis: Sentiment, emotion, keywords, readability
- Embeddings: Semantic search, document similarity, clustering
- Content Generation: Templates, translation, paraphrasing, grammar

Version: 3.5.0 (Complete)
"""

__version__ = '3.5.0'

# Unified AI/ML API
from .ai_ml_api import (
    AIMLAPI,
    AIMLConfig,
    AIOperation,
    get_ai_ml_api,
    summarize,
    classify,
    recommend,
    sentiment,
    translate_text,
)

# LLM Integration
from .llm_integration import (
    LLMProvider,
    LLMConfig,
    LLMResponse,
    TokenUsage,
    BaseLLMClient,
    PromptTemplate,
    get_llm_client,
    complete,
    complete_stream,
    PROMPT_TEMPLATES,
)

# Document Intelligence
from .document_intelligence import (
    DocumentIntelligence,
    DocumentAnalysis,
    DocumentSummary,
    DocumentClassification,
    DocumentMetadata,
    Entity,
    KeyPoint,
    SummaryType,
    ClassificationType,
    get_document_intelligence,
)

# Recommendations
from .recommendations import (
    RecommendationEngine,
    Recommendation,
    RecommendationMethod,
    UserInteraction,
    UserProfile,
    Document as RecommendationDocument,
    get_recommendation_engine,
)

# Text Analysis
from .text_analysis import (
    TextAnalyzer,
    SentimentResult,
    SentimentLabel,
    EmotionResult,
    EmotionLabel,
    Keyword,
    TextClassification,
    LanguageDetection,
    ReadabilityMetrics,
    get_text_analyzer,
)

# Embeddings & Vector Search
from .embeddings import (
    EmbeddingService,
    Embedding,
    EmbeddingModel,
    SearchResult,
    ClusterResult,
    Document as EmbeddingDocument,
    get_embedding_service,
)

# Content Generation
from .content_generation import (
    ContentGenerator,
    GeneratedContent,
    GenerationType,
    ContentStyle,
    GenerationConfig,
    get_content_generator,
)

# Legacy AI services (for backward compatibility)
from .ai_services import (
    LLMClient,
    DocumentIntelligence as LegacyDocumentIntelligence,
    DocumentAnalysis as LegacyDocumentAnalysis,
    Entity as LegacyEntity,
    EntityType,
    RecommendationEngine as LegacyRecommendationEngine,
    Recommendation as LegacyRecommendation,
)

__all__ = [
    # Unified API
    'AIMLAPI',
    'AIMLConfig',
    'AIOperation',
    'get_ai_ml_api',
    'summarize',
    'classify',
    'recommend',
    'sentiment',
    'translate_text',

    # LLM Integration
    'LLMProvider',
    'LLMConfig',
    'LLMResponse',
    'TokenUsage',
    'BaseLLMClient',
    'PromptTemplate',
    'get_llm_client',
    'complete',
    'complete_stream',
    'PROMPT_TEMPLATES',

    # Document Intelligence
    'DocumentIntelligence',
    'DocumentAnalysis',
    'DocumentSummary',
    'DocumentClassification',
    'DocumentMetadata',
    'Entity',
    'KeyPoint',
    'SummaryType',
    'ClassificationType',
    'get_document_intelligence',

    # Recommendations
    'RecommendationEngine',
    'Recommendation',
    'RecommendationMethod',
    'UserInteraction',
    'UserProfile',
    'RecommendationDocument',
    'get_recommendation_engine',

    # Text Analysis
    'TextAnalyzer',
    'SentimentResult',
    'SentimentLabel',
    'EmotionResult',
    'EmotionLabel',
    'Keyword',
    'TextClassification',
    'LanguageDetection',
    'ReadabilityMetrics',
    'get_text_analyzer',

    # Embeddings & Vector Search
    'EmbeddingService',
    'Embedding',
    'EmbeddingModel',
    'SearchResult',
    'ClusterResult',
    'EmbeddingDocument',
    'get_embedding_service',

    # Content Generation
    'ContentGenerator',
    'GeneratedContent',
    'GenerationType',
    'ContentStyle',
    'GenerationConfig',
    'get_content_generator',

    # Legacy (backward compatibility)
    'LLMClient',
    'LegacyDocumentIntelligence',
    'LegacyDocumentAnalysis',
    'LegacyEntity',
    'EntityType',
    'LegacyRecommendationEngine',
    'LegacyRecommendation',
]
