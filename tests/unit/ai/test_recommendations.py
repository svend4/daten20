"""
Comprehensive tests for ai/recommendations.py module

Tests organized by size:
- Small: Enums, dataclasses, static utilities
- Medium: Individual recommenders, utilities
- Large: Full recommendation engine workflows

Test coverage: ~80% target
"""

from datetime import datetime, timedelta

import pytest

from src.ai.recommendations import (
    ABTestManager,
    ColdStartHandler,
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    Document,
    HybridRecommender,
    Recommendation,
    RecommendationEngine,
    RecommendationMethod,
    TFIDFCalculator,
    TrendingRecommender,
    UserInteraction,
    UserProfile,
    get_recommendation_engine,
)

# Import internal class for testing
from src.ai.recommendations import CosineSimilarity

# ============================================================================
# SMALL TESTS - Enums, Dataclasses, Static Utilities
# ============================================================================

pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestRecommendationMethod:
    """Test RecommendationMethod enum."""

    def test_all_methods_defined(self):
        """Test all recommendation methods are defined."""
        methods = [m for m in RecommendationMethod]
        assert len(methods) == 6

        assert RecommendationMethod.CONTENT_BASED in methods
        assert RecommendationMethod.COLLABORATIVE in methods
        assert RecommendationMethod.HYBRID in methods
        assert RecommendationMethod.TRENDING in methods

    def test_method_values(self):
        """Test method enum values."""
        assert RecommendationMethod.CONTENT_BASED.value == "content_based"
        assert RecommendationMethod.HYBRID.value == "hybrid"
        assert RecommendationMethod.PERSONALIZED.value == "personalized"


class TestUserInteractionDataclass:
    """Test UserInteraction dataclass."""

    def test_interaction_creation(self):
        """Test creating user interaction."""
        interaction = UserInteraction(
            user_id="user1",
            document_id="doc1",
            interaction_type="view",
            timestamp=datetime.now()
        )

        assert interaction.user_id == "user1"
        assert interaction.document_id == "doc1"
        assert interaction.interaction_type == "view"

    def test_interaction_with_rating(self):
        """Test interaction with rating."""
        interaction = UserInteraction(
            user_id="user1",
            document_id="doc1",
            interaction_type="favorite",
            timestamp=datetime.now(),
            duration_seconds=300,
            rating=4.5
        )

        assert interaction.duration_seconds == 300
        assert interaction.rating == 4.5


class TestDocumentDataclass:
    """Test Document dataclass."""

    def test_document_creation(self):
        """Test creating document."""
        doc = Document(
            doc_id="doc1",
            title="Machine Learning Basics",
            content="Introduction to ML...",
            tags=["ml", "tutorial"]
        )

        assert doc.doc_id == "doc1"
        assert doc.title == "Machine Learning Basics"
        assert "ml" in doc.tags

    def test_document_with_stats(self):
        """Test document with statistics."""
        doc = Document(
            doc_id="doc1",
            title="Popular Doc",
            view_count=1000,
            download_count=250,
            avg_rating=4.5
        )

        assert doc.view_count == 1000
        assert doc.download_count == 250
        assert doc.avg_rating == 4.5


class TestRecommendationDataclass:
    """Test Recommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating recommendation."""
        rec = Recommendation(
            document_id="doc1",
            score=0.85,
            reason="Similar content",
            method=RecommendationMethod.CONTENT_BASED
        )

        assert rec.document_id == "doc1"
        assert rec.score == 0.85
        assert rec.method == RecommendationMethod.CONTENT_BASED

    def test_recommendation_with_metadata(self):
        """Test recommendation with metadata."""
        rec = Recommendation(
            document_id="doc1",
            score=0.9,
            reason="Test",
            method=RecommendationMethod.HYBRID,
            metadata={"similarity": 0.95}
        )

        assert rec.metadata["similarity"] == 0.95


class TestUserProfileDataclass:
    """Test UserProfile dataclass."""

    def test_profile_creation(self):
        """Test creating user profile."""
        profile = UserProfile(user_id="user1")

        assert profile.user_id == "user1"
        assert profile.preferred_tags == []
        assert profile.interaction_history == []

    def test_profile_with_preferences(self):
        """Test profile with preferences."""
        profile = UserProfile(
            user_id="user1",
            preferred_tags=["ml", "ai"],
            favorite_documents={"doc1", "doc2"},
            preferences={"language": "en"}
        )

        assert "ml" in profile.preferred_tags
        assert "doc1" in profile.favorite_documents
        assert profile.preferences["language"] == "en"


