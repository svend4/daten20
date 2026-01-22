#!/usr/bin/env python3
"""
Test Coverage Analysis Script

Analyzes the codebase to identify modules that lack test coverage.
This provides a static analysis without running tests.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

def find_python_files(directory: str, exclude_patterns: List[str] = None) -> List[Path]:
    """Find all Python files in a directory, excluding certain patterns."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.pytest_cache', 'venv', 'env', '.git']

    python_files = []
    for root, dirs, files in os.walk(directory):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(Path(root) / file)

    return python_files

def extract_module_name(file_path: Path, src_dir: Path) -> str:
    """Extract module name from file path."""
    try:
        relative_path = file_path.relative_to(src_dir)
        module_path = str(relative_path).replace('.py', '').replace('/', '.')
        return module_path
    except ValueError:
        return str(file_path)

def find_test_file_for_module(module_path: Path, tests_dir: Path) -> Path:
    """Find the corresponding test file for a module."""
    # Try different test file naming conventions
    module_name = module_path.stem
    test_names = [
        f"test_{module_name}.py",
        f"{module_name}_test.py",
        f"test_{module_name}_comprehensive.py",
    ]

    # Check in tests/unit directory structure
    relative_path = module_path.parent
    if relative_path != Path('.'):
        # Try to find in corresponding tests/unit subdirectory
        test_dir = tests_dir / 'unit' / relative_path
        if test_dir.exists():
            for test_name in test_names:
                test_file = test_dir / test_name
                if test_file.exists():
                    return test_file

    # Try in tests/unit root
    for test_name in test_names:
        test_file = tests_dir / 'unit' / test_name
        if test_file.exists():
            return test_file

    return None

