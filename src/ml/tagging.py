"""
Auto-Tagging System using Machine Learning

Provides automatic tag generation and assignment:
- Keyword extraction (TF-IDF, TextRank)
- Topic modeling (LDA)
- Tag suggestion
- Tag clustering
- Multi-label classification
"""

from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import math
from collections import Counter, defaultdict


class TagType(str, Enum):
    """Tag types"""
    KEYWORD = "keyword"
    TOPIC = "topic"
    CATEGORY = "category"
    ENTITY = "entity"
    CUSTOM = "custom"


@dataclass
class Tag:
    """Document tag"""
    id: str
    name: str
    type: TagType
    confidence: float = 1.0
    frequency: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TagSuggestion:
    """Tag suggestion"""
    tag: str
    score: float
    source: str  # tfidf, textrank, lda, etc.
    context: Optional[str] = None


class TFIDFExtractor:
    """TF-IDF keyword extraction"""

    def __init__(self):
        self.document_frequency: Dict[str, int] = {}
        self.total_documents: int = 0

    def add_document(self, words: List[str]):
        """Add document to corpus"""
        unique_words = set(words)
        for word in unique_words:
            self.document_frequency[word] = self.document_frequency.get(word, 0) + 1
        self.total_documents += 1

    def extract_keywords(
        self,
        text: str,
        top_k: int = 10
    ) -> List[TagSuggestion]:
        """Extract keywords using TF-IDF"""
        words = self._tokenize(text)

        # Calculate term frequency
        tf = Counter(words)
        total_words = len(words)

        # Calculate TF-IDF scores
        tfidf_scores = {}
        for word, count in tf.items():
            # TF
            tf_score = count / total_words

            # IDF
            df = self.document_frequency.get(word, 1)
            idf_score = math.log((self.total_documents + 1) / (df + 1))

            # TF-IDF
            tfidf_scores[word] = tf_score * idf_score

        # Sort by score
        sorted_keywords = sorted(
            tfidf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top-k
        suggestions = []
        for word, score in sorted_keywords[:top_k]:
            suggestions.append(TagSuggestion(
                tag=word,
                score=score,
                source="tfidf"
            ))

        return suggestions

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        # Lowercase and remove special chars
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9äöüßÄÖÜ\s]', ' ', text)

        # Split into words
        words = text.split()

        # Filter short words and stopwords
        stopwords = {
            'der', 'die', 'das', 'und', 'oder', 'aber', 'ist', 'sind',
            'the', 'and', 'or', 'but', 'is', 'are', 'a', 'an'
        }
        words = [w for w in words if len(w) > 2 and w not in stopwords]

        return words


class TextRankExtractor:
    """TextRank algorithm for keyword extraction"""

    def __init__(self, window_size: int = 3):
        self.window_size = window_size

    def extract_keywords(
        self,
        text: str,
        top_k: int = 10,
        iterations: int = 20
    ) -> List[TagSuggestion]:
        """Extract keywords using TextRank"""
        words = self._tokenize(text)

        if not words:
            return []

        # Build word graph
        graph = self._build_graph(words)

        # Run PageRank
        scores = self._pagerank(graph, iterations)

        # Sort by score
        sorted_keywords = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top-k
        suggestions = []
        for word, score in sorted_keywords[:top_k]:
            suggestions.append(TagSuggestion(
                tag=word,
                score=score,
                source="textrank"
            ))

        return suggestions

    def _build_graph(self, words: List[str]) -> Dict[str, Set[str]]:
        """Build co-occurrence graph"""
        graph = defaultdict(set)

        for i, word in enumerate(words):
            # Add edges to words in window
            start = max(0, i - self.window_size)
            end = min(len(words), i + self.window_size + 1)

            for j in range(start, end):
                if i != j:
                    graph[word].add(words[j])

        return graph

    def _pagerank(
        self,
        graph: Dict[str, Set[str]],
        iterations: int,
        damping: float = 0.85
    ) -> Dict[str, float]:
        """Run PageRank algorithm"""
        # Initialize scores
        scores = {word: 1.0 for word in graph}

        for _ in range(iterations):
            new_scores = {}

            for word in graph:
                score = (1 - damping)

                for neighbor in graph:
                    if word in graph[neighbor]:
                        out_degree = len(graph[neighbor])
                        score += damping * (scores[neighbor] / out_degree)

                new_scores[word] = score

            scores = new_scores

        return scores

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9äöüßÄÖÜ\s]', ' ', text)
        words = text.split()

        stopwords = {
            'der', 'die', 'das', 'und', 'oder', 'aber', 'ist', 'sind',
            'the', 'and', 'or', 'but', 'is', 'are', 'a', 'an'
        }
        words = [w for w in words if len(w) > 2 and w not in stopwords]

        return words


