"""
BCI Signal Processing - v4.4 (Pure Python)

EEG signal processing and feature extraction for brain-computer interfaces.
Pure Python implementation with mock/simplified DSP algorithms.

Version: 4.4.0
"""

__version__ = '4.4.0'

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import math
import random
import logging

logger = logging.getLogger(__name__)

# Type alias for signal data
SignalData = Union[List[List[float]], List[float]]


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
    EEG Signal Processor (Pure Python - Mock/Simplified)

    Processes raw EEG signals for BCI applications:
    - Filtering (bandpass, notch) - Mock
    - Artifact rejection (eye blinks, muscle activity) - Simplified
    - Feature extraction (band powers, Hjorth parameters) - Mock
    - Spectral analysis (FFT, PSD) - Mock
    - Time-frequency analysis (wavelet transform) - Mock

    Note: This Pure Python version uses simplified/mock algorithms.
    For production use, consider using the NumPy version.

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
        logger.info(f"Signal Processor initialized (Pure Python) - Sampling rate: {self.config.sampling_rate_hz} Hz")

    def filter_signal(self, signal: SignalData) -> SignalData:
        """
        Apply filtering to raw EEG signal (Mock)

        Args:
            signal: Raw EEG signal (channels x samples or samples)

        Returns:
            Filtered signal (mock - returns input unchanged)
        """
        # Mock filtering - in Pure Python, we just return the signal
        # Real implementation would use IIR/FIR filters
        logger.debug(f"Mock: Filtered signal")
        return signal

    def remove_artifacts(self, signal: SignalData) -> Tuple[SignalData, List[int]]:
        """
        Remove artifacts from EEG signal (Simplified)

        Args:
            signal: EEG signal

        Returns:
            Tuple of (cleaned signal, artifact indices)
        """
        if not self.config.artifact_rejection:
            return signal, []

        artifact_indices = []

        # Detect artifacts using amplitude threshold
        if isinstance(signal, list) and len(signal) > 0:
            if isinstance(signal[0], list):
                # Multi-channel
                for i in range(len(signal[0])):
                    epoch_length = int(self.config.epoch_length_sec * self.config.sampling_rate_hz)
                    if i + epoch_length < len(signal[0]):
                        epoch_values = []
                        for ch in range(len(signal)):
                            epoch_values.extend([abs(signal[ch][j]) for j in range(i, min(i + epoch_length, len(signal[ch])))])

                        if epoch_values:
                            max_amplitude = max(epoch_values)
                            if max_amplitude > self.config.artifact_threshold:
                                artifact_indices.append(i)
            else:
                # Single channel
                for i in range(len(signal)):
                    epoch_length = int(self.config.epoch_length_sec * self.config.sampling_rate_hz)
                    if i + epoch_length < len(signal):
                        epoch = signal[i:i + epoch_length]
                        max_amplitude = max(abs(v) for v in epoch)
                        if max_amplitude > self.config.artifact_threshold:
                            artifact_indices.append(i)

        logger.info(f"Detected {len(artifact_indices)} artifacts")

        # For simplicity, return original signal
        # Real implementation would remove artifact epochs
        return signal, artifact_indices

    def extract_features(self, signal: SignalData, channel_idx: int = 0) -> SignalFeatures:
        """
        Extract features from EEG signal (Mock)

        Args:
            signal: Filtered EEG signal
            channel_idx: Channel index to analyze

        Returns:
            Extracted features (mock values)
        """
        # Extract channel signal
        if isinstance(signal, list) and len(signal) > 0:
            if isinstance(signal[0], list):
                # Multi-channel
                if channel_idx < len(signal):
                    channel_signal = signal[channel_idx]
                else:
                    channel_signal = signal[0] if signal else []
            else:
                # Single channel
                channel_signal = signal
        else:
            channel_signal = []

        features = SignalFeatures()

        # Mock band powers
        features.band_powers = self._compute_band_powers(channel_signal)

        # Mock peak frequency
        features.peak_frequency = self._compute_peak_frequency(channel_signal)

        # Compute Hjorth parameters (simplified)
        activity, mobility, complexity = self._compute_hjorth_parameters(channel_signal)
        features.hjorth_activity = activity
        features.hjorth_mobility = mobility
        features.hjorth_complexity = complexity

        # Mock entropy
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

    def assess_signal_quality(self, signal: SignalData) -> SignalQuality:
        """
        Assess EEG signal quality (Simplified)

        Args:
            signal: EEG signal

        Returns:
            Signal quality level
        """
        # Flatten signal for analysis
        flat_signal = []
        if isinstance(signal, list) and len(signal) > 0:
            if isinstance(signal[0], list):
                # Multi-channel - flatten
                for ch in signal:
                    flat_signal.extend(ch)
            else:
                flat_signal = signal

        if not flat_signal:
            return SignalQuality.NO_SIGNAL

        # Check signal variance (simplified)
        variance = self._variance(flat_signal)

        # Check for flat signal
        if variance < 0.1:
            return SignalQuality.NO_SIGNAL

        # Check signal power (simplified)
        mean_power = sum(abs(v) for v in flat_signal) / len(flat_signal)

        if mean_power > 50:
            return SignalQuality.POOR
        elif mean_power > 20:
            return SignalQuality.FAIR
        elif mean_power > 10:
            return SignalQuality.GOOD
        else:
            return SignalQuality.EXCELLENT

    # Private helper methods

    def _variance(self, data: List[float]) -> float:
        """Compute variance"""
        if not data:
            return 0.0
        mean = sum(data) / len(data)
        return sum((x - mean) ** 2 for x in data) / len(data)

    def _std(self, data: List[float]) -> float:
        """Compute standard deviation"""
        return math.sqrt(self._variance(data))

    def _compute_band_powers(self, signal: List[float]) -> Dict[str, float]:
        """Compute power in each frequency band (Mock)"""
        # Mock band powers with random values
        # In real implementation, use FFT + frequency band integration

        if not signal:
            return {
                'delta': 0.0,
                'theta': 0.0,
                'alpha': 0.0,
                'beta': 0.0,
                'gamma': 0.0
            }

        # Use signal characteristics to generate deterministic-ish values
        signal_sum = sum(abs(v) for v in signal[:100]) if len(signal) > 100 else sum(abs(v) for v in signal)
        seed_value = int(signal_sum * 1000) % 10000
        random.seed(seed_value)

        band_powers = {
            'delta': random.uniform(0.1, 0.5),
            'theta': random.uniform(0.2, 0.6),
            'alpha': random.uniform(0.3, 0.8),
            'beta': random.uniform(0.4, 1.0),
            'gamma': random.uniform(0.1, 0.4)
        }

        random.seed()  # Reset seed
        return band_powers

    def _compute_psd(self, signal: List[float]) -> Tuple[List[float], List[float]]:
        """
        Compute power spectral density (Mock)

        Returns:
            Tuple of (frequencies, power spectral density)
        """
        # Mock PSD
        # In real implementation, use FFT
        num_freqs = 128
        freqs = [i * self.config.sampling_rate_hz / (2 * num_freqs) for i in range(num_freqs)]

        # Generate mock PSD based on signal characteristics
        if signal:
            signal_sum = sum(abs(v) for v in signal[:100]) if len(signal) > 100 else sum(abs(v) for v in signal)
            seed_value = int(signal_sum * 1000) % 10000
            random.seed(seed_value)
            psd = [random.uniform(0.1, 1.0) for _ in range(num_freqs)]
            random.seed()
        else:
            psd = [0.1] * num_freqs

        return freqs, psd

    def _compute_peak_frequency(self, signal: List[float]) -> float:
        """Compute dominant frequency (Mock)"""
        freqs, psd = self._compute_psd(signal)
        if psd:
            peak_idx = psd.index(max(psd))
            return freqs[peak_idx]
        return 0.0

    def _compute_hjorth_parameters(self, signal: List[float]) -> Tuple[float, float, float]:
        """
        Compute Hjorth parameters (activity, mobility, complexity) - Simplified

        Hjorth parameters describe signal properties:
        - Activity: Signal variance
        - Mobility: Mean frequency (related to first derivative)
        - Complexity: Change in frequency (related to second derivative)
        """
        if not signal or len(signal) < 3:
            return 0.0, 0.0, 0.0

        # Activity (variance)
        activity = self._variance(signal)

        # First derivative (approximation)
        diff1 = [signal[i+1] - signal[i] for i in range(len(signal) - 1)]
        var_diff1 = self._variance(diff1)
        mobility = math.sqrt(var_diff1 / activity) if activity > 0 else 0.0

        # Second derivative (approximation)
        if len(diff1) > 1:
            diff2 = [diff1[i+1] - diff1[i] for i in range(len(diff1) - 1)]
            var_diff2 = self._variance(diff2)
            complexity_numerator = math.sqrt(var_diff2 / var_diff1) if var_diff1 > 0 else 0.0
            complexity = complexity_numerator / mobility if mobility > 0 else 0.0
        else:
            complexity = 0.0

        return float(activity), float(mobility), float(complexity)

    def _compute_sample_entropy(self, signal: List[float], m: int = 2, r: float = 0.2) -> float:
        """
        Compute sample entropy (measure of signal regularity) - Simplified

        Lower values indicate more regular/predictable signals.
        """
        # Simplified entropy - just return standard deviation
        if not signal:
            return 0.0
        return self._std(signal)


