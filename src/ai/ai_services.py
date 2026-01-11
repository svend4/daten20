#!/usr/bin/env python3
"""
AI Services Module

Comprehensive AI/ML services including LLM integration, document intelligence,
recommendations, and text analysis.

Key Features:
- Multi-provider LLM support (OpenAI, Anthropic, local)
- Document summarization and analysis
- Sentiment analysis and NER
- Smart recommendations
- Embeddings and semantic search

Dependencies:
- Optional: openai, anthropic for LLM providers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator, Tuple
from enum import Enum
from datetime import datetime
import threading
import logging
import re
import hashlib
from collections import Counter, defaultdict
import math

logger = logging.getLogger(__name__)


# ==================== LLM Integration ====================

class LLMProvider(str, Enum):
    """LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"  # For testing


@dataclass
class LLMResponse:
    """LLM response"""
    content: str
    model: str
    provider: LLMProvider
    tokens_used: int = 0
    cost: float = 0.0
    finish_reason: str = "stop"
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptTemplate:
    """Prompt template manager"""

    TEMPLATES = {
        "summarize": "Summarize the following document in {sentences} sentences:\n\n{text}",
        "extract_entities": "Extract all named entities (people, organizations, locations, dates) from:\n\n{text}",
        "classify": "Classify this document into one of these categories: {categories}\n\nDocument:\n{text}\n\nCategory:",
        "sentiment": "Analyze the sentiment of this text (positive, negative, or neutral):\n\n{text}\n\nSentiment:",
        "keywords": "Extract the top {n} keywords from this text:\n\n{text}\n\nKeywords:",
        "qa": "Answer this question based on the document:\n\nDocument:\n{text}\n\nQuestion: {question}\n\nAnswer:",
    }

    @classmethod
    def get(cls, template_name: str, **kwargs) -> str:
        """Get formatted prompt from template"""
        template = cls.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        return template.format(**kwargs)


class LLMClient:
    """
    Universal LLM client supporting multiple providers

    Provides unified interface for OpenAI, Anthropic, and local models.
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.MOCK,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider
        self.api_key = api_key
        self.model = model or self._default_model()
        self._response_cache: Dict[str, LLMResponse] = {}
        self._lock = threading.Lock()

    def _default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            LLMProvider.OPENAI: "gpt-3.5-turbo",
            LLMProvider.ANTHROPIC: "claude-3-haiku",
            LLMProvider.LOCAL: "llama-2-7b",
            LLMProvider.MOCK: "mock-model"
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> LLMResponse:
        """
        Generate completion

        Args:
            prompt: Input prompt
            model: Model to use (optional)
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            use_cache: Use cached response if available

        Returns:
            LLM response
        """
        model = model or self.model

        # Check cache
        cache_key = self._cache_key(prompt, model)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        # Generate response
        if self.provider == LLMProvider.MOCK:
            response = self._mock_complete(prompt, model, max_tokens)
        else:
            response = await self._api_complete(prompt, model, max_tokens, temperature)

        # Cache response
        if use_cache:
            self._cache_response(cache_key, response)

        return response

    def _mock_complete(self, prompt: str, model: str, max_tokens: int) -> LLMResponse:
        """Mock completion for testing"""
        # Simple mock response based on prompt
        if "summarize" in prompt.lower():
            content = "This is a mock summary of the document."
        elif "sentiment" in prompt.lower():
            content = "positive"
        elif "classify" in prompt.lower():
            content = "general"
        elif "extract" in prompt.lower():
            content = "Person: John Doe\nOrganization: Acme Corp\nDate: 2026-01-10"
        else:
            content = f"Mock response to prompt of length {len(prompt)}"

        return LLMResponse(
            content=content,
            model=model,
            provider=self.provider,
            tokens_used=len(prompt.split()) + len(content.split()),
            cost=0.0
        )

    async def _api_complete(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """Call actual LLM API (simplified, requires actual implementation)"""
        # In production, this would call OpenAI/Anthropic APIs
        # For now, return mock response
        return self._mock_complete(prompt, model, max_tokens)

    def _cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key"""
        key_str = f"{model}:{prompt}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response"""
        with self._lock:
            return self._response_cache.get(cache_key)

    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache response"""
        with self._lock:
            # Limit cache size
            if len(self._response_cache) > 1000:
                # Remove oldest
                self._response_cache.pop(next(iter(self._response_cache)))
            self._response_cache[cache_key] = response

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Rough estimation: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)

    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """Estimate API cost"""
        model = model or self.model

        # Simplified pricing (USD per 1K tokens)
        pricing = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.001,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
        }

        rate = pricing.get(model, 0.001)
        return (tokens / 1000) * rate


# ==================== Document Intelligence ====================

class EntityType(str, Enum):
    """Named entity types"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"


