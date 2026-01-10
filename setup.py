#!/usr/bin/env python3
"""Setup script for Document Management System"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="document-management-system",
    version="1.0.0",
    author="Claude AI",
    description="Комплексная система управления документами для планирования социальных услуг",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svend4/daten20",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Social Services",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "pdf": ["weasyprint>=60.0"],
        "docx": ["python-docx>=0.8.11"],
        "web": ["Flask>=3.0.0"],
        "all": [
            "weasyprint>=60.0",
            "python-docx>=0.8.11",
            "Flask>=3.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "template-analyzer=src.template_analyzer:main",
            "financial-calculator=src.financial_calculator:main",
            "document-generator=src.document_generator:main",
            "interactive-editor=src.interactive_editor:main",
            "service-manager=src.service_manager:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "mSchablone"],
    },
)
