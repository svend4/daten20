#!/usr/bin/env python
"""
Unified Test Runner for Dual-Version Modules

Automatically discovers and runs all tests for dual-version pattern modules.
Tests are run in both Pure Python and NumPy modes (if available).
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Tuple, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestResult:
    """Test result container"""

    def __init__(self, module: str, passed: bool, duration: float, output: str, error: Optional[str] = None):
        self.module = module
        self.passed = passed
        self.duration = duration
        self.output = output
        self.error = error


class DualVersionTestRunner:
    """Runner for dual-version module tests"""

    def __init__(self):
        self.src_dir = Path(__file__).parent.parent / "src"
        self.test_files = []
        self.results: List[TestResult] = []

    def discover_tests(self) -> List[Path]:
        """Discover all dual-version test files"""
        test_patterns = [
            "test_dual_version.py",
            "test_pure_python.py",
            "test_bci_pure_python.py",
        ]

        test_files = []
        for pattern in test_patterns:
            test_files.extend(self.src_dir.rglob(pattern))

        # Sort by module name
        test_files.sort(key=lambda p: str(p))

        print(f"Discovered {len(test_files)} test files")
        for test_file in test_files:
            print(f"  - {test_file.relative_to(self.src_dir)}")

        return test_files

    def run_test(self, test_file: Path) -> TestResult:
        """Run a single test file"""
        module_name = test_file.parent.name
        print(f"\n{'=' * 60}")
        print(f"Testing: {module_name}")
        print(f"File: {test_file.relative_to(self.src_dir)}")
        print(f"{'=' * 60}")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.src_dir)

        start_time = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )

            duration = time.time() - start_time
            passed = result.returncode == 0

            output = result.stdout
            error = result.stderr if result.returncode != 0 else None

            if passed:
                print(f"✓ PASSED in {duration:.2f}s")
            else:
                print(f"✗ FAILED in {duration:.2f}s")
                if error:
                    print(f"Error: {error[:200]}")

            return TestResult(module_name, passed, duration, output, error)

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"✗ TIMEOUT after {duration:.2f}s")
            return TestResult(module_name, False, duration, "", "Test timeout after 60s")

        except Exception as e:
            duration = time.time() - start_time
            print(f"✗ ERROR: {e}")
            return TestResult(module_name, False, duration, "", str(e))

    def run_all_tests(self) -> bool:
        """Run all discovered tests"""
        self.test_files = self.discover_tests()

        if not self.test_files:
            print("\n⚠ No test files found!")
            return False

        print(f"\n{'=' * 60}")
        print(f"RUNNING {len(self.test_files)} TEST SUITES")
        print(f"{'=' * 60}")

        for test_file in self.test_files:
            result = self.run_test(test_file)
            self.results.append(result)

        return self.print_summary()

    def print_summary(self) -> bool:
        """Print test summary"""
        print(f"\n{'=' * 60}")
        print("TEST SUMMARY")
        print(f"{'=' * 60}")

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_duration = sum(r.duration for r in self.results)

        print(f"\nTotal: {len(self.results)} test suites")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Duration: {total_duration:.2f}s")

        if failed > 0:
            print(f"\n{'=' * 60}")
            print("FAILED TESTS")
            print(f"{'=' * 60}")
            for result in self.results:
                if not result.passed:
                    print(f"\n✗ {result.module}")
                    if result.error:
                        print(f"  Error: {result.error[:300]}")

        print(f"\n{'=' * 60}")
        if failed == 0:
            print("✓ ALL TESTS PASSED!")
        else:
            print(f"✗ {failed} TEST(S) FAILED")
        print(f"{'=' * 60}")

        return failed == 0

    def check_numpy_availability(self):
        """Check if NumPy is available"""
        try:
            import numpy as np
            print(f"✓ NumPy {np.__version__} available - will test optimized versions")
            return True
        except ImportError:
            print("⚠ NumPy not available - will test Pure Python versions only")
            return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("DUAL-VERSION PATTERN TEST RUNNER")
    print("=" * 60)

    runner = DualVersionTestRunner()

    # Check NumPy availability
    has_numpy = runner.check_numpy_availability()
    print()

    # Run all tests
    success = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
