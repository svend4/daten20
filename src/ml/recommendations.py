"""
Recommendation Engine

Provides recommendations using:
- Collaborative filtering
- Content-based filtering
- Hybrid approach
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math


@dataclass
class Recommendation:
    """Recommendation result"""
    item_id: str
    score: float
    reason: str


class CollaborativeFilter:
    """Collaborative filtering"""

    def __init__(self):
        self.user_items: Dict[int, Set[str]] = defaultdict(set)
        self.item_users: Dict[str, Set[int]] = defaultdict(set)

    def add_interaction(self, user_id: int, item_id: str):
        """Add user-item interaction"""
        self.user_items[user_id].add(item_id)
        self.item_users[item_id].add(user_id)

    def recommend(self, user_id: int, top_k: int = 10) -> List[Recommendation]:
        """Recommend items for user"""
        if user_id not in self.user_items:
            return []

        user_items = self.user_items[user_id]

        # Find similar users
        similar_users = self._find_similar_users(user_id)

        # Aggregate their items
        item_scores = defaultdict(float)
        for other_user, similarity in similar_users[:20]:
            for item in self.user_items[other_user]:
                if item not in user_items:
                    item_scores[item] += similarity

        # Sort and return top-k
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for item_id, score in sorted_items[:top_k]:
            recommendations.append(Recommendation(
                item_id=item_id,
                score=score,
                reason="Users like you also used this"
            ))

        return recommendations

    def _find_similar_users(self, user_id: int) -> List[Tuple[int, float]]:
        """Find similar users using Jaccard similarity"""
        user_items = self.user_items[user_id]
        similarities = []

        for other_user in self.user_items:
            if other_user == user_id:
                continue

            other_items = self.user_items[other_user]
            intersection = len(user_items & other_items)
            union = len(user_items | other_items)

            if union > 0:
                similarity = intersection / union
                similarities.append((other_user, similarity))

        return sorted(similarities, key=lambda x: x[1], reverse=True)


class ContentBasedFilter:
    """Content-based filtering"""

    def __init__(self):
        self.item_features: Dict[str, Dict[str, float]] = {}

    def add_item(self, item_id: str, features: Dict[str, float]):
        """Add item with features"""
        self.item_features[item_id] = features

    def recommend(
        self,
        reference_items: List[str],
        top_k: int = 10
    ) -> List[Recommendation]:
        """Recommend similar items"""
        if not reference_items:
            return []

        # Average features of reference items
        avg_features = defaultdict(float)
        for item_id in reference_items:
            if item_id in self.item_features:
                for feature, value in self.item_features[item_id].items():
                    avg_features[feature] += value

        for feature in avg_features:
            avg_features[feature] /= len(reference_items)

        # Calculate similarity to all items
        similarities = []
        for item_id, features in self.item_features.items():
            if item_id in reference_items:
                continue

            similarity = self._cosine_similarity(dict(avg_features), features)
            similarities.append((item_id, similarity))

        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for item_id, score in similarities[:top_k]:
            recommendations.append(Recommendation(
                item_id=item_id,
                score=score,
                reason="Similar to items you've used"
            ))

        return recommendations

    def _cosine_similarity(
        self,
        features1: Dict[str, float],
        features2: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity"""
        dot_product = sum(features1.get(k, 0) * features2.get(k, 0) for k in set(features1) | set(features2))

        norm1 = math.sqrt(sum(v**2 for v in features1.values()))
        norm2 = math.sqrt(sum(v**2 for v in features2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class RecommendationEngine:
    """Main recommendation engine"""

    def __init__(self):
        self.collaborative_filter = CollaborativeFilter()
        self.content_filter = ContentBasedFilter()

    def recommend(
        self,
        user_id: int,
        user_items: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[Recommendation]:
        """Generate hybrid recommendations"""
        collaborative_recs = self.collaborative_filter.recommend(user_id, top_k)
        content_recs = self.content_filter.recommend(user_items or [], top_k) if user_items else []

        # Combine recommendations
        combined_scores = defaultdict(float)
        for rec in collaborative_recs:
            combined_scores[rec.item_id] += rec.score * 0.6

        for rec in content_recs:
            combined_scores[rec.item_id] += rec.score * 0.4

        # Sort and return top-k
        sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for item_id, score in sorted_items[:top_k]:
            recommendations.append(Recommendation(
                item_id=item_id,
                score=score,
                reason="Recommended for you"
            ))

        return recommendations


# Global instance
_recommendation_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get global recommendation engine"""
    global _recommendation_engine

    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()

    return _recommendation_engine
