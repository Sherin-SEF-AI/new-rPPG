"""
Video Widget Module
Widget for displaying and processing video frames.
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QFont

from rppg_core import FaceDetector, SignalProcessor, QualityMetrics, HRVAnalyzer


class VideoProcessor(QThread):
    """Thread for video processing."""
    
    frame_processed = pyqtSignal(np.ndarray, float, float, np.ndarray)
    face_detected = pyqtSignal(bool, float)
    heart_rate_updated = pyqtSignal(float)
    quality_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.video_source = None
        self.face_detector = FaceDetector()
        self.signal_processor = SignalProcessor()
        self.quality_metrics = QualityMetrics()
        self.hrv_analyzer = HRVAnalyzer()
        
    def set_video_source(self, source):
        """Set video source (camera index or file path)."""
        self.video_source = source
        
    def run(self):
        """Main processing loop."""
        if self.video_source is None:
            return
            
        # Open video capture
        if isinstance(self.video_source, int):
            cap = cv2.VideoCapture(self.video_source)
        else:
            cap = cv2.VideoCapture(self.video_source)
            
        if not cap.isOpened():
            return
            
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                if isinstance(self.video_source, str):  # File ended
                    break
                continue
                
            # Process frame
            processed_frame, hr, quality, filtered_signal = self.process_frame(frame)
            
            # Emit signals
            self.frame_processed.emit(processed_frame, hr, quality, filtered_signal)
            self.face_detected.emit(hr > 0, quality)
            self.heart_rate_updated.emit(hr)
            
            # Calculate comprehensive quality metrics
            rgb_signals = (self.signal_processor.r_signal, 
                          self.signal_processor.g_signal, 
                          self.signal_processor.b_signal)
            quality_metrics = self.quality_metrics.calculate_comprehensive_quality(
                rgb_signals, quality
            )
            self.quality_updated.emit(quality_metrics)
            
            # Add heart rate to HRV analyzer
            if hr > 0:
                self.hrv_analyzer.add_heart_rate(hr, self.signal_processor.timestamps[-1] if self.signal_processor.timestamps else 0)
            
            # Control frame rate
            self.msleep(33)  # ~30 fps
            
        cap.release()
        
    def process_frame(self, frame):
        """Process a single frame."""
        # Detect face
        face_roi, face_quality = self.face_detector.detect_face(frame)
        
        # Process rPPG signal
        if face_roi is not None:
            hr, quality, filtered_signal = self.signal_processor.process_frame(face_roi)
        else:
            hr, quality, filtered_signal = 0.0, 0.0, np.array([])
        
        # Draw face detection info
        processed_frame = self.face_detector.draw_face_info(frame)
        
        return processed_frame, hr, quality, filtered_signal
        
    def stop(self):
        """Stop processing."""
        self.running = False
        self.wait()
        
    def reset(self):
        """Reset all processors."""
        self.signal_processor.reset()
        self.quality_metrics = QualityMetrics()
        self.hrv_analyzer.reset()


class VideoWidget(QWidget):
    """Widget for displaying video and processing controls."""
    
    frame_processed = pyqtSignal(np.ndarray, float, float, np.ndarray)
    face_detected = pyqtSignal(bool, float)
    heart_rate_updated = pyqtSignal(float)
    quality_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.current_heart_rate = 0.0
        self.current_quality = 0.0
        self._is_processing = False
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.video_label.setText("No video source")
        layout.addWidget(self.video_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Live")
        self.start_button.setFont(QFont("Arial", 10))
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont("Arial", 10))
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.load_button = QPushButton("Load Video")
        self.load_button.setFont(QFont("Arial", 10))
        button_layout.addWidget(self.load_button)
        
        button_layout.addStretch()
        
        # Status labels
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 9))
        button_layout.addWidget(self.status_label)
        
        layout.addLayout(button_layout)
        
    def setup_connections(self):
        """Setup signal connections."""
        # Connect processor signals
        self.video_processor.frame_processed.connect(self.update_video_frame)
        self.video_processor.face_detected.connect(self.update_face_status)
        self.video_processor.heart_rate_updated.connect(self.update_heart_rate)
        self.video_processor.quality_updated.connect(self.update_quality)
        
        # Connect button signals
        self.start_button.clicked.connect(self.start_live_capture)
        self.stop_button.clicked.connect(self.stop_live_capture)
        self.load_button.clicked.connect(self.load_video_file)
        
    def start_live_capture(self):
        """Start live video capture."""
        if not self._is_processing:
            self.video_processor.set_video_source(0)  # Default camera
            self.video_processor.start()
            self._is_processing = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Status: Live capture active")
            
    def stop_live_capture(self):
        """Stop live video capture."""
        if self._is_processing:
            self.video_processor.stop()
            self._is_processing = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Status: Stopped")
            self.video_label.setText("No video source")
            
    def load_video_file(self, file_path=None):
        """Load video file for processing."""
        if file_path is None:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Video File",
                "",
                "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
            )
            
        if file_path:
            if self._is_processing:
                self.stop_live_capture()
                
            self.video_processor.set_video_source(file_path)
            self.video_processor.start()
            self._is_processing = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText(f"Status: Processing {file_path}")
            
    def update_video_frame(self, frame, hr, quality, filtered_signal):
        """Update video frame display."""
        # Convert OpenCV frame to Qt format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale image to fit label
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        
        self.video_label.setPixmap(scaled_pixmap)
        
        # Emit signals
        self.frame_processed.emit(frame, hr, quality, filtered_signal)
        
    def update_face_status(self, detected, quality):
        """Update face detection status."""
        self.face_detected.emit(detected, quality)
        
    def update_heart_rate(self, hr):
        """Update heart rate display."""
        self.current_heart_rate = hr
        self.heart_rate_updated.emit(hr)
        
    def update_quality(self, quality_metrics):
        """Update quality metrics."""
        self.current_quality = quality_metrics.get('overall_quality', 0.0)
        self.quality_updated.emit(quality_metrics)
        
    def get_current_heart_rate(self):
        """Get current heart rate."""
        return self.current_heart_rate
        
    def get_current_quality(self):
        """Get current quality score."""
        return self.current_quality
        
    def is_processing(self):
        """Check if processing is active."""
        return self._is_processing
        
    def reset(self):
        """Reset the video widget."""
        if self._is_processing:
            self.stop_live_capture()
        self.video_processor.reset()
        self.current_heart_rate = 0.0
        self.current_quality = 0.0
        self.status_label.setText("Status: Ready")
        
    def save_data_csv(self, file_path):
        """Save data to CSV file."""
        import pandas as pd
        
        data = {
            'timestamp': self.video_processor.signal_processor.timestamps,
            'heart_rate': self.video_processor.signal_processor.r_signal,
            'r_signal': self.video_processor.signal_processor.r_signal,
            'g_signal': self.video_processor.signal_processor.g_signal,
            'b_signal': self.video_processor.signal_processor.b_signal
        }
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        
    def save_data_json(self, file_path):
        """Save data to JSON file."""
        import json
        
        data = {
            'timestamps': self.video_processor.signal_processor.timestamps,
            'heart_rates': self.video_processor.signal_processor.r_signal,
            'r_signals': self.video_processor.signal_processor.r_signal,
            'g_signals': self.video_processor.signal_processor.g_signal,
            'b_signals': self.video_processor.signal_processor.b_signal,
            'hrv_metrics': self.video_processor.hrv_analyzer.calculate_hrv_metrics()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2) 