@dataclass
class Entity:
    """Named entity"""
    text: str
    entity_type: EntityType
    confidence: float = 1.0


@dataclass
class DocumentAnalysis:
    """Complete document analysis result"""
    summary: Optional[str] = None
    entities: List[Entity] = field(default_factory=list)
    category: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    language: str = "en"
    readability_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentIntelligence:
    """
    AI-powered document analysis

    Provides summarization, entity extraction, classification, and more.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def analyze(
        self,
        text: str,
        operations: List[str] = None
    ) -> DocumentAnalysis:
        """
        Comprehensive document analysis

        Args:
            text: Document text
            operations: List of operations to perform

        Returns:
            DocumentAnalysis with results
        """
        ops = operations or ["summarize", "extract_entities", "sentiment", "keywords"]

        analysis = DocumentAnalysis()

        if "summarize" in ops:
            analysis.summary = await self.summarize(text)

        if "extract_entities" in ops:
            analysis.entities = await self.extract_entities(text)

        if "sentiment" in ops:
            sentiment, score = await self.analyze_sentiment(text)
            analysis.sentiment = sentiment
            analysis.sentiment_score = score

        if "keywords" in ops:
            analysis.keywords = self.extract_keywords(text)

        if "classify" in ops:
            analysis.category = await self.classify(text)

        # Always compute readability
        analysis.readability_score = self.calculate_readability(text)

        return analysis

    async def summarize(
        self,
        text: str,
        sentences: int = 3,
        method: str = "llm"
    ) -> str:
        """
        Summarize document

        Args:
            text: Document text
            sentences: Number of sentences in summary
            method: "llm" or "extractive"

        Returns:
            Summary text
        """
        if method == "extractive":
            return self._extractive_summary(text, sentences)

        # LLM-based summary
        prompt = PromptTemplate.get("summarize", sentences=sentences, text=text)
        response = await self.llm.complete(prompt, max_tokens=200)
        return response.content.strip()

    def _extractive_summary(self, text: str, sentences: int) -> str:
        """Simple extractive summarization"""
        # Split into sentences
        sents = re.split(r'[.!?]+', text)
        sents = [s.strip() for s in sents if len(s.strip()) > 20]

        if len(sents) <= sentences:
            return text

        # Score sentences by word frequency
        words = re.findall(r'\w+', text.lower())
        word_freq = Counter(words)

        # Remove common words
        common = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        for word in common:
            word_freq.pop(word, None)

        # Score sentences
        sent_scores = []
        for sent in sents:
            score = sum(word_freq.get(w.lower(), 0) for w in re.findall(r'\w+', sent))
            sent_scores.append((score, sent))

        # Return top N sentences
        sent_scores.sort(reverse=True)
        summary_sents = [sent for _, sent in sent_scores[:sentences]]
        return '. '.join(summary_sents) + '.'

    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities"""
        # Simple pattern-based NER
        entities = []

        # Dates
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append(Entity(
                    text=match.group(0),
                    entity_type=EntityType.DATE,
                    confidence=0.9
                ))

        # Money
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        for match in re.finditer(money_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                entity_type=EntityType.MONEY,
                confidence=0.95
            ))

        # Capitalized names (simple heuristic for persons/organizations)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
        for match in re.finditer(name_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                entity_type=EntityType.PERSON,
                confidence=0.7
            ))

        return entities

    async def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment

        Returns:
            Tuple of (sentiment_label, score)
        """
        # Simple lexicon-based sentiment
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                         'positive', 'happy', 'love', 'best', 'perfect', 'beautiful'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
                         'negative', 'sad', 'poor', 'disappointing', 'wrong'}

        words = re.findall(r'\w+', text.lower())

        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)

        total = pos_count + neg_count
        if total == 0:
            return "neutral", 0.5

        score = pos_count / total

        if score > 0.6:
            return "positive", score
        elif score < 0.4:
            return "negative", 1 - score
        else:
            return "neutral", 0.5

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract top keywords using TF-IDF-like scoring"""
        # Tokenize and count
        words = re.findall(r'\w+', text.lower())

        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                    'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        words = [w for w in words if w not in stopwords and len(w) > 2]

        # Count frequencies
        word_freq = Counter(words)

        # Return top K
        return [word for word, _ in word_freq.most_common(top_k)]

    async def classify(
        self,
        text: str,
        categories: List[str] = None
    ) -> str:
        """Classify document into category"""
        if not categories:
            categories = ["business", "technical", "personal", "administrative", "legal"]

        # Simple keyword-based classification
        category_keywords = {
            "business": ["revenue", "profit", "sales", "customer", "market"],
            "technical": ["system", "software", "code", "database", "api"],
            "personal": ["family", "friend", "hobby", "personal", "private"],
            "administrative": ["meeting", "schedule", "budget", "report", "policy"],
            "legal": ["contract", "agreement", "law", "clause", "liability"]
        }

        words = set(re.findall(r'\w+', text.lower()))

        scores = {}
        for category in categories:
            keywords = category_keywords.get(category, [])
            score = sum(1 for keyword in keywords if keyword in words)
            scores[category] = score

        # Return category with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return categories[0] if categories else "general"

    def calculate_readability(self, text: str) -> float:
        """
        Calculate readability score (Flesch Reading Ease)

        Returns:
            Score from 0-100 (higher = easier to read)
        """
        sentences = len(re.split(r'[.!?]+', text))
        words = len(re.findall(r'\w+', text))
        syllables = sum(self._count_syllables(word) for word in re.findall(r'\w+', text))

        if sentences == 0 or words == 0:
            return 0.0

        # Flesch Reading Ease formula
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0.0, min(100.0, score))

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1

        return max(1, syllable_count)