def count_lines_of_code(file_path: Path) -> Tuple[int, int]:
    """Count total lines and code lines (excluding comments and blank lines)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)
        code_lines = 0

        for line in lines:
            stripped = line.strip()
            # Skip empty lines and comments
            if stripped and not stripped.startswith('#'):
                code_lines += 1

        return total_lines, code_lines
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return 0, 0

def analyze_coverage(src_dir: Path, tests_dir: Path) -> Dict:
    """Analyze test coverage for the codebase."""
    print(f"\n📊 Analyzing test coverage...")
    print(f"Source directory: {src_dir}")
    print(f"Tests directory: {tests_dir}")
    print("-" * 80)

    # Find all source files
    source_files = find_python_files(str(src_dir))
    print(f"\nFound {len(source_files)} Python source files")

    # Analyze coverage
    covered_modules = []
    uncovered_modules = []
    partially_covered_modules = []

    total_source_lines = 0
    total_code_lines = 0
    total_test_lines = 0

    for source_file in source_files:
        # Skip __init__.py files
        if source_file.name == '__init__.py':
            continue

        # Count source file lines
        total_lines, code_lines = count_lines_of_code(source_file)
        total_source_lines += total_lines
        total_code_lines += code_lines

        # Find corresponding test file
        try:
            relative_path = source_file.relative_to(src_dir)
        except ValueError:
            continue

        test_file = find_test_file_for_module(relative_path, tests_dir)

        module_info = {
            'path': str(relative_path),
            'source_file': str(source_file),
            'lines': total_lines,
            'code_lines': code_lines,
            'test_file': None,
            'test_lines': 0
        }

        if test_file and test_file.exists():
            test_total, test_code = count_lines_of_code(test_file)
            total_test_lines += test_total
            module_info['test_file'] = str(test_file)
            module_info['test_lines'] = test_total

            # Classify coverage
            if test_code > code_lines * 0.5:  # Good coverage (tests > 50% of source)
                covered_modules.append(module_info)
            else:  # Partial coverage
                partially_covered_modules.append(module_info)
        else:
            uncovered_modules.append(module_info)

    # Calculate statistics
    total_modules = len(covered_modules) + len(partially_covered_modules) + len(uncovered_modules)
    coverage_percentage = (len(covered_modules) / total_modules * 100) if total_modules > 0 else 0

    return {
        'covered': covered_modules,
        'partially_covered': partially_covered_modules,
        'uncovered': uncovered_modules,
        'stats': {
            'total_modules': total_modules,
            'covered_count': len(covered_modules),
            'partially_covered_count': len(partially_covered_modules),
            'uncovered_count': len(uncovered_modules),
            'coverage_percentage': coverage_percentage,
            'total_source_lines': total_source_lines,
            'total_code_lines': total_code_lines,
            'total_test_lines': total_test_lines
        }
    }

def print_report(analysis: Dict):
    """Print a detailed coverage report."""
    stats = analysis['stats']

    print("\n" + "=" * 80)
    print("📊 TEST COVERAGE ANALYSIS REPORT")
    print("=" * 80)

    print(f"\n📈 Overall Statistics:")
    print(f"  Total modules analyzed: {stats['total_modules']}")
    print(f"  Modules with good coverage: {stats['covered_count']} ({stats['covered_count']/stats['total_modules']*100:.1f}%)")
    print(f"  Modules with partial coverage: {stats['partially_covered_count']} ({stats['partially_covered_count']/stats['total_modules']*100:.1f}%)")
    print(f"  Modules without tests: {stats['uncovered_count']} ({stats['uncovered_count']/stats['total_modules']*100:.1f}%)")
    print(f"\n  Estimated coverage: {stats['coverage_percentage']:.1f}%")

    print(f"\n📏 Code Statistics:")
    print(f"  Total source lines: {stats['total_source_lines']:,}")
    print(f"  Total code lines: {stats['total_code_lines']:,}")
    print(f"  Total test lines: {stats['total_test_lines']:,}")
    print(f"  Test to code ratio: {stats['total_test_lines']/stats['total_code_lines']:.2f}:1" if stats['total_code_lines'] > 0 else "  Test to code ratio: N/A")

    # Print uncovered modules (highest priority)
    if analysis['uncovered']:
        print(f"\n❌ Modules WITHOUT Tests ({len(analysis['uncovered'])}):")
        print("-" * 80)

        # Sort by code lines (descending) - largest modules first
        sorted_uncovered = sorted(analysis['uncovered'], key=lambda x: x['code_lines'], reverse=True)

        for i, module in enumerate(sorted_uncovered[:20], 1):  # Top 20
            print(f"  {i:2d}. {module['path']:60s} ({module['code_lines']:4d} lines)")

    # Print partially covered modules
    if analysis['partially_covered']:
        print(f"\n⚠️  Modules with PARTIAL Coverage ({len(analysis['partially_covered'])}):")
        print("-" * 80)

        sorted_partial = sorted(analysis['partially_covered'], key=lambda x: x['code_lines'], reverse=True)

        for i, module in enumerate(sorted_partial[:15], 1):  # Top 15
            print(f"  {i:2d}. {module['path']:60s} ({module['code_lines']:4d} lines, {module['test_lines']:4d} test lines)")

    # Print well-covered modules
    if analysis['covered']:
        print(f"\n✅ Modules with GOOD Coverage ({len(analysis['covered'])}):")
        print(f"  (Showing {min(10, len(analysis['covered']))} examples)")
        print("-" * 80)

        sorted_covered = sorted(analysis['covered'], key=lambda x: x['code_lines'], reverse=True)

        for i, module in enumerate(sorted_covered[:10], 1):  # Top 10
            print(f"  {i:2d}. {module['path']:60s} ({module['code_lines']:4d} lines, {module['test_lines']:4d} test lines)")

    print("\n" + "=" * 80)
    print("💡 Recommendation:")
    if stats['coverage_percentage'] < 80:
        print(f"  Current coverage: ~{stats['coverage_percentage']:.0f}%")
        print(f"  Target coverage: 80%")
        print(f"  Gap: ~{80 - stats['coverage_percentage']:.0f}%")
        print(f"\n  Priority: Focus on testing the {len(analysis['uncovered'])} uncovered modules")
        print(f"  Start with the largest modules (most lines of code) listed above")
    else:
        print(f"  Coverage is good! ({stats['coverage_percentage']:.1f}%)")
        print(f"  Continue improving by adding tests for remaining {len(analysis['uncovered'])} modules")
    print("=" * 80)

def main():
    """Main entry point."""
    # Set up paths
    project_root = Path(__file__).parent.parent
    src_dir = project_root / 'src'
    tests_dir = project_root / 'tests'

    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)

    if not tests_dir.exists():
        print(f"Error: Tests directory not found: {tests_dir}", file=sys.stderr)
        sys.exit(1)

    # Analyze coverage
    analysis = analyze_coverage(src_dir, tests_dir)

    # Print report
    print_report(analysis)

    # Export to file
    report_file = project_root / 'TEST_COVERAGE_ANALYSIS.md'
    with open(report_file, 'w') as f:
        stats = analysis['stats']
        f.write("# Test Coverage Analysis Report\n\n")
        f.write(f"**Generated:** {Path(__file__).name}\n")
        f.write(f"**Date:** 2026-01-18\n\n")

        f.write("## Overall Statistics\n\n")
        f.write(f"- Total modules: {stats['total_modules']}\n")
        f.write(f"- Covered: {stats['covered_count']} ({stats['covered_count']/stats['total_modules']*100:.1f}%)\n")
        f.write(f"- Partially covered: {stats['partially_covered_count']} ({stats['partially_covered_count']/stats['total_modules']*100:.1f}%)\n")
        f.write(f"- Uncovered: {stats['uncovered_count']} ({stats['uncovered_count']/stats['total_modules']*100:.1f}%)\n")
        f.write(f"- **Estimated coverage:** {stats['coverage_percentage']:.1f}%\n\n")

        f.write("## Modules Without Tests\n\n")
        if analysis['uncovered']:
            sorted_uncovered = sorted(analysis['uncovered'], key=lambda x: x['code_lines'], reverse=True)
            for module in sorted_uncovered:
                f.write(f"- `{module['path']}` ({module['code_lines']} lines)\n")
        else:
            f.write("All modules have tests! ✅\n")

        f.write("\n## Modules with Partial Coverage\n\n")
        if analysis['partially_covered']:
            sorted_partial = sorted(analysis['partially_covered'], key=lambda x: x['code_lines'], reverse=True)
            for module in sorted_partial:
                f.write(f"- `{module['path']}` ({module['code_lines']} lines, {module['test_lines']} test lines)\n")
        else:
            f.write("No modules with partial coverage.\n")

    print(f"\n📄 Report saved to: {report_file}")

if __name__ == '__main__':
    main()
