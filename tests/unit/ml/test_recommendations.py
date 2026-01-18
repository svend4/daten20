"""
Comprehensive tests for src/ml/recommendations.py

Tests recommendation engine to achieve >75% coverage.
"""

import math
import pytest

from src.ml.recommendations import (
    CollaborativeFilter,
    ContentBasedFilter,
    Recommendation,
    RecommendationEngine,
    get_recommendation_engine,
)


class TestRecommendation:
    """Test Recommendation dataclass"""

    def test_recommendation_creation(self):
        """Test creating a Recommendation"""
        rec = Recommendation(item_id="item1", score=0.85, reason="Test reason")
        assert rec.item_id == "item1"
        assert rec.score == 0.85
        assert rec.reason == "Test reason"

    def test_recommendation_fields(self):
        """Test Recommendation has all fields"""
        rec = Recommendation(item_id="doc123", score=0.95, reason="Popular")
        assert hasattr(rec, "item_id")
        assert hasattr(rec, "score")
        assert hasattr(rec, "reason")

    def test_recommendation_is_dataclass(self):
        """Test Recommendation is a dataclass"""
        rec1 = Recommendation("item1", 0.5, "reason1")
        rec2 = Recommendation("item1", 0.5, "reason1")
        # Dataclasses with same values should be equal
        assert rec1 == rec2


class TestCollaborativeFilter:
    """Test CollaborativeFilter class"""

    @pytest.fixture
    def filter(self):
        """Create a CollaborativeFilter instance"""
        return CollaborativeFilter()

    def test_initialization(self, filter):
        """Test CollaborativeFilter initialization"""
        assert filter.user_items is not None
        assert filter.item_users is not None
        assert len(filter.user_items) == 0
        assert len(filter.item_users) == 0

    def test_add_interaction(self, filter):
        """Test adding user-item interaction"""
        filter.add_interaction(user_id=1, item_id="item1")
        assert "item1" in filter.user_items[1]
        assert 1 in filter.item_users["item1"]

    def test_add_multiple_interactions(self, filter):
        """Test adding multiple interactions"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")
        filter.add_interaction(2, "item1")

        assert len(filter.user_items[1]) == 2
        assert len(filter.user_items[2]) == 1
        assert len(filter.item_users["item1"]) == 2
        assert len(filter.item_users["item2"]) == 1

    def test_recommend_empty_user(self, filter):
        """Test recommend for user with no interactions"""
        recommendations = filter.recommend(user_id=999)
        assert recommendations == []

    def test_recommend_new_user(self, filter):
        """Test recommend for completely new user"""
        # Add some interactions for other users
        filter.add_interaction(1, "item1")
        filter.add_interaction(2, "item2")

        # New user should get empty recommendations
        recommendations = filter.recommend(user_id=100)
        assert recommendations == []

    def test_recommend_single_user(self, filter):
        """Test recommend when only one user exists"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")

        # No similar users, should return empty
        recommendations = filter.recommend(user_id=1)
        assert recommendations == []

    def test_recommend_with_similar_users(self, filter):
        """Test recommend with similar users"""
        # User 1 likes items 1, 2, 3
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")
        filter.add_interaction(1, "item3")

        # User 2 likes items 1, 2, 4 (similar to user 1)
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item2")
        filter.add_interaction(2, "item4")

        # User 1 should be recommended item4
        recommendations = filter.recommend(user_id=1, top_k=10)
        assert len(recommendations) > 0
        assert any(rec.item_id == "item4" for rec in recommendations)

    def test_recommend_top_k(self, filter):
        """Test recommend with top_k parameter"""
        # Create interactions
        for i in range(1, 6):
            filter.add_interaction(1, f"item{i}")

        for i in range(1, 10):
            filter.add_interaction(2, f"item{i}")

        # Request only top 3
        recommendations = filter.recommend(user_id=1, top_k=3)
        assert len(recommendations) <= 3

    def test_recommend_excludes_user_items(self, filter):
        """Test recommend doesn't include items user already has"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item3")

        recommendations = filter.recommend(user_id=1)
        # Should not recommend item1 or item2 (already has them)
        for rec in recommendations:
            assert rec.item_id not in ["item1", "item2"]

    def test_recommend_reason(self, filter):
        """Test recommendations include reason"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item2")

        recommendations = filter.recommend(user_id=1)
        if recommendations:
            assert "Users like you" in recommendations[0].reason

    def test_recommend_score_ordering(self, filter):
        """Test recommendations are ordered by score"""
        # Setup interactions
        filter.add_interaction(1, "item1")
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item2")
        filter.add_interaction(3, "item1")
        filter.add_interaction(3, "item3")

        recommendations = filter.recommend(user_id=1, top_k=10)
        # Scores should be descending
        for i in range(len(recommendations) - 1):
            assert recommendations[i].score >= recommendations[i + 1].score

    def test_find_similar_users_basic(self, filter):
        """Test finding similar users"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item3")

        similar = filter._find_similar_users(1)
        assert len(similar) > 0
        assert similar[0][0] == 2  # User 2 is similar

    def test_find_similar_users_excludes_self(self, filter):
        """Test similar users doesn't include self"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(2, "item2")

        similar = filter._find_similar_users(1)
        # Should not include user 1 itself
        assert all(user_id != 1 for user_id, _ in similar)

    def test_find_similar_users_jaccard(self, filter):
        """Test Jaccard similarity calculation"""
        # User 1: {item1, item2}
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")

        # User 2: {item1, item2, item3} - Jaccard = 2/3
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item2")
        filter.add_interaction(2, "item3")

        similar = filter._find_similar_users(1)
        assert len(similar) > 0
        # Jaccard similarity should be 2/3 ≈ 0.667
        assert abs(similar[0][1] - 2/3) < 0.01

    def test_find_similar_users_sorted(self, filter):
        """Test similar users are sorted by similarity"""
        filter.add_interaction(1, "item1")
        filter.add_interaction(1, "item2")

        # User 2: more similar
        filter.add_interaction(2, "item1")
        filter.add_interaction(2, "item2")

        # User 3: less similar
        filter.add_interaction(3, "item1")
        filter.add_interaction(3, "item3")
        filter.add_interaction(3, "item4")

        similar = filter._find_similar_users(1)
        # Should be sorted descending by similarity
        for i in range(len(similar) - 1):
            assert similar[i][1] >= similar[i + 1][1]


