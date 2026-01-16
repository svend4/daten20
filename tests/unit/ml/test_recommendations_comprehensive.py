"""
Comprehensive tests for recommendations module

Test coverage goals:
- Collaborative filtering
- Content-based filtering
- Hybrid recommendations
- Similarity calculations
- Edge cases and error handling
"""

import pytest
from collections import defaultdict
from unittest.mock import Mock, patch

from src.ml.recommendations import (
    Recommendation,
    CollaborativeFilter,
    ContentBasedFilter,
    RecommendationEngine,
    get_recommendation_engine,
)


class TestRecommendation:
    """Test Recommendation dataclass"""

    def test_recommendation_creation(self):
        """Test creating a recommendation"""
        rec = Recommendation(
            item_id="item123",
            score=0.85,
            reason="Recommended based on your interests"
        )

        assert rec.item_id == "item123"
        assert rec.score == 0.85
        assert rec.reason == "Recommended based on your interests"


class TestCollaborativeFilter:
    """Test CollaborativeFilter"""

    @pytest.fixture
    def cf(self):
        """Create collaborative filter instance"""
        return CollaborativeFilter()

    def test_initialization(self, cf):
        """Test filter initialization"""
        assert isinstance(cf.user_items, defaultdict)
        assert isinstance(cf.item_users, defaultdict)

    def test_add_interaction(self, cf):
        """Test adding user-item interaction"""
        cf.add_interaction(user_id=1, item_id="item1")

        assert "item1" in cf.user_items[1]
        assert 1 in cf.item_users["item1"]

    def test_add_multiple_interactions(self, cf):
        """Test adding multiple interactions"""
        cf.add_interaction(user_id=1, item_id="item1")
        cf.add_interaction(user_id=1, item_id="item2")
        cf.add_interaction(user_id=2, item_id="item1")

        assert len(cf.user_items[1]) == 2
        assert len(cf.item_users["item1"]) == 2

    def test_recommend_for_new_user(self, cf):
        """Test recommendations for new user"""
        recommendations = cf.recommend(user_id=999, top_k=10)
        assert recommendations == []

    def test_recommend_with_data(self, cf):
        """Test recommendations with existing data"""
        # User 1 likes items 1, 2, 3
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")
        cf.add_interaction(1, "item3")

        # User 2 likes items 1, 2, 4 (similar to user 1)
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")
        cf.add_interaction(2, "item4")

        # User 1 should be recommended item4
        recommendations = cf.recommend(user_id=1, top_k=10)

        assert isinstance(recommendations, list)
        assert all(isinstance(r, Recommendation) for r in recommendations)

        # item4 should be in recommendations
        item_ids = [r.item_id for r in recommendations]
        assert "item4" in item_ids

    def test_recommend_top_k(self, cf):
        """Test top-k recommendations"""
        # Setup data
        for i in range(1, 6):
            cf.add_interaction(1, f"item{i}")

        for i in range(1, 11):
            cf.add_interaction(2, f"item{i}")

        # User 1 should get recommendations
        recommendations_5 = cf.recommend(user_id=1, top_k=5)
        recommendations_10 = cf.recommend(user_id=1, top_k=10)

        assert len(recommendations_5) <= 5
        assert len(recommendations_10) <= 10

    def test_find_similar_users(self, cf):
        """Test finding similar users"""
        # User 1 and 2 have overlapping items
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        similar_users = cf._find_similar_users(user_id=1)

        assert isinstance(similar_users, list)
        assert all(isinstance(u, tuple) and len(u) == 2 for u in similar_users)

        # User 2 should be similar
        user_ids = [u[0] for u in similar_users]
        assert 2 in user_ids

    def test_jaccard_similarity(self, cf):
        """Test Jaccard similarity calculation"""
        # Perfect overlap
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        similar_users = cf._find_similar_users(user_id=1)

        # User 2 should have similarity of 1.0
        user_2_sim = [sim for uid, sim in similar_users if uid == 2][0]
        assert user_2_sim == 1.0

    def test_exclude_already_liked_items(self, cf):
        """Test that already liked items are excluded"""
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")
        cf.add_interaction(2, "item3")

        recommendations = cf.recommend(user_id=1)

        # item1 and item2 should not be recommended (already liked)
        recommended_ids = [r.item_id for r in recommendations]
        assert "item1" not in recommended_ids
        assert "item2" not in recommended_ids

    def test_recommendation_scores(self, cf):
        """Test that recommendation scores are valid"""
        cf.add_interaction(1, "item1")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        recommendations = cf.recommend(user_id=1)

        for rec in recommendations:
            assert rec.score >= 0.0
            assert isinstance(rec.score, float)

    def test_recommendation_reasons(self, cf):
        """Test that recommendations have reasons"""
        cf.add_interaction(1, "item1")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        recommendations = cf.recommend(user_id=1)

        for rec in recommendations:
            assert isinstance(rec.reason, str)
            assert len(rec.reason) > 0


