# Integration Tests

## Overview

Integration tests verify end-to-end functionality by executing actual CLI commands (not mocks). These tests:

- ✅ Test real file I/O operations
- ✅ Verify complete workflows
- ✅ Measure actual code coverage
- ✅ Test component integration
- ✅ Use temporary files and directories

## Running Integration Tests

### Run all integration tests:
```bash
pytest tests/integration/ -v
```

### Run specific test file:
```bash
pytest tests/integration/test_cli_integration.py -v
```

### Run only integration tests (using marker):
```bash
pytest -m integration -v
```

### Run with coverage:
```bash
pytest tests/integration/ -v --cov=. --cov-report=html
```

## Test Categories

### 1. CLI Application Tests
- `TestDocProcessorIntegration` - Document processing
- `TestDocComparatorIntegration` - Document comparison
- `TestDocAnonymizerIntegration` - Data anonymization
- `TestDocQualityIntegration` - Quality assessment
- `TestDocMergerIntegration` - Document merging
- `TestDocSplitterIntegration` - Document splitting
- `TestDocMasterIntegration` - Control panel

### 2. End-to-End Workflows
- `TestEndToEndWorkflows` - Complete multi-step workflows

## Writing New Integration Tests

### Template:
```python
import subprocess
from pathlib import Path
import pytest

@pytest.mark.integration
class TestMyAppIntegration:
    """Integration tests for my-app.py"""

    def test_basic_functionality(self, tmp_path):
        """Test basic functionality"""
        # Create test data
        input_file = tmp_path / "input.txt"
        input_file.write_text("Test content")

        # Run CLI command
        result = subprocess.run(
            ['python', 'my-app.py', str(input_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Verify results
        assert result.returncode == 0
        assert "expected output" in result.stdout
```

### Best Practices:

1. **Use tmp_path fixture** - Pytest provides temporary directories automatically
2. **Set timeouts** - Prevent tests from hanging (default: 10 seconds)
3. **Clean up** - tmp_path is automatically cleaned up after tests
4. **Check return codes** - Always verify result.returncode
5. **Test edge cases** - Empty files, large files, special characters
6. **Test error handling** - Invalid inputs, missing files, etc.

## Fixtures Available

### Pytest Built-in Fixtures:
- `tmp_path` - Temporary directory (Path object)
- `tmpdir` - Temporary directory (py.path.local object)
- `capsys` - Capture stdout/stderr
- `monkeypatch` - Modify environment variables

### Custom Fixtures:
Add custom fixtures in `tests/integration/conftest.py`:

```python
import pytest

@pytest.fixture
def sample_document(tmp_path):
    """Create a sample document for testing"""
    doc = tmp_path / "sample.txt"
    doc.write_text("Sample document content")
    return doc
```

## Troubleshooting

### Tests timing out:
- Increase timeout value: `timeout=30`
- Check if application is hanging
- Verify all required dependencies are installed

### File not found errors:
- Ensure CLI scripts are in project root
- Check file paths are correct
- Verify tmp_path is being used properly

### Permission errors:
- Check file permissions
- Ensure output directories are writable
- Verify tmp_path is accessible

### Import errors:
- Install all required dependencies
- Check PYTHONPATH is set correctly
- Verify virtual environment is activated

## Coverage Goals

Integration tests aim to achieve:
- **70%+** coverage for CLI applications
- **80%+** coverage for core modules
- **60%+** coverage for AI/ML modules

Current coverage can be viewed in `htmlcov/index.html` after running:
```bash
pytest tests/integration/ --cov=. --cov-report=html
```

## CI/CD Integration

Integration tests run automatically in GitHub Actions:
- Triggered on push to main, develop, and feature branches
- Run across Python 3.9, 3.10, and 3.11
- Results visible in Actions tab
- Coverage reports uploaded to Codecov

## Performance Considerations

Integration tests are slower than unit tests because they:
- Execute actual CLI commands
- Perform real file I/O
- Run complete application logic

Typical execution times:
- Single integration test: 1-5 seconds
- Full integration test suite: 2-5 minutes
- With coverage: 3-7 minutes

## Next Steps

1. Add more integration tests for remaining CLI tools
2. Increase coverage to 70%+
3. Add performance benchmarks
4. Create E2E tests for web interfaces
5. Add database integration tests

## Questions?

If you have questions about integration tests:
1. Check pytest documentation: https://docs.pytest.org/
2. Review existing test examples
3. Open an issue on GitHub
4. Ask in team chat
