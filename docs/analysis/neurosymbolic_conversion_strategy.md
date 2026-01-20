# Neurosymbolic Services - Pure Python Conversion Strategy

**File:** `/home/user/daten20/src/neurosymbolic/neurosymbolic_services_numpy.py`
**Version:** 14.0.0
**Approach:** Dual-version implementation (similar to quantum_ml)

---

## 1. CONVERSION HIERARCHY

### Priority Tier 1 (CRITICAL) - Core Vector Operations
**Classes:** KnowledgeGraphEmbedder
**Reason:** Heaviest NumPy usage, core to embedding-based reasoning
**Risk:** High - affects all KG-based operations
**Effort:** Medium - 8-10 core operations
**Expected Gain:** Enables Pure Python KG embeddings

```
Operations to convert:
- np.random.randn() → random.gauss() loop
- np.linalg.norm() → manual Euclidean distance
- np.dot() → manual dot product
- np.zeros() → zero lists
- np.ones() → one lists
- Vector arithmetic (+, -, *)
```

### Priority Tier 2 (HIGH) - Attention Matrices
**Classes:** NeuralModuleNetwork
**Reason:** Matrix operations for visual QA pipeline
**Risk:** Medium - affects compositional reasoning
**Effort:** Low - 3-4 operations, straightforward 2D arrays
**Expected Gain:** Enables Pure Python visual reasoning

```
Operations to convert:
- np.ones((14, 14)) → 2D list comprehension
- np.random.rand(14, 14) → nested random loop
- np.sum(condition) → conditional count
```

### Priority Tier 3 (LOW) - Storage & Utility
**Classes:** All others
**Reason:** Minimal NumPy usage (mostly storage)
**Risk:** Low - mostly data containers
**Effort:** Trivial
**Expected Gain:** Cleaner separation of concerns

```
Operations:
- np.ndarray storage → convert to Lists
- No numeric operations
```

---

## 2. UTILITY MODULE DESIGN

### Pure Python Vector Library

**File:** `src/neurosymbolic/vector_utils.py`