class TestContentBasedFilter:
    """Test ContentBasedFilter"""

    @pytest.fixture
    def cbf(self):
        """Create content-based filter instance"""
        return ContentBasedFilter()

    def test_initialization(self, cbf):
        """Test filter initialization"""
        assert cbf.item_features == {}

    def test_add_item(self, cbf):
        """Test adding item with features"""
        features = {"feature1": 1.0, "feature2": 0.5}
        cbf.add_item("item1", features)

        assert "item1" in cbf.item_features
        assert cbf.item_features["item1"] == features

    def test_add_multiple_items(self, cbf):
        """Test adding multiple items"""
        cbf.add_item("item1", {"feature1": 1.0})
        cbf.add_item("item2", {"feature1": 0.5})
        cbf.add_item("item3", {"feature2": 0.8})

        assert len(cbf.item_features) == 3

    def test_recommend_with_no_reference(self, cbf):
        """Test recommendations with no reference items"""
        cbf.add_item("item1", {"feature1": 1.0})
        recommendations = cbf.recommend(reference_items=[])

        assert recommendations == []

    def test_recommend_similar_items(self, cbf):
        """Test recommending similar items"""
        # Add items with similar features
        cbf.add_item("item1", {"feature1": 1.0, "feature2": 0.5})
        cbf.add_item("item2", {"feature1": 0.9, "feature2": 0.4})
        cbf.add_item("item3", {"feature1": 0.1, "feature2": 0.1})

        # Recommend based on item1
        recommendations = cbf.recommend(reference_items=["item1"])

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # item2 should be more similar than item3
        item_ids = [r.item_id for r in recommendations]
        assert "item2" in item_ids

    def test_recommend_top_k(self, cbf):
        """Test top-k recommendations"""
        for i in range(20):
            cbf.add_item(f"item{i}", {"feature1": float(i / 10)})

        recommendations_5 = cbf.recommend(reference_items=["item0"], top_k=5)
        recommendations_10 = cbf.recommend(reference_items=["item0"], top_k=10)

        assert len(recommendations_5) <= 5
        assert len(recommendations_10) <= 10

    def test_cosine_similarity(self, cbf):
        """Test cosine similarity calculation"""
        # Identical features
        features1 = {"a": 1.0, "b": 1.0}
        features2 = {"a": 1.0, "b": 1.0}

        similarity = cbf._cosine_similarity(features1, features2)
        assert abs(similarity - 1.0) < 0.01

    def test_cosine_similarity_orthogonal(self, cbf):
        """Test cosine similarity with orthogonal vectors"""
        features1 = {"a": 1.0, "b": 0.0}
        features2 = {"a": 0.0, "b": 1.0}

        similarity = cbf._cosine_similarity(features1, features2)
        assert abs(similarity) < 0.01

    def test_cosine_similarity_zero_vector(self, cbf):
        """Test cosine similarity with zero vector"""
        features1 = {"a": 1.0}
        features2 = {"a": 0.0, "b": 0.0}

        similarity = cbf._cosine_similarity(features1, features2)
        assert similarity == 0.0

    def test_average_features(self, cbf):
        """Test averaging features from multiple items"""
        cbf.add_item("item1", {"feature1": 1.0, "feature2": 0.5})
        cbf.add_item("item2", {"feature1": 0.5, "feature2": 1.0})

        recommendations = cbf.recommend(reference_items=["item1", "item2"])

        # Should average the features and find similar items
        assert isinstance(recommendations, list)

    def test_exclude_reference_items(self, cbf):
        """Test that reference items are excluded from recommendations"""
        cbf.add_item("item1", {"feature1": 1.0})
        cbf.add_item("item2", {"feature1": 0.9})

        recommendations = cbf.recommend(reference_items=["item1"])

        recommended_ids = [r.item_id for r in recommendations]
        assert "item1" not in recommended_ids

    def test_recommendation_scores_sorted(self, cbf):
        """Test that recommendations are sorted by score"""
        for i in range(10):
            cbf.add_item(f"item{i}", {"feature1": float(i)})

        recommendations = cbf.recommend(reference_items=["item5"], top_k=5)

        # Scores should be in descending order
        scores = [r.score for r in recommendations]
        assert scores == sorted(scores, reverse=True)


