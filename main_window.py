"""
Main Window Module
Main PyQt5 window for the rPPG application.
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QStatusBar, QMenuBar, 
                             QAction, QFileDialog, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from .video_widget import VideoWidget
from .plot_widget import PlotWidget
from .control_panel import ControlPanel


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced rPPG Application")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.video_widget = None
        self.plot_widget = None
        self.control_panel = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
    def setup_ui(self):
        """Setup the main user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Video and plots
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video widget
        self.video_widget = VideoWidget()
        left_layout.addWidget(self.video_widget)
        
        # Tab widget for plots
        self.plot_tabs = QTabWidget()
        left_layout.addWidget(self.plot_tabs)
        
        # Create plot widgets
        self.plot_widget = PlotWidget()
        self.plot_tabs.addTab(self.plot_widget, "Real-time Plots")
        
        # Right panel - Controls
        self.control_panel = ControlPanel()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.control_panel)
        
        # Set splitter proportions
        splitter.setSizes([1000, 400])
        
        # Connect signals
        self.control_panel.start_live_clicked.connect(self.video_widget.start_live_capture)
        self.control_panel.stop_live_clicked.connect(self.video_widget.stop_live_capture)
        self.control_panel.load_video_clicked.connect(self.load_video_file)
        self.control_panel.reset_clicked.connect(self.reset_application)
        
        # Connect video widget signals
        self.video_widget.frame_processed.connect(self.plot_widget.update_plots)
        self.video_widget.face_detected.connect(self.control_panel.update_face_status)
        self.video_widget.heart_rate_updated.connect(self.control_panel.update_heart_rate)
        self.video_widget.quality_updated.connect(self.control_panel.update_quality)
        
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open video action
        open_action = QAction('Open Video File', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_video_file)
        file_menu.addAction(open_action)
        
        # Save data action
        save_action = QAction('Save Data', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_data)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Reset layout action
        reset_layout_action = QAction('Reset Layout', self)
        reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.heart_rate_label = QLabel("HR: -- BPM")
        self.quality_label = QLabel("Quality: --")
        
        # Add labels to status bar
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.heart_rate_label)
        self.status_bar.addPermanentWidget(self.quality_label)
        
    def load_video_file(self):
        """Load a video file for processing."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        
        if file_path:
            try:
                self.video_widget.load_video_file(file_path)
                self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load video: {str(e)}")
    
    def save_data(self):
        """Save processed data."""
        if not self.video_widget.is_processing():
            QMessageBox.information(self, "Info", "No data to save. Start processing first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Save data based on file extension
                if file_path.endswith('.csv'):
                    self.video_widget.save_data_csv(file_path)
                elif file_path.endswith('.json'):
                    self.video_widget.save_data_json(file_path)
                else:
                    file_path += '.csv'
                    self.video_widget.save_data_csv(file_path)
                
                self.status_label.setText(f"Data saved: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
    
    def reset_application(self):
        """Reset the application state."""
        reply = QMessageBox.question(
            self,
            "Reset Application",
            "Are you sure you want to reset the application? This will clear all data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.video_widget.reset()
            self.plot_widget.reset()
            self.control_panel.reset()
            self.status_label.setText("Application reset")
    
    def reset_layout(self):
        """Reset the window layout."""
        # Reset splitter sizes
        splitter = self.centralWidget().layout().itemAt(0).widget()
        splitter.setSizes([1000, 400])
        
        self.status_label.setText("Layout reset")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About rPPG Application",
            "Advanced Remote Photoplethysmography Application\n\n"
            "Version: 1.0.0\n"
            "Features:\n"
            "• Real-time heart rate monitoring\n"
            "• HRV analysis\n"
            "• Signal quality assessment\n"
            "• Face detection and tracking\n"
            "• Live and file-based processing\n\n"
            "Built with Python, OpenCV, MediaPipe, and PyQt5"
        )
    
    def update_status(self):
        """Update status bar information."""
        if self.video_widget.is_processing():
            # Update heart rate display
            hr = self.video_widget.get_current_heart_rate()
            if hr > 0:
                self.heart_rate_label.setText(f"HR: {hr:.1f} BPM")
            
            # Update quality display
            quality = self.video_widget.get_current_quality()
            if quality > 0:
                quality_text = f"Quality: {quality:.2f}"
                self.quality_label.setText(quality_text)
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.video_widget.is_processing():
            reply = QMessageBox.question(
                self,
                "Exit Application",
                "Processing is active. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.video_widget.stop_live_capture()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 