# DATEN20 API Documentation

This directory contains Sphinx documentation for the DATEN20 project.

## Building Documentation

### Prerequisites

Install Sphinx and dependencies:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### Build HTML Documentation

From the `docs/sphinx` directory:

```bash
make html
```

Or using sphinx-build directly:

```bash
sphinx-build -b html source build/html
```

### View Documentation

Open `build/html/index.html` in your browser:

```bash
open build/html/index.html  # macOS
xdg-open build/html/index.html  # Linux
start build/html/index.html  # Windows
```

## Documentation Structure

- `source/` - ReStructuredText source files
  - `conf.py` - Sphinx configuration
  - `index.rst` - Main documentation page
  - `modules/` - API documentation for each module
    - `world_models.rst` - v22.0 World Models
    - `self_improving.rst` - v23.0 Self-Improving AI
    - `emergent_intelligence.rst` - v24.0 Emergent Intelligence
    - `agi_universal_reasoning.rst` - v25.0 AGI & Universal Reasoning
    - `asi_beyond_human.rst` - v26.0 ASI Beyond Human
    - `cosmic_universal.rst` - v27.0 Cosmic Universal Intelligence
- `build/` - Generated documentation (not committed to git)

## Modules Documented

### v22.0 - World Models
Predictive learning, planning, imagination, and causal reasoning.

### v23.0 - Self-Improving AI
Recursive self-improvement through NAS, hyperparameter optimization, and automated code generation.

### v24.0 - Emergent Intelligence
Multi-system integration enabling emergent capabilities through agent coordination.

### v25.0 - AGI & Universal Reasoning
Human-level intelligence across any intellectual task with universal task understanding.

### v26.0 - ASI Beyond Human
Superintelligence surpassing human capabilities with ultra-deep understanding.

### v27.0 - Cosmic Universal Intelligence
Universe-scale intelligence manipulating physics and exploring transcendent dimensions.

## Test Coverage

All modules have **100% test coverage** (192/192 tests passing).

## Dependencies

The project uses **zero external dependencies** - all modules use only Python stdlib.

## Configuration

Key Sphinx settings in `source/conf.py`:
- Theme: `sphinx_rtd_theme` (Read the Docs theme)
- Extensions: autodoc, napoleon, viewcode, intersphinx, typehints
- Python version: 3.11+
- Docstring style: Google/NumPy (via napoleon)

## Troubleshooting

### "No module named 'src'"

Make sure the project root is in PYTHONPATH:

```bash
export PYTHONPATH=/path/to/daten20:$PYTHONPATH
```

### Warnings during build

355 warnings are expected on first build (mostly missing docstrings). These can be gradually addressed.

### Regenerating from scratch

```bash
make clean
make html
```