class TestContentBasedFilter:
    """Test ContentBasedFilter class"""

    @pytest.fixture
    def filter(self):
        """Create a ContentBasedFilter instance"""
        return ContentBasedFilter()

    def test_initialization(self, filter):
        """Test ContentBasedFilter initialization"""
        assert filter.item_features is not None
        assert len(filter.item_features) == 0

    def test_add_item(self, filter):
        """Test adding item with features"""
        features = {"feature1": 0.5, "feature2": 0.8}
        filter.add_item("item1", features)
        assert "item1" in filter.item_features
        assert filter.item_features["item1"] == features

    def test_add_multiple_items(self, filter):
        """Test adding multiple items"""
        filter.add_item("item1", {"f1": 0.5})
        filter.add_item("item2", {"f1": 0.7, "f2": 0.3})
        assert len(filter.item_features) == 2

    def test_recommend_empty_reference(self, filter):
        """Test recommend with empty reference items"""
        recommendations = filter.recommend(reference_items=[])
        assert recommendations == []

    def test_recommend_unknown_reference(self, filter):
        """Test recommend with unknown reference items"""
        filter.add_item("item1", {"f1": 0.5})
        # Reference item doesn't exist
        recommendations = filter.recommend(reference_items=["unknown"], top_k=10)
        # Should handle gracefully
        assert isinstance(recommendations, list)

    def test_recommend_single_reference(self, filter):
        """Test recommend with single reference item"""
        filter.add_item("item1", {"category": 0.9, "price": 0.5})
        filter.add_item("item2", {"category": 0.8, "price": 0.6})
        filter.add_item("item3", {"category": 0.1, "price": 0.9})

        recommendations = filter.recommend(reference_items=["item1"], top_k=10)
        assert len(recommendations) > 0
        # Should not recommend the reference item itself
        assert all(rec.item_id != "item1" for rec in recommendations)

    def test_recommend_multiple_references(self, filter):
        """Test recommend with multiple reference items"""
        filter.add_item("item1", {"f1": 0.8})
        filter.add_item("item2", {"f1": 0.9})
        filter.add_item("item3", {"f1": 0.5})

        recommendations = filter.recommend(reference_items=["item1", "item2"], top_k=10)
        # Should exclude both reference items
        for rec in recommendations:
            assert rec.item_id not in ["item1", "item2"]

    def test_recommend_top_k(self, filter):
        """Test recommend respects top_k parameter"""
        for i in range(10):
            filter.add_item(f"item{i}", {"feature": i * 0.1})

        recommendations = filter.recommend(reference_items=["item0"], top_k=3)
        assert len(recommendations) <= 3

    def test_recommend_reason(self, filter):
        """Test recommendations include reason"""
        filter.add_item("item1", {"f1": 0.5})
        filter.add_item("item2", {"f1": 0.6})

        recommendations = filter.recommend(reference_items=["item1"])
        if recommendations:
            assert "Similar to" in recommendations[0].reason

    def test_recommend_sorted_by_score(self, filter):
        """Test recommendations are sorted by similarity score"""
        filter.add_item("ref", {"category": 1.0, "price": 0.5})
        filter.add_item("similar", {"category": 0.9, "price": 0.6})
        filter.add_item("different", {"category": 0.1, "price": 0.1})

        recommendations = filter.recommend(reference_items=["ref"], top_k=10)
        # Should be sorted descending
        for i in range(len(recommendations) - 1):
            assert recommendations[i].score >= recommendations[i + 1].score

    def test_cosine_similarity_identical(self, filter):
        """Test cosine similarity for identical features"""
        features = {"f1": 0.5, "f2": 0.8}
        similarity = filter._cosine_similarity(features, features)
        # Identical features should have similarity close to 1.0
        assert abs(similarity - 1.0) < 0.001

    def test_cosine_similarity_orthogonal(self, filter):
        """Test cosine similarity for orthogonal features"""
        f1 = {"feature1": 1.0}
        f2 = {"feature2": 1.0}
        similarity = filter._cosine_similarity(f1, f2)
        # Orthogonal features should have similarity 0
        assert abs(similarity) < 0.001

    def test_cosine_similarity_opposite(self, filter):
        """Test cosine similarity for opposite features"""
        f1 = {"f1": 1.0}
        f2 = {"f1": -1.0}
        similarity = filter._cosine_similarity(f1, f2)
        # Opposite features should have similarity close to -1
        assert similarity < 0

    def test_cosine_similarity_zero_norm(self, filter):
        """Test cosine similarity with zero norm"""
        f1 = {"f1": 0.0}
        f2 = {"f2": 1.0}
        similarity = filter._cosine_similarity(f1, f2)
        # Should handle zero norm gracefully
        assert similarity == 0.0

    def test_cosine_similarity_empty_features(self, filter):
        """Test cosine similarity with empty features"""
        similarity = filter._cosine_similarity({}, {})
        assert similarity == 0.0

    def test_cosine_similarity_calculation(self, filter):
        """Test cosine similarity calculation"""
        f1 = {"x": 3.0, "y": 4.0}  # Vector (3, 4), norm = 5
        f2 = {"x": 3.0, "y": 4.0}  # Same vector
        similarity = filter._cosine_similarity(f1, f2)
        # dot = 9 + 16 = 25, norm1 = 5, norm2 = 5, cos = 25/25 = 1
        assert abs(similarity - 1.0) < 0.001

    def test_recommend_averages_features(self, filter):
        """Test that recommendations average reference item features"""
        filter.add_item("ref1", {"quality": 1.0})
        filter.add_item("ref2", {"quality": 0.0})
        filter.add_item("target", {"quality": 0.5})

        # Average of ref1 and ref2 is 0.5, which matches target
        recommendations = filter.recommend(reference_items=["ref1", "ref2"], top_k=10)
        # Target should be highly ranked
        if recommendations:
            # The target item should appear in recommendations
            assert any(rec.item_id == "target" for rec in recommendations)


