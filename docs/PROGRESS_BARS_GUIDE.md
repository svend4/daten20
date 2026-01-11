# 📊 Progress Bars Guide - Document Management System

## Overview

Professional progress bar system using `tqdm` with consistent styling and advanced features.

**Module:** `src/utils/progress.py`
**Examples:** `examples/progress_examples.py`
**Version:** 1.0.0
**Date:** 2026-01-11

---

## 🎯 Features

### Core Capabilities
- ✅ **Automatic ETA calculation** - shows estimated time remaining
- ✅ **Speed/rate display** - items per second, files per second
- ✅ **Clean terminal output** - professional formatting
- ✅ **Nested progress bars** - for multi-level operations
- ✅ **Custom colours** - green, blue, red, cyan, yellow, etc.
- ✅ **File size tracking** - shows bytes/MB/GB processed
- ✅ **Step-by-step progress** - for multi-stage pipelines
- ✅ **Error handling** - graceful failure handling
- ✅ **Silent mode** - disable progress for scripts

---

## 📚 Usage Guide

### 1. Basic Progress Bar

```python
from src.utils.progress import ProgressBar

# Simple progress bar
with ProgressBar(total=100, desc="Processing items", unit="item") as pbar:
    for i in range(100):
        # Do work
        process_item(i)
        pbar.update(1)
```

**Output:**
```
Processing items: 100%|██████████| 100/100 [00:02<00:00, 48.92item/s]
```

---

### 2. Iterator Wrapper

```python
from src.utils.progress import progress_iterator

items = range(100)

for item in progress_iterator(items, desc="Processing", unit="item", colour="blue"):
    process(item)
```

**Output:**
```
Processing: 100%|██████████| 100/100 [00:02<00:00, 50.00item/s]
```

---

### 3. Progress Map (Apply Function)

```python
from src.utils.progress import progress_map

def process_item(x):
    return x * 2

items = range(100)
results = progress_map(
    process_item,
    items,
    desc="Doubling numbers",
    unit="number"
)
```

**Output:**
```
Doubling numbers: 100%|██████████| 100/100 [00:02<00:00, 50.00number/s]
```

---

### 4. Nested Progress Bars

```python
from src.utils.progress import MultiProgress

mp = MultiProgress()

# Main progress bar (position 0 = top)
with mp.add_bar(total=10, desc="Main task", position=0, colour="cyan") as main:
    for i in range(10):
        # Sub progress bar (position 1 = nested)
        with mp.add_bar(total=100, desc=f"Subtask {i+1}", position=1, colour="yellow") as sub:
            for j in range(100):
                process(i, j)
                sub.update(1)

        main.update(1)

mp.close_all()
```

**Output:**
```
Main task: 50%|█████     | 5/10 [00:05<00:05, 1.00it/s]
  Subtask 6: 100%|██████████| 100/100 [00:00<00:00, 500.00it/s]
```

---

### 5. File Processing with Size Tracking

```python
from src.utils.progress import FileProgressBar

files = [
    {"path": "doc1.pdf", "size": 5_000_000},
    {"path": "doc2.pdf", "size": 3_500_000},
    # ...
]

total_size = sum(f["size"] for f in files)

with FileProgressBar(
    total_files=len(files),
    total_size=total_size,
    desc="Processing files"
) as fpbar:
    for file_info in files:
        process_file(file_info["path"])
        fpbar.update(n=1, bytes_processed=file_info["size"])
```

**Output:**
```
Processing files: 100%|██████████| 20/20 [00:05<00:00, 4.00file/s, 100.2MB/100.2MB]
```

---

### 6. Step-by-Step Pipeline Progress

```python
from src.utils.progress import StepProgress

steps = ["Parse", "Analyze", "Extract", "Export"]

with StepProgress(steps, desc="Pipeline") as spbar:
    for step in steps:
        spbar.next_step()

        # Do work for this step
        execute_step(step)

        # Update status mid-step if needed
        if step == "Analyze":
            spbar.set_step_status("extracting entities")
```

**Output:**
```
Pipeline: Analyze - extracting entities: 50%|█████     | 2/4 [00:02<00:02, 1.00step/s]
```

---

### 7. Batch Document Processing (Real-World Example)

