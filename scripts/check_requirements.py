#!/usr/bin/env python3
"""
System Requirements Checker
============================

Checks if all system requirements are met before running the application.

Usage:
    python scripts/check_requirements.py
    python scripts/check_requirements.py --fix
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path


class Color:
    """Terminal colors."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print section header."""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Color.GREEN}✓{Color.END} {text}")


def print_warning(text):
    """Print warning message."""
    print(f"{Color.YELLOW}⚠{Color.END} {text}")


def print_error(text):
    """Print error message."""
    print(f"{Color.RED}✗{Color.END} {text}")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python version: {version_str} (OK)")
        return True
    else:
        print_error(f"Python version: {version_str} (FAILED)")
        print_warning("  Required: Python 3.9 or higher")
        print_warning("  Install: https://www.python.org/downloads/")
        return False


def check_pip():
    """Check if pip is installed."""
    print_header("Checking pip")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                              capture_output=True, text=True, check=True)
        version = result.stdout.split()[1]
        print_success(f"pip version: {version} (OK)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pip not found")
        print_warning("  Install: python -m ensurepip --upgrade")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        'flask', 'pyyaml', 'openpyxl', 'pytest', 'tqdm'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} (OK)")
        except ImportError:
            print_error(f"{package} (MISSING)")
            all_installed = False
    
    if not all_installed:
        print_warning("\n  Install missing packages:")
        print_warning("  pip install -r requirements.txt")
    
    return all_installed


def check_spacy_models():
    """Check if spaCy models are downloaded."""
    print_header("Checking spaCy Models")
    
    models = ['en_core_web_sm', 'ru_core_news_sm']
    all_installed = True
    
    try:
        import spacy
        
        for model in models:
            try:
                spacy.load(model)
                print_success(f"{model} (OK)")
            except OSError:
                print_error(f"{model} (MISSING)")
                all_installed = False
        
        if not all_installed:
            print_warning("\n  Download missing models:")
            print_warning("  python -m spacy download en_core_web_sm")
            print_warning("  python -m spacy download ru_core_news_sm")
    
    except ImportError:
        print_error("spaCy not installed")
        print_warning("  Install: pip install spacy")
        return False
    
    return all_installed


def check_disk_space():
    """Check available disk space."""
    print_header("Checking Disk Space")
    
    try:
        stat = shutil.disk_usage(Path.cwd())
        free_gb = stat.free / (1024 ** 3)
        
        if free_gb >= 1.0:
            print_success(f"Available disk space: {free_gb:.2f} GB (OK)")
            return True
        else:
            print_warning(f"Available disk space: {free_gb:.2f} GB (LOW)")
            print_warning("  Recommended: At least 1 GB free space")
            return True  # Warning, not error
    except Exception as e:
        print_error(f"Could not check disk space: {e}")
        return True


def check_memory():
    """Check available memory."""
    print_header("Checking Memory")
    
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo') as f:
                meminfo = dict((line.split()[0].rstrip(':'), int(line.split()[1]))
                             for line in f if len(line.split()) > 1)
                mem_available_gb = meminfo['MemAvailable'] / (1024 ** 2)
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['sysctl', 'hw.memsize'],
                                  capture_output=True, text=True, check=True)
            mem_bytes = int(result.stdout.split()[1])
            mem_available_gb = mem_bytes / (1024 ** 3)
        else:
            print_warning("Memory check not supported on this platform")
            return True
        
        if mem_available_gb >= 4.0:
            print_success(f"Available memory: {mem_available_gb:.2f} GB (OK)")
            return True
        else:
            print_warning(f"Available memory: {mem_available_gb:.2f} GB (LOW)")
            print_warning("  Recommended: At least 4 GB RAM")
            return True  # Warning, not error
    except Exception as e:
        print_warning(f"Could not check memory: {e}")
        return True


def check_directories():
    """Check if required directories exist."""
    print_header("Checking Directories")
    
    required_dirs = [
        'src', 'src/core', 'src/ml', 'src/models',
        'tests', 'logs', 'database', 'config'
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}/ (OK)")
        else:
            print_warning(f"{dir_path}/ (MISSING)")
            all_exist = False
    
    if not all_exist:
        print_warning("\n  Create missing directories:")
        for dir_path in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                print_warning(f"  mkdir -p {dir_path}")
    
    return all_exist


def check_config_files():
    """Check if configuration files exist."""
    print_header("Checking Configuration Files")
    
    config_files = [
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    
    for file_path in config_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} (OK)")
        else:
            print_error(f"{file_path} (MISSING)")
            all_exist = False
    
    return all_exist


def main():
    """Main function."""
    print(f"\n{Color.BOLD}Document Management System - Requirements Checker{Color.END}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    checks = [
        ("Python Version", check_python_version),
        ("pip", check_pip),
        ("Dependencies", check_dependencies),
        ("spaCy Models", check_spacy_models),
        ("Disk Space", check_disk_space),
        ("Memory", check_memory),
        ("Directories", check_directories),
        ("Configuration Files", check_config_files)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Error checking {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nChecks passed: {passed}/{total}")
    
    if passed == total:
        print_success("\n✓ All checks passed! System is ready.")
        return 0
    else:
        print_error("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
