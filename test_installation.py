#!/usr/bin/env python3
"""
Test script to verify rPPG application installation
"""

import sys
import importlib
from typing import List, Tuple


def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True, f"✓ {package_name or module_name}"
    except ImportError as e:
        return False, f"✗ {package_name or module_name}: {e}"


def test_core_modules() -> List[Tuple[bool, str]]:
    """Test core rPPG modules."""
    results = []
    
    # Test basic dependencies
    results.append(test_import("cv2", "OpenCV"))
    results.append(test_import("numpy", "NumPy"))
    results.append(test_import("scipy", "SciPy"))
    results.append(test_import("mediapipe", "MediaPipe"))
    results.append(test_import("pyqtgraph", "PyQtGraph"))
    results.append(test_import("pandas", "Pandas"))
    
    # Test PyQt5
    results.append(test_import("PyQt5", "PyQt5"))
    
    # Test rPPG core modules
    try:
        from rppg_core import FaceDetector, SignalProcessor, QualityMetrics, HRVAnalyzer
        results.append((True, "✓ rPPG Core Modules"))
    except ImportError as e:
        results.append((False, f"✗ rPPG Core Modules: {e}"))
    
    return results


def test_gui_modules() -> List[Tuple[bool, str]]:
    """Test GUI modules."""
    results = []
    
    try:
        from gui import MainWindow, VideoWidget, PlotWidget, ControlPanel
        results.append((True, "✓ GUI Modules"))
    except ImportError as e:
        results.append((False, f"✗ GUI Modules: {e}"))
    
    return results


def test_utils_modules() -> List[Tuple[bool, str]]:
    """Test utility modules."""
    results = []
    
    try:
        from utils import save_data, load_data, export_results
        results.append((True, "✓ Utils Modules"))
    except ImportError as e:
        results.append((False, f"✗ Utils Modules: {e}"))
    
    return results


def main():
    """Main test function."""
    print("=" * 50)
    print("Advanced rPPG Application - Installation Test")
    print("=" * 50)
    print()
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} (3.8+ required)")
        return False
    
    print()
    
    # Test core modules
    print("Testing Core Dependencies:")
    print("-" * 30)
    core_results = test_core_modules()
    for success, message in core_results:
        print(message)
    
    print()
    
    # Test GUI modules
    print("Testing GUI Modules:")
    print("-" * 20)
    gui_results = test_gui_modules()
    for success, message in gui_results:
        print(message)
    
    print()
    
    # Test utils modules
    print("Testing Utils Modules:")
    print("-" * 20)
    utils_results = test_utils_modules()
    for success, message in utils_results:
        print(message)
    
    print()
    
    # Summary
    all_results = core_results + gui_results + utils_results
    passed = sum(1 for success, _ in all_results if success)
    total = len(all_results)
    
    print("=" * 50)
    print(f"Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is successful.")
        print()
        print("You can now run the application with:")
        print("  python main.py")
        print("  or")
        print("  rppg-app")
        return True
    else:
        print("❌ Some tests failed. Please check the installation.")
        print()
        print("Try reinstalling with:")
        print("  pip install -r requirements.txt")
        print("  pip install -e .")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 