class TopicModeler:
    """Topic modeling using LDA (Latent Dirichlet Allocation)"""

    def __init__(self, num_topics: int = 5):
        self.num_topics = num_topics
        self.topics: Dict[int, List[str]] = {}
        self.trained = False

    def train(self, documents: List[str]):
        """Train LDA model"""
        # In production, use gensim or sklearn
        # from gensim import corpora, models
        # from gensim.models import LdaModel

        # Tokenize documents
        tokenized_docs = [self._tokenize(doc) for doc in documents]

        # Create dictionary and corpus
        # dictionary = corpora.Dictionary(tokenized_docs)
        # corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]

        # Train LDA
        # lda_model = LdaModel(corpus, num_topics=self.num_topics, id2word=dictionary)

        # Simulated topics
        self.topics = {
            0: ['rechnung', 'betrag', 'zahlung', 'invoice', 'payment'],
            1: ['vertrag', 'vereinbarung', 'contract', 'agreement'],
            2: ['bericht', 'analyse', 'report', 'analysis'],
            3: ['budget', 'finanzplan', 'kosten', 'financial', 'cost'],
            4: ['dienst', 'service', 'leistung', 'provision']
        }

        self.trained = True

    def get_document_topics(
        self,
        text: str,
        top_k: int = 3
    ) -> List[TagSuggestion]:
        """Get topics for document"""
        if not self.trained:
            return []

        words = set(self._tokenize(text))

        # Calculate topic scores
        topic_scores = {}
        for topic_id, topic_words in self.topics.items():
            # Count overlapping words
            overlap = len(words.intersection(set(topic_words)))
            if overlap > 0:
                topic_scores[topic_id] = overlap / len(topic_words)

        # Sort by score
        sorted_topics = sorted(
            topic_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top-k topics
        suggestions = []
        for topic_id, score in sorted_topics[:top_k]:
            # Use most representative word as tag
            tag = self.topics[topic_id][0]
            suggestions.append(TagSuggestion(
                tag=tag,
                score=score,
                source="lda",
                context=f"topic_{topic_id}"
            ))

        return suggestions

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9äöüßÄÖÜ\s]', ' ', text)
        words = text.split()
        words = [w for w in words if len(w) > 2]
        return words