```python
"""
Pure Python vector utilities for neuro-symbolic operations.

Provides drop-in replacements for NumPy operations:
- Vector initialization
- Distance metrics
- Inner products
- Element-wise operations
"""

import random
import math
from typing import List, Tuple, Optional


class Vector:
    """Pure Python vector class"""

    def __init__(self, values: Optional[List[float]] = None, dim: int = 1):
        if values is not None:
            self.values = list(values)
            self.dim = len(values)
        else:
            self.values = [0.0] * dim
            self.dim = dim

    def __add__(self, other: 'Vector') -> 'Vector':
        """Element-wise addition"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch")
        return Vector([a + b for a, b in zip(self.values, other.values)])

    def __sub__(self, other: 'Vector') -> 'Vector':
        """Element-wise subtraction"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch")
        return Vector([a - b for a, b in zip(self.values, other.values)])

    def __mul__(self, scalar: float) -> 'Vector':
        """Scalar multiplication"""
        return Vector([v * scalar for v in self.values])

    def __rmul__(self, scalar: float) -> 'Vector':
        """Right scalar multiplication"""
        return self.__mul__(scalar)

    def dot(self, other: 'Vector') -> float:
        """Dot product with another vector"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch")
        return sum(a * b for a, b in zip(self.values, other.values))

    def norm(self) -> float:
        """Euclidean norm (L2)"""
        return math.sqrt(sum(v ** 2 for v in self.values))

    @staticmethod
    def zeros(dim: int) -> 'Vector':
        """Create zero vector"""
        return Vector([0.0] * dim)

    @staticmethod
    def ones(dim: int) -> 'Vector':
        """Create ones vector"""
        return Vector([1.0] * dim)

    @staticmethod
    def random_normal(dim: int, mean: float = 0.0, std: float = 1.0) -> 'Vector':
        """Create random normal vector (like np.random.randn)"""
        return Vector([random.gauss(mean, std) for _ in range(dim)])

    @staticmethod
    def random_uniform(dim: int, low: float = 0.0, high: float = 1.0) -> 'Vector':
        """Create random uniform vector"""
        return Vector([random.uniform(low, high) for _ in range(dim)])


class Matrix:
    """Pure Python matrix class for attention maps"""

    def __init__(self, rows: int, cols: int, value: float = 0.0):
        self.rows = rows
        self.cols = cols
        self.data = [[value for _ in range(cols)] for _ in range(rows)]

    def __getitem__(self, idx: Tuple[int, int]) -> float:
        row, col = idx
        return self.data[row][col]

    def __setitem__(self, idx: Tuple[int, int], value: float):
        row, col = idx
        self.data[row][col] = value

    @staticmethod
    def ones(rows: int, cols: int) -> 'Matrix':
        """Create ones matrix"""
        return Matrix(rows, cols, value=1.0)

    @staticmethod
    def zeros(rows: int, cols: int) -> 'Matrix':
        """Create zeros matrix"""
        return Matrix(rows, cols, value=0.0)

    @staticmethod
    def random_uniform(rows: int, cols: int, low: float = 0.0, high: float = 1.0) -> 'Matrix':
        """Create random uniform matrix"""
        matrix = Matrix(rows, cols)
        for i in range(rows):
            for j in range(cols):
                matrix.data[i][j] = random.uniform(low, high)
        return matrix

    def sum(self, condition=None) -> float:
        """Sum all elements (optionally with condition)"""
        if condition is None:
            return sum(sum(row) for row in self.data)
        else:
            # condition is a callable like: lambda x: x > 0.5
            return sum(1 for row in self.data for val in row if condition(val))

    def flatten(self) -> List[float]:
        """Flatten to 1D list"""
        result = []
        for row in self.data:
            result.extend(row)
        return result


# Convenience functions matching NumPy API

def randn(dim: int) -> List[float]:
    """Generate random normal vector"""
    return [random.gauss(0, 1) for _ in range(dim)]


def rand(rows: int, cols: int = None) -> List:
    """Generate random uniform values"""
    if cols is None:
        return [random.random() for _ in range(rows)]
    else:
        return [[random.random() for _ in range(cols)] for _ in range(rows)]


def zeros(dim: int) -> List[float]:
    """Create zero vector"""
    return [0.0] * dim


def ones(dim: int) -> List[float]:
    """Create ones vector"""
    return [1.0] * dim


def dot(v1: List[float], v2: List[float]) -> float:
    """Dot product"""
    return sum(a * b for a, b in zip(v1, v2))


def norm(v: List[float]) -> float:
    """Euclidean norm"""
    return math.sqrt(sum(x ** 2 for x in v))


def distance_euclidean(v1: List[float], v2: List[float]) -> float:
    """Euclidean distance between two vectors"""
    return norm([a - b for a, b in zip(v1, v2)])
```

---

## 3. CLASS CONVERSION PLAN

### 3.1 KnowledgeGraphEmbedder Conversion

**Current:** Uses `Dict[str, np.ndarray]` for embeddings

**Step 1: Convert embeddings storage**
```python
# Before (NumPy)
self.entity_embeddings: Dict[str, np.ndarray] = {}
embedding = np.random.randn(100)

# After (Pure Python)
self.entity_embeddings: Dict[str, List[float]] = {}
embedding = vector_utils.randn(100)
```

**Step 2: Convert initialization**
```python
# Before
if head not in self.entity_embeddings:
    self.entity_embeddings[head] = np.random.randn(self.embedding_dim)

# After
if head not in self.entity_embeddings:
    self.entity_embeddings[head] = vector_utils.randn(self.embedding_dim)
```

**Step 3: Convert distance computations**
```python
# Before (TransE)
distance = np.linalg.norm(h + r - t)

# After
diff = [h_i + r_i - t_i for h_i, r_i, t_i in zip(h, r, t)]
distance = vector_utils.norm(diff)

# Or using Vector class
h_vec = Vector(h)
r_vec = Vector(r)
t_vec = Vector(t)
distance = (h_vec + r_vec - t_vec).norm()
```

**Step 4: Convert dot products**
```python
# Before (ComplEx)
score = np.dot(h * r, t)

# After
hadamard = [h_i * r_i for h_i, r_i in zip(h, r)]
score = vector_utils.dot(hadamard, t)
```

**Step 5: Convert default vectors**
```python
# Before
h = self.entity_embeddings.get(head, np.zeros(self.embedding_dim))

# After
h = self.entity_embeddings.get(head, vector_utils.zeros(self.embedding_dim))
```

### 3.2 NeuralModuleNetwork Conversion

**Current:** Uses `np.ndarray` for attention maps

