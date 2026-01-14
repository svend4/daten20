# End-to-End (E2E) Tests

This directory contains end-to-end tests that verify complete user workflows from start to finish, simulating real-world usage scenarios of the Document Management System.

## Overview

E2E tests differ from unit and integration tests:
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **E2E Tests**: Test complete user workflows involving multiple components, real file I/O, and database operations

## Test Files

### 1. `test_document_processing_workflow.py`
Tests the complete document processing pipeline from upload to export.

**Workflows Covered:**
- ✅ Complete text document workflow (upload → parse → NER → classify → store → export)
- ✅ Batch processing multiple documents
- ✅ Document update workflow
- ✅ Document search workflow

**Key Features:**
- Real file I/O operations
- Database interactions (DocumentDatabase)
- ML/AI processing (NER, classification)
- Multi-format export (JSON, TXT)

### 2. `test_document_comparison_workflow.py`
Tests document comparison and similarity analysis workflows.

**Workflows Covered:**
- ✅ Similar documents comparison with similarity metrics
- ✅ Different documents comparison verification
- ✅ Version comparison workflow (tracking changes across versions)
- ✅ Batch comparison workflow (similarity matrix for multiple documents)

**Key Features:**
- Similarity scoring algorithms
- Version history tracking
- Batch comparison operations
- Comprehensive comparison reports

### 3. `test_document_anonymization_workflow.py`
Tests GDPR/HIPAA-compliant document anonymization workflows.

**Workflows Covered:**
- ✅ PII detection and anonymization
- ✅ Reversible anonymization (with secure mapping)
- ✅ Batch anonymization of multiple documents
- ✅ Compliance verification workflow

**Key Features:**
- PII detection (emails, phones, SSNs, dates)
- Secure anonymization with mapping
- Compliance reporting
- Reversible de-anonymization

### 4. `test_document_merge_split_workflow.py`
Tests document merging and splitting operations.

**Workflows Covered:**
- ✅ Simple merge workflow (multiple documents → one)
- ✅ Document split workflow (one document → multiple parts)
- ✅ Merge-split roundtrip (verify content preservation)
- ✅ Smart merge with metadata preservation
- ✅ Conditional split (by markers or size)

**Key Features:**
- Multiple merge strategies
- Various split conditions
- Metadata preservation
- Content integrity verification

## Running E2E Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Specific Test File
```bash
pytest tests/e2e/test_document_processing_workflow.py -v
```

### Run Specific Test
```bash
pytest tests/e2e/test_document_processing_workflow.py::TestDocumentProcessingWorkflow::test_complete_text_document_workflow -v
```

### Run with Output
```bash
pytest tests/e2e/ -v -s
```

### Run with Coverage
```bash
pytest tests/e2e/ --cov=src --cov-report=html
```

## Test Environment

E2E tests use temporary directories for:
- Document uploads
- Processing outputs
- Database files
- Reports and exports

All test artifacts are automatically cleaned up after each test.

## Test Fixtures

Common fixtures used across E2E tests:

```python
@pytest.fixture(autouse=True)
def setup(self):
    """Set up test environment with temporary directories"""
    self.test_dir = tempfile.mkdtemp()
    # Create test directories
    yield
    # Cleanup
    shutil.rmtree(self.test_dir)
```

## Key Test Patterns

### 1. Complete Workflow Pattern
```python
def test_complete_workflow(self):
    # Step 1: Setup (create test data)
    # Step 2: Process (run operations)
    # Step 3: Verify (check results)
    # Step 4: Report (generate outputs)
```

### 2. Roundtrip Pattern
```python
def test_roundtrip(self):
    # Create original → Transform → Reverse → Verify matches original
```

### 3. Batch Operations Pattern
```python
def test_batch_operations(self):
    # Create multiple items → Process all → Verify all → Report
```

## Expected Outcomes

All E2E tests should:
- ✅ Use real file system operations (no mocks)
- ✅ Test complete workflows from start to finish
- ✅ Verify data integrity throughout the pipeline
- ✅ Generate reports and validate outputs
- ✅ Clean up all temporary resources
- ✅ Handle errors gracefully
- ✅ Provide detailed output for debugging

## Test Coverage

Current E2E test coverage:

| Workflow Type | Tests | Status |
|---------------|-------|--------|
| Document Processing | 4 | ✅ Complete |
| Document Comparison | 4 | ✅ Complete |
| Document Anonymization | 4 | ✅ Complete |
| Document Merge/Split | 6 | ✅ Complete |
| **Total** | **18** | **✅ Complete** |

## Adding New E2E Tests

When adding new E2E tests:

1. **Identify the Complete Workflow**
   - What is the user's goal?
   - What are all the steps involved?

2. **Create Test Class**
   ```python
   class TestNewWorkflow:
       @pytest.fixture(autouse=True)
       def setup(self):
           # Setup temporary environment
           yield
           # Cleanup
   ```

3. **Write Test Methods**
   - One test per complete workflow
   - Follow the Step 1-4 pattern
   - Add assertions at each step

4. **Document the Test**
   - Add docstring explaining the workflow
   - List all steps clearly
   - Document expected outcomes

5. **Update This README**
   - Add to the test files list
   - Update coverage table

## Debugging E2E Tests

### View Detailed Output
```bash
pytest tests/e2e/ -v -s --tb=short
```

### Run Single Test in Debug Mode
```bash
pytest tests/e2e/test_document_processing_workflow.py::TestDocumentProcessingWorkflow::test_complete_text_document_workflow -v -s --pdb
```

### Preserve Test Artifacts
Temporarily comment out the cleanup in fixture to inspect generated files:
```python
# shutil.rmtree(self.test_dir, ignore_errors=True)
print(f"Test artifacts preserved in: {self.test_dir}")
```

## Performance Considerations

E2E tests are slower than unit tests because they:
- Perform real file I/O
- Use actual databases
- Run ML/AI models
- Generate reports

**Best Practices:**
- Keep E2E tests focused on critical workflows
- Use integration tests for component interactions
- Use unit tests for detailed logic testing
- Run E2E tests in CI/CD pipeline

## Continuous Integration

E2E tests are run automatically in CI/CD pipeline:
- On pull requests
- On main branch commits
- On release tags

GitHub Actions workflow: `.github/workflows/ci.yml`

## Success Criteria

E2E tests pass when:
- ✅ All workflow steps complete successfully
- ✅ Output files are created and valid
- ✅ Data integrity is maintained
- ✅ Reports are accurate
- ✅ Cleanup is successful
- ✅ No errors or warnings

## Troubleshooting

### Common Issues

**Issue: Tests fail with file not found**
```
Solution: Check that test documents are created before use
```

**Issue: Database errors**
```
Solution: Ensure database is properly initialized and closed in fixtures
```

**Issue: Cleanup fails**
```
Solution: Add ignore_errors=True to shutil.rmtree() calls
```

**Issue: ML/AI models not loading**
```
Solution: Add try-except blocks with fallback behavior
```

## Related Documentation

- [Unit Tests](../unit/README.md)
- [Integration Tests](../integration/README.md)
- [Performance Tests](../performance/README.md)
- [Test Fixtures](../fixtures/README.md)

## Contact

For questions or issues with E2E tests:
- Check existing issues on GitHub
- Review test documentation
- Contact the development team

---

**Last Updated:** 2026-01-14
**Status:** ✅ Complete (18 E2E tests covering all major workflows)
