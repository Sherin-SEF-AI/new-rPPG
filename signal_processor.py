"""
rPPG Signal Processing Module
Implements various rPPG algorithms for heart rate estimation.
"""

import cv2
import numpy as np
from scipy import signal
from scipy.signal import windows
from scipy.fft import fft, fftfreq
from typing import Tuple, List, Optional
import time


class SignalProcessor:
    """Advanced rPPG signal processor with multiple algorithms."""
    
    def __init__(self, fps: int = 30, window_size: int = 300):
        """
        Initialize signal processor.
        
        Args:
            fps: Video frame rate
            window_size: Size of sliding window for processing
        """
        self.fps = fps
        self.window_size = window_size
        
        # Signal buffers
        self.r_signal = []
        self.g_signal = []
        self.b_signal = []
        self.timestamps = []
        
        # Processing parameters
        self.min_hr = 40  # Minimum heart rate (BPM)
        self.max_hr = 200  # Maximum heart rate (BPM)
        
        # Filter parameters
        self.low_cutoff = 0.7  # Hz
        self.high_cutoff = 4.0  # Hz
        
        # Results
        self.current_hr = 0.0
        self.signal_quality = 0.0
        
    def extract_rgb_signals(self, roi: np.ndarray) -> Tuple[float, float, float]:
        """
        Extract RGB signals from ROI.
        
        Args:
            roi: Region of interest (face/forehead)
            
        Returns:
            Tuple of (R, G, B) mean values
        """
        if roi is None or roi.size == 0:
            return 0.0, 0.0, 0.0
        
        # Calculate mean RGB values
        r_mean = float(np.mean(roi[:, :, 2]))  # Red channel
        g_mean = float(np.mean(roi[:, :, 1]))  # Green channel
        b_mean = float(np.mean(roi[:, :, 0]))  # Blue channel
        
        return r_mean, g_mean, b_mean
    
    def add_frame_data(self, roi: np.ndarray, timestamp: float):
        """
        Add frame data to signal buffers.
        
        Args:
            roi: Region of interest
            timestamp: Frame timestamp
        """
        r, g, b = self.extract_rgb_signals(roi)
        
        self.r_signal.append(r)
        self.g_signal.append(g)
        self.b_signal.append(b)
        self.timestamps.append(timestamp)
        
        # Maintain window size
        if len(self.r_signal) > self.window_size:
            self.r_signal.pop(0)
            self.g_signal.pop(0)
            self.b_signal.pop(0)
            self.timestamps.pop(0)
    
    def chrominance_method(self) -> Tuple[float, np.ndarray]:
        """
        Implement chrominance-based rPPG method.
        
        Returns:
            Tuple of (heart_rate, filtered_signal)
        """
        if len(self.r_signal) < 30:  # Need minimum data
            return 0.0, np.array([])
        
        # Convert to numpy arrays
        r = np.array(self.r_signal)
        g = np.array(self.g_signal)
        b = np.array(self.b_signal)
        
        # Normalize signals
        r_norm = (r - np.mean(r)) / np.std(r)
        g_norm = (g - np.mean(g)) / np.std(g)
        b_norm = (b - np.mean(b)) / np.std(b)
        
        # Chrominance signals
        x = 3 * r_norm - 2 * g_norm
        y = 1.5 * r_norm + g_norm - 1.5 * b_norm
        
        # Combine chrominance signals
        chrominance = x - y
        
        # Apply bandpass filter
        filtered_signal = self._apply_bandpass_filter(chrominance)
        
        # Calculate heart rate
        hr = self._estimate_heart_rate(filtered_signal)
        
        return hr, filtered_signal
    
    def pos_method(self) -> Tuple[float, np.ndarray]:
        """
        Implement Plane-Orthogonal-to-Skin (POS) method.
        
        Returns:
            Tuple of (heart_rate, filtered_signal)
        """
        if len(self.r_signal) < 30:
            return 0.0, np.array([])
        
        # Convert to numpy arrays
        r = np.array(self.r_signal)
        g = np.array(self.g_signal)
        b = np.array(self.b_signal)
        
        # Normalize signals
        r_norm = (r - np.mean(r)) / np.std(r)
        g_norm = (g - np.mean(g)) / np.std(g)
        b_norm = (b - np.mean(b)) / np.std(b)
        
        # POS algorithm
        # Project signals onto plane orthogonal to skin tone
        # Simplified implementation
        pos_signal = g_norm - 0.5 * (r_norm + b_norm)
        
        # Apply bandpass filter
        filtered_signal = self._apply_bandpass_filter(pos_signal)
        
        # Calculate heart rate
        hr = self._estimate_heart_rate(filtered_signal)
        
        return hr, filtered_signal
    
    def green_channel_method(self) -> Tuple[float, np.ndarray]:
        """
        Simple green channel method (baseline).
        
        Returns:
            Tuple of (heart_rate, filtered_signal)
        """
        if len(self.g_signal) < 30:
            return 0.0, np.array([])
        
        # Use green channel directly
        g = np.array(self.g_signal)
        
        # Normalize
        g_norm = (g - np.mean(g)) / np.std(g)
        
        # Apply bandpass filter
        filtered_signal = self._apply_bandpass_filter(g_norm)
        
        # Calculate heart rate
        hr = self._estimate_heart_rate(filtered_signal)
        
        return hr, filtered_signal
    
    def _apply_bandpass_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """
        Apply bandpass filter to signal.
        
        Args:
            signal_data: Input signal
            
        Returns:
            Filtered signal
        """
        # Design bandpass filter
        nyquist = self.fps / 2
        low = self.low_cutoff / nyquist
        high = self.high_cutoff / nyquist
        
        # Butterworth bandpass filter
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal_data)
        
        return filtered
    
    def _estimate_heart_rate(self, signal_data: np.ndarray) -> float:
        """
        Estimate heart rate from filtered signal using FFT.
        
        Args:
            signal_data: Filtered signal
            
        Returns:
            Estimated heart rate in BPM
        """
        if len(signal_data) < 30:
            return 0.0
        
        # Apply window function
        window = windows.hann(len(signal_data))
        windowed_signal = signal_data * window
        
        # Compute FFT
        fft_result = fft(windowed_signal)
        freqs = fftfreq(len(signal_data), 1/self.fps)
        
        # Get positive frequencies only
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_result[:len(freqs)//2])
        
        # Find peak in heart rate range
        hr_min_idx = np.argmin(np.abs(positive_freqs - self.min_hr/60))
        hr_max_idx = np.argmin(np.abs(positive_freqs - self.max_hr/60))
        
        # Find maximum in heart rate range
        hr_range_fft = positive_fft[hr_min_idx:hr_max_idx]
        hr_range_freqs = positive_freqs[hr_min_idx:hr_max_idx]
        
        if len(hr_range_fft) == 0:
            return 0.0
        
        max_idx = np.argmax(hr_range_fft)
        peak_freq = hr_range_freqs[max_idx]
        
        # Convert to BPM
        heart_rate = peak_freq * 60
        
        return float(heart_rate)
    
    def process_frame(self, roi: np.ndarray) -> Tuple[float, float, np.ndarray]:
        """
        Process a single frame and return heart rate estimate.
        
        Args:
            roi: Region of interest
            
        Returns:
            Tuple of (heart_rate, signal_quality, filtered_signal)
        """
        timestamp = time.time()
        self.add_frame_data(roi, timestamp)
        
        # Use chrominance method as primary
        hr, filtered_signal = self.chrominance_method()
        
        # Calculate signal quality
        quality = self._calculate_signal_quality(filtered_signal)
        
        self.current_hr = hr
        self.signal_quality = quality
        
        return hr, quality, filtered_signal
    
    def _calculate_signal_quality(self, signal_data: np.ndarray) -> float:
        """
        Calculate signal quality metric.
        
        Args:
            signal_data: Filtered signal
            
        Returns:
            Quality score (0-1)
        """
        if len(signal_data) < 10:
            return 0.0
        
        # Calculate signal-to-noise ratio approximation
        signal_power = np.mean(signal_data**2)
        noise_power = np.var(signal_data)
        
        if noise_power == 0:
            return 0.0
        
        snr = signal_power / noise_power
        
        # Normalize to 0-1 range
        quality = min(1.0, snr / 10.0)
        
        return float(quality)
    
    def get_signal_statistics(self) -> dict:
        """
        Get signal statistics for analysis.
        
        Returns:
            Dictionary with signal statistics
        """
        if len(self.r_signal) < 10:
            return {}
        
        r = np.array(self.r_signal)
        g = np.array(self.g_signal)
        b = np.array(self.b_signal)
        
        stats = {
            'r_mean': float(np.mean(r)),
            'g_mean': float(np.mean(g)),
            'b_mean': float(np.mean(b)),
            'r_std': float(np.std(r)),
            'g_std': float(np.std(g)),
            'b_std': float(np.std(b)),
            'signal_length': len(self.r_signal),
            'current_hr': self.current_hr,
            'signal_quality': self.signal_quality
        }
        
        return stats
    
    def reset(self):
        """Reset signal buffers."""
        self.r_signal.clear()
        self.g_signal.clear()
        self.b_signal.clear()
        self.timestamps.clear()
        self.current_hr = 0.0
        self.signal_quality = 0.0 