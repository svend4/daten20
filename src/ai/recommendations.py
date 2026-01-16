"""
Smart Recommendations Module

ML-powered recommendation engine with content-based, collaborative filtering,
and hybrid approaches for document recommendations.

Part of v3.5 AI/ML Services implementation.
"""

import logging
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class RecommendationMethod(Enum):
    """Recommendation methods."""

    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    TRENDING = "trending"
    SIMILAR = "similar"
    PERSONALIZED = "personalized"


@dataclass
class UserInteraction:
    """User interaction with document."""

    user_id: str
    document_id: str
    interaction_type: str  # view, download, share, favorite
    timestamp: datetime
    duration_seconds: Optional[int] = None
    rating: Optional[float] = None


@dataclass
class Document:
    """Document representation for recommendations."""

    doc_id: str
    title: str
    content: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    view_count: int = 0
    download_count: int = 0
    avg_rating: float = 0.0


@dataclass
class Recommendation:
    """Recommendation result."""

    document_id: str
    score: float
    reason: str
    method: RecommendationMethod
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """User profile for personalization."""

    user_id: str
    preferred_tags: List[str] = field(default_factory=list)
    interaction_history: List[UserInteraction] = field(default_factory=list)
    favorite_documents: Set[str] = field(default_factory=set)
    blocked_documents: Set[str] = field(default_factory=set)
    preferences: Dict[str, Any] = field(default_factory=dict)


class TFIDFCalculator:
    """TF-IDF calculation for content-based filtering."""

    def __init__(self):
        self.document_frequency: Dict[str, int] = defaultdict(int)
        self.num_documents: int = 0

    def fit(self, documents: List[Document]):
        """Fit TF-IDF on document corpus."""
        self.num_documents = len(documents)

        # Calculate document frequency
        for doc in documents:
            words = self._extract_words(doc)
            unique_words = set(words)

            for word in unique_words:
                self.document_frequency[word] += 1

    def calculate_tfidf(self, document: Document) -> Dict[str, float]:
        """Calculate TF-IDF vector for document."""
        words = self._extract_words(document)
        word_count = len(words)

        if word_count == 0:
            return {}

        # Calculate term frequency
        term_freq = defaultdict(int)
        for word in words:
            term_freq[word] += 1

        # Calculate TF-IDF
        tfidf = {}
        for word, count in term_freq.items():
            tf = count / word_count
            idf = math.log(self.num_documents / (self.document_frequency[word] + 1))
            tfidf[word] = tf * idf

        return tfidf

    def _extract_words(self, document: Document) -> List[str]:
        """Extract words from document."""
        text = f"{document.title} {' '.join(document.tags)}"
        if document.content:
            text += f" {document.content}"

        # Simple tokenization
        words = text.lower().split()

        # Remove stopwords
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}
        words = [w for w in words if w not in stopwords and len(w) > 2]

        return words