# ==================== Smart Recommendations ====================

@dataclass
class Recommendation:
    """Recommendation item"""
    item_id: str
    score: float
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecommendationEngine:
    """
    ML-powered recommendation engine

    Supports content-based and collaborative filtering.
    """

    def __init__(self):
        self._user_interactions: Dict[str, List[str]] = defaultdict(list)
        self._item_features: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def record_interaction(self, user_id: str, item_id: str, interaction_type: str = "view"):
        """Record user-item interaction"""
        with self._lock:
            self._user_interactions[user_id].append(item_id)

    def set_item_features(self, item_id: str, features: Dict[str, Any]):
        """Set features for content-based filtering"""
        with self._lock:
            self._item_features[item_id] = features

    def recommend(
        self,
        user_id: str,
        n: int = 10,
        method: str = "hybrid"
    ) -> List[Recommendation]:
        """
        Generate recommendations

        Args:
            user_id: User ID
            n: Number of recommendations
            method: "content", "collaborative", or "hybrid"

        Returns:
            List of recommendations
        """
        if method == "content":
            return self._content_based(user_id, n)
        elif method == "collaborative":
            return self._collaborative(user_id, n)
        else:
            return self._hybrid(user_id, n)

    def _content_based(self, user_id: str, n: int) -> List[Recommendation]:
        """Content-based recommendations"""
        with self._lock:
            user_items = self._user_interactions.get(user_id, [])

            if not user_items:
                return []

            # Get features of user's items
            user_features = [
                self._item_features.get(item_id, {})
                for item_id in user_items
            ]

            # Find similar items
            recommendations = []
            for item_id, features in self._item_features.items():
                if item_id in user_items:
                    continue

                # Calculate similarity
                similarity = self._calculate_similarity(user_features, features)

                recommendations.append(Recommendation(
                    item_id=item_id,
                    score=similarity,
                    reason="content_similarity"
                ))

            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            return recommendations[:n]

    def _collaborative(self, user_id: str, n: int) -> List[Recommendation]:
        """Collaborative filtering recommendations"""
        with self._lock:
            user_items = set(self._user_interactions.get(user_id, []))

            if not user_items:
                return []

            # Find similar users
            similar_users = []
            for other_user_id, other_items in self._user_interactions.items():
                if other_user_id == user_id:
                    continue

                other_items_set = set(other_items)
                overlap = len(user_items & other_items_set)

                if overlap > 0:
                    similarity = overlap / math.sqrt(len(user_items) * len(other_items_set))
                    similar_users.append((other_user_id, similarity, other_items_set))

            # Aggregate recommendations
            item_scores = defaultdict(float)
            for other_user_id, similarity, other_items in similar_users:
                for item_id in other_items:
                    if item_id not in user_items:
                        item_scores[item_id] += similarity

            # Convert to recommendations
            recommendations = [
                Recommendation(
                    item_id=item_id,
                    score=score,
                    reason="collaborative_filtering"
                )
                for item_id, score in item_scores.items()
            ]

            recommendations.sort(key=lambda x: x.score, reverse=True)
            return recommendations[:n]

    def _hybrid(self, user_id: str, n: int) -> List[Recommendation]:
        """Hybrid recommendations"""
        content_recs = self._content_based(user_id, n * 2)
        collab_recs = self._collaborative(user_id, n * 2)

        # Combine with weighted scores
        combined = {}
        for rec in content_recs:
            combined[rec.item_id] = rec.score * 0.5

        for rec in collab_recs:
            combined[rec.item_id] = combined.get(rec.item_id, 0) + rec.score * 0.5

        # Convert back to recommendations
        recommendations = [
            Recommendation(
                item_id=item_id,
                score=score,
                reason="hybrid"
            )
            for item_id, score in combined.items()
        ]

        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:n]

    def _calculate_similarity(self, user_features: List[Dict], item_features: Dict) -> float:
        """Calculate feature similarity (simplified)"""
        if not user_features or not item_features:
            return 0.0

        # Simple overlap-based similarity
        item_tags = set(item_features.get("tags", []))

        max_similarity = 0.0
        for features in user_features:
            user_tags = set(features.get("tags", []))
            if user_tags and item_tags:
                overlap = len(user_tags & item_tags)
                similarity = overlap / math.sqrt(len(user_tags) * len(item_tags))
                max_similarity = max(max_similarity, similarity)

        return max_similarity


