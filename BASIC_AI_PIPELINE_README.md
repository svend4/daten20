# Basic AI Pipeline (v10-v20) - README

## Overview

The **Basic AI Pipeline** (`src/integration/basic_ai_pipeline.py`) provides a unified interface for integrating and orchestrating all basic AI modules (v10-v20) in the DATEN20 system.

## Architecture

### Modules Integrated

1. **v10: Deployment** - Infrastructure orchestration (always available)
2. **v11: Federated Learning** - Privacy-preserving distributed learning (always available)
3. **v12: Autonomous Systems** - Autonomous agents and reasoning (always available)
4. **v13: Explainable AI** - Model interpretability (optional: requires dependencies)
5. **v14: Neurosymbolic AI** - Neural-symbolic reasoning (optional: requires numpy)
6. **v15: Quantum ML** - Quantum machine learning (optional: requires numpy)
7. **v16: Edge AI** - Edge deployment (optional: requires dependencies)
8. **v17: Multimodal AI** - Multi-modal processing (optional: requires numpy)
9. **v18: AI Safety** - Safety verification (optional: requires dependencies)
10. **v19: AI Agents** - Tool-using agents (optional: requires dependencies)
11. **v20: Human-AI Collaboration** - Human oversight (optional: requires dependencies)

### Operation Modes

The pipeline supports 11 progressive operation modes:

1. **DEPLOYMENT** (v10) - Infrastructure orchestration only
2. **FEDERATED** (v10-v11) - + Privacy-preserving distributed learning
3. **AUTONOMOUS** (v10-v12) - + Autonomous agents
4. **EXPLAINABLE** (v10-v13) - + Model explanations
5. **NEUROSYMBOLIC** (v10-v14) - + Symbolic reasoning
6. **QUANTUM** (v10-v15) - + Quantum speedup
7. **EDGE** (v10-v16) - + Edge deployment
8. **MULTIMODAL** (v10-v17) - + Multi-modal AI
9. **SAFE** (v10-v18) - + AI safety checks
10. **AGENTIC** (v10-v19) - + Tool-calling agents
11. **COLLABORATIVE** (v10-v20) - + Human oversight (**FULL**)

## Dependencies

### Core Dependencies (Always Required)
- Python 3.9+
- Standard library only

### Optional Dependencies (For Full Functionality)
```bash
# For v14 (Neurosymbolic), v15 (Quantum ML), v17 (Multimodal)
pip install numpy

# For advanced AI modules
pip install numpy scipy scikit-learn

# For v21+ (Continual Learning with NumPy acceleration)
pip install numpy
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd daten20

# Install core dependencies (minimal - v10-v12 only)
# No additional installation needed - uses stdlib only

# Install optional dependencies for full functionality (v10-v20)
pip install numpy scipy scikit-learn
```

## Usage

### Basic Usage (Core Modules Only - v10-v12)

```python
import asyncio
from src.integration.basic_ai_pipeline import (
    get_basic_ai_pipeline,
    BasicAIPipelineConfig,
    BasicAIMode
)

async def main():
    # Get pipeline instance
    pipeline = await get_basic_ai_pipeline()

    # Define task
    task_spec = {
        "task_id": "my_task",
        "description": "Solve a complex problem",
        "domain": "general"
    }

    # Configure pipeline (autonomous mode - v10-v12)
    config = BasicAIPipelineConfig(
        mode=BasicAIMode.AUTONOMOUS,
        enable_privacy=True
    )

    # Solve task
    result = await pipeline.solve_task(task_spec, config)

    print(f"Success: {result.success}")
    print(f"Quality: {result.quality_score:.2f}")
    print(f"Modules used: {result.modules_used}")

asyncio.run(main())
```

### Advanced Usage (Full Pipeline - v10-v20)

