"""
HRV Analysis Module
Provides comprehensive Heart Rate Variability analysis for rPPG applications.
"""

import numpy as np
from scipy import signal
from scipy.stats import pearsonr
from typing import Dict, List, Tuple, Optional
import time


class HRVAnalyzer:
    """Advanced HRV analyzer for rPPG applications."""
    
    def __init__(self, min_hr: float = 40.0, max_hr: float = 200.0):
        """
        Initialize HRV analyzer.
        
        Args:
            min_hr: Minimum heart rate (BPM)
            max_hr: Maximum heart rate (BPM)
        """
        self.min_hr = min_hr
        self.max_hr = max_hr
        
        # HRV data storage
        self.rr_intervals = []
        self.heart_rates = []
        self.timestamps = []
        
        # Analysis parameters
        self.min_rr_count = 10  # Minimum RR intervals for analysis
        self.outlier_threshold = 0.5  # RR interval outlier threshold
        
    def add_heart_rate(self, hr: float, timestamp: float):
        """
        Add heart rate measurement.
        
        Args:
            hr: Heart rate in BPM
            timestamp: Measurement timestamp
        """
        if self.min_hr <= hr <= self.max_hr:
            self.heart_rates.append(hr)
            self.timestamps.append(timestamp)
            
            # Calculate RR interval
            if len(self.heart_rates) >= 2:
                rr_interval = 60.0 / hr  # Convert BPM to RR interval in seconds
                self.rr_intervals.append(rr_interval)
            
            # Maintain reasonable buffer size
            if len(self.heart_rates) > 300:  # 10 minutes at 30 fps
                self.heart_rates.pop(0)
                self.timestamps.pop(0)
                if len(self.rr_intervals) > 0:
                    self.rr_intervals.pop(0)
    
    def calculate_hrv_metrics(self) -> Dict[str, float]:
        """
        Calculate comprehensive HRV metrics.
        
        Returns:
            Dictionary of HRV metrics
        """
        if len(self.rr_intervals) < self.min_rr_count:
            return self._get_default_hrv_metrics()
        
        # Clean RR intervals
        clean_rr = self._clean_rr_intervals()
        
        if len(clean_rr) < self.min_rr_count:
            return self._get_default_hrv_metrics()
        
        metrics = {}
        
        # Time domain metrics
        time_metrics = self._calculate_time_domain_metrics(clean_rr)
        metrics.update(time_metrics)
        
        # Frequency domain metrics
        freq_metrics = self._calculate_frequency_domain_metrics(clean_rr)
        metrics.update(freq_metrics)
        
        # Non-linear metrics
        nonlin_metrics = self._calculate_nonlinear_metrics(clean_rr)
        metrics.update(nonlin_metrics)
        
        # Current heart rate
        if len(self.heart_rates) > 0:
            metrics['current_hr'] = self.heart_rates[-1]
        
        return metrics
    
    def _clean_rr_intervals(self) -> List[float]:
        """Clean RR intervals by removing outliers."""
        if len(self.rr_intervals) < 3:
            return self.rr_intervals
        
        rr_array = np.array(self.rr_intervals)
        
        # Remove outliers using median absolute deviation
        median_rr = np.median(rr_array)
        mad = np.median(np.abs(rr_array - median_rr))
        
        # Define outlier threshold
        threshold = median_rr + self.outlier_threshold * mad
        
        # Filter outliers
        clean_rr = [rr for rr in self.rr_intervals if abs(rr - median_rr) <= threshold]
        
        return clean_rr
    
    def _calculate_time_domain_metrics(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate time domain HRV metrics."""
        rr_array = np.array(rr_intervals)
        
        metrics = {}
        
        # Mean RR interval
        metrics['mean_rr'] = np.mean(rr_array)
        
        # Standard deviation of RR intervals (SDNN)
        metrics['sdnn'] = np.std(rr_array)
        
        # Root mean square of successive differences (RMSSD)
        if len(rr_array) >= 2:
            differences = np.diff(rr_array)
            metrics['rmssd'] = np.sqrt(np.mean(differences**2))
        else:
            metrics['rmssd'] = 0.0
        
        # Percentage of successive RR intervals > 50ms (pNN50)
        if len(rr_array) >= 2:
            differences = np.abs(np.diff(rr_array))
            nn50 = np.sum(differences > 0.05)  # 50ms = 0.05s
            metrics['pnn50'] = (nn50 / len(differences)) * 100
        else:
            metrics['pnn50'] = 0.0
        
        # Coefficient of variation
        if metrics['mean_rr'] > 0:
            metrics['cv'] = metrics['sdnn'] / metrics['mean_rr']
        else:
            metrics['cv'] = 0.0
        
        return metrics
    
    def _calculate_frequency_domain_metrics(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate frequency domain HRV metrics."""
        if len(rr_intervals) < 10:
            return {}
        
        rr_array = np.array(rr_intervals)
        
        # Resample to uniform time grid
        # Assume 30 fps, so time step is 1/30 seconds
        time_step = 1.0 / 30.0
        total_time = len(rr_intervals) * time_step
        
        # Create time grid
        time_grid = np.arange(0, total_time, time_step)
        
        # Interpolate RR intervals to uniform grid
        rr_times = np.cumsum(rr_intervals)
        rr_interpolated = np.interp(time_grid, rr_times, rr_intervals)
        
        # Remove DC component
        rr_detrended = rr_interpolated - np.mean(rr_interpolated)
        
        # Apply window function
        window = signal.hann(len(rr_detrended))
        rr_windowed = rr_detrended * window
        
        # Compute power spectral density
        freqs, psd = signal.welch(rr_windowed, fs=30, nperseg=min(256, len(rr_windowed)//2))
        
        metrics = {}
        
        # Define frequency bands
        vlf_mask = (freqs >= 0.0033) & (freqs < 0.04)  # Very Low Frequency
        lf_mask = (freqs >= 0.04) & (freqs < 0.15)     # Low Frequency
        hf_mask = (freqs >= 0.15) & (freqs < 0.4)      # High Frequency
        
        # Calculate power in each band
        vlf_power = np.trapz(psd[vlf_mask], freqs[vlf_mask])
        lf_power = np.trapz(psd[lf_mask], freqs[lf_mask])
        hf_power = np.trapz(psd[hf_mask], freqs[hf_mask])
        
        # Total power
        total_power = vlf_power + lf_power + hf_power
        
        metrics['vlf_power'] = vlf_power
        metrics['lf_power'] = lf_power
        metrics['hf_power'] = hf_power
        metrics['total_power'] = total_power
        
        # Normalized powers
        if total_power > 0:
            metrics['lf_nu'] = (lf_power / (lf_power + hf_power)) * 100
            metrics['hf_nu'] = (hf_power / (lf_power + hf_power)) * 100
        else:
            metrics['lf_nu'] = 0.0
            metrics['hf_nu'] = 0.0
        
        # LF/HF ratio
        if hf_power > 0:
            metrics['lf_hf_ratio'] = lf_power / hf_power
        else:
            metrics['lf_hf_ratio'] = 0.0
        
        return metrics
    
    def _calculate_nonlinear_metrics(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate non-linear HRV metrics."""
        if len(rr_intervals) < 10:
            return {}
        
        rr_array = np.array(rr_intervals)
        
        metrics = {}
        
        # Approximate Entropy (ApEn) - simplified version
        metrics['apen'] = self._calculate_approximate_entropy(rr_array)
        
        # Sample Entropy (SampEn) - simplified version
        metrics['sampen'] = self._calculate_sample_entropy(rr_array)
        
        return metrics
    
    def _calculate_approximate_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """Calculate Approximate Entropy (simplified)."""
        if len(data) < 2*m + 1:
            return 0.0
        
        # Simplified ApEn calculation
        std_data = np.std(data)
        if std_data == 0:
            return 0.0
        
        r_threshold = r * std_data
        
        # Count similar patterns
        phi_m = 0
        phi_m1 = 0
        
        for i in range(len(data) - m):
            pattern_m = data[i:i+m]
            pattern_m1 = data[i:i+m+1]
            
            count_m = 0
            count_m1 = 0
            
            for j in range(len(data) - m):
                if np.all(np.abs(data[j:j+m] - pattern_m) <= r_threshold):
                    count_m += 1
                    if j < len(data) - m - 1 and np.abs(data[j+m] - pattern_m1[-1]) <= r_threshold:
                        count_m1 += 1
            
            if count_m > 0:
                phi_m += np.log(count_m / (len(data) - m))
                phi_m1 += np.log(count_m1 / (len(data) - m))
        
        phi_m /= (len(data) - m)
        phi_m1 /= (len(data) - m)
        
        apen = phi_m - phi_m1
        return max(0.0, apen)
    
    def _calculate_sample_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """Calculate Sample Entropy (simplified)."""
        if len(data) < 2*m + 1:
            return 0.0
        
        # Simplified SampEn calculation
        std_data = np.std(data)
        if std_data == 0:
            return 0.0
        
        r_threshold = r * std_data
        
        # Count similar patterns
        count_m = 0
        count_m1 = 0
        
        for i in range(len(data) - m):
            for j in range(i + 1, len(data) - m):
                if np.all(np.abs(data[j:j+m] - data[i:i+m]) <= r_threshold):
                    count_m += 1
                    if j < len(data) - m - 1 and np.abs(data[j+m] - data[i+m]) <= r_threshold:
                        count_m1 += 1
        
        if count_m == 0:
            return 0.0
        
        sampen = -np.log(count_m1 / count_m)
        return max(0.0, sampen)
    
    def _get_default_hrv_metrics(self) -> Dict[str, float]:
        """Get default HRV metrics when insufficient data."""
        return {
            'mean_rr': 0.0,
            'sdnn': 0.0,
            'rmssd': 0.0,
            'pnn50': 0.0,
            'cv': 0.0,
            'vlf_power': 0.0,
            'lf_power': 0.0,
            'hf_power': 0.0,
            'total_power': 0.0,
            'lf_nu': 0.0,
            'hf_nu': 0.0,
            'lf_hf_ratio': 0.0,
            'apen': 0.0,
            'sampen': 0.0,
            'current_hr': 0.0
        }
    
    def get_hrv_status(self, metrics: Dict[str, float]) -> str:
        """
        Get HRV status based on metrics.
        
        Args:
            metrics: HRV metrics dictionary
            
        Returns:
            HRV status string
        """
        rmssd = metrics.get('rmssd', 0.0)
        
        if rmssd >= 50:
            return "Excellent"
        elif rmssd >= 30:
            return "Good"
        elif rmssd >= 20:
            return "Fair"
        elif rmssd >= 10:
            return "Poor"
        else:
            return "Very Poor"
    
    def reset(self):
        """Reset HRV data."""
        self.rr_intervals.clear()
        self.heart_rates.clear()
        self.timestamps.clear() 