class TestCosineSimilarity:
    """Test CosineSimilarity utility."""

    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vec = {"a": 1.0, "b": 2.0, "c": 3.0}
        similarity = CosineSimilarity.calculate(vec, vec)

        assert abs(similarity - 1.0) < 1e-10

    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = {"a": 1.0}
        vec2 = {"b": 1.0}

        similarity = CosineSimilarity.calculate(vec1, vec2)

        assert similarity == 0.0

    def test_similar_vectors(self):
        """Test cosine similarity of similar vectors."""
        vec1 = {"a": 1.0, "b": 2.0, "c": 3.0}
        vec2 = {"a": 1.1, "b": 1.9, "c": 3.1}

        similarity = CosineSimilarity.calculate(vec1, vec2)

        assert 0.95 < similarity < 1.0

    def test_empty_vectors(self):
        """Test cosine similarity of empty vectors."""
        vec1 = {}
        vec2 = {"a": 1.0}

        similarity = CosineSimilarity.calculate(vec1, vec2)

        assert similarity == 0.0


# ============================================================================
# MEDIUM TESTS - Individual Recommenders
# ============================================================================


@pytest.mark.medium
@pytest.mark.integration
class TestTFIDFCalculator:
    """Test TFIDFCalculator class."""

    def test_tfidf_initialization(self):
        """Test creating TF-IDF calculator."""
        tfidf = TFIDFCalculator()

        assert tfidf.num_documents == 0

    def test_tfidf_fit(self):
        """Test fitting TF-IDF on documents."""
        tfidf = TFIDFCalculator()

        docs = [
            Document("1", "Machine learning", tags=["ml"]),
            Document("2", "Deep learning", tags=["ml", "dl"]),
            Document("3", "Cooking recipes", tags=["food"]),
        ]

        tfidf.fit(docs)

        assert tfidf.num_documents == 3
        assert len(tfidf.document_frequency) > 0

    def test_tfidf_calculate(self):
        """Test calculating TF-IDF vector."""
        tfidf = TFIDFCalculator()

        docs = [
            Document("1", "Machine learning algorithms"),
            Document("2", "Deep learning networks"),
        ]

        tfidf.fit(docs)

        vector = tfidf.calculate_tfidf(docs[0])

        assert isinstance(vector, dict)
        assert len(vector) > 0
        assert all(isinstance(v, float) for v in vector.values())


@pytest.mark.medium
@pytest.mark.integration
class TestContentBasedRecommender:
    """Test ContentBasedRecommender class."""

    def test_content_recommender_initialization(self):
        """Test creating content-based recommender."""
        recommender = ContentBasedRecommender()

        assert recommender.tfidf is not None

    def test_content_recommender_fit(self):
        """Test fitting content-based recommender."""
        recommender = ContentBasedRecommender()

        docs = [
            Document("1", "Machine learning tutorial", tags=["ml"]),
            Document("2", "Deep learning guide", tags=["ml", "dl"]),
            Document("3", "Cooking recipes collection", tags=["food"]),
        ]

        recommender.fit(docs)

        assert len(recommender.document_vectors) == 3

    def test_content_recommend(self):
        """Test content-based recommendations."""
        recommender = ContentBasedRecommender()

        docs = [
            Document("1", "Machine learning basics"),
            Document("2", "Deep learning advanced"),
            Document("3", "Cooking pasta"),
            Document("4", "Neural networks intro"),
        ]

        recommender.fit(docs)

        # Recommend similar to doc 1 (ML)
        recommendations = recommender.recommend("1", n=2)

        assert len(recommendations) <= 2
        assert all(isinstance(r, Recommendation) for r in recommendations)
        assert all(r.method == RecommendationMethod.CONTENT_BASED for r in recommendations)


@pytest.mark.medium
@pytest.mark.integration
class TestCollaborativeFilteringRecommender:
    """Test CollaborativeFilteringRecommender class."""

    def test_collaborative_initialization(self):
        """Test creating collaborative filtering recommender."""
        recommender = CollaborativeFilteringRecommender()

        assert recommender.user_item_matrix is not None

    def test_collaborative_fit(self):
        """Test fitting collaborative filtering."""
        recommender = CollaborativeFilteringRecommender()

        interactions = [
            UserInteraction("user1", "doc1", "view", datetime.now()),
            UserInteraction("user1", "doc2", "download", datetime.now()),
            UserInteraction("user2", "doc1", "view", datetime.now()),
            UserInteraction("user2", "doc3", "favorite", datetime.now()),
        ]

        recommender.fit(interactions)

        assert len(recommender.user_item_matrix) == 2  # 2 users

    def test_collaborative_recommend(self):
        """Test collaborative filtering recommendations."""
        recommender = CollaborativeFilteringRecommender()

        interactions = [
            UserInteraction("user1", "doc1", "view", datetime.now()),
            UserInteraction("user1", "doc2", "favorite", datetime.now()),
            UserInteraction("user2", "doc1", "view", datetime.now()),
            UserInteraction("user2", "doc3", "download", datetime.now()),
        ]

        recommender.fit(interactions)

        # Recommend for user1
        recommendations = recommender.recommend("user1", n=2)

        assert isinstance(recommendations, list)
        assert all(r.method == RecommendationMethod.COLLABORATIVE for r in recommendations)


