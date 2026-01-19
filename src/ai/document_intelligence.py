"""
Document Intelligence Module

AI-powered document analysis and understanding including summarization,
entity extraction, classification, Q&A, and metadata extraction.

Part of v3.5 AI/ML Services implementation.
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .llm_integration import PROMPT_TEMPLATES, LLMProvider, get_llm_client

logger = logging.getLogger(__name__)


class SummaryType(Enum):
    """Types of summarization."""

    EXTRACTIVE = "extractive"  # Extract key sentences
    ABSTRACTIVE = "abstractive"  # Generate new summary with LLM
    BULLET_POINTS = "bullet_points"  # Bullet point format
    TLDR = "tldr"  # Very short summary


class ClassificationType(Enum):
    """Document classification types."""

    TOPIC = "topic"  # Subject matter
    SENTIMENT = "sentiment"  # Positive/negative/neutral
    INTENT = "intent"  # Purpose/goal
    URGENCY = "urgency"  # Priority level
    LANGUAGE = "language"  # Detected language


@dataclass
class Entity:
    """Named entity."""

    text: str
    type: str  # PERSON, ORG, LOC, DATE, etc.
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class KeyPoint:
    """Key point from document."""

    text: str
    importance: float
    sentence_index: int
    keywords: List[str] = field(default_factory=list)


@dataclass
class DocumentSummary:
    """Document summary."""

    summary: str
    summary_type: SummaryType
    key_points: List[KeyPoint]
    word_count_original: int
    word_count_summary: int
    compression_ratio: float


@dataclass
class DocumentClassification:
    """Classification result."""

    category: str
    confidence: float
    classification_type: ClassificationType
    all_categories: Dict[str, float] = field(default_factory=dict)


@dataclass
class DocumentMetadata:
    """Extracted document metadata."""

    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[datetime] = None
    language: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0


@dataclass
class DocumentAnalysis:
    """Complete document analysis."""

    summary: Optional[DocumentSummary] = None
    classification: Optional[DocumentClassification] = None
    metadata: Optional[DocumentMetadata] = None
    entities: List[Entity] = field(default_factory=list)
    sentiment: Optional[Dict[str, float]] = None
    readability_score: Optional[float] = None
    topics: List[str] = field(default_factory=list)


class TextPreprocessor:
    """Text preprocessing utilities."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep punctuation
        text = re.sub(r"[^\w\s.,!?;:\-\']", "", text)
        return text.strip()

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def split_paragraphs(text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Extract words from text."""
        words = re.findall(r"\b\w+\b", text.lower())
        return words


class ExtractiveSummarizer:
    """Extractive summarization using sentence scoring."""

    def __init__(self, num_sentences: int = 3):
        self.num_sentences = num_sentences

    def summarize(self, text: str) -> DocumentSummary:
        """Create extractive summary."""
        sentences = TextPreprocessor.split_sentences(text)

        if len(sentences) <= self.num_sentences:
            summary_text = text
            key_sentences = sentences
        else:
            # Score sentences
            scored_sentences = self._score_sentences(text, sentences)

            # Select top sentences
            top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[: self.num_sentences]

            # Sort by original order
            top_sentences = sorted(top_sentences, key=lambda x: x[2])

            key_sentences = [s[0] for s in top_sentences]
            summary_text = ". ".join(key_sentences) + "."

        # Create key points
        key_points = [
            KeyPoint(text=sent, importance=1.0 / (i + 1), sentence_index=i, keywords=self._extract_keywords(sent))
            for i, sent in enumerate(key_sentences)
        ]

        words_original = len(TextPreprocessor.extract_words(text))
        words_summary = len(TextPreprocessor.extract_words(summary_text))

        return DocumentSummary(
            summary=summary_text,
            summary_type=SummaryType.EXTRACTIVE,
            key_points=key_points,
            word_count_original=words_original,
            word_count_summary=words_summary,
            compression_ratio=words_summary / max(words_original, 1),
        )

    def _score_sentences(self, text: str, sentences: List[str]) -> List[Tuple[str, float, int]]:
        """Score sentences by importance."""
        # Calculate word frequencies
        all_words = TextPreprocessor.extract_words(text)
        word_freq = Counter(all_words)

        # Remove common words (simple stopwords)
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        for word in stopwords:
            word_freq.pop(word, None)

        # Score each sentence
        scored = []
        for idx, sent in enumerate(sentences):
            words = TextPreprocessor.extract_words(sent)
            score = sum(word_freq.get(w, 0) for w in words)
            scored.append((sent, score, idx))

        return scored

    def _extract_keywords(self, sentence: str, top_k: int = 3) -> List[str]:
        """Extract keywords from sentence."""
        words = TextPreprocessor.extract_words(sentence)
        word_freq = Counter(words)

        # Remove stopwords
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        for word in stopwords:
            word_freq.pop(word, None)

        return [word for word, _ in word_freq.most_common(top_k)]


class AbstractiveSummarizer:
    """Abstractive summarization using LLM."""

    def __init__(self, llm_provider: str = "openai", model: str = "gpt-3.5-turbo"):
        self.llm_provider = llm_provider
        self.model = model

    async def summarize(self, text: str, num_points: int = 3) -> DocumentSummary:
        """Create abstractive summary using LLM."""
        # Use LLM to generate summary
        client = get_llm_client(provider=self.llm_provider, model=self.model)

        prompt = PROMPT_TEMPLATES["summarize"].render(text=text, num_points=num_points)

        try:
            response = await client.complete(prompt, max_tokens=300)
            summary_text = response.content

            # Parse bullet points
            bullet_points = self._parse_bullet_points(summary_text)

            key_points = [
                KeyPoint(text=point, importance=1.0 / (i + 1), sentence_index=i, keywords=self._extract_keywords(point))
                for i, point in enumerate(bullet_points)
            ]

            words_original = len(TextPreprocessor.extract_words(text))
            words_summary = len(TextPreprocessor.extract_words(summary_text))

            return DocumentSummary(
                summary=summary_text,
                summary_type=SummaryType.ABSTRACTIVE,
                key_points=key_points,
                word_count_original=words_original,
                word_count_summary=words_summary,
                compression_ratio=words_summary / max(words_original, 1),
            )

        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            # Fallback to extractive
            extractive = ExtractiveSummarizer(num_sentences=num_points)
            return extractive.summarize(text)

    def _parse_bullet_points(self, text: str) -> List[str]:
        """Parse bullet points from text."""
        lines = text.split("\n")
        points = []

        for line in lines:
            line = line.strip()
            # Remove bullet markers
            line = re.sub(r"^[-*•]\s*", "", line)
            line = re.sub(r"^\d+\.\s*", "", line)

            if line:
                points.append(line)

        return points

    def _extract_keywords(self, text: str, top_k: int = 3) -> List[str]:
        """Extract keywords."""
        words = TextPreprocessor.extract_words(text)
        word_freq = Counter(words)

        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        for word in stopwords:
            word_freq.pop(word, None)

        return [word for word, _ in word_freq.most_common(top_k)]


class EntityExtractor:
    """Named entity extraction."""

    # Entity patterns (simplified - in production would use spaCy)
    ENTITY_PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "URL": r"https?://[^\s]+",
        "PHONE": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "DATE": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    }

    async def extract(self, text: str, use_llm: bool = True) -> List[Entity]:
        """Extract named entities from text."""
        entities = []

        # Pattern-based extraction
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append(
                    Entity(text=match.group(), type=entity_type, start=match.start(), end=match.end(), confidence=1.0)
                )

        # LLM-based extraction for more complex entities
        if use_llm:
            try:
                llm_entities = await self._extract_with_llm(text)
                entities.extend(llm_entities)
            except Exception as e:
                logger.warning(f"LLM entity extraction failed: {e}")

        return entities

    async def _extract_with_llm(self, text: str) -> List[Entity]:
        """Extract entities using LLM."""
        client = get_llm_client()

        prompt = PROMPT_TEMPLATES["extract_entities"].render(text=text)

        try:
            response = await client.complete(prompt, max_tokens=200)

            # Parse entities from response (simplified)
            entities = []
            lines = response.content.split("\n")

            for line in lines:
                # Look for patterns like "John Doe (PERSON)" or "- Google (ORG)"
                match = re.search(r"([^(]+)\s*\((\w+)\)", line)
                if match:
                    entity_text = match.group(1).strip("-• ").strip()
                    entity_type = match.group(2).upper()

                    # Find position in original text
                    pos = text.find(entity_text)
                    if pos >= 0:
                        entities.append(
                            Entity(
                                text=entity_text,
                                type=entity_type,
                                start=pos,
                                end=pos + len(entity_text),
                                confidence=0.8,
                            )
                        )

            return entities

        except Exception as e:
            logger.error(f"LLM entity extraction error: {e}")
            return []


class DocumentClassifier:
    """Document classification."""

    DEFAULT_CATEGORIES = {
        "topic": ["business", "technology", "science", "health", "politics", "sports", "entertainment"],
        "sentiment": ["positive", "negative", "neutral"],
        "urgency": ["high", "medium", "low"],
    }

    async def classify(
        self,
        text: str,
        classification_type: ClassificationType = ClassificationType.TOPIC,
        categories: Optional[List[str]] = None,
    ) -> DocumentClassification:
        """Classify document."""
        if categories is None:
            categories = self.DEFAULT_CATEGORIES.get(classification_type.value, [])

        # Use LLM for classification
        client = get_llm_client()

        prompt = PROMPT_TEMPLATES["classify"].render(
            text=text[:1000], categories=", ".join(categories)  # Truncate for efficiency
        )

        try:
            response = await client.complete(prompt, max_tokens=50)

            # Parse category from response
            category = self._parse_category(response.content, categories)

            return DocumentClassification(
                category=category,
                confidence=0.85,
                classification_type=classification_type,
                all_categories={category: 0.85},
            )

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            # Fallback to first category
            return DocumentClassification(
                category=categories[0] if categories else "unknown",
                confidence=0.5,
                classification_type=classification_type,
            )

    def _parse_category(self, response: str, categories: List[str]) -> str:
        """Parse category from LLM response."""
        response_lower = response.lower()

        for category in categories:
            if category.lower() in response_lower:
                return category

        # Default to first category
        return categories[0] if categories else "unknown"


class QuestionAnswering:
    """Question answering over documents."""

    async def answer(self, context: str, question: str) -> str:
        """Answer question based on context."""
        client = get_llm_client()

        prompt = PROMPT_TEMPLATES["qa"].render(context=context, question=question)

        try:
            response = await client.complete(prompt, max_tokens=200)
            return response.content

        except Exception as e:
            logger.error(f"Q&A failed: {e}")
            return "I couldn't find an answer to that question."


class DocumentComparison:
    """Compare documents for similarity and differences."""

    def compare(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """Compare two documents."""
        # Extract words
        words1 = set(TextPreprocessor.extract_words(doc1))
        words2 = set(TextPreprocessor.extract_words(doc2))

        # Calculate similarity
        intersection = words1 & words2
        union = words1 | words2

        jaccard_similarity = len(intersection) / len(union) if union else 0.0

        # Find unique words
        unique_to_doc1 = words1 - words2
        unique_to_doc2 = words2 - words1

        return {
            "similarity": jaccard_similarity,
            "common_words": len(intersection),
            "unique_to_doc1": len(unique_to_doc1),
            "unique_to_doc2": len(unique_to_doc2),
            "top_unique_doc1": list(unique_to_doc1)[:10],
            "top_unique_doc2": list(unique_to_doc2)[:10],
        }


class DocumentIntelligence:
    """Main document intelligence service."""

    def __init__(self, llm_provider: str = "openai", model: str = "gpt-3.5-turbo"):
        self.llm_provider = llm_provider
        self.model = model
        self.entity_extractor = EntityExtractor()
        self.classifier = DocumentClassifier()
        self.qa = QuestionAnswering()
        self.comparison = DocumentComparison()

    async def analyze(self, text: str, operations: Optional[List[str]] = None) -> DocumentAnalysis:
        """Perform comprehensive document analysis."""
        if operations is None:
            operations = ["summarize", "extract_entities", "classify", "metadata"]

        analysis = DocumentAnalysis()

        # Summarization
        if "summarize" in operations:
            summarizer = AbstractiveSummarizer(self.llm_provider, self.model)
            analysis.summary = await summarizer.summarize(text)

        # Entity extraction
        if "extract_entities" in operations:
            analysis.entities = await self.entity_extractor.extract(text)

        # Classification
        if "classify" in operations:
            analysis.classification = await self.classifier.classify(text)

        # Metadata extraction
        if "metadata" in operations:
            analysis.metadata = self._extract_metadata(text, analysis.entities)

        # Sentiment
        if "sentiment" in operations:
            analysis.sentiment = await self._analyze_sentiment(text)

        # Topics
        if "topics" in operations:
            analysis.topics = self._extract_topics(text)

        return analysis

    def _extract_metadata(self, text: str, entities: List[Entity]) -> DocumentMetadata:
        """Extract document metadata."""
        # Count words, sentences, paragraphs
        words = TextPreprocessor.extract_words(text)
        sentences = TextPreprocessor.split_sentences(text)
        paragraphs = TextPreprocessor.split_paragraphs(text)

        # Extract keywords (most common words)
        word_freq = Counter(words)
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}
        for word in stopwords:
            word_freq.pop(word, None)

        keywords = [word for word, _ in word_freq.most_common(10)]

        return DocumentMetadata(
            word_count=len(words),
            sentence_count=len(sentences),
            paragraph_count=len(paragraphs),
            keywords=keywords,
            entities=entities,
        )

    async def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze document sentiment."""
        client = get_llm_client()

        prompt = PROMPT_TEMPLATES["sentiment"].render(text=text[:500])

        try:
            response = await client.complete(prompt, max_tokens=50)

            # Parse sentiment from response
            response_lower = response.content.lower()

            if "positive" in response_lower:
                return {"positive": 0.7, "negative": 0.1, "neutral": 0.2}
            elif "negative" in response_lower:
                return {"positive": 0.1, "negative": 0.7, "neutral": 0.2}
            else:
                return {"positive": 0.2, "negative": 0.2, "neutral": 0.6}

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34}

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from document."""
        # Simple topic extraction based on keywords
        words = TextPreprocessor.extract_words(text)
        word_freq = Counter(words)

        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}
        for word in stopwords:
            word_freq.pop(word, None)

        topics = [word for word, _ in word_freq.most_common(5)]
        return topics


# Singleton instance
_doc_intelligence: Optional[DocumentIntelligence] = None


def get_document_intelligence(llm_provider: str = "openai", model: str = "gpt-3.5-turbo") -> DocumentIntelligence:
    """Get or create document intelligence service."""
    global _doc_intelligence

    if _doc_intelligence is None:
        _doc_intelligence = DocumentIntelligence(llm_provider, model)

    return _doc_intelligence