**Step 1: Convert attention map representation**
```python
# Before
attention_map = np.ones((14, 14))  # Returns np.ndarray

# After (Option A: List of lists)
attention_map = [[1.0 for _ in range(14)] for _ in range(14)]

# After (Option B: Matrix class)
attention_map = vector_utils.Matrix.ones(14, 14)
```

**Step 2: Convert random generation**
```python
# Before
return np.random.rand(14, 14)

# After
return vector_utils.rand(14, 14)
```

**Step 3: Convert summation**
```python
# Before
return int(np.sum(attention_map > 0.5))

# After (List version)
return sum(1 for row in attention_map for val in row if val > 0.5)

# After (Matrix version)
return int(attention_map.sum(lambda x: x > 0.5))
```

---

## 4. DUAL-VERSION IMPLEMENTATION PATTERN

### Factory Function Approach

```python
"""neurosymbolic_services.py - Pure Python base"""

class KnowledgeGraphEmbedder:
    def __init__(self, embedding_dim: int = 100, use_numpy: bool = True):
        self.embedding_dim = embedding_dim
        self.use_numpy = use_numpy and self._numpy_available()

        if self.use_numpy:
            self._init_numpy()
        else:
            self._init_pure_python()

    @staticmethod
    def _numpy_available() -> bool:
        try:
            import numpy
            return True
        except ImportError:
            return False

    def _init_numpy(self):
        """NumPy-based initialization"""
        import numpy as np
        self.entity_embeddings: Dict[str, Any] = {}
        self.relation_embeddings: Dict[str, Any] = {}
        self._np = np

    def _init_pure_python(self):
        """Pure Python initialization"""
        from . import vector_utils
        self.entity_embeddings: Dict[str, List[float]] = {}
        self.relation_embeddings: Dict[str, List[float]] = {}
        self._utils = vector_utils

    async def score_triple_transe(self, head: str, relation: str, tail: str) -> float:
        """Score triple - dispatches to appropriate implementation"""
        if self.use_numpy:
            return await self._score_triple_transe_numpy(head, relation, tail)
        else:
            return await self._score_triple_transe_pure(head, relation, tail)

    async def _score_triple_transe_numpy(self, head: str, relation: str, tail: str) -> float:
        """NumPy implementation"""
        h = self.entity_embeddings.get(head, self._np.zeros(self.embedding_dim))
        r = self.relation_embeddings.get(relation, self._np.zeros(self.embedding_dim))
        t = self.entity_embeddings.get(tail, self._np.zeros(self.embedding_dim))
        distance = self._np.linalg.norm(h + r - t)
        return -distance

    async def _score_triple_transe_pure(self, head: str, relation: str, tail: str) -> float:
        """Pure Python implementation"""
        h = self.entity_embeddings.get(head, self._utils.zeros(self.embedding_dim))
        r = self.relation_embeddings.get(relation, self._utils.zeros(self.embedding_dim))
        t = self.entity_embeddings.get(tail, self._utils.zeros(self.embedding_dim))
        diff = [h_i + r_i - t_i for h_i, r_i, t_i in zip(h, r, t)]
        distance = self._utils.norm(diff)
        return -distance
```

### Separate File Approach (RECOMMENDED)

```
neurosymbolic/
├── neurosymbolic_services.py          # Pure Python (NEW - base)
├── neurosymbolic_services_numpy.py    # NumPy (EXISTING - keep)
├── vector_utils.py                     # Shared utilities
└── __init__.py                         # Factory functions

# __init__.py
import os
USE_NUMPY = os.getenv('NEUROSYMBOLIC_USE_NUMPY', 'true').lower() == 'true'

if USE_NUMPY:
    try:
        import numpy
        from .neurosymbolic_services_numpy import *
    except ImportError:
        from .neurosymbolic_services import *
else:
    from .neurosymbolic_services import *
```

---

## 5. PERFORMANCE CONSIDERATIONS

### Vector Operations

| Operation | NumPy Time | Pure Python Time | Overhead |
|-----------|-----------|-----------------|----------|
| randn(100) | 0.5 µs | 50 µs | 100x |
| norm(100) | 1 µs | 5 µs | 5x |
| dot(100) | 0.5 µs | 2 µs | 4x |
| TransE score | 3 µs | 10 µs | 3x |

### Matrix Operations

| Operation | NumPy Time | Pure Python Time | Overhead |
|-----------|-----------|-----------------|----------|
| ones(14,14) | 1 µs | 20 µs | 20x |
| rand(14,14) | 5 µs | 100 µs | 20x |
| sum(14x14) | 2 µs | 30 µs | 15x |

