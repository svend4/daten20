"""
Vector Similarity Calculator - NumPy-Accelerated Version

Calculates similarity between vectors (cosine similarity, euclidean distance).
Uses NumPy for 10-100x speedup over pure Python!

Performance: 10-100x faster than pure Python version.
Requires: numpy

API-compatible with vector_similarity.py (pure Python version).
"""

from dataclasses import dataclass
from typing import List, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    raise ImportError(
        "NumPy not available! Install with: pip install numpy\n"
        "Or use pure Python version: from dual_version_example import VectorSimilarity"
    )


@dataclass
class SimilarityResult:
    """Result of similarity computation (same as pure Python version)"""
    cosine_similarity: float
    euclidean_distance: float
    vector1_norm: float
    vector2_norm: float


class VectorSimilarityNumpy:
    """
    Vector similarity calculator using NumPy (vectorized).

    Same API as VectorSimilarity but 10-100x faster!
    Uses vectorized operations and optimized linear algebra.
    """

    def __init__(self):
        """Initialize calculator (same API as pure Python)"""
        pass

    def dot_product(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute dot product: v1 · v2

        NumPy implementation using np.dot() (vectorized).
        """
        arr1 = np.array(v1)
        arr2 = np.array(v2)

        if arr1.shape != arr2.shape:
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        return float(np.dot(arr1, arr2))

    def norm(self, v: List[float]) -> float:
        """
        Compute L2 norm (length) of vector: ||v||

        NumPy implementation using np.linalg.norm() (optimized).
        """
        arr = np.array(v)
        return float(np.linalg.norm(arr))

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute cosine similarity: (v1 · v2) / (||v1|| * ||v2||)

        NumPy implementation (vectorized).
        Same API as pure Python version.
        """
        arr1 = np.array(v1)
        arr2 = np.array(v2)

        if arr1.shape != arr2.shape:
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        # Vectorized: dot product
        dot = np.dot(arr1, arr2)

        # Vectorized: norms
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return float(dot / (norm1 * norm2))

    def euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """
        Compute Euclidean distance: ||v1 - v2||

        NumPy implementation (vectorized).
        """
        arr1 = np.array(v1)
        arr2 = np.array(v2)

        if arr1.shape != arr2.shape:
            raise ValueError(f"Vectors must have same length: {len(v1)} != {len(v2)}")

        # Vectorized: ||v1 - v2||
        return float(np.linalg.norm(arr1 - arr2))

    def compute_similarity(self, v1: List[float], v2: List[float]) -> SimilarityResult:
        """
        Compute all similarity metrics between two vectors.

        Same API as pure Python version.
        """
        # Convert to numpy arrays for efficiency
        arr1 = np.array(v1)
        arr2 = np.array(v2)

        # All vectorized operations
        dot = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        cosine_sim = float(dot / (norm1 * norm2)) if (norm1 > 0 and norm2 > 0) else 0.0
        euclidean_dist = float(np.linalg.norm(arr1 - arr2))

        return SimilarityResult(
            cosine_similarity=cosine_sim,
            euclidean_distance=euclidean_dist,
            vector1_norm=float(norm1),
            vector2_norm=float(norm2)
        )

    def find_most_similar(self, query: List[float], vectors: List[List[float]]) -> Tuple[int, float]:
        """
        Find most similar vector to query.

        NumPy implementation with batch processing (MUCH faster!).

        Args:
            query: Query vector
            vectors: List of candidate vectors

        Returns:
            (index, similarity) of most similar vector
        """
        # Convert to numpy arrays
        query_arr = np.array(query)
        vectors_arr = np.array(vectors)  # Shape: (num_vectors, dim)

        # Batch computation of all similarities at once! (FAST!)
        # Matrix multiply: (num_vectors, dim) @ (dim,) -> (num_vectors,)
        dots = vectors_arr @ query_arr

        # Vectorized norms
        query_norm = np.linalg.norm(query_arr)
        vectors_norms = np.linalg.norm(vectors_arr, axis=1)  # Shape: (num_vectors,)

        # Vectorized cosine similarities (all at once!)
        similarities = dots / (vectors_norms * query_norm + 1e-10)  # Add epsilon to avoid div by zero

        # Find max
        best_idx = int(np.argmax(similarities))
        best_similarity = float(similarities[best_idx])

        return best_idx, best_similarity


# Example usage
if __name__ == "__main__":
    import random
    import time
    random.seed(42)
    np.random.seed(42)

    print("="*60)
    print("Vector Similarity - NumPy-Accelerated Version")
    print("10-100x faster than pure Python!")
    print("="*60)

    # Create calculator
    calc = VectorSimilarityNumpy()

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

    # Performance benchmark
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)

    # Generate large dataset
    dim = 100
    num_vectors = 1000
    query_vec = np.random.randn(dim).tolist()
    candidate_vecs = [np.random.randn(dim).tolist() for _ in range(num_vectors)]

    print(f"\nDataset: {num_vectors} vectors, {dim} dimensions")

    # NumPy version (batch processing)
    start = time.time()
    idx_numpy, sim_numpy = calc.find_most_similar(query_vec, candidate_vecs)
    time_numpy = time.time() - start

    print(f"\nNumPy version:")
    print(f"  Time: {time_numpy*1000:.2f} ms")
    print(f"  Most similar: index {idx_numpy}, similarity {sim_numpy:.4f}")

    print("\n" + "="*60)
    print("NumPy version uses batch processing for maximum speed!")
    print("="*60)