```python
from src.utils.progress import MultiProgress
from pathlib import Path

documents = list(Path("documents/").glob("*.pdf"))

mp = MultiProgress()

# Overall document progress
with mp.add_bar(total=len(documents), desc="Documents", position=0, colour="blue") as doc_bar:
    for doc in documents:
        steps = ["Parse", "NER", "Classify", "Extract Relations"]

        # Steps for each document
        with mp.add_bar(total=len(steps), desc=f"  {doc.name}", position=1, colour="green") as step_bar:
            for step in steps:
                step_bar.set_description(f"  {doc.name}: {step}")

                # Execute step
                execute_pipeline_step(doc, step)

                step_bar.update(1)

        doc_bar.update(1)

mp.close_all()
```

**Output:**
```
Documents: 75%|███████▌  | 15/20 [00:45<00:15, 3.00s/file]
  doc_015.pdf: Classify: 50%|█████     | 2/4 [00:01<00:01, 2.00step/s]
```

---

### 8. Error Handling with Progress

```python
from src.utils.progress import progress_iterator

errors = []
successes = 0

for item in progress_iterator(items, desc="Processing", unit="item", colour="yellow"):
    try:
        process(item)
        successes += 1
    except Exception as e:
        errors.append({"item": item, "error": str(e)})

print(f"Successes: {successes}, Errors: {len(errors)}")
```

---

### 9. Silent Mode (Conditional Progress)

```python
from src.utils.progress import progress_iterator, silent_progress

# Choose based on verbosity
verbose = args.verbose

if verbose:
    iterator = progress_iterator(items, desc="Processing")
else:
    iterator = silent_progress(items)  # No progress bar

for item in iterator:
    process(item)
```

Or using helper function:

```python
from src.utils.progress import get_progress_function

progress_func = get_progress_function(verbose=args.verbose)

for item in progress_func(items, desc="Processing"):
    process(item)
```

---

### 10. Custom Colours

Available colours:
- `green` (default for success)
- `blue` (default for files)
- `cyan` (default for steps)
- `yellow` (default for warnings)
- `red` (for errors)
- `magenta`
- `white`

```python
from src.utils.progress import progress_iterator

# Different colours for different stages
for file in progress_iterator(files, desc="Parsing", colour="blue"):
    parse(file)

for file in progress_iterator(files, desc="Analyzing", colour="cyan"):
    analyze(file)

for file in progress_iterator(files, desc="Exporting", colour="green"):
    export(file)
```

---

## 🔧 Advanced Configuration

### Custom Format

```python
from tqdm import tqdm

pbar = tqdm(
    total=100,
    desc="Custom",
    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
)
```

### Position for Nested Bars

- `position=0` - Top-level progress bar
- `position=1` - First nested level
- `position=2` - Second nested level
- etc.

### Leave vs No Leave

```python
# Keep progress bar after completion
with ProgressBar(total=100, leave=True) as pbar:
    ...

# Remove progress bar after completion
with ProgressBar(total=100, leave=False) as pbar:
    ...
```

---

## 📋 Integration Examples

### In doc-batch-processor.py

```python
from src.utils.progress import FileProgressBar

with FileProgressBar(
    total_files=len(files),
    total_size=total_size,
    desc="Processing documents"
) as fpbar:
    for file_path in files:
        result = process_document(file_path)
        fpbar.update(n=1, bytes_processed=os.path.getsize(file_path))
```

### In doc-anonymizer.py

```python
from src.utils.progress import StepProgress

steps = ["Scan PII", "Anonymize", "Validate", "Export"]

with StepProgress(steps, desc="Anonymization") as spbar:
    for step in steps:
        spbar.next_step()
        execute_anonymization_step(step)
```

### In doc-quality.py

```python
from src.utils.progress import MultiProgress

mp = MultiProgress()

dimensions = ["Completeness", "Accuracy", "Consistency", "Readability", "Timeliness"]

with mp.add_bar(total=len(documents), desc="Documents", position=0) as doc_bar:
    for doc in documents:
        with mp.add_bar(total=len(dimensions), desc="  Quality checks", position=1) as dim_bar:
            for dimension in dimensions:
                score = check_dimension(doc, dimension)
                dim_bar.update(1)

        doc_bar.update(1)

mp.close_all()
```

---

## 🎨 Best Practices

### 1. Use Descriptive Names
```python
# Good
desc="Processing documents"
unit="doc"

# Bad
desc="Processing"
unit="it"
```

### 2. Choose Appropriate Colours
```python
# Parsing stage - blue
progress_iterator(files, desc="Parsing", colour="blue")

# Analysis stage - cyan
progress_iterator(files, desc="Analyzing", colour="cyan")

# Success - green
progress_iterator(files, desc="Exporting", colour="green")

# Errors/warnings - yellow or red
progress_iterator(files, desc="Validating", colour="yellow")
```

