"""
Vector Similarity Calculator - Pure Python Version

Calculates similarity between vectors (cosine similarity, euclidean distance).
Uses only Python stdlib - no external dependencies!

This is the baseline implementation that works everywhere.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SimilarityResult:
    """Result of similarity computation"""
    cosine_similarity: float
    euclidean_distance: float
    vector1_norm: float
    vector2_norm: float


class VectorSimilarity:
    """
    Vector similarity calculator using pure Python.

    Uses only Python stdlib (math module, list comprehensions).
    Performance: Good for small vectors (< 1000 dimensions).
    """

    def __init__(self):
        """Initialize calculator"""
        pass

    def dot_product(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute dot product: v1 · v2

        Pure Python implementation using sum() and zip().
        """
        if len(v1) != len(v2):
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        return sum(x * y for x, y in zip(v1, v2))

    def norm(self, v: List[float]) -> float:
        """
        Compute L2 norm (length) of vector: ||v||

        Pure Python implementation using math.sqrt().
        """
        return math.sqrt(sum(x * x for x in v))

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute cosine similarity: (v1 · v2) / (||v1|| * ||v2||)

        Returns value in [-1, 1]:
        - 1.0: vectors point in same direction (identical)
        - 0.0: vectors are orthogonal (independent)
        - -1.0: vectors point in opposite directions

        Pure Python implementation.
        """
        if len(v1) != len(v2):
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        dot = self.dot_product(v1, v2)
        norm1 = self.norm(v1)
        norm2 = self.norm(v2)

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return dot / (norm1 * norm2)

    def euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute Euclidean distance: ||v1 - v2||

        Pure Python implementation.
        """
        if len(v1) != len(v2):
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        return math.sqrt(sum((x - y) ** 2 for x, y in zip(v1, v2)))

    def compute_similarity(self, v1: List[float], v2: List[float]) -> SimilarityResult:
        """
        Compute all similarity metrics between two vectors.

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            SimilarityResult with all metrics
        """
        cosine_sim = self.cosine_similarity(v1, v2)
        euclidean_dist = self.euclidean_distance(v1, v2)
        norm1 = self.norm(v1)
        norm2 = self.norm(v2)

        return SimilarityResult(
            cosine_similarity=cosine_sim,
            euclidean_distance=euclidean_dist,
            vector1_norm=norm1,
            vector2_norm=norm2
        )

    def find_most_similar(self, query: List[float], vectors: List[List[float]]) -> Tuple[int, float]:
        """
        Find most similar vector to query.

        Args:
            query: Query vector
            vectors: List of candidate vectors

        Returns:
            (index, similarity) of most similar vector
        """
        best_idx = 0
        best_similarity = -1.0

        for i, vec in enumerate(vectors):
            similarity = self.cosine_similarity(query, vec)
            if similarity > best_similarity:
                best_similarity = similarity
                best_idx = i

        return best_idx, best_similarity


# Example usage
if __name__ == "__main__":
    import random
    random.seed(42)

    print("="*60)
    print("Vector Similarity - Pure Python Version")
    print("="*60)

    # Create calculator
    calc = VectorSimilarity()

    # Example vectors
    v1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    v2 = [2.0, 4.0, 6.0, 8.0, 10.0]  # v2 = 2 * v1 (same direction)
    v3 = [5.0, 4.0, 3.0, 2.0, 1.0]   # v3 is reversed

    # Compute similarities
    result12 = calc.compute_similarity(v1, v2)
    result13 = calc.compute_similarity(v1, v3)

    print(f"\nv1 = {v1}")
    print(f"v2 = {v2} (2 * v1)")
    print(f"v3 = {v3} (reversed)")

    print(f"\nSimilarity v1 vs v2:")
    print(f"  Cosine similarity: {result12.cosine_similarity:.4f}")
    print(f"  Euclidean distance: {result12.euclidean_distance:.4f}")

    print(f"\nSimilarity v1 vs v3:")
    print(f"  Cosine similarity: {result13.cosine_similarity:.4f}")
    print(f"  Euclidean distance: {result13.euclidean_distance:.4f}")

    # Find most similar
    print("\n" + "="*60)
    query = [1.0, 2.0, 3.0]
    candidates = [
        [1.0, 2.0, 3.0],   # Identical
        [2.0, 4.0, 6.0],   # Same direction
        [3.0, 2.0, 1.0],   # Different
        [-1.0, -2.0, -3.0] # Opposite direction
    ]

    idx, similarity = calc.find_most_similar(query, candidates)
    print(f"Query: {query}")
    print(f"Most similar candidate: {candidates[idx]} (similarity: {similarity:.4f})")
    print("="*60)