class ERPDetector:
    """
    Event-Related Potential (ERP) Detector (Pure Python - Mock)

    Detects P300 and other ERPs for BCI applications.
    P300 is a positive deflection at ~300ms after rare/target stimuli.
    """

    def __init__(self):
        """Initialize ERP Detector"""
        self.templates: Dict[str, List[float]] = {}
        logger.info("ERP Detector initialized (Pure Python)")

    def detect_p300(self,
                   signal: SignalData,
                   event_times: List[float],
                   sampling_rate: int = 256) -> List[float]:
        """
        Detect P300 responses (Mock)

        Args:
            signal: EEG signal
            event_times: Stimulus presentation times (seconds)
            sampling_rate: Sampling rate (Hz)

        Returns:
            List of P300 amplitudes for each event (mock values)
        """
        p300_amplitudes = []

        # P300 window: 250-500ms after stimulus
        window_start = int(0.25 * sampling_rate)
        window_end = int(0.5 * sampling_rate)

        # Convert signal to flat list
        flat_signal = []
        if isinstance(signal, list) and len(signal) > 0:
            if isinstance(signal[0], list):
                # Multi-channel - use first channel
                flat_signal = signal[0] if signal else []
            else:
                flat_signal = signal

        for event_time in event_times:
            event_sample = int(event_time * sampling_rate)
            if event_sample + window_end < len(flat_signal):
                epoch = flat_signal[event_sample + window_start:event_sample + window_end]
                # Find peak amplitude in P300 window
                p300_amp = max(epoch) if epoch else 0.0
                p300_amplitudes.append(float(p300_amp))
            else:
                # Mock value if not enough data
                p300_amplitudes.append(random.uniform(1.0, 5.0))

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