### 3. Use Context Managers
```python
# Good - automatically closes
with ProgressBar(total=100, desc="Processing") as pbar:
    for item in items:
        process(item)
        pbar.update(1)

# Bad - manual management
pbar = tqdm(total=100)
for item in items:
    process(item)
    pbar.update(1)
pbar.close()  # Easy to forget!
```

### 4. Nested Bars - Use Positions
```python
# Always use position parameter for nested bars
with mp.add_bar(..., position=0) as main:  # Top level
    with mp.add_bar(..., position=1) as sub:  # Nested
        ...
```

### 5. File Processing - Track Size
```python
# Include file size tracking for better UX
with FileProgressBar(total_files=len(files), total_size=total_size) as fpbar:
    ...
```

---

## 🚀 Performance Tips

### 1. Update Frequency
```python
# Update less frequently for large datasets
if i % 10 == 0:  # Update every 10 items
    pbar.update(10)
```

### 2. Disable for Scripts
```python
# Disable progress bars in non-interactive environments
disable = not sys.stdout.isatty()

with ProgressBar(total=100, disable=disable) as pbar:
    ...
```

### 3. Use Appropriate Data Structures
```python
# If you know the total, specify it
with ProgressBar(total=len(items)) as pbar:  # Better
    ...

# Instead of
with ProgressBar() as pbar:  # No total = no ETA
    ...
```

---

## 📊 Output Examples

### Basic Progress
```
Processing: 100%|██████████| 1000/1000 [00:20<00:00, 50.00it/s]
```

### File Progress with Size
```
Processing files: 100%|██████████| 50/50 [00:30<00:00, 1.67file/s, 250.5MB/250.5MB]
```

### Step Progress
```
Pipeline: Export: 100%|██████████| 5/5 [00:45<00:00, 9.00s/step]
```

### Nested Progress
```
Documents: 75%|███████▌  | 15/20 [00:45<00:15, 3.00s/doc]
  doc_015.pdf: NER: 50%|█████     | 2/4 [00:01<00:01, 2.00step/s]
```

---

## 🧪 Testing

Run examples:
```bash
# All examples
python examples/progress_examples.py

# Specific example
python examples/progress_examples.py --example 1
python examples/progress_examples.py --example 7
```

---

## 📖 API Reference

### Classes

#### ProgressBar
```python
ProgressBar(
    total: Optional[int] = None,
    desc: str = "Processing",
    unit: str = "item",
    disable: bool = False,
    leave: bool = True,
    position: int = 0,
    colour: Optional[str] = None
)
```

#### FileProgressBar
```python
FileProgressBar(
    total_files: int,
    total_size: int = 0,
    desc: str = "Processing files",
    disable: bool = False
)
```

#### StepProgress
```python
StepProgress(
    steps: list,
    desc: str = "Processing",
    disable: bool = False
)
```

#### MultiProgress
```python
MultiProgress()
```

### Functions

#### progress_iterator
```python
progress_iterator(
    iterable: Iterable,
    desc: str = "Processing",
    unit: str = "item",
    total: Optional[int] = None,
    disable: bool = False,
    colour: str = "green"
) -> Iterable
```

#### progress_map
```python
progress_map(
    func: Callable,
    iterable: Iterable,
    desc: str = "Processing",
    unit: str = "item",
    total: Optional[int] = None,
    disable: bool = False,
    colour: str = "green"
) -> list
```

---

## ✅ Checklist for Integration

When adding progress bars to an application:

- [ ] Choose appropriate progress bar type (basic, file, step, nested)
- [ ] Use descriptive `desc` parameter
- [ ] Choose appropriate `unit` ("file", "doc", "item", etc.)
- [ ] Set appropriate `colour` for the operation
- [ ] Use context managers (`with` statement)
- [ ] Handle errors gracefully
- [ ] Test with small and large datasets
- [ ] Add `--no-progress` flag for silent mode
- [ ] Document usage in application help text

---

## 🎓 Conclusion

Progress bars dramatically improve user experience by:
- ✅ Showing operation is in progress
- ✅ Estimating time remaining
- ✅ Providing visual feedback
- ✅ Making applications feel responsive
- ✅ Helping users plan their time

**Recommended for all batch operations and long-running tasks!**

---

**Author:** Document Management System
**Date:** 2026-01-11
**Version:** 1.0.0
**Module:** `src/utils/progress.py`
