"""
Quality Metrics Module
Provides comprehensive signal quality assessment for rPPG applications.
"""

import numpy as np
from scipy import signal
from scipy.stats import pearsonr
from typing import Dict, Tuple, List
import time


class QualityMetrics:
    """Advanced quality metrics for rPPG signal assessment."""
    
    def __init__(self):
        """Initialize quality metrics calculator."""
        self.metrics_history = []
        self.quality_thresholds = {
            'snr_threshold': 2.0,
            'motion_threshold': 0.1,
            'lighting_threshold': 0.3,
            'face_quality_threshold': 0.5
        }
    
    def calculate_comprehensive_quality(self, 
                                      rgb_signals: Tuple[List[float], List[float], List[float]],
                                      face_quality: float,
                                      motion_score: float = 0.0) -> Dict[str, float]:
        """
        Calculate comprehensive quality metrics.
        
        Args:
            rgb_signals: Tuple of (R, G, B) signal lists
            face_quality: Face detection quality (0-1)
            motion_score: Motion artifact score (0-1)
            
        Returns:
            Dictionary of quality metrics
        """
        r_signal, g_signal, b_signal = rgb_signals
        
        if len(r_signal) < 30:
            return self._get_default_metrics()
        
        # Convert to numpy arrays
        r = np.array(r_signal)
        g = np.array(g_signal)
        b = np.array(b_signal)
        
        metrics = {}
        
        # Signal-to-Noise Ratio
        metrics['snr'] = self._calculate_snr(g)
        
        # Signal stability
        metrics['stability'] = self._calculate_stability(g)
        
        # Lighting consistency
        metrics['lighting_consistency'] = self._calculate_lighting_consistency(r, g, b)
        
        # Motion artifacts
        metrics['motion_artifacts'] = motion_score
        
        # Face detection quality
        metrics['face_quality'] = face_quality
        
        # Overall quality score
        metrics['overall_quality'] = self._calculate_overall_quality(metrics)
        
        # Signal strength
        metrics['signal_strength'] = self._calculate_signal_strength(g)
        
        # Frequency domain quality
        metrics['frequency_quality'] = self._calculate_frequency_quality(g)
        
        # Store metrics history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
        
        return metrics
    
    def _calculate_snr(self, signal_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""
        if len(signal_data) < 10:
            return 0.0
        
        # Apply bandpass filter to isolate heart rate component
        fs = 30  # Assuming 30 fps
        low = 0.7 / (fs/2)
        high = 4.0 / (fs/2)
        
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal_data)
        
        # Calculate SNR
        signal_power = np.mean(filtered**2)
        noise_power = np.var(signal_data - filtered)
        
        if noise_power == 0:
            return 0.0
        
        snr = 10 * np.log10(signal_power / noise_power)
        return max(0.0, min(1.0, snr / 20.0))  # Normalize to 0-1
    
    def _calculate_stability(self, signal_data: np.ndarray) -> float:
        """Calculate signal stability."""
        if len(signal_data) < 20:
            return 0.0
        
        # Calculate coefficient of variation
        mean_val = np.mean(signal_data)
        std_val = np.std(signal_data)
        
        if mean_val == 0:
            return 0.0
        
        cv = std_val / mean_val
        stability = max(0.0, 1.0 - cv)
        
        return stability
    
    def _calculate_lighting_consistency(self, r: np.ndarray, g: np.ndarray, b: np.ndarray) -> float:
        """Calculate lighting consistency across RGB channels."""
        if len(r) < 10:
            return 0.0
        
        # Calculate correlation between channels
        try:
            r_g_corr, _ = pearsonr(r, g)
            r_b_corr, _ = pearsonr(r, b)
            g_b_corr, _ = pearsonr(g, b)
            
            # Average correlation
            avg_corr = (r_g_corr + r_b_corr + g_b_corr) / 3
            consistency = max(0.0, avg_corr)
            
        except:
            consistency = 0.0
        
        return consistency
    
    def _calculate_signal_strength(self, signal_data: np.ndarray) -> float:
        """Calculate signal strength."""
        if len(signal_data) < 10:
            return 0.0
        
        # Calculate RMS of signal
        rms = np.sqrt(np.mean(signal_data**2))
        
        # Normalize to 0-1 range
        strength = min(1.0, rms / 100.0)
        
        return strength
    
    def _calculate_frequency_quality(self, signal_data: np.ndarray) -> float:
        """Calculate frequency domain quality."""
        if len(signal_data) < 30:
            return 0.0
        
        # Compute power spectral density
        freqs, psd = signal.welch(signal_data, fs=30, nperseg=min(256, len(signal_data)//2))
        
        # Find peak in heart rate range (0.7-4.0 Hz)
        hr_mask = (freqs >= 0.7) & (freqs <= 4.0)
        hr_psd = psd[hr_mask]
        hr_freqs = freqs[hr_mask]
        
        if len(hr_psd) == 0:
            return 0.0
        
        # Calculate peak prominence
        peak_idx = np.argmax(hr_psd)
        peak_power = hr_psd[peak_idx]
        
        # Calculate total power in HR range
        total_power = np.sum(hr_psd)
        
        if total_power == 0:
            return 0.0
        
        # Quality based on peak prominence
        quality = peak_power / total_power
        
        return quality
    
    def _calculate_overall_quality(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score."""
        weights = {
            'snr': 0.25,
            'stability': 0.20,
            'lighting_consistency': 0.15,
            'motion_artifacts': 0.15,
            'face_quality': 0.15,
            'signal_strength': 0.05,
            'frequency_quality': 0.05
        }
        
        overall_quality = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                overall_quality += metrics[metric] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return overall_quality / total_weight
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """Get default metrics when insufficient data."""
        return {
            'snr': 0.0,
            'stability': 0.0,
            'lighting_consistency': 0.0,
            'motion_artifacts': 0.0,
            'face_quality': 0.0,
            'overall_quality': 0.0,
            'signal_strength': 0.0,
            'frequency_quality': 0.0
        }
    
    def get_quality_status(self, metrics: Dict[str, float]) -> str:
        """
        Get quality status based on metrics.
        
        Args:
            metrics: Quality metrics dictionary
            
        Returns:
            Quality status string
        """
        overall_quality = metrics.get('overall_quality', 0.0)
        
        if overall_quality >= 0.8:
            return "Excellent"
        elif overall_quality >= 0.6:
            return "Good"
        elif overall_quality >= 0.4:
            return "Fair"
        elif overall_quality >= 0.2:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_quality_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """
        Get recommendations for improving signal quality.
        
        Args:
            metrics: Quality metrics dictionary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if metrics.get('face_quality', 0.0) < 0.5:
            recommendations.append("Improve face detection - ensure face is clearly visible")
        
        if metrics.get('lighting_consistency', 0.0) < 0.3:
            recommendations.append("Improve lighting - ensure consistent, even lighting")
        
        if metrics.get('motion_artifacts', 0.0) > 0.5:
            recommendations.append("Reduce motion - stay still during measurement")
        
        if metrics.get('snr', 0.0) < 0.3:
            recommendations.append("Improve signal quality - check camera positioning and lighting")
        
        if metrics.get('stability', 0.0) < 0.5:
            recommendations.append("Improve stability - ensure consistent camera distance")
        
        if not recommendations:
            recommendations.append("Signal quality is good - continue monitoring")
        
        return recommendations
    
    def get_trend_analysis(self) -> Dict[str, float]:
        """
        Analyze quality trends over time.
        
        Returns:
            Dictionary with trend information
        """
        if len(self.metrics_history) < 10:
            return {}
        
        # Calculate trends for key metrics
        trends = {}
        
        for metric in ['overall_quality', 'snr', 'stability']:
            values = [m.get(metric, 0.0) for m in self.metrics_history]
            if len(values) >= 2:
                # Simple linear trend
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                trends[f'{metric}_trend'] = slope
        
        return trends 