class AutoTagger:
    """Automatic tagging system"""

    def __init__(self):
        self.tfidf_extractor = TFIDFExtractor()
        self.textrank_extractor = TextRankExtractor()
        self.topic_modeler = TopicModeler()
        self.tag_registry: Dict[str, Tag] = {}
        self.tag_statistics: Dict[str, int] = defaultdict(int)

    def initialize_corpus(self, documents: List[str]):
        """Initialize with document corpus"""
        # Build TF-IDF model
        for doc in documents:
            words = self.tfidf_extractor._tokenize(doc)
            self.tfidf_extractor.add_document(words)

        # Train topic model
        self.topic_modeler.train(documents)

    def suggest_tags(
        self,
        text: str,
        top_k: int = 10,
        combine_methods: bool = True
    ) -> List[TagSuggestion]:
        """Suggest tags for text"""
        all_suggestions = []

        # TF-IDF keywords
        tfidf_tags = self.tfidf_extractor.extract_keywords(text, top_k=top_k)
        all_suggestions.extend(tfidf_tags)

        # TextRank keywords
        textrank_tags = self.textrank_extractor.extract_keywords(text, top_k=top_k)
        all_suggestions.extend(textrank_tags)

        # Topic modeling
        topic_tags = self.topic_modeler.get_document_topics(text, top_k=5)
        all_suggestions.extend(topic_tags)

        if combine_methods:
            # Combine and re-rank suggestions
            tag_scores = defaultdict(float)
            tag_sources = defaultdict(list)

            for suggestion in all_suggestions:
                tag_scores[suggestion.tag] += suggestion.score
                tag_sources[suggestion.tag].append(suggestion.source)

            # Create combined suggestions
            combined = []
            for tag, score in tag_scores.items():
                # Boost score if tag appears in multiple methods
                boost = len(tag_sources[tag]) * 0.2
                combined.append(TagSuggestion(
                    tag=tag,
                    score=score + boost,
                    source=','.join(tag_sources[tag])
                ))

            # Sort and return top-k
            combined.sort(key=lambda x: x.score, reverse=True)
            return combined[:top_k]

        else:
            # Return raw suggestions
            all_suggestions.sort(key=lambda x: x.score, reverse=True)
            return all_suggestions[:top_k]

    def auto_tag_document(
        self,
        document_id: str,
        text: str,
        threshold: float = 0.3,
        max_tags: int = 5
    ) -> List[Tag]:
        """Automatically tag document"""
        suggestions = self.suggest_tags(text, top_k=max_tags * 2)

        # Filter by threshold
        filtered = [s for s in suggestions if s.score >= threshold][:max_tags]

        # Create tags
        tags = []
        for suggestion in filtered:
            tag_id = self._get_or_create_tag_id(suggestion.tag)

            tag = Tag(
                id=tag_id,
                name=suggestion.tag,
                type=TagType.KEYWORD,
                confidence=suggestion.score,
                frequency=self.tag_statistics[suggestion.tag]
            )

            tags.append(tag)

            # Update statistics
            self.tag_statistics[suggestion.tag] += 1

        return tags

    def _get_or_create_tag_id(self, tag_name: str) -> str:
        """Get or create tag ID"""
        # Normalize tag name
        normalized = tag_name.lower().strip()

        # Check if tag exists
        for tag_id, tag in self.tag_registry.items():
            if tag.name.lower() == normalized:
                return tag_id

        # Create new tag
        tag_id = f"tag_{len(self.tag_registry) + 1}"
        self.tag_registry[tag_id] = Tag(
            id=tag_id,
            name=tag_name,
            type=TagType.KEYWORD
        )

        return tag_id

    def get_popular_tags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get most popular tags"""
        sorted_tags = sorted(
            self.tag_statistics.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_tags[:limit]

    def get_related_tags(self, tag: str, limit: int = 5) -> List[str]:
        """Get tags related to given tag"""
        # In production, use word embeddings or co-occurrence analysis
        # For now, return empty list
        return []

    def cluster_tags(self) -> Dict[str, List[str]]:
        """Cluster similar tags"""
        # In production, use clustering algorithms (K-means, DBSCAN)
        # on tag embeddings

        # Simulated clusters
        return {
            'financial': ['rechnung', 'zahlung', 'budget', 'kosten'],
            'legal': ['vertrag', 'vereinbarung', 'contract'],
            'administrative': ['bericht', 'dienst', 'service']
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get tagging statistics"""
        return {
            'total_tags': len(self.tag_registry),
            'total_applications': sum(self.tag_statistics.values()),
            'avg_tags_per_document': sum(self.tag_statistics.values()) / max(len(self.tag_statistics), 1),
            'popular_tags': self.get_popular_tags(limit=10),
            'tfidf_corpus_size': self.tfidf_extractor.total_documents,
            'topics': len(self.topic_modeler.topics)
        }


# Global instance
_auto_tagger: Optional[AutoTagger] = None


def get_auto_tagger() -> AutoTagger:
    """Get global auto-tagger instance"""
    global _auto_tagger

    if _auto_tagger is None:
        _auto_tagger = AutoTagger()

    return _auto_tagger


def configure_auto_tagger():
    """Configure auto-tagger"""
    global _auto_tagger
    _auto_tagger = AutoTagger()