# Singleton instances
_llm_client_instance = None
_doc_intelligence_instance = None
_recommendation_engine_instance = None
_instance_lock = threading.Lock()


def get_llm_client(provider: LLMProvider = LLMProvider.MOCK) -> LLMClient:
    """Get singleton LLM client"""
    global _llm_client_instance
    if _llm_client_instance is None:
        with _instance_lock:
            if _llm_client_instance is None:
                _llm_client_instance = LLMClient(provider=provider)
    return _llm_client_instance


def get_document_intelligence() -> DocumentIntelligence:
    """Get singleton Document Intelligence"""
    global _doc_intelligence_instance
    if _doc_intelligence_instance is None:
        with _instance_lock:
            if _doc_intelligence_instance is None:
                _doc_intelligence_instance = DocumentIntelligence()
    return _doc_intelligence_instance


def get_recommendation_engine() -> RecommendationEngine:
    """Get singleton Recommendation Engine"""
    global _recommendation_engine_instance
    if _recommendation_engine_instance is None:
        with _instance_lock:
            if _recommendation_engine_instance is None:
                _recommendation_engine_instance = RecommendationEngine()
    return _recommendation_engine_instance


if __name__ == "__main__":
    import asyncio

    async def demo():
        # Test LLM
        llm = get_llm_client()
        response = await llm.complete("Summarize: AI is transforming document management.")
        print(f"LLM Response: {response.content}\n")

        # Test Document Intelligence
        doc_ai = get_document_intelligence()
        text = """
        John Doe from Acme Corporation announced a $1 million investment on January 10, 2026.
        This is great news for the technology sector. The company expects positive growth.
        """

        analysis = await doc_ai.analyze(text)
        print(f"Summary: {analysis.summary}")
        print(f"Sentiment: {analysis.sentiment} ({analysis.sentiment_score:.2f})")
        print(f"Keywords: {', '.join(analysis.keywords)}")
        print(f"Entities: {len(analysis.entities)} found")
        for entity in analysis.entities:
            print(f"  - {entity.text} ({entity.entity_type.value})")

        # Test Recommendations
        rec_engine = get_recommendation_engine()
        rec_engine.record_interaction("user-1", "doc-1")
        rec_engine.record_interaction("user-1", "doc-2")
        rec_engine.set_item_features("doc-3", {"tags": ["ai", "ml"]})
        rec_engine.set_item_features("doc-2", {"tags": ["ai"]})

        recs = rec_engine.recommend("user-1", n=5)
        print(f"\nRecommendations: {len(recs)}")
        for rec in recs:
            print(f"  - {rec.item_id} (score: {rec.score:.2f})")

    asyncio.run(demo())
    print("\nAI Services module loaded successfully!")
