# Enhanced Error Messages Guide

## Overview

The enhanced error messages module provides helpful, actionable error messages with suggestions for fixing common issues.

## Features

- ✅ Context-aware error messages
- ✅ Actionable suggestions
- ✅ Links to documentation
- ✅ Common troubleshooting steps
- ✅ Beautiful formatting

## Usage

### Import

\`\`\`python
from src.utils.error_messages import (
    FileNotFoundEnhancedError,
    InvalidFormatEnhancedError,
    DependencyMissingEnhancedError,
    ConfigurationEnhancedError,
    DatabaseEnhancedError,
    PermissionEnhancedError
)
\`\`\`

### File Not Found Error

\`\`\`python
try:
    with open(file_path, 'r') as f:
        content = f.read()
except FileNotFoundError:
    raise FileNotFoundEnhancedError(file_path)
\`\`\`

**Output:**
\`\`\`
======================================================================
❌ ERROR: File not found: /path/to/file.txt

💡 SUGGESTION: The path '/path/to/file.txt' is relative. Try using an absolute path:
   Example: /home/user/path/to/file.txt
Or ensure you're running from the correct directory.

📖 DOCUMENTATION: https://docs.example.com/troubleshooting#file-not-found

📋 CONTEXT:
   • Current directory: /home/user
   • File path: /path/to/file.txt
   • Parent directory exists: False
======================================================================
\`\`\`

### Invalid Format Error

\`\`\`python
if not file_path.endswith(('.pdf', '.docx', '.txt')):
    raise InvalidFormatEnhancedError(
        file_path=file_path,
        expected_formats=['pdf', 'docx', 'txt'],
        detected_format=file_path.split('.')[-1]
    )
\`\`\`

### Missing Dependency Error

\`\`\`python
try:
    import spacy
except ImportError:
    raise DependencyMissingEnhancedError(
        package_name='spacy',
        feature='Named Entity Recognition',
        install_command='pip install spacy && python -m spacy download en_core_web_sm'
    )
\`\`\`

### Configuration Error

\`\`\`python
if 'database_path' not in config:
    raise ConfigurationEnhancedError(
        config_key='database_path',
        config_file='config/default.yml',
        expected_type='string'
    )
\`\`\`

### Database Error

\`\`\`python
try:
    db.connect()
except Exception as e:
    raise DatabaseEnhancedError(
        operation='connection',
        db_path='/path/to/database.db',
        original_error=str(e)
    )
\`\`\`

### Permission Error

\`\`\`python
try:
    with open(output_path, 'w') as f:
        f.write(content)
except PermissionError:
    raise PermissionEnhancedError(
        path=output_path,
        operation='write to'
    )
\`\`\`

## Creating Custom Enhanced Errors

\`\`\`python
from src.utils.error_messages import EnhancedError

class MyCustomError(EnhancedError):
    def __init__(self, detail: str):
        message = f"My custom error: {detail}"
        suggestion = "Try this solution..."
        context = {"Detail": detail}
        
        super().__init__(
            message=message,
            suggestion=suggestion,
            doc_link="https://docs.example.com/my-error",
            context=context
        )
\`\`\`

## Error Templates

For common errors without custom classes:

\`\`\`python
from src.utils.error_messages import get_error_template

template = get_error_template('memory_error')
print(template['message'])
print(template['suggestion'])
\`\`\`

Available templates:
- \`file_empty\`
- \`memory_error\`
- \`timeout\`
- \`api_error\`

## Best Practices

1. **Always provide context**: Include relevant information about what went wrong
2. **Be specific**: Give actionable suggestions, not generic advice
3. **Include examples**: Show exact commands to fix the issue
4. **Link to docs**: Provide documentation links when available
5. **Check before raising**: Verify the error condition before raising

## Migration Guide

### Before
\`\`\`python
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")
\`\`\`

### After
\`\`\`python
if not os.path.exists(file_path):
    raise FileNotFoundEnhancedError(file_path)
\`\`\`

## Examples in Codebase

See these files for usage examples:
- \`doc-processor.py\` - File handling errors
- \`doc-batch-processor.py\` - Batch processing errors
- \`src/core/database.py\` - Database errors
- \`src/core/parser.py\` - Parsing errors