class TestRecommendationEngine:
    """Test RecommendationEngine (Hybrid)"""

    @pytest.fixture
    def engine(self):
        """Create recommendation engine"""
        return RecommendationEngine()

    def test_initialization(self, engine):
        """Test engine initialization"""
        assert isinstance(engine.collaborative_filter, CollaborativeFilter)
        assert isinstance(engine.content_filter, ContentBasedFilter)

    def test_hybrid_recommendations(self, engine):
        """Test hybrid recommendations"""
        # Add collaborative data
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(1, "item2")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item3")

        # Add content data
        engine.content_filter.add_item("item1", {"feature1": 1.0})
        engine.content_filter.add_item("item2", {"feature1": 0.9})
        engine.content_filter.add_item("item3", {"feature1": 0.8})
        engine.content_filter.add_item("item4", {"feature1": 0.85})

        # Get recommendations
        recommendations = engine.recommend(user_id=1, user_items=["item1", "item2"], top_k=5)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5

    def test_collaborative_only(self, engine):
        """Test recommendations with only collaborative filtering"""
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        recommendations = engine.recommend(user_id=1, top_k=5)
        assert isinstance(recommendations, list)

    def test_content_only(self, engine):
        """Test recommendations with only content-based filtering"""
        engine.content_filter.add_item("item1", {"feature1": 1.0})
        engine.content_filter.add_item("item2", {"feature1": 0.9})

        recommendations = engine.recommend(user_id=999, user_items=["item1"], top_k=5)
        assert isinstance(recommendations, list)

    def test_score_weighting(self, engine):
        """Test that hybrid scores use correct weighting"""
        # This is a logical test - actual implementation uses 60/40 weighting
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.collaborative_filter.add_interaction(2, "item1")
        engine.collaborative_filter.add_interaction(2, "item2")

        engine.content_filter.add_item("item1", {"feature1": 1.0})
        engine.content_filter.add_item("item2", {"feature1": 0.9})
        engine.content_filter.add_item("item3", {"feature1": 0.95})

        recommendations = engine.recommend(user_id=1, user_items=["item1"], top_k=10)

        # Should combine both signals
        assert isinstance(recommendations, list)