```python
import asyncio
from src.integration.basic_ai_pipeline import (
    get_basic_ai_pipeline,
    BasicAIPipelineConfig,
    BasicAIMode
)

async def main():
    pipeline = await get_basic_ai_pipeline()

    task_spec = {
        "task_id": "complex_task",
        "description": "Multi-modal task requiring human oversight",
        "domain": "medical_diagnosis",
        "modalities": ["text", "vision", "audio"],
        "tools": ["calculator", "web_search", "database"]
    }

    # Full collaborative mode (v10-v20)
    config = BasicAIPipelineConfig(
        mode=BasicAIMode.COLLABORATIVE,
        enable_privacy=True,
        enable_explainability=True,
        enable_safety_checks=True,
        enable_human_oversight=True
    )

    result = await pipeline.solve_task(task_spec, config)

    # Access comprehensive metrics
    print(f"Success: {result.success}")
    print(f"Quality: {result.quality_score:.2f}")
    print(f"Safety score: {result.metrics.safety_score:.2f}")
    print(f"Explainability: {result.metrics.explainability_score:.2f}")
    print(f"Human approved: {result.metrics.human_approval}")
    print(f"Privacy preserved: {result.metrics.privacy_preserved}")
    print(f"Modules used: {', '.join(result.modules_used)}")

asyncio.run(main())
```

## Features

### Graceful Degradation
- Pipeline automatically detects available modules
- Falls back gracefully if optional dependencies are missing
- Logs which modules are available at initialization

### Progressive Enhancement
- Start with minimal functionality (v10)
- Add capabilities incrementally (v11-v20)
- Quality score improves with more modules (0.80 → 0.95)

### Comprehensive Metrics
- Execution time tracking
- Safety score monitoring
- Explainability assessment
- Privacy verification
- Human approval tracking

## Testing

### Minimal Tests (No NumPy Required)
```bash
# Test core functionality (v10-v12 only)
python -m pytest tests/test_basic_ai_pipeline_minimal.py -v
```

### Full Test Suite (Requires NumPy)
```bash
# Install test dependencies
pip install numpy scipy scikit-learn pytest

# Run comprehensive tests
python -m pytest tests/test_basic_ai_integration.py -v
```

## Logging

The pipeline provides detailed logging at multiple levels:

```python
import logging

# Enable INFO logging to see module availability
logging.basicConfig(level=logging.INFO)

# Enable WARNING logging for missing dependencies (default)
logging.basicConfig(level=logging.WARNING)

# Enable DEBUG logging for detailed execution tracking
logging.basicConfig(level=logging.DEBUG)
```

Example output:
```
INFO:src.integration.basic_ai_pipeline:Initializing Basic AI Pipeline (v10-v20)...
WARNING:src.integration.basic_ai_pipeline:Neurosymbolic module not available (missing dependencies)
WARNING:src.integration.basic_ai_pipeline:Quantum ML module not available (missing dependencies)
INFO:src.integration.basic_ai_pipeline:Basic AI Pipeline initialized with 5 modules: v10 (Deployment), v11 (Federated), v12 (Autonomous), v13 (Explainable AI), v20 (Human-AI Collab)
```

## Troubleshooting

### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'numpy'`

**Solution**: Install numpy for full functionality:
```bash
pip install numpy
```

Or use core modules only (v10-v12) which don't require numpy.

### Pipeline Initialization Issues

**Problem**: Pipeline fails to initialize

**Solution**: Check logs to see which modules are available:
```python
import logging
logging.basicConfig(level=logging.INFO)

from src.integration.basic_ai_pipeline import BasicAIPipeline
pipeline = BasicAIPipeline()
# Check logs for module availability
```

## Comparison with Advanced AI Pipeline

| Feature | Basic AI Pipeline (v10-v20) | Advanced AI Pipeline (v22-v27) |
|---------|----------------------------|-------------------------------|
| **Focus** | Core AI capabilities | Research-level AI systems |
| **Modules** | 11 modules | 6 modules |
| **Dependencies** | Minimal (stdlib + optional numpy) | NumPy required |
| **Quality Range** | 0.80 → 0.95 | 0.85 → 0.99 |
| **Use Cases** | Production systems, deployment | Research, cosmic-scale AI |
| **Maturity** | Production-ready | Experimental |

## See Also

- **Advanced AI Pipeline**: `src/integration/pipeline.py` (v22-v27)
- **Integration Documentation**: `INTEGRATION_IMPROVEMENTS.md`
- **Version History**: `COMPLETE_VERSION_HISTORY.md`

## Contributing

When adding new modules to the pipeline:

1. Add optional import with try/except
2. Add corresponding HAS_* flag
3. Update __init__ to use the flag
4. Add to available_modules list
5. Create corresponding operation mode
6. Add tests (both minimal and full)
7. Update this README

## License

Part of DATEN20 Document Management System.
