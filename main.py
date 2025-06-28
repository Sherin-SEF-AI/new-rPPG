#!/usr/bin/env python3
"""
Advanced rPPG Application
Main entry point for the remote Photoplethysmography application.
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import scipy
    except ImportError:
        missing_deps.append("scipy")
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
    
    try:
        import pyqtgraph
    except ImportError:
        missing_deps.append("pyqtgraph")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    if missing_deps:
        error_msg = f"Missing dependencies: {', '.join(missing_deps)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install -r requirements.txt"
        return False, error_msg
    
    return True, ""


def create_data_directory():
    """Create data directory if it doesn't exist."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def main():
    """Main application function."""
    # Check dependencies
    deps_ok, deps_error = check_dependencies()
    if not deps_ok:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Dependency Error", deps_error)
        sys.exit(1)
    
    # Create data directory
    try:
        create_data_directory()
    except Exception as e:
        print(f"Warning: Could not create data directory: {e}")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced rPPG Application")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("rPPG Research")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        error_msg = f"Application error: {str(e)}\n\n"
        error_msg += "Traceback:\n"
        error_msg += traceback.format_exc()
        
        QMessageBox.critical(None, "Application Error", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main() 