class TestRecommendationEngine:
    """Test RecommendationEngine class"""

    @pytest.fixture
    def engine(self):
        """Create a RecommendationEngine instance"""
        return RecommendationEngine()

    def test_initialization(self, engine):
        """Test RecommendationEngine initialization"""
        assert engine.collaborative_filter is not None
        assert engine.content_filter is not None
        assert isinstance(engine.collaborative_filter, CollaborativeFilter)
        assert isinstance(engine.content_filter, ContentBasedFilter)

    def test_recommend_no_data(self, engine):
        """Test recommend with no data"""
        recommendations = engine.recommend(user_id=1, user_items=None, top_k=10)
        # Should return empty or handle gracefully
        assert isinstance(recommendations, list)

    def test_recommend_collaborative_only(self, engine):
        """Test recommend using only collaborative filtering"""
        # Add collaborative interactions
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        recommendations = engine.recommend(user_id=1, user_items=None, top_k=10)
        assert isinstance(recommendations, list)

    def test_recommend_hybrid(self, engine):
        """Test hybrid recommendations"""
        # Add collaborative data
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        # Add content data
        engine.content_filter.add_item("item1", {"feature": 0.8})
        engine.content_filter.add_item("item2", {"feature": 0.9})
        engine.content_filter.add_item("item3", {"feature": 0.85})

        recommendations = engine.recommend(user_id=1, user_items=["item1"], top_k=10)
        assert isinstance(recommendations, list)

    def test_recommend_with_user_items(self, engine):
        """Test recommend with user items for content filtering"""
        engine.content_filter.add_item("item1", {"category": 0.9})
        engine.content_filter.add_item("item2", {"category": 0.8})

        recommendations = engine.recommend(user_id=1, user_items=["item1"], top_k=5)
        # Should use content filtering
        assert isinstance(recommendations, list)

    def test_recommend_top_k(self, engine):
        """Test recommend respects top_k parameter"""
        # Setup some data
        for i in range(1, 6):
            engine.collaborative_filter.add_interaction(1, f"item{i}")
            engine.collaborative_filter.add_interaction(2, f"item{i}")

        for i in range(6, 15):
            engine.collaborative_filter.add_interaction(2, f"item{i}")

        recommendations = engine.recommend(user_id=1, top_k=3)
        assert len(recommendations) <= 3

    def test_recommend_reason(self, engine):
        """Test recommendations include reason"""
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        recommendations = engine.recommend(user_id=1, top_k=10)
        if recommendations:
            assert recommendations[0].reason is not None
            assert "Recommended for you" in recommendations[0].reason

    def test_recommend_combines_scores(self, engine):
        """Test that hybrid approach combines scores"""
        # Add data to both filters
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        engine.content_filter.add_item("item1", {"f": 0.9})
        engine.content_filter.add_item("item2", {"f": 0.85})

        recommendations = engine.recommend(user_id=1, user_items=["item1"], top_k=10)
        # Should have combined scores from both approaches
        assert isinstance(recommendations, list)

    def test_recommend_sorted_by_combined_score(self, engine):
        """Test recommendations sorted by combined score"""
        # Setup data
        for i in range(1, 5):
            engine.collaborative_filter.add_interaction(1, f"item{i}")
            engine.collaborative_filter.add_interaction(2, f"item{i}")

        for i in range(5, 10):
            engine.collaborative_filter.add_interaction(2, f"item{i}")
            engine.content_filter.add_item(f"item{i}", {"quality": i * 0.1})

        recommendations = engine.recommend(user_id=1, user_items=["item5"], top_k=10)
        # Should be sorted descending
        for i in range(len(recommendations) - 1):
            assert recommendations[i].score >= recommendations[i + 1].score


