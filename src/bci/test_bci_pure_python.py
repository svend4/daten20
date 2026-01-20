"""
Test BCI modules (Pure Python version)
"""

import sys
import random


def test_signal_processing():
    """Test signal processing module"""
    print("\n=== Testing BCI Signal Processing (Pure Python) ===")

    from bci.signal_processing import (
        SignalProcessor,
        ERPDetector,
        SignalProcessingConfig,
        SignalQuality,
        BandPower,
    )

    # Test SignalProcessor
    config = SignalProcessingConfig(sampling_rate_hz=256)
    processor = SignalProcessor(config)

    # Generate mock EEG signal (8 channels x 256 samples)
    num_channels = 8
    num_samples = 256
    eeg_signal = [[random.gauss(0, 10) for _ in range(num_samples)] for _ in range(num_channels)]

    print(f"✓ Created mock EEG signal: {num_channels} channels x {num_samples} samples")

    # Test filtering
    filtered = processor.filter_signal(eeg_signal)
    assert filtered is not None
    print(f"✓ Filtered signal: {len(filtered)} channels")

    # Test artifact removal
    clean_signal, artifacts = processor.remove_artifacts(filtered)
    print(f"✓ Removed artifacts: {len(artifacts)} artifacts detected")

    # Test feature extraction
    features = processor.extract_features(clean_signal, channel_idx=0)
    assert features is not None
    assert 'alpha' in features.band_powers
    assert 'beta' in features.band_powers
    print(f"✓ Extracted features:")
    print(f"  - Alpha power: {features.band_powers['alpha']:.3f}")
    print(f"  - Beta power: {features.band_powers['beta']:.3f}")
    print(f"  - Theta power: {features.band_powers['theta']:.3f}")
    print(f"  - Peak frequency: {features.peak_frequency:.2f} Hz")
    print(f"  - Hjorth activity: {features.hjorth_activity:.3f}")

    # Test attention/relaxation computation
    attention = processor.compute_attention_level(features)
    relaxation = processor.compute_relaxation_level(features)
    assert 0 <= attention <= 1
    assert 0 <= relaxation <= 1
    print(f"✓ Attention level: {attention:.2f}")
    print(f"✓ Relaxation level: {relaxation:.2f}")

    # Test signal quality assessment
    quality = processor.assess_signal_quality(eeg_signal)
    assert quality is not None
    print(f"✓ Signal quality: {quality.value}")

    # Test ERPDetector
    erp_detector = ERPDetector()
    event_times = [0.5, 1.0, 1.5, 2.0]  # seconds
    p300_amps = erp_detector.detect_p300(eeg_signal[0], event_times)
    assert len(p300_amps) == len(event_times)
    print(f"✓ P300 detection: {len(p300_amps)} events processed")

    print("\n✓ Signal Processing tests passed!")
    return True


def test_bci_interface():
    """Test BCI interface module"""
    print("\n=== Testing BCI Interface (Pure Python) ===")

    from bci.bci_interface import (
        BCIInterface,
        BCIFeedback,
        BCIConfig,
        BCIMode,
        MentalCommand,
    )

    # Test BCIInterface
    config = BCIConfig(
        simulation_mode=True,
        num_channels=8,
        sampling_rate_hz=256,
        mode=BCIMode.HYBRID
    )
    bci = BCIInterface(config)
    print(f"✓ Created BCI interface in {config.mode.value} mode")

    # Start session
    session_id = bci.start_session("test_user_001", mode=BCIMode.ACTIVE)
    assert session_id is not None
    print(f"✓ Started session: {session_id}")

    # Calibrate
    calibration_data = [[random.gauss(0, 10) for _ in range(256)] for _ in range(8)]
    success = bci.calibrate(session_id, calibration_data)
    assert success
    print(f"✓ Calibration completed")

    # Process signal
    eeg_data = [[random.gauss(0, 10) for _ in range(512)] for _ in range(8)]
    success = bci.process_signal(session_id, eeg_data)
    assert success
    print(f"✓ Processed EEG signal")

    # Get mental state
    state = bci.get_mental_state(session_id)
    assert state is not None
    print(f"✓ Mental state:")
    print(f"  - Attention: {state.attention:.2f}")
    print(f"  - Relaxation: {state.relaxation:.2f}")
    print(f"  - Stress: {state.stress:.2f}")
    print(f"  - Drowsiness: {state.drowsiness:.2f}")
    print(f"  - Engagement: {state.engagement:.2f}")

    # Test command callback
    command_received = []

    def on_focus(sid):
        command_received.append(MentalCommand.FOCUS)

    bci.register_command_callback(MentalCommand.FOCUS, on_focus)
    bci.send_mental_command(session_id, MentalCommand.FOCUS)
    assert len(command_received) == 1
    print(f"✓ Mental command callback triggered")

    # Stop session
    success = bci.stop_session(session_id)
    assert success
    print(f"✓ Session stopped")

    # Test BCIFeedback
    feedback_sys = BCIFeedback()

    from bci.signal_processing import SignalQuality
    from bci.bci_interface import MentalState

    test_state = MentalState(attention=0.85, relaxation=0.4)
    feedback = feedback_sys.provide_feedback(test_state, SignalQuality.GOOD)
    assert 'signal' in feedback
    assert 'attention' in feedback
    assert 'relaxation' in feedback
    print(f"✓ Feedback generated:")
    print(f"  - Signal: {feedback['signal']}")
    print(f"  - Attention: {feedback['attention']}")
    print(f"  - Relaxation: {feedback['relaxation']}")

    print("\n✓ BCI Interface tests passed!")
    return True


def main():
    """Run all BCI tests"""
    print("=" * 60)
    print("BCI MODULES TEST (Pure Python Version)")
    print("=" * 60)

    try:
        # Test signal processing
        if not test_signal_processing():
            print("\n✗ Signal processing tests failed")
            return False

        # Test BCI interface
        if not test_bci_interface():
            print("\n✗ BCI interface tests failed")
            return False

        print("\n" + "=" * 60)
        print("✓ ALL BCI TESTS PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