class CosineSimilarity:
    """Cosine similarity calculation."""

    @staticmethod
    def calculate(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        # Get common keys
        common_keys = set(vec1.keys()) & set(vec2.keys())

        if not common_keys:
            return 0.0

        # Calculate dot product
        dot_product = sum(vec1[key] * vec2[key] for key in common_keys)

        # Calculate magnitudes
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


class ContentBasedRecommender:
    """Content-based recommendation using TF-IDF and cosine similarity."""

    def __init__(self):
        self.tfidf = TFIDFCalculator()
        self.document_vectors: Dict[str, Dict[str, float]] = {}

    def fit(self, documents: List[Document]):
        """Train on document corpus."""
        self.tfidf.fit(documents)

        # Calculate TF-IDF vectors for all documents
        for doc in documents:
            self.document_vectors[doc.doc_id] = self.tfidf.calculate_tfidf(doc)

    def recommend(
        self, target_doc_id: str, n: int = 10, exclude_ids: Optional[Set[str]] = None
    ) -> List[Recommendation]:
        """Recommend similar documents."""
        if target_doc_id not in self.document_vectors:
            return []

        target_vector = self.document_vectors[target_doc_id]
        exclude_ids = exclude_ids or set()
        exclude_ids.add(target_doc_id)

        # Calculate similarities
        similarities = []
        for doc_id, doc_vector in self.document_vectors.items():
            if doc_id in exclude_ids:
                continue

            similarity = CosineSimilarity.calculate(target_vector, doc_vector)
            if similarity > 0:
                similarities.append((doc_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Create recommendations
        recommendations = [
            Recommendation(
                document_id=doc_id,
                score=score,
                reason="Similar content",
                method=RecommendationMethod.CONTENT_BASED,
                metadata={"similarity": score},
            )
            for doc_id, score in similarities[:n]
        ]

        return recommendations


class CollaborativeFilteringRecommender:
    """Collaborative filtering using user-item matrix."""

    def __init__(self):
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.item_user_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)

    def fit(self, interactions: List[UserInteraction]):
        """Train on user interactions."""
        # Build user-item matrix
        interaction_weights = {"view": 1.0, "download": 2.0, "share": 3.0, "favorite": 5.0}

        for interaction in interactions:
            weight = interaction_weights.get(interaction.interaction_type, 1.0)

            # Add rating if available
            if interaction.rating:
                weight *= interaction.rating

            self.user_item_matrix[interaction.user_id][interaction.document_id] = weight
            self.item_user_matrix[interaction.document_id][interaction.user_id] = weight

    def recommend(self, user_id: str, n: int = 10, exclude_ids: Optional[Set[str]] = None) -> List[Recommendation]:
        """Recommend documents using collaborative filtering."""
        if user_id not in self.user_item_matrix:
            return []

        user_interactions = self.user_item_matrix[user_id]
        exclude_ids = exclude_ids or set()
        exclude_ids.update(user_interactions.keys())

        # Find similar users
        similar_users = self._find_similar_users(user_id)

        # Aggregate recommendations from similar users
        doc_scores: Dict[str, float] = defaultdict(float)

        for similar_user_id, similarity in similar_users[:20]:
            for doc_id, score in self.user_item_matrix[similar_user_id].items():
                if doc_id not in exclude_ids:
                    doc_scores[doc_id] += score * similarity

        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # Create recommendations
        recommendations = [
            Recommendation(
                document_id=doc_id,
                score=score,
                reason="Users like you also liked this",
                method=RecommendationMethod.COLLABORATIVE,
                metadata={"collaborative_score": score},
            )
            for doc_id, score in sorted_docs[:n]
        ]

        return recommendations

    def _find_similar_users(self, user_id: str, top_k: int = 50) -> List[Tuple[str, float]]:
        """Find users with similar preferences."""
        target_interactions = self.user_item_matrix[user_id]

        similarities = []
        for other_user_id, other_interactions in self.user_item_matrix.items():
            if other_user_id == user_id:
                continue

            similarity = CosineSimilarity.calculate(target_interactions, other_interactions)
            if similarity > 0:
                similarities.append((other_user_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class HybridRecommender:
    """Hybrid recommender combining multiple methods."""

    def __init__(
        self,
        content_based: ContentBasedRecommender,
        collaborative: CollaborativeFilteringRecommender,
        content_weight: float = 0.5,
        collaborative_weight: float = 0.5,
    ):
        self.content_based = content_based
        self.collaborative = collaborative
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight

    def recommend(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        n: int = 10,
        exclude_ids: Optional[Set[str]] = None,
    ) -> List[Recommendation]:
        """Hybrid recommendations."""
        exclude_ids = exclude_ids or set()

        # Get content-based recommendations
        content_recs = []
        if user_profile and user_profile.interaction_history:
            # Use recent interactions as seed
            recent_docs = [i.document_id for i in user_profile.interaction_history[-5:]]
            for doc_id in recent_docs:
                recs = self.content_based.recommend(doc_id, n=n, exclude_ids=exclude_ids)
                content_recs.extend(recs)

        # Get collaborative recommendations
        collab_recs = self.collaborative.recommend(user_id, n=n, exclude_ids=exclude_ids)

        # Combine recommendations
        combined_scores: Dict[str, float] = defaultdict(float)

        for rec in content_recs:
            combined_scores[rec.document_id] += rec.score * self.content_weight

        for rec in collab_recs:
            combined_scores[rec.document_id] += rec.score * self.collaborative_weight

        # Sort by combined score
        sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # Create recommendations
        recommendations = [
            Recommendation(
                document_id=doc_id,
                score=score,
                reason="Personalized recommendation",
                method=RecommendationMethod.HYBRID,
                metadata={"hybrid_score": score},
            )
            for doc_id, score in sorted_docs[:n]
        ]

        return recommendations


class TrendingRecommender:
    """Trending documents recommender."""

    def __init__(self, time_window_days: int = 7):
        self.time_window_days = time_window_days

    def recommend(
        self,
        interactions: List[UserInteraction],
        documents: List[Document],
        n: int = 10,
        exclude_ids: Optional[Set[str]] = None,
    ) -> List[Recommendation]:
        """Recommend trending documents."""
        exclude_ids = exclude_ids or set()

        # Filter recent interactions
        cutoff_date = datetime.now() - timedelta(days=self.time_window_days)
        recent_interactions = [i for i in interactions if i.timestamp >= cutoff_date]

        # Count interactions per document
        doc_popularity: Dict[str, int] = defaultdict(int)
        for interaction in recent_interactions:
            doc_popularity[interaction.document_id] += 1

        # Calculate trending score (popularity + recency)
        trending_scores = []
        for doc in documents:
            if doc.doc_id in exclude_ids:
                continue

            popularity = doc_popularity[doc.doc_id]
            if popularity == 0:
                continue

            # Recency factor
            days_old = (datetime.now() - doc.created_at).days
            recency_factor = 1.0 / (1.0 + days_old / 7)  # Decay over weeks

            trending_score = popularity * recency_factor
            trending_scores.append((doc.doc_id, trending_score))

        # Sort by trending score
        trending_scores.sort(key=lambda x: x[1], reverse=True)

        # Create recommendations
        recommendations = [
            Recommendation(
                document_id=doc_id,
                score=score,
                reason="Trending now",
                method=RecommendationMethod.TRENDING,
                metadata={"trending_score": score},
            )
            for doc_id, score in trending_scores[:n]
        ]

        return recommendations


class ColdStartHandler:
    """Handle cold start problem for new users/documents."""

    def recommend_for_new_user(self, documents: List[Document], n: int = 10) -> List[Recommendation]:
        """Recommend for users with no history."""
        # Recommend most popular documents
        sorted_docs = sorted(documents, key=lambda d: (d.view_count + d.download_count, d.avg_rating), reverse=True)

        recommendations = [
            Recommendation(
                document_id=doc.doc_id,
                score=float(doc.view_count + doc.download_count) / 100,
                reason="Popular with other users",
                method=RecommendationMethod.PERSONALIZED,
                metadata={"views": doc.view_count, "downloads": doc.download_count},
            )
            for doc in sorted_docs[:n]
        ]

        return recommendations

    def recommend_for_new_document(
        self, new_document: Document, content_recommender: ContentBasedRecommender, n: int = 10
    ) -> List[Recommendation]:
        """Find similar documents for new document."""
        # Use content-based similarity
        return content_recommender.recommend(new_document.doc_id, n=n)


class ABTestManager:
    """A/B testing for recommendations."""

    def __init__(self, test_groups: Dict[str, float]):
        """
        Args:
            test_groups: Map of group name to probability (must sum to 1.0)
        """
        self.test_groups = test_groups
        self.user_assignments: Dict[str, str] = {}

    def assign_user(self, user_id: str) -> str:
        """Assign user to test group."""
        if user_id in self.user_assignments:
            return self.user_assignments[user_id]

        # Random assignment based on probabilities
        rand = random.random()
        cumulative = 0.0

        for group, prob in self.test_groups.items():
            cumulative += prob
            if rand <= cumulative:
                self.user_assignments[user_id] = group
                return group

        # Fallback to first group
        first_group = list(self.test_groups.keys())[0]
        self.user_assignments[user_id] = first_group
        return first_group

    def get_user_group(self, user_id: str) -> Optional[str]:
        """Get user's assigned group."""
        return self.user_assignments.get(user_id)


class RecommendationEngine:
    """Main recommendation engine."""

    def __init__(self):
        self.content_based = ContentBasedRecommender()
        self.collaborative = CollaborativeFilteringRecommender()
        self.hybrid = HybridRecommender(self.content_based, self.collaborative)
        self.trending = TrendingRecommender()
        self.cold_start = ColdStartHandler()

        self.documents: Dict[str, Document] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.interactions: List[UserInteraction] = []

        self.ab_test = ABTestManager({"control": 0.5, "experimental": 0.5})

    def fit(self, documents: List[Document], interactions: List[UserInteraction]):
        """Train recommendation models."""
        # Store data
        self.documents = {doc.doc_id: doc for doc in documents}
        self.interactions = interactions

        # Train models
        logger.info("Training content-based recommender...")
        self.content_based.fit(documents)

        logger.info("Training collaborative filtering...")
        self.collaborative.fit(interactions)

        logger.info("Recommendation engine ready")

    def recommend(
        self,
        user_id: str,
        n: int = 10,
        method: RecommendationMethod = RecommendationMethod.HYBRID,
        exclude_ids: Optional[Set[str]] = None,
    ) -> List[Recommendation]:
        """Get recommendations for user."""
        user_profile = self.user_profiles.get(user_id)
        exclude_ids = exclude_ids or set()

        # Add user's favorites to exclude
        if user_profile:
            exclude_ids.update(user_profile.favorite_documents)
            exclude_ids.update(user_profile.blocked_documents)

        # Handle cold start
        if user_profile is None or not user_profile.interaction_history:
            logger.info(f"Cold start for user {user_id}")
            return self.cold_start.recommend_for_new_user(list(self.documents.values()), n=n)

        # Get recommendations based on method
        if method == RecommendationMethod.HYBRID:
            recommendations = self.hybrid.recommend(user_id, user_profile=user_profile, n=n, exclude_ids=exclude_ids)
        elif method == RecommendationMethod.COLLABORATIVE:
            recommendations = self.collaborative.recommend(user_id, n=n, exclude_ids=exclude_ids)
        elif method == RecommendationMethod.TRENDING:
            recommendations = self.trending.recommend(
                self.interactions, list(self.documents.values()), n=n, exclude_ids=exclude_ids
            )
        else:
            # Default to hybrid
            recommendations = self.hybrid.recommend(user_id, user_profile=user_profile, n=n, exclude_ids=exclude_ids)

        return recommendations

    def add_interaction(self, interaction: UserInteraction):
        """Add user interaction."""
        self.interactions.append(interaction)

        # Update user profile
        if interaction.user_id not in self.user_profiles:
            self.user_profiles[interaction.user_id] = UserProfile(user_id=interaction.user_id)

        profile = self.user_profiles[interaction.user_id]
        profile.interaction_history.append(interaction)

        # Update favorites
        if interaction.interaction_type == "favorite":
            profile.favorite_documents.add(interaction.document_id)

    def get_similar_documents(self, document_id: str, n: int = 10) -> List[Recommendation]:
        """Find similar documents."""
        return self.content_based.recommend(document_id, n=n)


# Singleton instance
_recommendation_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get or create recommendation engine."""
    global _recommendation_engine

    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()

    return _recommendation_engine
