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

Version: 3.5.0
"""

__version__ = "3.5.0"

# Legacy AI services (for backward compatibility)
from .ai_services import DocumentAnalysis as LegacyDocumentAnalysis
from .ai_services import DocumentIntelligence as LegacyDocumentIntelligence
from .ai_services import Entity as LegacyEntity
from .ai_services import (
    EntityType,
    LLMClient,
)
from .ai_services import Recommendation as LegacyRecommendation
from .ai_services import RecommendationEngine as LegacyRecommendationEngine

# Content Generation
from .content_generation import (
    ContentGenerator,
    ContentStyle,
    GeneratedContent,
    GenerationConfig,
    GenerationType,
    get_content_generator,
)

# Document Intelligence
from .document_intelligence import (
    ClassificationType,
    DocumentAnalysis,
    DocumentClassification,
    DocumentIntelligence,
    DocumentMetadata,
    DocumentSummary,
    Entity,
    KeyPoint,
    SummaryType,
    get_document_intelligence,
)

# Embeddings & Vector Search
from .embeddings import (
    ClusterResult,
)
from .embeddings import Document as EmbeddingDocument
from .embeddings import (
    Embedding,
    EmbeddingModel,
    EmbeddingService,
    SearchResult,
    get_embedding_service,
)

# LLM Integration
from .llm_integration import (
    PROMPT_TEMPLATES,
    BaseLLMClient,
    LLMConfig,
    LLMProvider,
    LLMResponse,
    PromptTemplate,
    TokenUsage,
    complete,
    complete_stream,
    get_llm_client,
)

# Recommendations
from .recommendations import Document as RecommendationDocument
from .recommendations import (
    Recommendation,
    RecommendationEngine,
    RecommendationMethod,
    UserInteraction,
    UserProfile,
    get_recommendation_engine,
)

# Text Analysis
from .text_analysis import (
    EmotionLabel,
    EmotionResult,
    Keyword,
    LanguageDetection,
    ReadabilityMetrics,
    SentimentLabel,
    SentimentResult,
    TextAnalyzer,
    TextClassification,
    get_text_analyzer,
)

__all__ = [
    # LLM Integration
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "TokenUsage",
    "BaseLLMClient",
    "PromptTemplate",
    "get_llm_client",
    "complete",
    "complete_stream",
    "PROMPT_TEMPLATES",
    # Document Intelligence
    "DocumentIntelligence",
    "DocumentAnalysis",
    "DocumentSummary",
    "DocumentClassification",
    "DocumentMetadata",
    "Entity",
    "KeyPoint",
    "SummaryType",
    "ClassificationType",
    "get_document_intelligence",
    # Recommendations
    "RecommendationEngine",
    "Recommendation",
    "RecommendationMethod",
    "UserInteraction",
    "UserProfile",
    "RecommendationDocument",
    "get_recommendation_engine",
    # Text Analysis
    "TextAnalyzer",
    "SentimentResult",
    "SentimentLabel",
    "EmotionResult",
    "EmotionLabel",
    "Keyword",
    "TextClassification",
    "LanguageDetection",
    "ReadabilityMetrics",
    "get_text_analyzer",
    # Embeddings & Vector Search
    "EmbeddingService",
    "Embedding",
    "EmbeddingModel",
    "SearchResult",
    "ClusterResult",
    "EmbeddingDocument",
    "get_embedding_service",
    # Content Generation
    "ContentGenerator",
    "GeneratedContent",
    "GenerationType",
    "ContentStyle",
    "GenerationConfig",
    "get_content_generator",
    # Legacy (backward compatibility)
    "LLMClient",
    "LegacyDocumentIntelligence",
    "LegacyDocumentAnalysis",
    "LegacyEntity",
    "EntityType",
    "LegacyRecommendationEngine",
    "LegacyRecommendation",
]