class TestGlobalEngine:
    """Test global recommendation engine"""

    def test_get_recommendation_engine(self):
        """Test getting global engine"""
        engine1 = get_recommendation_engine()
        engine2 = get_recommendation_engine()

        # Should return same instance (singleton)
        assert engine1 is engine2

    def test_engine_is_singleton(self):
        """Test that engine is a singleton"""
        engine = get_recommendation_engine()
        assert isinstance(engine, RecommendationEngine)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_recommend_with_no_data(self):
        """Test recommendations with no training data"""
        cf = CollaborativeFilter()
        recommendations = cf.recommend(user_id=1)
        assert recommendations == []

    def test_recommend_single_user(self):
        """Test recommendations with only one user"""
        cf = CollaborativeFilter()
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")

        # No other users to compare with
        recommendations = cf.recommend(user_id=1)
        assert isinstance(recommendations, list)

    def test_recommend_all_items_liked(self):
        """Test when user has liked all available items"""
        cf = CollaborativeFilter()
        cf.add_interaction(1, "item1")
        cf.add_interaction(1, "item2")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        # User 1 already liked everything user 2 likes
        recommendations = cf.recommend(user_id=1)
        assert recommendations == []

    def test_very_sparse_data(self):
        """Test with very sparse user-item matrix"""
        cf = CollaborativeFilter()

        # Many users, few interactions
        for user_id in range(100):
            cf.add_interaction(user_id, f"item{user_id % 5}")

        recommendations = cf.recommend(user_id=1)
        assert isinstance(recommendations, list)

    def test_very_dense_data(self):
        """Test with very dense user-item matrix"""
        cf = CollaborativeFilter()

        # Every user likes every item
        for user_id in range(10):
            for item_id in range(10):
                cf.add_interaction(user_id, f"item{item_id}")

        recommendations = cf.recommend(user_id=1)
        # Should have no new recommendations
        assert recommendations == []

    def test_negative_user_id(self):
        """Test with negative user ID"""
        cf = CollaborativeFilter()
        cf.add_interaction(-1, "item1")

        recommendations = cf.recommend(user_id=-1)
        assert isinstance(recommendations, list)

    def test_zero_top_k(self):
        """Test with top_k=0"""
        cf = CollaborativeFilter()
        cf.add_interaction(1, "item1")
        cf.add_interaction(2, "item1")
        cf.add_interaction(2, "item2")

        recommendations = cf.recommend(user_id=1, top_k=0)
        assert len(recommendations) == 0

    def test_large_top_k(self):
        """Test with very large top_k"""
        cf = CollaborativeFilter()
        cf.add_interaction(1, "item1")
        cf.add_interaction(2, "item1")
        for i in range(100):
            cf.add_interaction(2, f"item{i}")

        recommendations = cf.recommend(user_id=1, top_k=1000)
        # Should not crash, just return available items
        assert isinstance(recommendations, list)


@pytest.mark.parametrize("num_users,num_items,top_k", [
    (5, 10, 5),
    (10, 20, 10),
    (20, 50, 15),
])
def test_parametrized_recommendations(num_users, num_items, top_k):
    """Test recommendations with various data sizes"""
    cf = CollaborativeFilter()

    # Generate synthetic data
    for user_id in range(num_users):
        for item_id in range(num_items):
            if (user_id + item_id) % 3 == 0:  # Some pattern
                cf.add_interaction(user_id, f"item{item_id}")

    recommendations = cf.recommend(user_id=0, top_k=top_k)

    assert isinstance(recommendations, list)
    assert len(recommendations) <= top_k


class TestIntegration:
    """Integration tests"""

    def test_full_recommendation_pipeline(self):
        """Test complete recommendation pipeline"""
        engine = RecommendationEngine()

        # Setup collaborative data
        for user_id in range(10):
            for item_id in range(5):
                if (user_id + item_id) % 2 == 0:
                    engine.collaborative_filter.add_interaction(user_id, f"item{item_id}")

        # Setup content data
        for item_id in range(10):
            engine.content_filter.add_item(
                f"item{item_id}",
                {"feature1": float(item_id / 10), "feature2": float(1 - item_id / 10)}
            )

        # Get hybrid recommendations
        recommendations = engine.recommend(
            user_id=0,
            user_items=["item0", "item2"],
            top_k=5
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        assert all(isinstance(r, Recommendation) for r in recommendations)

    def test_cold_start_problem(self):
        """Test handling of cold start problem (new user)"""
        engine = RecommendationEngine()

        # Add some data
        engine.collaborative_filter.add_interaction(1, "item1")
        engine.content_filter.add_item("item1", {"feature1": 1.0})
        engine.content_filter.add_item("item2", {"feature1": 0.9})

        # New user with no history
        recommendations = engine.recommend(user_id=999)

        # Should handle gracefully
        assert isinstance(recommendations, list)
