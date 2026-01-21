# Performance Tests

Automated performance regression testing using `pytest-benchmark`.

## Overview

Performance tests track execution time, throughput, and resource usage for critical operations. Tests automatically detect performance regressions by comparing against historical baselines.

## Test Categories

### 1. Document Processing (`test_document_processing_perf.py`)
- Text extraction performance
- Document validation
- Metadata extraction
- Batch processing
- PDF processing (mocked)
- Search operations
- Caching mechanisms

### 2. ML Inference (`test_ml_inference_perf.py`)
- Text classification inference
- Named Entity Recognition (NER)
- Batch inference
- Embedding generation
- Model loading and initialization
- Feature extraction (TF-IDF, n-grams)
- Model optimization (quantization, pruning)

### 3. Consciousness AI (`test_consciousness_perf.py`)
- Processing cycle performance
- Global workspace operations
- Introspection operations
- Qualia generation
- Metrics computation
- Memory operations
- Scalability under load

### 4. API Endpoints (`test_api_performance.py`)
- REST endpoint response times
- Batch operations
- Authentication and session management
- Pagination
- Serialization/deserialization
- Compression (gzip)
- Caching strategies
- Rate limiting

## Installation

```bash
pip install pytest-benchmark
```

## Running Tests

### Run all performance tests:
```bash
pytest tests/performance/ -v --benchmark-only
```

### Run specific test file:
```bash
pytest tests/performance/test_document_processing_perf.py -v --benchmark-only
```

### Run with detailed statistics:
```bash
pytest tests/performance/ --benchmark-verbose --benchmark-only
```

### Include slow tests:
```bash
pytest tests/performance/ -v --benchmark-only -m slow
```

## Baseline Management

### Save baseline:
```bash
pytest tests/performance/ --benchmark-save=baseline_2024_01
```

### Compare against baseline:
```bash
pytest tests/performance/ --benchmark-compare=baseline_2024_01
```

### Compare with fail on regression:
```bash
pytest tests/performance/ --benchmark-compare=baseline_2024_01 --benchmark-compare-fail=mean:10%
```

This fails if mean performance degrades by more than 10%.

## Continuous Integration

### In CI Pipeline:
```yaml
# .github/workflows/performance.yml already configured
- name: Run performance tests
  run: |
    pytest tests/performance/ --benchmark-only --benchmark-json=output.json

- name: Compare with baseline
  run: |
    pytest tests/performance/ --benchmark-compare=main_baseline --benchmark-compare-fail=mean:15%
```

## Interpreting Results

### Output Format:
```
test_single_cycle_performance      Min: 0.0010s  Max: 0.0015s  Mean: 0.0012s  StdDev: 0.0001s
```

- **Min**: Fastest execution time (best case)
- **Max**: Slowest execution time (worst case)
- **Mean**: Average execution time (typical performance)
- **StdDev**: Standard deviation (consistency indicator)
- **Median**: Middle value (robust against outliers)
- **IQR**: Interquartile range (spread of middle 50%)
- **Outliers**: Number of outlier measurements
- **Rounds**: Number of benchmark iterations
- **Iterations**: Operations per round

### Performance Thresholds:

**Critical Operations** (should be fast):
- API endpoints: < 100ms (p95)
- Document processing: < 500ms per document
- ML inference: < 200ms per prediction
- Consciousness cycle: < 50ms per cycle

**Batch Operations** (can be slower):
- Batch inference (10 items): < 2s
- Large document processing: < 5s
- Sustained operations (50 cycles): < 5s

## Best Practices

### 1. Benchmark Scope
- Test one operation per benchmark
- Avoid including setup/teardown in timed section
- Use fixtures for common setup

### 2. Statistical Validity
- Let pytest-benchmark auto-calibrate rounds/iterations
- Run enough iterations for statistical significance
- Be aware of system noise (background processes)

### 3. Isolation
- Run on consistent hardware
- Close unnecessary applications
- Use dedicated CI runners for critical baselines

### 4. Regression Detection
- Set appropriate thresholds (10-20% for most operations)
- Tighter thresholds for critical paths (5-10%)
- Review trends over time, not just single comparisons

## Troubleshooting

### Test Failures:
1. **High variance**: System load, increase warmup rounds
2. **Baseline mismatch**: Different hardware, create new baseline
3. **Consistent regression**: Real performance issue, investigate

### Optimization Tips:
1. Profile slow tests: `pytest --benchmark-cprofile`
2. Check memory usage: `pytest --memprof`
3. Analyze hotspots with cProfile output

## Historical Baselines

Baselines are stored in `.benchmarks/` (gitignored).

To track baselines in git:
```bash
# Save important baselines
pytest tests/performance/ --benchmark-save=release_v4_3
cp .benchmarks/release_v4_3.json benchmarks/historical/
git add benchmarks/historical/release_v4_3.json
```

## Metrics Dashboard

View performance trends:
```bash
pytest-benchmark compare
```

Generate HTML report:
```bash
pytest tests/performance/ --benchmark-only --benchmark-histogram
```

## Contact

For performance issues or questions, see: `CONTRIBUTING.md`
