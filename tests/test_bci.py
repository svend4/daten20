"""
Tests for Brain-Computer Interface (v4.4)

Tests for EEG signal processing and BCI interface.
"""

import pytest
import numpy as np


class TestSignalProcessing:
    """Test EEG Signal Processing (v4.4)"""

    def test_import_signal_processor(self):
        """Test importing SignalProcessor"""
        from bci.signal_processing import (
            SignalProcessor,
            BandPower,
            SignalQuality,
            SignalFeatures
        )
        assert SignalProcessor is not None
        assert BandPower.ALPHA is not None
        assert SignalQuality.GOOD is not None

    def test_create_signal_processor(self):
        """Test creating signal processor"""
        from bci.signal_processing import SignalProcessor, SignalProcessingConfig

        config = SignalProcessingConfig(
            sampling_rate_hz=256,
            notch_filter_hz=50.0,
            highpass_hz=0.5,
            lowpass_hz=50.0
        )

        processor = SignalProcessor(config)
        assert processor is not None
        assert processor.config.sampling_rate_hz == 256

    def test_filter_signal(self):
        """Test signal filtering"""
        from bci.signal_processing import SignalProcessor

        processor = SignalProcessor()

        # Generate fake EEG signal (8 channels, 256 samples)
        signal = np.random.randn(8, 256) * 10  # Simulate EEG with noise

        filtered_signal = processor.filter_signal(signal)

        assert filtered_signal.shape == signal.shape
        assert isinstance(filtered_signal, np.ndarray)

    def test_remove_artifacts(self):
        """Test artifact removal"""
        from bci.signal_processing import SignalProcessor

        processor = SignalProcessor()

        # Generate signal with artifacts
        signal = np.random.randn(8, 256) * 10
        # Add artifact (large amplitude spike)
        signal[:, 50:60] = 200  # Artifact above threshold

        cleaned_signal, artifact_indices = processor.remove_artifacts(signal)

        assert isinstance(cleaned_signal, np.ndarray)
        assert isinstance(artifact_indices, list)
        # Should detect artifact
        assert len(artifact_indices) > 0

    def test_extract_features(self):
        """Test feature extraction"""
        from bci.signal_processing import SignalProcessor, SignalFeatures

        processor = SignalProcessor()
        signal = np.random.randn(8, 256) * 10

        features = processor.extract_features(signal, channel_idx=0)

        assert isinstance(features, SignalFeatures)
        assert 'alpha' in features.band_powers
        assert 'beta' in features.band_powers
        assert 'theta' in features.band_powers
        assert features.peak_frequency > 0

    def test_compute_band_powers(self):
        """Test band power computation"""
        from bci.signal_processing import SignalProcessor

        processor = SignalProcessor()
        signal = np.random.randn(256) * 10

        band_powers = processor._compute_band_powers(signal)

        assert 'delta' in band_powers
        assert 'theta' in band_powers
        assert 'alpha' in band_powers
        assert 'beta' in band_powers
        assert 'gamma' in band_powers

        # All powers should be non-negative
        for power in band_powers.values():
            assert power >= 0

    def test_compute_attention_level(self):
        """Test attention level computation"""
        from bci.signal_processing import SignalProcessor, SignalFeatures

        processor = SignalProcessor()

        # Create features with high beta (attention)
        features = SignalFeatures()
        features.band_powers = {
            'alpha': 0.5,
            'beta': 1.0,
            'theta': 0.3
        }

        attention = processor.compute_attention_level(features)

        assert 0.0 <= attention <= 1.0
        assert attention > 0  # Should have some attention

    def test_compute_relaxation_level(self):
        """Test relaxation level computation"""
        from bci.signal_processing import SignalProcessor, SignalFeatures

        processor = SignalProcessor()

        # Create features with high alpha (relaxation)
        features = SignalFeatures()
        features.band_powers = {
            'alpha': 1.5,
            'beta': 0.5,
            'theta': 0.3
        }

        relaxation = processor.compute_relaxation_level(features)

        assert 0.0 <= relaxation <= 1.0
        assert relaxation > 0  # Should have some relaxation

    def test_assess_signal_quality(self):
        """Test signal quality assessment"""
        from bci.signal_processing import SignalProcessor, SignalQuality

        processor = SignalProcessor()

        # Good signal
        good_signal = np.random.randn(8, 256) * 5
        quality = processor.assess_signal_quality(good_signal)
        assert quality in [SignalQuality.EXCELLENT, SignalQuality.GOOD,
                          SignalQuality.FAIR, SignalQuality.POOR]

        # Flat signal (no signal)
        flat_signal = np.zeros((8, 256))
        quality = processor.assess_signal_quality(flat_signal)
        assert quality == SignalQuality.NO_SIGNAL


class TestERPDetector:
    """Test Event-Related Potential Detector (v4.4)"""

    def test_import_erp_detector(self):
        """Test importing ERPDetector"""
        from bci.signal_processing import ERPDetector
        assert ERPDetector is not None

    def test_create_erp_detector(self):
        """Test creating ERP detector"""
        from bci.signal_processing import ERPDetector

        detector = ERPDetector()
        assert detector is not None

    def test_detect_p300(self):
        """Test P300 detection"""
        from bci.signal_processing import ERPDetector

        detector = ERPDetector()

        # Generate fake EEG signal with events
        signal = np.random.randn(1000) * 10
        event_times = [1.0, 2.0, 3.0]  # seconds

        p300_amplitudes = detector.detect_p300(
            signal,
            event_times,
            sampling_rate=256
        )

        assert isinstance(p300_amplitudes, list)
        assert len(p300_amplitudes) <= len(event_times)


