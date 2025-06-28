"""
Plot Widget Module
Widget for real-time plotting of rPPG signals and metrics.
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class PlotWidget(QWidget):
    """Widget for real-time plotting."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_plots()
        
        # Data buffers
        self.heart_rates = []
        self.qualities = []
        self.timestamps = []
        self.filtered_signals = []
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(100)  # Update every 100ms
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Real-time rPPG Monitoring")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Plot layout
        plot_layout = QHBoxLayout()
        layout.addLayout(plot_layout)
        
        # Create plot widgets
        self.heart_rate_plot = pg.PlotWidget()
        self.heart_rate_plot.setTitle("Heart Rate (BPM)")
        self.heart_rate_plot.setLabel('left', 'Heart Rate', 'BPM')
        self.heart_rate_plot.setLabel('bottom', 'Time', 's')
        self.heart_rate_plot.showGrid(x=True, y=True)
        plot_layout.addWidget(self.heart_rate_plot)
        
        self.quality_plot = pg.PlotWidget()
        self.quality_plot.setTitle("Signal Quality")
        self.quality_plot.setLabel('left', 'Quality', 'Score')
        self.quality_plot.setLabel('bottom', 'Time', 's')
        self.quality_plot.showGrid(x=True, y=True)
        plot_layout.addWidget(self.quality_plot)
        
        # Signal plot
        self.signal_plot = pg.PlotWidget()
        self.signal_plot.setTitle("Filtered rPPG Signal")
        self.signal_plot.setLabel('left', 'Amplitude')
        self.signal_plot.setLabel('bottom', 'Samples')
        self.signal_plot.showGrid(x=True, y=True)
        layout.addWidget(self.signal_plot)
        
        # Set plot colors
        self.heart_rate_plot.setBackground('w')
        self.quality_plot.setBackground('w')
        self.signal_plot.setBackground('w')
        
    def setup_plots(self):
        """Setup plot curves."""
        # Heart rate curve
        self.hr_curve = self.heart_rate_plot.plot(pen=pg.mkPen('r', width=2))
        
        # Quality curve
        self.quality_curve = self.quality_plot.plot(pen=pg.mkPen('b', width=2))
        
        # Signal curve
        self.signal_curve = self.signal_plot.plot(pen=pg.mkPen('g', width=1))
        
    def update_plots(self, frame=None, hr=0.0, quality=0.0, filtered_signal=None):
        """Update all plots with new data."""
        current_time = len(self.timestamps) * 0.033  # Assuming 30 fps
        
        # Update heart rate plot
        if hr > 0:
            self.heart_rates.append(hr)
            self.timestamps.append(current_time)
            
            # Keep only last 300 points (10 seconds at 30 fps)
            if len(self.heart_rates) > 300:
                self.heart_rates.pop(0)
                self.timestamps.pop(0)
            
            # Update heart rate curve
            if len(self.heart_rates) > 1:
                self.hr_curve.setData(self.timestamps, self.heart_rates)
        
        # Update quality plot
        if quality > 0:
            self.qualities.append(quality)
            
            # Keep only last 300 points
            if len(self.qualities) > 300:
                self.qualities.pop(0)
            
            # Update quality curve
            if len(self.qualities) > 1:
                quality_times = self.timestamps[:len(self.qualities)]
                self.quality_curve.setData(quality_times, self.qualities)
        
        # Update signal plot
        if filtered_signal is not None and len(filtered_signal) > 0:
            self.filtered_signals = filtered_signal.tolist()
            
            # Keep only last 200 points for signal display
            if len(self.filtered_signals) > 200:
                self.filtered_signals = self.filtered_signals[-200:]
            
            # Update signal curve
            signal_indices = np.arange(len(self.filtered_signals))
            self.signal_curve.setData(signal_indices, self.filtered_signals)
    
    def reset(self):
        """Reset all plots."""
        self.heart_rates.clear()
        self.qualities.clear()
        self.timestamps.clear()
        self.filtered_signals.clear()
        
        # Clear plot curves
        self.hr_curve.clear()
        self.quality_curve.clear()
        self.signal_curve.clear()


class HRVPlotWidget(QWidget):
    """Widget for HRV-specific plots."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Heart Rate Variability Analysis")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create HRV plots
        self.rr_plot = pg.PlotWidget()
        self.rr_plot.setTitle("RR Intervals")
        self.rr_plot.setLabel('left', 'RR Interval', 's')
        self.rr_plot.setLabel('bottom', 'Beat Number')
        self.rr_plot.showGrid(x=True, y=True)
        self.rr_plot.setBackground('w')
        layout.addWidget(self.rr_plot)
        
        # Poincaré plot
        self.poincare_plot = pg.PlotWidget()
        self.poincare_plot.setTitle("Poincaré Plot")
        self.poincare_plot.setLabel('left', 'RR(n+1)', 's')
        self.poincare_plot.setLabel('bottom', 'RR(n)', 's')
        self.poincare_plot.showGrid(x=True, y=True)
        self.poincare_plot.setBackground('w')
        layout.addWidget(self.poincare_plot)
        
    def update_hrv_plots(self, rr_intervals):
        """Update HRV plots with RR intervals."""
        if len(rr_intervals) < 2:
            return
            
        rr_array = np.array(rr_intervals)
        
        # Update RR interval plot
        beat_numbers = np.arange(len(rr_array))
        self.rr_plot.plot(beat_numbers, rr_array, clear=True, pen=pg.mkPen('b', width=2))
        
        # Update Poincaré plot
        if len(rr_array) >= 2:
            rr_n = rr_array[:-1]
            rr_n1 = rr_array[1:]
            self.poincare_plot.plot(rr_n, rr_n1, clear=True, pen=None, 
                                  symbol='o', symbolBrush='r', symbolSize=5) 