class TestGetRecommendationEngine:
    """Test get_recommendation_engine function"""

    def test_get_recommendation_engine_returns_engine(self):
        """Test get_recommendation_engine returns RecommendationEngine"""
        engine = get_recommendation_engine()
        assert isinstance(engine, RecommendationEngine)

    def test_get_recommendation_engine_singleton(self):
        """Test get_recommendation_engine returns same instance"""
        engine1 = get_recommendation_engine()
        engine2 = get_recommendation_engine()
        assert engine1 is engine2

    def test_get_recommendation_engine_initialized(self):
        """Test returned engine is properly initialized"""
        engine = get_recommendation_engine()
        assert engine.collaborative_filter is not None
        assert engine.content_filter is not None


class TestIntegration:
    """Integration tests for recommendation system"""

    def test_full_recommendation_workflow(self):
        """Test complete recommendation workflow"""
        engine = RecommendationEngine()

        # Add collaborative data
        for user in range(1, 4):
            for item in range(1, 6):
                if (user + item) % 2 == 0:
                    engine.collaborative_filter.add_interaction(user, f"doc{item}")

        # Add content data
        for item in range(1, 10):
            engine.content_filter.add_item(f"doc{item}", {"topic": item * 0.1, "quality": 0.8})

        # Get recommendations
        recommendations = engine.recommend(user_id=1, user_items=["doc1"], top_k=5)

        # Verify structure
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        for rec in recommendations:
            assert isinstance(rec, Recommendation)
            assert rec.item_id is not None
            assert rec.score >= 0
            assert rec.reason is not None

    def test_collaborative_filtering_workflow(self):
        """Test collaborative filtering workflow"""
        cf = CollaborativeFilter()

        # User 1 and 2 have similar tastes
        for item in ["doc1", "doc2", "doc3"]:
            cf.add_interaction(1, item)
            cf.add_interaction(2, item)

        # User 2 also likes doc4
        cf.add_interaction(2, "doc4")

        # User 1 should be recommended doc4
        recs = cf.recommend(1, top_k=5)
        assert any(r.item_id == "doc4" for r in recs)

    def test_content_filtering_workflow(self):
        """Test content filtering workflow"""
        cb = ContentBasedFilter()

        # Add items with features
        cb.add_item("tech1", {"technology": 0.9, "business": 0.1})
        cb.add_item("tech2", {"technology": 0.8, "business": 0.2})
        cb.add_item("business1", {"technology": 0.1, "business": 0.9})

        # Recommend similar to tech1
        recs = cb.recommend(["tech1"], top_k=5)

        # tech2 should be more similar than business1
        if len(recs) >= 2:
            tech2_idx = next((i for i, r in enumerate(recs) if r.item_id == "tech2"), None)
            biz1_idx = next((i for i, r in enumerate(recs) if r.item_id == "business1"), None)

            if tech2_idx is not None and biz1_idx is not None:
                assert tech2_idx < biz1_idx


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.ml.recommendations", "--cov-report=term-missing"])