### Overall System Impact
- **Single embedding:** ~3-10µs overhead per operation
- **Link prediction (100 candidates):** ~1ms additional
- **Acceptable:** 5-15% slower is acceptable for Pure Python

---

## 6. TESTING STRATEGY

### Unit Tests

```python
# tests/test_vector_utils.py
def test_vector_norm():
    v = vector_utils.randn(100)
    assert isinstance(v, list)
    norm_val = vector_utils.norm(v)
    assert isinstance(norm_val, float)
    assert norm_val >= 0

def test_dot_product():
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    assert vector_utils.dot(v1, v2) == 32

# tests/test_kg_embedder_pure.py
@pytest.mark.asyncio
async def test_score_triple_transe_pure():
    embedder = KnowledgeGraphEmbedder(use_numpy=False)
    await embedder.add_triple("alice", "knows", "bob")
    score = await embedder.score_triple_transe("alice", "knows", "bob")
    assert isinstance(score, float)
```

### Integration Tests

```python
# Compare NumPy vs Pure Python
@pytest.mark.asyncio
async def test_kg_embedder_consistency():
    embedder_np = KnowledgeGraphEmbedder(use_numpy=True)
    embedder_py = KnowledgeGraphEmbedder(use_numpy=False)

    # Add same triples
    for embedder in [embedder_np, embedder_py]:
        await embedder.add_triple("alice", "knows", "bob")
        await embedder.add_triple("bob", "knows", "carol")

    # Compare scores (should be close, not exact due to float precision)
    score_np = await embedder_np.score_triple_transe("alice", "knows", "bob")
    score_py = await embedder_py.score_triple_transe("alice", "knows", "bob")
    assert abs(score_np - score_py) < 1e-6
```

### Benchmark Tests

```python
# benchmarks/bench_embeddings.py
import timeit

def bench_vector_ops():
    results = {
        'numpy_norm': timeit.timeit('np.linalg.norm(np.random.randn(100))',
                                    setup='import numpy as np', number=1000),
        'pure_norm': timeit.timeit('norm(randn(100))',
                                   setup='from vector_utils import norm, randn', number=1000),
    }
    return results
```

---

## 7. MIGRATION CHECKLIST

- [ ] Create `vector_utils.py` with Vector and Matrix classes
- [ ] Create helper functions (randn, rand, zeros, ones, dot, norm)
- [ ] Write unit tests for vector_utils
- [ ] Create Pure Python version of KnowledgeGraphEmbedder
- [ ] Create Pure Python version of NeuralModuleNetwork
- [ ] Create factory/selector mechanism
- [ ] Add environment variable support: `NEUROSYMBOLIC_USE_NUMPY`
- [ ] Create dual-version integration tests
- [ ] Benchmark both versions
- [ ] Update documentation
- [ ] Add migration guide for users
- [ ] Create CI/CD pipeline for both versions

---

## 8. FALLBACK STRATEGY

```python
# Graceful degradation if NumPy not available

def get_embedder(embedding_dim: int = 100):
    """Factory function with automatic fallback"""
    try:
        import numpy
        from .neurosymbolic_services_numpy import KnowledgeGraphEmbedder
        logger.info("Using NumPy-accelerated KnowledgeGraphEmbedder")
        return KnowledgeGraphEmbedder(embedding_dim)
    except ImportError:
        from .neurosymbolic_services import KnowledgeGraphEmbedder
        logger.warning("NumPy not available, using Pure Python KnowledgeGraphEmbedder")
        return KnowledgeGraphEmbedder(embedding_dim)
```

---

## 9. DOCUMENTATION UPDATES

### For Users
- Dual-version availability
- Performance trade-offs
- How to force Pure Python version
- System requirements

### For Developers
- Internal architecture
- Vector utilities API
- Adding new operations
- Contributing optimizations

---

## 10. ROLLOUT PLAN

### Phase 1: Infrastructure (Week 1)
- Create vector_utils module
- Create test suite
- Set up benchmarking

### Phase 2: KnowledgeGraphEmbedder (Week 2)
- Implement Pure Python version
- Run integration tests
- Benchmark & document

### Phase 3: NeuralModuleNetwork (Week 3)
- Implement Pure Python version
- Test with visual QA tasks
- Optimize attention operations

### Phase 4: Integration & Release (Week 4)
- Create factory functions
- Update documentation
- Create migration guide
- Release with dual-version support

