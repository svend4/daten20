#!/usr/bin/env python3
"""
Progress Bar Usage Examples
============================

Demonstrates how to use the progress bar utilities in various scenarios.

Author: Document Management System
Version: 1.0.0
"""

import time
import random
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.progress import (
    ProgressBar,
    progress_iterator,
    progress_map,
    MultiProgress,
    FileProgressBar,
    StepProgress,
    create_progress
)


def example_1_basic_progress():
    """Example 1: Basic progress bar"""
    print("\n=== Example 1: Basic Progress Bar ===")

    with ProgressBar(total=100, desc="Processing items", unit="item") as pbar:
        for i in range(100):
            # Simulate work
            time.sleep(0.02)
            pbar.update(1)

    print("✓ Complete!")


def example_2_iterator_wrapper():
    """Example 2: Wrap an iterator with progress"""
    print("\n=== Example 2: Progress Iterator ===")

    items = range(50)

    for item in progress_iterator(items, desc="Processing", unit="item", colour="blue"):
        # Simulate work
        time.sleep(0.03)
        # Process item here
        pass

    print("✓ Complete!")


def example_3_progress_map():
    """Example 3: Apply function with progress"""
    print("\n=== Example 3: Progress Map ===")

    def process_item(x):
        """Simulate processing"""
        time.sleep(0.02)
        return x * 2

    items = range(50)
    results = progress_map(
        process_item,
        items,
        desc="Doubling numbers",
        unit="number",
        colour="green"
    )

    print(f"✓ Processed {len(results)} items")
    print(f"  First 10 results: {results[:10]}")


def example_4_nested_progress():
    """Example 4: Nested progress bars"""
    print("\n=== Example 4: Nested Progress Bars ===")

    mp = MultiProgress()

    # Main progress bar
    with mp.add_bar(total=5, desc="Main task", position=0, colour="cyan") as main_bar:
        for i in range(5):
            # Sub progress bar
            with mp.add_bar(total=10, desc=f"  Subtask {i+1}", position=1, colour="yellow") as sub_bar:
                for j in range(10):
                    time.sleep(0.01)
                    sub_bar.update(1)

            main_bar.update(1)

    mp.close_all()
    print("✓ All tasks complete!")


def example_5_file_progress():
    """Example 5: File processing with size tracking"""
    print("\n=== Example 5: File Progress with Size ===")

    # Simulate files with sizes
    files = [
        {"name": f"file_{i}.pdf", "size": random.randint(100_000, 10_000_000)}
        for i in range(20)
    ]

    total_size = sum(f["size"] for f in files)

    with FileProgressBar(
        total_files=len(files),
        total_size=total_size,
        desc="Processing files"
    ) as fpbar:
        for file_info in files:
            # Simulate processing
            time.sleep(0.05)

            # Update with file size
            fpbar.update(n=1, bytes_processed=file_info["size"])

    print("✓ All files processed!")


def example_6_step_progress():
    """Example 6: Multi-step process"""
    print("\n=== Example 6: Step-by-Step Progress ===")

    steps = [
        "Initialize",
        "Load data",
        "Process",
        "Validate",
        "Export",
        "Cleanup"
    ]

    with StepProgress(steps, desc="Pipeline") as spbar:
        for step in steps:
            spbar.next_step()
            # Simulate work
            time.sleep(0.3)

            # Update status mid-step
            if step == "Process":
                spbar.set_step_status("analyzing entities")
                time.sleep(0.2)
                spbar.set_step_status("extracting relations")
                time.sleep(0.2)

    print("✓ Pipeline complete!")


def example_7_batch_document_processing():
    """Example 7: Realistic document processing scenario"""
    print("\n=== Example 7: Batch Document Processing ===")

    # Simulate document files
    documents = [f"document_{i:03d}.pdf" for i in range(30)]

    mp = MultiProgress()

    # Overall progress
    with mp.add_bar(total=len(documents), desc="Documents", position=0, colour="blue") as doc_bar:
        for doc_idx, doc in enumerate(documents):
            # Processing steps for each document
            steps = ["Parse", "NER", "Classify", "Extract"]

            with mp.add_bar(total=len(steps), desc=f"  {doc}", position=1, colour="green") as step_bar:
                for step in steps:
                    # Simulate step processing
                    time.sleep(0.02)
                    step_bar.set_description(f"  {doc}: {step}")
                    step_bar.update(1)

            doc_bar.update(1)

    mp.close_all()
    print("✓ All documents processed!")


def example_8_error_handling():
    """Example 8: Progress with error handling"""
    print("\n=== Example 8: Progress with Error Handling ===")

    items = range(30)
    errors = []
    successes = 0

    for i in progress_iterator(items, desc="Processing with errors", unit="item", colour="yellow"):
        try:
            # Simulate random failures
            if random.random() < 0.15:  # 15% failure rate
                raise ValueError(f"Error processing item {i}")

            # Simulate work
            time.sleep(0.03)
            successes += 1

        except Exception as e:
            errors.append({"item": i, "error": str(e)})

    print(f"\n✓ Processing complete!")
    print(f"  Successes: {successes}")
    print(f"  Errors: {len(errors)}")


def example_9_conditional_progress():
    """Example 9: Conditional progress (verbose mode)"""
    print("\n=== Example 9: Conditional Progress (Silent Mode) ===")

    verbose = False  # Silent mode

    items = range(50)

    # No progress bar in silent mode
    if verbose:
        iterator = progress_iterator(items, desc="Processing")
    else:
        iterator = items

    for item in iterator:
        # Process silently
        time.sleep(0.01)

    print("✓ Silent processing complete!")


def example_10_custom_format():
    """Example 10: Custom progress bar styling"""
    print("\n=== Example 10: Custom Styling ===")

    # Different colours for different stages
    stages = [
        ("Parsing", "blue", 20),
        ("Analyzing", "cyan", 15),
        ("Processing", "green", 25),
        ("Exporting", "yellow", 10)
    ]

    for stage_name, colour, count in stages:
        for i in progress_iterator(
            range(count),
            desc=f"{stage_name}",
            unit="file",
            colour=colour
        ):
            time.sleep(0.05)

    print("✓ All stages complete!")


def run_all_examples():
    """Run all examples"""
    print("=" * 70)
    print("PROGRESS BAR EXAMPLES - Document Management System")
    print("=" * 70)

    examples = [
        example_1_basic_progress,
        example_2_iterator_wrapper,
        example_3_progress_map,
        example_4_nested_progress,
        example_5_file_progress,
        example_6_step_progress,
        example_7_batch_document_processing,
        example_8_error_handling,
        example_9_conditional_progress,
        example_10_custom_format
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
            time.sleep(0.5)  # Brief pause between examples
        except KeyboardInterrupt:
            print("\n\n⚠ Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Example {i} failed: {e}")

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Progress bar examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=range(1, 11),
        help="Run specific example (1-10)"
    )

    args = parser.parse_args()

    if args.example:
        # Run specific example
        examples = {
            1: example_1_basic_progress,
            2: example_2_iterator_wrapper,
            3: example_3_progress_map,
            4: example_4_nested_progress,
            5: example_5_file_progress,
            6: example_6_step_progress,
            7: example_7_batch_document_processing,
            8: example_8_error_handling,
            9: example_9_conditional_progress,
            10: example_10_custom_format
        }
        examples[args.example]()
    else:
        # Run all examples
        run_all_examples()


if __name__ == "__main__":
    main()
