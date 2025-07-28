#!/usr/bin/env python3
"""
Setup script for Legacy Code Analyzer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="legacy-code-analyzer",
    version="1.0.0",
    description="A comprehensive CLI tool for analyzing legacy codebases using AST, LLM, and D3.js visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Legacy Code Analyzer Team",
    author_email="team@legacycodeanalyzer.com",
    url="https://github.com/your-org/legacy-code-analyzer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "code-analyzer=main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="legacy code analysis cobol ast llm visualization d3",
    project_urls={
        "Bug Reports": "https://github.com/your-org/legacy-code-analyzer/issues",
        "Source": "https://github.com/your-org/legacy-code-analyzer",
        "Documentation": "https://github.com/your-org/legacy-code-analyzer/blob/main/README.md",
    },
) 