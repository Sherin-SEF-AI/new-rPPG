#!/usr/bin/env python3
"""
Setup script for Advanced rPPG Application
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="advanced-rppg",
    version="1.0.0",
    author="rPPG Research Team",
    author_email="contact@rppg-research.com",
    description="Advanced Remote Photoplethysmography Application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rppg-research/advanced-rppg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rppg-app=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
    },
    keywords="rppg, photoplethysmography, heart-rate, computer-vision, medical, health",
    project_urls={
        "Bug Reports": "https://github.com/rppg-research/advanced-rppg/issues",
        "Source": "https://github.com/rppg-research/advanced-rppg",
        "Documentation": "https://advanced-rppg.readthedocs.io/",
    },
) 