"""
Dual-Version Example: Vector Similarity Calculator

Demonstrates the Dual-Version Pattern with NumPy + Pure Python.

Two implementations available:
1. Pure Python (default): Zero dependencies, works everywhere
2. NumPy version: 10-100x faster, requires numpy

Example usage (automatic selection):
    from dual_version_example import VectorSimilarity, HAS_NUMPY

    # Automatically uses NumPy if available, otherwise pure Python
    calc = VectorSimilarity()
    result = calc.compute_similarity([1, 2, 3], [4, 5, 6])

    print(f"Using NumPy: {HAS_NUMPY}")
    print(f"Cosine similarity: {result.cosine_similarity:.4f}")

Example usage (explicit version selection):
    from dual_version_example import HAS_NUMPY

    if HAS_NUMPY:
        from dual_version_example import VectorSimilarityNumpy
        calc = VectorSimilarityNumpy()
    else:
        from dual_version_example import VectorSimilarityPython
        calc = VectorSimilarityPython()

    # Same API for both versions!
    result = calc.compute_similarity([1, 2, 3], [4, 5, 6])
"""

__version__ = "1.0.0"

# ALWAYS import pure Python version (default, always available)
from .vector_similarity import (
    VectorSimilarity as VectorSimilarityPython,
    SimilarityResult,
)

# Try to import NumPy version (optional, 10-100x faster)
try:
    from .vector_similarity_numpy import (
        VectorSimilarityNumpy,
        SimilarityResult as SimilarityResultNumpy,
    )
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Export intelligent default: NumPy if available, otherwise pure Python
if HAS_NUMPY:
    VectorSimilarity = VectorSimilarityNumpy  # Use fast version
else:
    VectorSimilarity = VectorSimilarityPython  # Fallback to pure Python

__all__ = [
    "__version__",
    # Default (auto-selected based on numpy availability)
    "VectorSimilarity",
    # Pure Python (always available)
    "VectorSimilarityPython",
    # Data structures
    "SimilarityResult",
    # Version flag
    "HAS_NUMPY",
]

# Add NumPy-specific exports if available
if HAS_NUMPY:
    __all__.extend([
        "VectorSimilarityNumpy",
        "SimilarityResultNumpy",
    ])
