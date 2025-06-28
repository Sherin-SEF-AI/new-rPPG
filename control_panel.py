"""
Control Panel Module
Widget for user controls and status display.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QProgressBar, QTextEdit, 
                             QSlider, QCheckBox, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class ControlPanel(QWidget):
    """Control panel for rPPG application."""
    
    # Define signals
    start_live_clicked = pyqtSignal()
    stop_live_clicked = pyqtSignal()
    load_video_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(500)  # Update every 500ms
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Control Panel")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Control buttons group
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)
        
        # Live capture controls
        live_layout = QHBoxLayout()
        self.start_live_button = QPushButton("Start Live")
        self.start_live_button.setFont(QFont("Arial", 10))
        self.start_live_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        live_layout.addWidget(self.start_live_button)
        
        self.stop_live_button = QPushButton("Stop Live")
        self.stop_live_button.setFont(QFont("Arial", 10))
        self.stop_live_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        self.stop_live_button.setEnabled(False)
        live_layout.addWidget(self.stop_live_button)
        
        control_layout.addLayout(live_layout)
        
        # File controls
        file_layout = QHBoxLayout()
        self.load_video_button = QPushButton("Load Video")
        self.load_video_button.setFont(QFont("Arial", 10))
        file_layout.addWidget(self.load_video_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Arial", 10))
        self.reset_button.setStyleSheet("QPushButton { background-color: #ff9800; color: white; }")
        file_layout.addWidget(self.reset_button)
        
        control_layout.addLayout(file_layout)
        layout.addWidget(control_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        # Face detection status
        self.face_status_label = QLabel("Face Detection: Not Detected")
        self.face_status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.face_status_label)
        
        # Heart rate display
        self.heart_rate_label = QLabel("Heart Rate: -- BPM")
        self.heart_rate_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.heart_rate_label.setStyleSheet("QLabel { color: #2196F3; }")
        status_layout.addWidget(self.heart_rate_label)
        
        # Quality display
        self.quality_label = QLabel("Signal Quality: --")
        self.quality_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.quality_label)
        
        # Quality progress bar
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(0)
        status_layout.addWidget(self.quality_bar)
        
        layout.addWidget(status_group)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Algorithm selection
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algorithm:"))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Chrominance", "POS", "Green Channel"])
        algo_layout.addWidget(self.algorithm_combo)
        settings_layout.addLayout(algo_layout)
        
        # Processing parameters
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(15, 60)
        self.fps_spinbox.setValue(30)
        param_layout.addWidget(self.fps_spinbox)
        settings_layout.addLayout(param_layout)
        
        # Display options
        self.show_landmarks_check = QCheckBox("Show Face Landmarks")
        self.show_landmarks_check.setChecked(True)
        settings_layout.addWidget(self.show_landmarks_check)
        
        self.show_quality_check = QCheckBox("Show Quality Metrics")
        self.show_quality_check.setChecked(True)
        settings_layout.addWidget(self.show_quality_check)
        
        layout.addWidget(settings_group)
        
        # HRV metrics group
        hrv_group = QGroupBox("HRV Metrics")
        hrv_layout = QVBoxLayout(hrv_group)
        
        self.hrv_text = QTextEdit()
        self.hrv_text.setMaximumHeight(150)
        self.hrv_text.setReadOnly(True)
        self.hrv_text.setFont(QFont("Courier", 9))
        hrv_layout.addWidget(self.hrv_text)
        
        layout.addWidget(hrv_group)
        
        # Quality recommendations
        quality_group = QGroupBox("Quality Recommendations")
        quality_layout = QVBoxLayout(quality_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(100)
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setFont(QFont("Arial", 9))
        quality_layout.addWidget(self.recommendations_text)
        
        layout.addWidget(quality_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    def setup_connections(self):
        """Setup signal connections."""
        self.start_live_button.clicked.connect(self.start_live_clicked.emit)
        self.stop_live_button.clicked.connect(self.stop_live_clicked.emit)
        self.load_video_button.clicked.connect(self.load_video_clicked.emit)
        self.reset_button.clicked.connect(self.reset_clicked.emit)
        
    def update_face_status(self, detected, quality):
        """Update face detection status."""
        if detected:
            self.face_status_label.setText(f"Face Detection: Detected (Quality: {quality:.2f})")
            self.face_status_label.setStyleSheet("QLabel { color: green; }")
        else:
            self.face_status_label.setText("Face Detection: Not Detected")
            self.face_status_label.setStyleSheet("QLabel { color: red; }")
            
    def update_heart_rate(self, hr):
        """Update heart rate display."""
        if hr > 0:
            self.heart_rate_label.setText(f"Heart Rate: {hr:.1f} BPM")
            
            # Color coding based on heart rate
            if 60 <= hr <= 100:
                self.heart_rate_label.setStyleSheet("QLabel { color: #4CAF50; }")
            elif 50 <= hr < 60 or 100 < hr <= 120:
                self.heart_rate_label.setStyleSheet("QLabel { color: #ff9800; }")
            else:
                self.heart_rate_label.setStyleSheet("QLabel { color: #f44336; }")
        else:
            self.heart_rate_label.setText("Heart Rate: -- BPM")
            self.heart_rate_label.setStyleSheet("QLabel { color: gray; }")
            
    def update_quality(self, quality_metrics):
        """Update quality metrics display."""
        overall_quality = quality_metrics.get('overall_quality', 0.0)
        
        # Update quality label
        quality_text = f"Signal Quality: {overall_quality:.2f}"
        self.quality_label.setText(quality_text)
        
        # Update progress bar
        quality_percent = int(overall_quality * 100)
        self.quality_bar.setValue(quality_percent)
        
        # Color coding for progress bar
        if quality_percent >= 80:
            self.quality_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        elif quality_percent >= 60:
            self.quality_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff9800; }")
        else:
            self.quality_bar.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
            
        # Update HRV metrics
        self.update_hrv_display(quality_metrics)
        
        # Update recommendations
        self.update_recommendations(quality_metrics)
        
    def update_hrv_display(self, quality_metrics):
        """Update HRV metrics display."""
        # This would be populated with actual HRV data
        hrv_text = "HRV Metrics:\n"
        hrv_text += f"RMSSD: {quality_metrics.get('rmssd', 0.0):.2f} ms\n"
        hrv_text += f"SDNN: {quality_metrics.get('sdnn', 0.0):.2f} ms\n"
        hrv_text += f"pNN50: {quality_metrics.get('pnn50', 0.0):.1f}%\n"
        hrv_text += f"LF/HF Ratio: {quality_metrics.get('lf_hf_ratio', 0.0):.2f}"
        
        self.hrv_text.setText(hrv_text)
        
    def update_recommendations(self, quality_metrics):
        """Update quality recommendations."""
        recommendations = []
        
        if quality_metrics.get('face_quality', 0.0) < 0.5:
            recommendations.append("• Ensure face is clearly visible")
            
        if quality_metrics.get('lighting_consistency', 0.0) < 0.3:
            recommendations.append("• Improve lighting conditions")
            
        if quality_metrics.get('motion_artifacts', 0.0) > 0.5:
            recommendations.append("• Reduce movement during measurement")
            
        if quality_metrics.get('snr', 0.0) < 0.3:
            recommendations.append("• Check camera positioning")
            
        if not recommendations:
            recommendations.append("• Signal quality is good")
            
        self.recommendations_text.setText("\n".join(recommendations))
        
    def update_displays(self):
        """Update all displays."""
        # This method can be used for periodic updates
        pass
        
    def reset(self):
        """Reset the control panel."""
        self.face_status_label.setText("Face Detection: Not Detected")
        self.face_status_label.setStyleSheet("QLabel { color: gray; }")
        
        self.heart_rate_label.setText("Heart Rate: -- BPM")
        self.heart_rate_label.setStyleSheet("QLabel { color: gray; }")
        
        self.quality_label.setText("Signal Quality: --")
        self.quality_bar.setValue(0)
        
        self.hrv_text.clear()
        self.recommendations_text.clear()
        
        self.start_live_button.setEnabled(True)
        self.stop_live_button.setEnabled(False) 