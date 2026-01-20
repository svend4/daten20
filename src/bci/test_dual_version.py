"""Quick test for BCI dual-version"""
import sys
import asyncio

def test_imports():
    print("Testing imports...")
    from bci import (
        EEGProcessor,
        MotorImageryClassifier,
        P300Detector,
        SSVEPProcessor,
        CognitiveMonitor,
        BCIControlInterface,
        NeurofeedbackSystem,
        get_eeg_processor,
        HAS_NUMPY,
        EEGSignal,
        MotorImageryType,
        FilterType,
    )
    print(f"  HAS_NUMPY: {HAS_NUMPY}")
    print(f"  ✅ Imports work!")
    return HAS_NUMPY

async def test_eeg_processor():
    print("\nTesting EEG Processor...")
    from bci import get_eeg_processor, EEGSignal
    
    processor = get_eeg_processor(sampling_rate=250, n_channels=8)
    
    # Mock raw EEG data (8 channels, 250 samples)
    raw_data = [[0.5 + i*0.01 for i in range(250)] for _ in range(8)]
    
    # Process signal
    signal = await processor.process_signal(raw_data)
    
    print(f"  Sampling rate: {signal.sampling_rate} Hz")
    print(f"  Channels: {len(signal.channels)}")
    print(f"  Quality: {signal.quality_score:.2f}")
    print(f"  ✅ EEG Processor works!")

async def test_motor_imagery():
    print("\nTesting Motor Imagery Classifier...")
    from bci import get_motor_imagery_classifier, EEGSignal, MotorImageryType
    
    classifier = get_motor_imagery_classifier(n_channels=8, n_classes=4)
    
    # Mock EEG signal
    signal = EEGSignal(
        timestamp=1234567890.0,
        channels=["Ch1", "Ch2", "Ch3", "Ch4", "Ch5", "Ch6", "Ch7", "Ch8"],
        data=[[0.5 + i*0.01 for i in range(250)] for _ in range(8)],
        sampling_rate=250,
        quality_score=0.95,
    )
    
    # Classify (without training, should return REST)
    result = await classifier.classify(signal)
    
    print(f"  Predicted: {result.predicted_class.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Processing time: {result.processing_time*1000:.1f} ms")
    print(f"  ✅ Motor Imagery Classifier works!")

async def test_p300_detector():
    print("\nTesting P300 Detector...")
    from bci import get_p300_detector, EEGSignal, P300Stimulus, P300Paradigm
    
    detector = get_p300_detector(paradigm=P300Paradigm.MATRIX_SPELLER, n_channels=8)
    
    # Mock stimulus
    stimulus = P300Stimulus(
        stimulus_id="stim_1",
        paradigm=P300Paradigm.MATRIX_SPELLER,
        timestamp=1234567890.0,
        target=True,
        row=2,
        col=3,
        character="M"
    )
    
    # Mock EEG signal
    signal = EEGSignal(
        timestamp=1234567890.0,
        channels=["Ch1", "Ch2", "Ch3", "Ch4", "Ch5", "Ch6", "Ch7", "Ch8"],
        data=[[0.5 + i*0.01 for i in range(200)] for _ in range(8)],
        sampling_rate=250,
        quality_score=0.95,
    )
    
    # Detect P300
    response = await detector.detect_p300(signal, stimulus)
    
    print(f"  P300 amplitude: {response.p300_amplitude:.2f} µV")
    print(f"  P300 latency: {response.p300_latency:.0f} ms")
    print(f"  Is target: {response.is_target}")
    print(f"  ✅ P300 Detector works!")

async def test_system_status():
    print("\nTesting System Status...")
    from bci import get_eeg_processor, HAS_NUMPY
    
    processor = get_eeg_processor()
    stats = processor.get_statistics()
    print(f"  Implementation: {'NumPy' if HAS_NUMPY else 'Pure Python'}")
    print(f"  Sampling rate: {stats['sampling_rate']} Hz")
    print(f"  Channels: {stats['n_channels']}")
    print(f"  ✅ System works!")

def main():
    print("=" * 60)
    print("BCI DUAL-VERSION QUICK TEST")
    print("=" * 60)
    
    has_numpy = test_imports()
    asyncio.run(test_eeg_processor())
    asyncio.run(test_motor_imagery())
    asyncio.run(test_p300_detector())
    asyncio.run(test_system_status())
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print(f"Using: {'NumPy version' if has_numpy else 'Pure Python version'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