class TestBCIInterface:
    """Test BCI Interface (v4.4)"""

    def test_import_bci_interface(self):
        """Test importing BCIInterface"""
        from bci.bci_interface import (
            BCIInterface,
            BCIMode,
            MentalCommand,
            MentalState
        )
        assert BCIInterface is not None
        assert BCIMode.PASSIVE is not None
        assert MentalCommand.FOCUS is not None

    def test_create_bci_interface(self):
        """Test creating BCI interface"""
        from bci.bci_interface import BCIInterface, BCIConfig, BCIMode

        config = BCIConfig(
            simulation_mode=True,
            num_channels=8,
            sampling_rate_hz=256,
            mode=BCIMode.PASSIVE
        )

        bci = BCIInterface(config)
        assert bci is not None
        assert bci.config.num_channels == 8

    def test_start_session(self):
        """Test starting BCI session"""
        from bci.bci_interface import BCIInterface, BCIMode

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01", mode=BCIMode.PASSIVE)

        assert session_id is not None
        assert session_id in bci.sessions
        assert session_id in bci.mental_states

    def test_stop_session(self):
        """Test stopping BCI session"""
        from bci.bci_interface import BCIInterface

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01")

        result = bci.stop_session(session_id)
        assert result is True
        assert session_id not in bci.sessions

    def test_calibrate(self):
        """Test BCI calibration"""
        from bci.bci_interface import BCIInterface

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01")

        # Calibrate with sample data
        calibration_data = np.random.randn(8, 256) * 10

        result = bci.calibrate(session_id, calibration_data)
        assert result is True

        session = bci.sessions[session_id]
        assert session.calibrated is True

    def test_process_signal(self):
        """Test signal processing"""
        from bci.bci_interface import BCIInterface, BCIMode

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01", mode=BCIMode.PASSIVE)

        # Process EEG data
        eeg_data = np.random.randn(8, 256) * 10

        result = bci.process_signal(session_id, eeg_data)
        assert result is True

    def test_get_mental_state(self):
        """Test getting mental state"""
        from bci.bci_interface import BCIInterface, MentalState

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01")

        # Process some data first
        eeg_data = np.random.randn(8, 256) * 10
        bci.process_signal(session_id, eeg_data)

        mental_state = bci.get_mental_state(session_id)

        assert isinstance(mental_state, MentalState)
        assert 0.0 <= mental_state.attention <= 1.0
        assert 0.0 <= mental_state.relaxation <= 1.0
        assert 0.0 <= mental_state.stress <= 1.0

    def test_get_attention_level(self):
        """Test getting attention level"""
        from bci.bci_interface import BCIInterface

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01")

        eeg_data = np.random.randn(8, 256) * 10
        bci.process_signal(session_id, eeg_data)

        attention = bci.get_attention_level(session_id)

        assert 0.0 <= attention <= 1.0

    def test_register_command_callback(self):
        """Test registering command callback"""
        from bci.bci_interface import BCIInterface, MentalCommand

        bci = BCIInterface()

        callback_triggered = []

        def test_callback(session_id):
            callback_triggered.append(session_id)

        bci.register_command_callback(MentalCommand.FOCUS, test_callback)

        assert MentalCommand.FOCUS in bci.command_callbacks

    def test_send_mental_command(self):
        """Test sending mental command"""
        from bci.bci_interface import BCIInterface, MentalCommand

        bci = BCIInterface()
        session_id = bci.start_session("user_test_01")

        callback_triggered = []

        def test_callback(sid):
            callback_triggered.append(sid)

        bci.register_command_callback(MentalCommand.SELECT, test_callback)

        result = bci.send_mental_command(session_id, MentalCommand.SELECT)

        assert result is True
        assert session_id in callback_triggered


class TestBCIFeedback:
    """Test BCI Feedback System (v4.4)"""

    def test_import_bci_feedback(self):
        """Test importing BCIFeedback"""
        from bci.bci_interface import BCIFeedback
        assert BCIFeedback is not None

    def test_create_bci_feedback(self):
        """Test creating BCI feedback system"""
        from bci.bci_interface import BCIFeedback

        feedback_system = BCIFeedback()
        assert feedback_system is not None

    def test_provide_feedback(self):
        """Test providing feedback"""
        from bci.bci_interface import BCIFeedback, MentalState
        from bci.signal_processing import SignalQuality

        feedback_system = BCIFeedback()

        mental_state = MentalState(
            attention=0.9,
            relaxation=0.5,
            stress=0.3
        )

        feedback = feedback_system.provide_feedback(
            mental_state,
            SignalQuality.GOOD
        )

        assert 'signal' in feedback
        assert 'attention' in feedback
        assert 'relaxation' in feedback
        assert isinstance(feedback['signal'], str)


class TestBCIManager:
    """Test BCI Manager Integration (v4.4)"""

    def test_import_bci_manager(self):
        """Test importing BCIManager"""
        from bci import BCIManager
        assert BCIManager is not None

    def test_create_bci_manager(self):
        """Test creating BCI manager"""
        from bci import BCIManager

        manager = BCIManager()
        assert manager is not None

    def test_get_bci_manager_singleton(self):
        """Test getting singleton BCI manager"""
        from bci import get_bci_manager

        manager1 = get_bci_manager()
        manager2 = get_bci_manager()

        # Should be same instance
        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
