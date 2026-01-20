"""
BCI Signal Processing - v4.4

EEG signal processing and feature extraction for brain-computer interfaces.

Version: 4.4.0
"""

__version__ = '4.4.0'

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BandPower(Enum):
    """EEG frequency bands"""
    DELTA = "delta"      # 0.5-4 Hz (deep sleep)
    THETA = "theta"      # 4-8 Hz (drowsiness, meditation)
    ALPHA = "alpha"      # 8-13 Hz (relaxed, eyes closed)
    BETA = "beta"        # 13-30 Hz (active thinking, focus)
    GAMMA = "gamma"      # 30-100 Hz (cognitive processing)


class SignalQuality(Enum):
    """Signal quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NO_SIGNAL = "no_signal"


@dataclass
class EEGChannel:
    """EEG channel information"""
    name: str
    location: str        # e.g., "Fp1", "Fp2", "C3", "C4"
    impedance: float = 0.0  # kΩ
    enabled: bool = True


@dataclass
class SignalFeatures:
    """Extracted signal features"""
    band_powers: Dict[str, float] = field(default_factory=dict)
    peak_frequency: float = 0.0
    spectral_edge_frequency: float = 0.0
    hjorth_activity: float = 0.0
    hjorth_mobility: float = 0.0
    hjorth_complexity: float = 0.0
    sample_entropy: float = 0.0


@dataclass
class SignalProcessingConfig:
    """Signal processing configuration"""
    sampling_rate_hz: int = 256
    notch_filter_hz: float = 50.0  # Power line frequency (50 or 60 Hz)
    highpass_hz: float = 0.5
    lowpass_hz: float = 50.0
    epoch_length_sec: float = 1.0
    artifact_rejection: bool = True
    artifact_threshold: float = 100.0  # μV


class SignalProcessor:
    """
    EEG Signal Processor

    Processes raw EEG signals for BCI applications:
    - Filtering (bandpass, notch)
    - Artifact rejection (eye blinks, muscle activity)
    - Feature extraction (band powers, Hjorth parameters)
    - Spectral analysis (FFT, PSD)
    - Time-frequency analysis (wavelet transform)

    Example:
        >>> processor = SignalProcessor()
        >>> filtered = processor.filter_signal(raw_eeg)
        >>> features = processor.extract_features(filtered)
        >>> attention = processor.compute_attention_level(features)
    """

    def __init__(self, config: Optional[SignalProcessingConfig] = None):
        """
        Initialize Signal Processor

        Args:
            config: Signal processing configuration
        """
        self.config = config or SignalProcessingConfig()
        logger.info(f"Signal Processor initialized - Sampling rate: {self.config.sampling_rate_hz} Hz")

    def filter_signal(self, signal: np.ndarray) -> np.ndarray:
        """
        Apply filtering to raw EEG signal

        Args:
            signal: Raw EEG signal (channels x samples)

        Returns:
            Filtered signal
        """
        # Apply bandpass filter
        filtered = self._bandpass_filter(
            signal,
            self.config.highpass_hz,
            self.config.lowpass_hz,
            self.config.sampling_rate_hz
        )

        # Apply notch filter to remove power line interference
        filtered = self._notch_filter(
            filtered,
            self.config.notch_filter_hz,
            self.config.sampling_rate_hz
        )

        logger.debug(f"Filtered signal shape: {filtered.shape}")
        return filtered

    def remove_artifacts(self, signal: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """
        Remove artifacts from EEG signal

        Args:
            signal: EEG signal

        Returns:
            Tuple of (cleaned signal, artifact indices)
        """
        if not self.config.artifact_rejection:
            return signal, []

        artifact_indices = []

        # Detect artifacts using amplitude threshold
        for i in range(signal.shape[1]):
            epoch = signal[:, i:i+int(self.config.epoch_length_sec * self.config.sampling_rate_hz)]
            if epoch.size > 0:
                max_amplitude = np.max(np.abs(epoch))
                if max_amplitude > self.config.artifact_threshold:
                    artifact_indices.append(i)

        logger.info(f"Detected {len(artifact_indices)} artifacts")

        # Remove artifact epochs
        mask = np.ones(signal.shape[1], dtype=bool)
        mask[artifact_indices] = False
        cleaned = signal[:, mask]

        return cleaned, artifact_indices

    def extract_features(self, signal: np.ndarray, channel_idx: int = 0) -> SignalFeatures:
        """
        Extract features from EEG signal

        Args:
            signal: Filtered EEG signal
            channel_idx: Channel index to analyze

        Returns:
            Extracted features
        """
        channel_signal = signal[channel_idx, :] if signal.ndim > 1 else signal

        features = SignalFeatures()

        # Extract band powers
        features.band_powers = self._compute_band_powers(channel_signal)

        # Compute peak frequency
        features.peak_frequency = self._compute_peak_frequency(channel_signal)

        # Compute Hjorth parameters
        activity, mobility, complexity = self._compute_hjorth_parameters(channel_signal)
        features.hjorth_activity = activity
        features.hjorth_mobility = mobility
        features.hjorth_complexity = complexity

        # Compute entropy
        features.sample_entropy = self._compute_sample_entropy(channel_signal)

        logger.debug(f"Extracted features - Alpha power: {features.band_powers.get('alpha', 0):.3f}")
        return features

    def compute_attention_level(self, features: SignalFeatures) -> float:
        """
        Compute attention level from features

        Args:
            features: Signal features

        Returns:
            Attention level (0-1)
        """
        # Simple attention metric: beta / (alpha + theta)
        beta = features.band_powers.get('beta', 0.0)
        alpha = features.band_powers.get('alpha', 0.0)
        theta = features.band_powers.get('theta', 0.0)

        if alpha + theta > 0:
            attention = beta / (alpha + theta)
            # Normalize to 0-1 range
            attention = min(1.0, attention / 2.0)
        else:
            attention = 0.0

        return attention

    def compute_relaxation_level(self, features: SignalFeatures) -> float:
        """
        Compute relaxation level from features

        Args:
            features: Signal features

        Returns:
            Relaxation level (0-1)
        """
        # Simple relaxation metric: alpha / (beta + theta)
        alpha = features.band_powers.get('alpha', 0.0)
        beta = features.band_powers.get('beta', 0.0)
        theta = features.band_powers.get('theta', 0.0)

        if beta + theta > 0:
            relaxation = alpha / (beta + theta)
            # Normalize to 0-1 range
            relaxation = min(1.0, relaxation)
        else:
            relaxation = 0.0

        return relaxation

    def assess_signal_quality(self, signal: np.ndarray) -> SignalQuality:
        """
        Assess EEG signal quality

        Args:
            signal: EEG signal

        Returns:
            Signal quality level
        """
        # Check signal variance
        variance = np.var(signal)

        # Check for flat signal
        if variance < 0.1:
            return SignalQuality.NO_SIGNAL

        # Check signal-to-noise ratio (simplified)
        mean_power = np.mean(np.abs(signal))

        if mean_power > 50:
            return SignalQuality.POOR
        elif mean_power > 20:
            return SignalQuality.FAIR
        elif mean_power > 10:
            return SignalQuality.GOOD
        else:
            return SignalQuality.EXCELLENT

    # Private helper methods

    def _bandpass_filter(self,
                        signal: np.ndarray,
                        lowcut: float,
                        highcut: float,
                        fs: float,
                        order: int = 5) -> np.ndarray:
        """Apply bandpass filter"""
        # Simplified butterworth filter
        # In real implementation, use scipy.signal.butter + filtfilt
        return signal  # Placeholder

    def _notch_filter(self,
                     signal: np.ndarray,
                     freq: float,
                     fs: float,
                     quality: float = 30.0) -> np.ndarray:
        """Apply notch filter"""
        # Remove power line interference
        # In real implementation, use scipy.signal.iirnotch + filtfilt
        return signal  # Placeholder

    def _compute_band_powers(self, signal: np.ndarray) -> Dict[str, float]:
        """Compute power in each frequency band"""
        # Compute power spectral density
        freqs, psd = self._compute_psd(signal)

        band_powers = {}

        # Define frequency bands
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }

        # Compute power in each band
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            band_powers[band_name] = float(np.sum(psd[mask]))

        return band_powers

    def _compute_psd(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute power spectral density

        Returns:
            Tuple of (frequencies, power spectral density)
        """
        # Simplified PSD using FFT
        # In real implementation, use scipy.signal.welch
        n = len(signal)
        fft_vals = np.fft.fft(signal)
        fft_freq = np.fft.fftfreq(n, 1/self.config.sampling_rate_hz)

        # Take only positive frequencies
        positive_freq_idx = fft_freq > 0
        freqs = fft_freq[positive_freq_idx]
        psd = np.abs(fft_vals[positive_freq_idx]) ** 2

        return freqs, psd

    def _compute_peak_frequency(self, signal: np.ndarray) -> float:
        """Compute dominant frequency"""
        freqs, psd = self._compute_psd(signal)
        peak_idx = np.argmax(psd)
        return float(freqs[peak_idx])

    def _compute_hjorth_parameters(self, signal: np.ndarray) -> Tuple[float, float, float]:
        """
        Compute Hjorth parameters (activity, mobility, complexity)

        Hjorth parameters describe signal properties:
        - Activity: Signal variance
        - Mobility: Mean frequency (related to first derivative)
        - Complexity: Change in frequency (related to second derivative)
        """
        # Activity
        activity = np.var(signal)

        # First derivative
        diff1 = np.diff(signal)
        mobility = np.sqrt(np.var(diff1) / activity) if activity > 0 else 0.0

        # Second derivative
        diff2 = np.diff(diff1)
        complexity_numerator = np.sqrt(np.var(diff2) / np.var(diff1)) if np.var(diff1) > 0 else 0.0
        complexity = complexity_numerator / mobility if mobility > 0 else 0.0

        return float(activity), float(mobility), float(complexity)

    def _compute_sample_entropy(self, signal: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Compute sample entropy (measure of signal regularity)

        Lower values indicate more regular/predictable signals.
        """
        # Simplified entropy calculation
        # In real implementation, use proper sample entropy algorithm
        return float(np.std(signal))


class ERPDetector:
    """
    Event-Related Potential (ERP) Detector

    Detects P300 and other ERPs for BCI applications.
    P300 is a positive deflection at ~300ms after rare/target stimuli.
    """

    def __init__(self):
        """Initialize ERP Detector"""
        self.templates: Dict[str, np.ndarray] = {}
        logger.info("ERP Detector initialized")

    def detect_p300(self,
                   signal: np.ndarray,
                   event_times: List[float],
                   sampling_rate: int = 256) -> List[float]:
        """
        Detect P300 responses

        Args:
            signal: EEG signal
            event_times: Stimulus presentation times (seconds)
            sampling_rate: Sampling rate (Hz)

        Returns:
            List of P300 amplitudes for each event
        """
        p300_amplitudes = []

        # P300 window: 250-500ms after stimulus
        window_start = int(0.25 * sampling_rate)
        window_end = int(0.5 * sampling_rate)

        for event_time in event_times:
            event_sample = int(event_time * sampling_rate)
            if event_sample + window_end < len(signal):
                epoch = signal[event_sample + window_start:event_sample + window_end]
                # Find peak amplitude in P300 window
                p300_amp = np.max(epoch)
                p300_amplitudes.append(float(p300_amp))

        logger.debug(f"Detected {len(p300_amplitudes)} P300 responses")
        return p300_amplitudes


__all__ = [
    'SignalProcessor',
    'ERPDetector',
    'BandPower',
    'SignalQuality',
    'EEGChannel',
    'SignalFeatures',
    'SignalProcessingConfig',
]
