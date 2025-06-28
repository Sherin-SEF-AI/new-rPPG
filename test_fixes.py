#!/usr/bin/env python3
"""
Test script to verify that the rPPG application fixes are working.
"""

import sys
import os
import numpy as np
from scipy.signal import windows

def test_scipy_windows():
    """Test scipy.signal.windows.hann function."""
    print("Testing scipy.signal.windows.hann...")
    try:
        window = windows.hann(100)
        print(f"✓ scipy.signal.windows.hann works - window shape: {window.shape}")
        return True
    except Exception as e:
        print(f"✗ scipy.signal.windows.hann failed: {e}")
        return False

def test_imports():
    """Test all module imports."""
    print("Testing module imports...")
    
    modules_to_test = [
        'cv2',
        'numpy',
        'scipy',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'mediapipe',
        'matplotlib',
        'pandas'
    ]
    
    all_passed = True
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            all_passed = False
    
    return all_passed

def test_rppg_core():
    """Test rPPG core modules."""
    print("Testing rPPG core modules...")
    
    try:
        from rppg_core.face_detector import FaceDetector
        from rppg_core.signal_processor import SignalProcessor
        from rppg_core.quality_metrics import QualityMetrics
        from rppg_core.hrv_analyzer import HRVAnalyzer
        
        # Test signal processor
        processor = SignalProcessor()
        test_roi = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        hr, quality, filtered_signal = processor.process_frame(test_roi)
        
        print(f"✓ rPPG core modules work - HR: {hr:.1f}, Quality: {quality:.3f}")
        return True
        
    except Exception as e:
        print(f"✗ rPPG core modules failed: {e}")
        return False

def test_gui_modules():
    """Test GUI modules."""
    print("Testing GUI modules...")
    
    try:
        from gui.main_window import MainWindow
        from gui.video_widget import VideoWidget
        from gui.control_panel import ControlPanel
        from gui.plot_widget import PlotWidget
        
        print("✓ GUI modules imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI modules failed: {e}")
        return False

def test_utils():
    """Test utility modules."""
    print("Testing utility modules...")
    
    try:
        from utils.file_utils import save_data, load_data
        from utils.validation import validate_video_file, validate_parameters
        
        print("✓ Utility modules imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Utility modules failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("rPPG Application Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Scipy Windows", test_scipy_windows),
        ("Module Imports", test_imports),
        ("rPPG Core", test_rppg_core),
        ("GUI Modules", test_gui_modules),
        ("Utility Modules", test_utils)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 