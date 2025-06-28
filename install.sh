#!/bin/bash

# Advanced rPPG Application Installation Script
# This script installs the rPPG application and its dependencies

set -e  # Exit on any error

echo "=========================================="
echo "Advanced rPPG Application Installer"
echo "=========================================="

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✓ pip3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv rppg_env

# Activate virtual environment
echo "Activating virtual environment..."
source rppg_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the application
echo "Installing rPPG application..."
pip install -e .

echo ""
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment:"
echo "   source rppg_env/bin/activate"
echo ""
echo "2. Run the application:"
echo "   python main.py"
echo ""
echo "Or use the command:"
echo "   rppg-app"
echo ""
echo "To deactivate the virtual environment:"
echo "   deactivate"
echo ""
echo "==========================================" 