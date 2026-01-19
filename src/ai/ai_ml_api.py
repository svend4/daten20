"""
Unified AI/ML API - v3.5

Single interface for all AI/ML operations.
Provides a simplified API for accessing all AI/ML services.
"""

from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import logging

from .llm_integration import get_llm_client, LLMProvider
from .document_intelligence import get_document_intelligence, SummaryType
from .recommendations import get_recommendation_engine, RecommendationMethod
from .text_analysis import get_text_analyzer, SentimentLabel
from .embeddings import get_embedding_service, EmbeddingModel
from .content_generation import get_content_generator, GenerationType

logger = logging.getLogger(__name__)


class AIOperation(Enum):
    """AI/ML operation types"""
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"
    EXTRACT_ENTITIES = "extract_entities"
    SENTIMENT = "sentiment"
    RECOMMEND = "recommend"
    GENERATE = "generate"
    EMBED = "embed"
    SEARCH = "search"
    TRANSLATE = "translate"
    COMPLETE = "complete"


@dataclass
class AIMLConfig:
    """Configuration for AI/ML API"""
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    enable_caching: bool = True
    cache_ttl: int = 3600
    max_retries: int = 3
    timeout: int = 30


class AIMLAPI:
    """
    Unified AI/ML API - Single interface for all AI/ML operations

    This class provides a simplified, unified interface to all AI/ML services:
    - LLM operations (completion, chat, streaming)
    - Document intelligence (summarization, classification, entity extraction)
    - Recommendations (content-based, collaborative, hybrid)
    - Text analysis (sentiment, keywords, NER)
    - Embeddings (semantic search, similarity)
    - Content generation (templates, translation, style transfer)

    Example:
        api = get_ai_ml_api()

        # Summarize document
        summary = await api.summarize_document(text, max_length=200)

        # Get recommendations
        recommendations = await api.recommend(user_id="user-123", n=10)

        # Analyze sentiment
        sentiment = api.analyze_sentiment(text)
    """

    def __init__(
        self,
        config: Optional[AIMLConfig] = None,
        enable_llm: bool = True,
        enable_doc_intelligence: bool = True,
        enable_recommendations: bool = True,
        enable_text_analysis: bool = True,
        enable_embeddings: bool = True,
        enable_content_gen: bool = True
    ):
        """Initialize AI/ML API with services"""
        self.config = config or AIMLConfig()

        # Initialize services
        self.llm_client = get_llm_client(provider=self.config.llm_provider) if enable_llm else None
        self.doc_intelligence = get_document_intelligence() if enable_doc_intelligence else None
        self.recommender = get_recommendation_engine() if enable_recommendations else None
        self.text_analyzer = get_text_analyzer() if enable_text_analysis else None
        self.embedding_service = get_embedding_service() if enable_embeddings else None
        self.content_generator = get_content_generator() if enable_content_gen else None

        # Statistics
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in AIOperation},
            "total_tokens": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        logger.info("AI/ML API initialized with all services")

    # ==================== LLM Operations ====================

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Complete text using LLM

        Args:
            prompt: Input prompt
            model: Model to use (default: from config)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if not self.llm_client:
            raise ValueError("LLM client not enabled")

        self._track_operation(AIOperation.COMPLETE)

        response = await self.llm_client.complete(
            prompt=prompt,
            model=model or self.config.llm_model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        self.stats["total_tokens"] += response.usage.total_tokens
        return response.content

    async def complete_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream LLM completion"""
        if not self.llm_client:
            raise ValueError("LLM client not enabled")

        self._track_operation(AIOperation.COMPLETE)

        async for chunk in self.llm_client.complete_stream(
            prompt=prompt,
            model=model or self.config.llm_model,
            **kwargs
        ):
            yield chunk

    # ==================== Document Intelligence ====================

    async def summarize_document(
        self,
        text: str,
        summary_type: SummaryType = SummaryType.EXTRACTIVE,
        max_length: int = 200,
        **kwargs
    ) -> str:
        """
        Summarize document

        Args:
            text: Document text
            summary_type: Extractive or abstractive
            max_length: Maximum summary length

        Returns:
            Document summary
        """
        if not self.doc_intelligence:
            raise ValueError("Document intelligence not enabled")

        self._track_operation(AIOperation.SUMMARIZE)

        summary = await self.doc_intelligence.summarize(
            text=text,
            summary_type=summary_type,
            max_length=max_length,
            **kwargs
        )

        return summary.text

    async def classify_document(
        self,
        text: str,
        categories: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Classify document into categories

        Args:
            text: Document text
            categories: List of possible categories

        Returns:
            Dict of category: confidence scores
        """
        if not self.doc_intelligence:
            raise ValueError("Document intelligence not enabled")

        self._track_operation(AIOperation.CLASSIFY)

        classification = await self.doc_intelligence.classify(
            text=text,
            categories=categories,
            **kwargs
        )

        return {c.category: c.confidence for c in classification}

    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract entities from document

        Args:
            text: Document text
            entity_types: Types of entities to extract

        Returns:
            List of extracted entities
        """
        if not self.doc_intelligence:
            raise ValueError("Document intelligence not enabled")

        self._track_operation(AIOperation.EXTRACT_ENTITIES)

        entities = await self.doc_intelligence.extract_entities(
            text=text,
            entity_types=entity_types,
            **kwargs
        )

        return [
            {
                "text": e.text,
                "type": e.type,
                "confidence": e.confidence,
                "start": e.start_pos,
                "end": e.end_pos
            }
            for e in entities
        ]

    async def analyze_document(
        self,
        text: str,
        operations: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Comprehensive document analysis

        Args:
            text: Document text
            operations: List of operations to perform

        Returns:
            Dict with analysis results
        """
        if not self.doc_intelligence:
            raise ValueError("Document intelligence not enabled")

        operations = operations or ["summarize", "classify", "extract_entities"]
        results = {}

        if "summarize" in operations:
            results["summary"] = await self.summarize_document(text, **kwargs)

        if "classify" in operations:
            results["categories"] = await self.classify_document(text, **kwargs)

        if "extract_entities" in operations:
            results["entities"] = await self.extract_entities(text, **kwargs)

        return results

    # ==================== Recommendations ====================

    async def recommend(
        self,
        user_id: str,
        n: int = 10,
        method: RecommendationMethod = RecommendationMethod.HYBRID,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations

        Args:
            user_id: User ID
            n: Number of recommendations
            method: Recommendation method
            filters: Optional filters

        Returns:
            List of recommendations
        """
        if not self.recommender:
            raise ValueError("Recommendation engine not enabled")

        self._track_operation(AIOperation.RECOMMEND)

        recommendations = await self.recommender.recommend(
            user_id=user_id,
            n=n,
            method=method,
            filters=filters,
            **kwargs
        )

        return [
            {
                "document_id": r.document_id,
                "title": r.title,
                "score": r.score,
                "reason": r.reason
            }
            for r in recommendations
        ]

    async def find_similar(
        self,
        document_id: str,
        n: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Find similar documents"""
        if not self.recommender:
            raise ValueError("Recommendation engine not enabled")

        similar = await self.recommender.find_similar(
            document_id=document_id,
            n=n,
            **kwargs
        )

        return [
            {
                "document_id": r.document_id,
                "title": r.title,
                "similarity": r.score
            }
            for r in similar
        ]

    # ==================== Text Analysis ====================

    def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze text sentiment

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results
        """
        if not self.text_analyzer:
            raise ValueError("Text analyzer not enabled")

        self._track_operation(AIOperation.SENTIMENT)

        sentiment = self.text_analyzer.analyze_sentiment(text, **kwargs)

        return {
            "label": sentiment.label.value,
            "score": sentiment.score,
            "confidence": sentiment.confidence,
            "positive": sentiment.positive_score,
            "negative": sentiment.negative_score,
            "neutral": sentiment.neutral_score
        }

    def extract_keywords(
        self,
        text: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Extract keywords from text"""
        if not self.text_analyzer:
            raise ValueError("Text analyzer not enabled")

        keywords = self.text_analyzer.extract_keywords(text, top_k=top_k, **kwargs)

        return [
            {
                "keyword": kw.word,
                "score": kw.score,
                "frequency": kw.frequency
            }
            for kw in keywords
        ]

    def detect_language(self, text: str) -> str:
        """Detect text language"""
        if not self.text_analyzer:
            raise ValueError("Text analyzer not enabled")

        detection = self.text_analyzer.detect_language(text)
        return detection.language

    # ==================== Embeddings & Search ====================

    async def embed_text(
        self,
        text: str,
        model: Optional[EmbeddingModel] = None,
        **kwargs
    ) -> List[float]:
        """
        Generate text embedding

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            Embedding vector
        """
        if not self.embedding_service:
            raise ValueError("Embedding service not enabled")

        self._track_operation(AIOperation.EMBED)

        embedding = await self.embedding_service.embed_text(
            text=text,
            model=model or self.config.embedding_model,
            **kwargs
        )

        return embedding.vector

    async def semantic_search(
        self,
        query: str,
        n: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using embeddings

        Args:
            query: Search query
            n: Number of results

        Returns:
            List of search results
        """
        if not self.embedding_service:
            raise ValueError("Embedding service not enabled")

        self._track_operation(AIOperation.SEARCH)

        results = await self.embedding_service.search(
            query=query,
            n=n,
            **kwargs
        )

        return [
            {
                "document_id": r.document_id,
                "title": r.title,
                "score": r.score,
                "snippet": r.snippet
            }
            for r in results
        ]

    async def compute_similarity(
        self,
        text1: str,
        text2: str,
        **kwargs
    ) -> float:
        """Compute semantic similarity between texts"""
        if not self.embedding_service:
            raise ValueError("Embedding service not enabled")

        similarity = await self.embedding_service.compute_similarity(
            text1=text1,
            text2=text2,
            **kwargs
        )

        return similarity

    # ==================== Content Generation ====================

    async def generate_content(
        self,
        generation_type: GenerationType,
        input_text: str,
        **kwargs
    ) -> str:
        """
        Generate content

        Args:
            generation_type: Type of generation
            input_text: Input text

        Returns:
            Generated content
        """
        if not self.content_generator:
            raise ValueError("Content generator not enabled")

        self._track_operation(AIOperation.GENERATE)

        generated = await self.content_generator.generate(
            generation_type=generation_type,
            input_text=input_text,
            **kwargs
        )

        return generated.text

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        **kwargs
    ) -> str:
        """Translate text"""
        if not self.content_generator:
            raise ValueError("Content generator not enabled")

        self._track_operation(AIOperation.TRANSLATE)

        translated = await self.content_generator.translate(
            text=text,
            target_language=target_language,
            source_language=source_language,
            **kwargs
        )

        return translated

    async def paraphrase(
        self,
        text: str,
        style: Optional[str] = None,
        **kwargs
    ) -> str:
        """Paraphrase text"""
        if not self.content_generator:
            raise ValueError("Content generator not enabled")

        paraphrased = await self.content_generator.paraphrase(
            text=text,
            style=style,
            **kwargs
        )

        return paraphrased

    # ==================== Utility Methods ====================

    def _track_operation(self, operation: AIOperation):
        """Track operation statistics"""
        self.stats["total_operations"] += 1
        self.stats["by_operation"][operation.value] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get API usage statistics

        Returns:
            Dict with usage statistics
        """
        return {
            **self.stats,
            "services_enabled": {
                "llm": self.llm_client is not None,
                "doc_intelligence": self.doc_intelligence is not None,
                "recommender": self.recommender is not None,
                "text_analyzer": self.text_analyzer is not None,
                "embeddings": self.embedding_service is not None,
                "content_generator": self.content_generator is not None,
            }
        }

    def reset_statistics(self):
        """Reset usage statistics"""
        self.stats = {
            "total_operations": 0,
            "by_operation": {op.value: 0 for op in AIOperation},
            "total_tokens": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        logger.info("Statistics reset")


# Singleton
_ai_ml_api = None


def get_ai_ml_api(config: Optional[AIMLConfig] = None) -> AIMLAPI:
    """
    Get singleton AI/ML API instance

    Args:
        config: Optional configuration

    Returns:
        AI/ML API instance
    """
    global _ai_ml_api
    if _ai_ml_api is None:
        _ai_ml_api = AIMLAPI(config=config)
    return _ai_ml_api


# Convenience functions

async def summarize(text: str, **kwargs) -> str:
    """Convenience function for summarization"""
    api = get_ai_ml_api()
    return await api.summarize_document(text, **kwargs)


async def classify(text: str, **kwargs) -> Dict[str, float]:
    """Convenience function for classification"""
    api = get_ai_ml_api()
    return await api.classify_document(text, **kwargs)


async def recommend(user_id: str, n: int = 10, **kwargs) -> List[Dict[str, Any]]:
    """Convenience function for recommendations"""
    api = get_ai_ml_api()
    return await api.recommend(user_id, n, **kwargs)


def sentiment(text: str) -> Dict[str, Any]:
    """Convenience function for sentiment analysis"""
    api = get_ai_ml_api()
    return api.analyze_sentiment(text)


async def translate_text(text: str, target_language: str, **kwargs) -> str:
    """Convenience function for translation"""
    api = get_ai_ml_api()
    return await api.translate(text, target_language, **kwargs)