@pytest.mark.medium
@pytest.mark.integration
class TestHybridRecommender:
    """Test HybridRecommender class."""

    def test_hybrid_initialization(self):
        """Test creating hybrid recommender."""
        content = ContentBasedRecommender()
        collab = CollaborativeFilteringRecommender()

        hybrid = HybridRecommender(content, collab)

        assert hybrid.content_based is not None
        assert hybrid.collaborative is not None

    def test_hybrid_weights(self):
        """Test hybrid recommender weights."""
        content = ContentBasedRecommender()
        collab = CollaborativeFilteringRecommender()

        hybrid = HybridRecommender(
            content, collab,
            content_weight=0.6,
            collaborative_weight=0.4
        )

        assert hybrid.content_weight == 0.6
        assert hybrid.collaborative_weight == 0.4


@pytest.mark.medium
@pytest.mark.integration
class TestTrendingRecommender:
    """Test TrendingRecommender class."""

    def test_trending_initialization(self):
        """Test creating trending recommender."""
        recommender = TrendingRecommender(time_window_days=7)

        assert recommender.time_window_days == 7

    def test_trending_recommend(self):
        """Test trending recommendations."""
        recommender = TrendingRecommender(time_window_days=7)

        # Recent interactions
        now = datetime.now()
        interactions = [
            UserInteraction("user1", "doc1", "view", now),
            UserInteraction("user2", "doc1", "view", now),
            UserInteraction("user3", "doc1", "download", now),
            UserInteraction("user4", "doc2", "view", now),
        ]

        # Documents
        docs = [
            Document("doc1", "Popular doc", created_at=now - timedelta(days=1)),
            Document("doc2", "Less popular", created_at=now - timedelta(days=2)),
            Document("doc3", "Old doc", created_at=now - timedelta(days=30)),
        ]

        recommendations = recommender.recommend(interactions, docs, n=2)

        assert len(recommendations) <= 2
        assert all(r.method == RecommendationMethod.TRENDING for r in recommendations)
        # doc1 should be more trending
        if len(recommendations) > 0:
            assert recommendations[0].document_id == "doc1"


@pytest.mark.medium
@pytest.mark.integration
class TestColdStartHandler:
    """Test ColdStartHandler class."""

    def test_coldstart_initialization(self):
        """Test creating cold start handler."""
        handler = ColdStartHandler()

        assert handler is not None

    def test_recommend_for_new_user(self):
        """Test recommendations for new user."""
        handler = ColdStartHandler()

        docs = [
            Document("doc1", "Popular", view_count=1000, download_count=500, avg_rating=4.5),
            Document("doc2", "Less popular", view_count=100, download_count=50, avg_rating=3.5),
            Document("doc3", "Unpopular", view_count=10, download_count=5, avg_rating=3.0),
        ]

        recommendations = handler.recommend_for_new_user(docs, n=2)

        assert len(recommendations) <= 2
        # Most popular should be first
        assert recommendations[0].document_id == "doc1"


@pytest.mark.medium
@pytest.mark.integration
class TestABTestManager:
    """Test ABTestManager class."""

    def test_ab_test_initialization(self):
        """Test creating A/B test manager."""
        manager = ABTestManager({"control": 0.5, "experimental": 0.5})

        assert manager.test_groups is not None

    def test_assign_user_to_group(self):
        """Test assigning user to test group."""
        manager = ABTestManager({"A": 0.5, "B": 0.5})

        group = manager.assign_user("user1")

        assert group in ["A", "B"]

    def test_consistent_assignment(self):
        """Test user gets same group consistently."""
        manager = ABTestManager({"A": 0.5, "B": 0.5})

        group1 = manager.assign_user("user1")
        group2 = manager.assign_user("user1")

        assert group1 == group2

    def test_get_user_group(self):
        """Test getting user's assigned group."""
        manager = ABTestManager({"control": 0.5, "test": 0.5})

        manager.assign_user("user1")
        group = manager.get_user_group("user1")

        assert group is not None


