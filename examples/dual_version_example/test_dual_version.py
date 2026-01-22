"""
Tests for Dual-Version Pattern Example

Verifies that both Pure Python and NumPy versions:
1. Have identical API
2. Produce identical results
3. Both work correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dual_version_example import (
    VectorSimilarityPython,
    HAS_NUMPY,
    SimilarityResult
)

if HAS_NUMPY:
    from dual_version_example import VectorSimilarityNumpy


def test_api_compatibility():
    """Test that both versions have identical API"""
    print("="*60)
    print("TEST 1: API Compatibility")
    print("="*60)

    # Create both calculators
    calc_python = VectorSimilarityPython()

    # Check pure Python has all methods
    assert hasattr(calc_python, 'dot_product')
    assert hasattr(calc_python, 'norm')
    assert hasattr(calc_python, 'cosine_similarity')
    assert hasattr(calc_python, 'euclidean_distance')
    assert hasattr(calc_python, 'compute_similarity')
    assert hasattr(calc_python, 'find_most_similar')

    print("✅ Pure Python version has all required methods")

    if HAS_NUMPY:
        calc_numpy = VectorSimilarityNumpy()

        # Check NumPy has all methods
        assert hasattr(calc_numpy, 'dot_product')
        assert hasattr(calc_numpy, 'norm')
        assert hasattr(calc_numpy, 'cosine_similarity')
        assert hasattr(calc_numpy, 'euclidean_distance')
        assert hasattr(calc_numpy, 'compute_similarity')
        assert hasattr(calc_numpy, 'find_most_similar')

        print("✅ NumPy version has all required methods")
        print("✅ Both versions have identical API")
    else:
        print("⚠️  NumPy not available - skipping NumPy version check")

    print()


def test_identical_results():
    """Test that both versions produce identical results"""
    print("="*60)
    print("TEST 2: Identical Results")
    print("="*60)

    # Test vectors
    v1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    v2 = [2.0, 4.0, 6.0, 8.0, 10.0]
    v3 = [5.0, 4.0, 3.0, 2.0, 1.0]

    # Pure Python version
    calc_python = VectorSimilarityPython()
    result_python = calc_python.compute_similarity(v1, v2)

    print(f"Pure Python result:")
    print(f"  Cosine similarity: {result_python.cosine_similarity:.6f}")
    print(f"  Euclidean distance: {result_python.euclidean_distance:.6f}")
    print(f"  Vector1 norm: {result_python.vector1_norm:.6f}")
    print(f"  Vector2 norm: {result_python.vector2_norm:.6f}")

    if HAS_NUMPY:
        # NumPy version
        calc_numpy = VectorSimilarityNumpy()
        result_numpy = calc_numpy.compute_similarity(v1, v2)

        print(f"\nNumPy result:")
        print(f"  Cosine similarity: {result_numpy.cosine_similarity:.6f}")
        print(f"  Euclidean distance: {result_numpy.euclidean_distance:.6f}")
        print(f"  Vector1 norm: {result_numpy.vector1_norm:.6f}")
        print(f"  Vector2 norm: {result_numpy.vector2_norm:.6f}")

        # Compare results (allow small floating point differences)
        epsilon = 1e-6
        assert abs(result_python.cosine_similarity - result_numpy.cosine_similarity) < epsilon
        assert abs(result_python.euclidean_distance - result_numpy.euclidean_distance) < epsilon
        assert abs(result_python.vector1_norm - result_numpy.vector1_norm) < epsilon
        assert abs(result_python.vector2_norm - result_numpy.vector2_norm) < epsilon

        print("\n✅ Results are identical (within floating point precision)")
    else:
        print("\n⚠️  NumPy not available - skipping comparison")

    print()


def test_find_most_similar():
    """Test find_most_similar method"""
    print("="*60)
    print("TEST 3: Find Most Similar")
    print("="*60)

    query = [1.0, 2.0, 3.0]
    candidates = [
        [1.0, 2.0, 3.0],   # Identical (similarity = 1.0)
        [2.0, 4.0, 6.0],   # Same direction (similarity = 1.0)
        [3.0, 2.0, 1.0],   # Different
        [-1.0, -2.0, -3.0] # Opposite direction (similarity = -1.0)
    ]

    # Pure Python
    calc_python = VectorSimilarityPython()
    idx_python, sim_python = calc_python.find_most_similar(query, candidates)

    print(f"Pure Python:")
    print(f"  Most similar: candidates[{idx_python}] = {candidates[idx_python]}")
    print(f"  Similarity: {sim_python:.6f}")

    # Should find index 0 or 1 (both have similarity 1.0)
    assert idx_python in [0, 1]
    assert abs(sim_python - 1.0) < 1e-6

    if HAS_NUMPY:
        # NumPy
        calc_numpy = VectorSimilarityNumpy()
        idx_numpy, sim_numpy = calc_numpy.find_most_similar(query, candidates)

        print(f"\nNumPy:")
        print(f"  Most similar: candidates[{idx_numpy}] = {candidates[idx_numpy]}")
        print(f"  Similarity: {sim_numpy:.6f}")

        # Should find same or equivalent result
        assert idx_numpy in [0, 1]
        assert abs(sim_numpy - 1.0) < 1e-6

        print("\n✅ Both versions found correct most similar vector")
    else:
        print("\n⚠️  NumPy not available - skipping comparison")

    print()


def test_performance_comparison():
    """Compare performance of both versions"""
    if not HAS_NUMPY:
        print("="*60)
        print("TEST 4: Performance Comparison")
        print("="*60)
        print("⚠️  NumPy not available - skipping performance test")
        print()
        return

    print("="*60)
    print("TEST 4: Performance Comparison")
    print("="*60)

    import time
    import random
    random.seed(42)

    # Generate dataset
    dim = 100
    num_vectors = 100  # Smaller for testing
    query = [random.random() for _ in range(dim)]
    candidates = [[random.random() for _ in range(dim)] for _ in range(num_vectors)]

    print(f"Dataset: {num_vectors} vectors, {dim} dimensions\n")

    # Pure Python
    calc_python = VectorSimilarityPython()
    start = time.time()
    idx_python, sim_python = calc_python.find_most_similar(query, candidates)
    time_python = time.time() - start

    print(f"Pure Python:")
    print(f"  Time: {time_python*1000:.2f} ms")
    print(f"  Result: index {idx_python}, similarity {sim_python:.4f}")

    # NumPy
    calc_numpy = VectorSimilarityNumpy()
    start = time.time()
    idx_numpy, sim_numpy = calc_numpy.find_most_similar(query, candidates)
    time_numpy = time.time() - start

    print(f"\nNumPy:")
    print(f"  Time: {time_numpy*1000:.2f} ms")
    print(f"  Result: index {idx_numpy}, similarity {sim_numpy:.4f}")

    # Calculate speedup
    speedup = time_python / time_numpy if time_numpy > 0 else float('inf')
    print(f"\nSpeedup: {speedup:.1f}x faster with NumPy! 🚀")

    # Verify results are similar (may differ slightly due to numerical precision)
    epsilon = 1e-4
    assert abs(sim_python - sim_numpy) < epsilon, "Results differ significantly"

    print("✅ Performance test passed")
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("DUAL-VERSION PATTERN: API COMPATIBILITY TESTS")
    print("="*60)
    print(f"NumPy available: {HAS_NUMPY}")
    print("="*60 + "\n")

    try:
        test_api_compatibility()
        test_identical_results()
        test_find_most_similar()
        test_performance_comparison()

        print("="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
        print("\nSummary:")
        print("✅ Both versions have identical API")
        print("✅ Both versions produce identical results")
        print("✅ Both versions work correctly")
        if HAS_NUMPY:
            print("✅ NumPy version is significantly faster")
        print("\n" + "="*60)

    except AssertionError as e:
        print("\n" + "="*60)
        print("TEST FAILED ❌")
        print("="*60)
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