# ============================================================================
# LARGE TESTS - Full Recommendation Engine Workflows
# ============================================================================


@pytest.mark.large
@pytest.mark.e2e
class TestRecommendationEngine:
    """Test RecommendationEngine end-to-end workflows."""

    def test_recommendation_engine_initialization(self):
        """Test creating recommendation engine."""
        engine = RecommendationEngine()

        assert engine.content_based is not None
        assert engine.collaborative is not None
        assert engine.hybrid is not None
        assert engine.trending is not None
        assert engine.cold_start is not None

    def test_engine_fit(self):
        """Test fitting recommendation engine."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "ML tutorial", tags=["ml"]),
            Document("2", "DL guide", tags=["ml", "dl"]),
            Document("3", "Cooking recipes", tags=["food"]),
        ]

        interactions = [
            UserInteraction("user1", "1", "view", datetime.now()),
            UserInteraction("user1", "2", "favorite", datetime.now()),
            UserInteraction("user2", "1", "view", datetime.now()),
        ]

        engine.fit(docs, interactions)

        assert len(engine.documents) == 3

    def test_recommend_for_new_user(self):
        """Test recommendations for new user (cold start)."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "Popular", view_count=1000),
            Document("2", "Less popular", view_count=100),
        ]

        interactions = [
            UserInteraction("user1", "1", "view", datetime.now()),
        ]

        engine.fit(docs, interactions)

        # New user
        recommendations = engine.recommend("new_user", n=2)

        assert len(recommendations) <= 2
        assert isinstance(recommendations[0], Recommendation)

    def test_recommend_for_existing_user(self):
        """Test recommendations for user with history."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "ML basics", tags=["ml"]),
            Document("2", "DL advanced", tags=["ml", "dl"]),
            Document("3", "Cooking", tags=["food"]),
            Document("4", "Neural networks", tags=["ml"]),
        ]

        interactions = [
            UserInteraction("user1", "1", "view", datetime.now()),
            UserInteraction("user1", "2", "favorite", datetime.now()),
        ]

        engine.fit(docs, interactions)

        # User with history
        recommendations = engine.recommend("user1", n=2, method=RecommendationMethod.HYBRID)

        assert len(recommendations) <= 2

    def test_add_interaction(self):
        """Test adding user interaction."""
        engine = RecommendationEngine()

        interaction = UserInteraction("user1", "doc1", "view", datetime.now())

        engine.add_interaction(interaction)

        assert "user1" in engine.user_profiles
        assert len(engine.user_profiles["user1"].interaction_history) == 1

    def test_get_similar_documents(self):
        """Test finding similar documents."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "Machine learning tutorial"),
            Document("2", "Deep learning guide"),
            Document("3", "Cooking recipes"),
        ]

        interactions = []

        engine.fit(docs, interactions)

        similar = engine.get_similar_documents("1", n=2)

        assert len(similar) <= 2

    def test_multiple_recommendation_methods(self):
        """Test using different recommendation methods."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "ML", tags=["ml"], created_at=datetime.now()),
            Document("2", "DL", tags=["ml"], created_at=datetime.now()),
        ]

        interactions = [
            UserInteraction("user1", "1", "view", datetime.now()),
        ]

        engine.fit(docs, interactions)

        # Try different methods
        hybrid_recs = engine.recommend("user1", n=2, method=RecommendationMethod.HYBRID)
        trending_recs = engine.recommend("user1", n=2, method=RecommendationMethod.TRENDING)

        assert isinstance(hybrid_recs, list)
        assert isinstance(trending_recs, list)

    def test_get_recommendation_engine_singleton(self):
        """Test get_recommendation_engine() function."""
        engine1 = get_recommendation_engine()
        engine2 = get_recommendation_engine()

        # Should return same instance
        assert engine1 is engine2

    def test_favorites_excluded_from_recommendations(self):
        """Test favorites are excluded from recommendations."""
        engine = RecommendationEngine()

        docs = [
            Document("1", "Doc 1"),
            Document("2", "Doc 2"),
            Document("3", "Doc 3"),
        ]

        # User with favorite
        interaction = UserInteraction("user1", "1", "favorite", datetime.now())
        engine.add_interaction(interaction)

        interactions = [interaction]
        engine.fit(docs, interactions)

        recommendations = engine.recommend("user1", n=5)

        # Doc 1 should not be in recommendations (it's a favorite)
        rec_ids = {r.document_id for r in recommendations}
        assert "1" not in rec_ids
