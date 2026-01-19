"""
BCI Interface - v4.4

High-level brain-computer interface for hands-free document management.

Version: 4.4.0
"""

__version__ = '4.4.0'

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import numpy as np
import logging

from bci.signal_processing import SignalProcessor, ERPDetector, SignalFeatures, SignalQuality

logger = logging.getLogger(__name__)


class MentalCommand(Enum):
    """Mental commands for BCI control"""
    FOCUS = "focus"
    SELECT = "select"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    BACK = "back"
    NEXT = "next"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class BCIMode(Enum):
    """BCI operation modes"""
    PASSIVE = "passive"          # Just monitoring (attention, stress)
    ACTIVE = "active"            # Active control (commands)
    HYBRID = "hybrid"            # Both passive + active


@dataclass
class BCISession:
    """BCI session data"""
    session_id: str
    user_id: str
    start_time: datetime
    mode: BCIMode = BCIMode.PASSIVE
    calibrated: bool = False
    signal_quality: SignalQuality = SignalQuality.NO_SIGNAL


@dataclass
class MentalState:
    """User's mental state"""
    attention: float = 0.0      # 0-1
    relaxation: float = 0.0     # 0-1
    stress: float = 0.0         # 0-1
    drowsiness: float = 0.0     # 0-1
    engagement: float = 0.0     # 0-1


@dataclass
class BCIConfig:
    """BCI system configuration"""
    simulation_mode: bool = True
    num_channels: int = 8
    sampling_rate_hz: int = 256
    mode: BCIMode = BCIMode.PASSIVE
    enable_artifact_rejection: bool = True
    enable_adaptive_filtering: bool = True
    command_threshold: float = 0.7  # Confidence threshold for commands


class BCIInterface:
    """
    Brain-Computer Interface

    High-level BCI system for hands-free document interaction:
    - Mental state monitoring (attention, relaxation, stress)
    - Mental command detection (select, scroll, navigate)
    - Adaptive calibration per user
    - Real-time feedback
    - Multiple BCI paradigms (P300, SSVEP, motor imagery)

    Example:
        >>> bci = BCIInterface()
        >>> session_id = bci.start_session("user123")
        >>> bci.calibrate(session_id)
        >>> while True:
        ...     eeg_data = read_eeg_device()
        ...     bci.process_signal(session_id, eeg_data)
        ...     state = bci.get_mental_state(session_id)
        ...     if state.attention > 0.8:
        ...         print("High focus detected!")
    """

    def __init__(self, config: Optional[BCIConfig] = None):
        """
        Initialize BCI Interface

        Args:
            config: BCI configuration
        """
        self.config = config or BCIConfig()
        self.processor = SignalProcessor()
        self.erp_detector = ERPDetector()

        self.sessions: Dict[str, BCISession] = {}
        self.mental_states: Dict[str, MentalState] = {}
        self.user_baselines: Dict[str, Dict[str, float]] = {}
        self.command_callbacks: Dict[MentalCommand, List[Callable]] = {}

        logger.info(f"BCI Interface initialized - Mode: {self.config.mode.value}, "
                   f"Channels: {self.config.num_channels}, Simulation: {self.config.simulation_mode}")

    def start_session(self, user_id: str, mode: Optional[BCIMode] = None) -> str:
        """
        Start BCI session

        Args:
            user_id: User identifier
            mode: Optional BCI mode (default from config)

        Returns:
            Session ID
        """
        session_id = f"bci_{user_id}_{int(datetime.now().timestamp())}"

        session = BCISession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            mode=mode or self.config.mode
        )

        self.sessions[session_id] = session
        self.mental_states[session_id] = MentalState()

        logger.info(f"Started BCI session: {session_id} for user {user_id}")
        return session_id

    def stop_session(self, session_id: str) -> bool:
        """
        Stop BCI session

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.mental_states:
                del self.mental_states[session_id]
            logger.info(f"Stopped BCI session: {session_id}")
            return True

        logger.warning(f"Session not found: {session_id}")
        return False

    def calibrate(self, session_id: str, calibration_data: Optional[np.ndarray] = None) -> bool:
        """
        Calibrate BCI for user

        Args:
            session_id: Session identifier
            calibration_data: Optional calibration EEG data

        Returns:
            True if calibration successful
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False

        session = self.sessions[session_id]
        user_id = session.user_id

        logger.info(f"Calibrating BCI for user: {user_id}")

        if calibration_data is not None:
            # Process calibration data to establish baseline
            features = self.processor.extract_features(calibration_data)

            baseline = {
                'alpha': features.band_powers.get('alpha', 0.0),
                'beta': features.band_powers.get('beta', 0.0),
                'theta': features.band_powers.get('theta', 0.0),
            }

            self.user_baselines[user_id] = baseline
            logger.info(f"Established baseline for user {user_id}: {baseline}")

        session.calibrated = True
        return True

    def process_signal(self, session_id: str, eeg_data: np.ndarray) -> bool:
        """
        Process EEG signal and update mental state

        Args:
            session_id: Session identifier
            eeg_data: Raw EEG data (channels x samples)

        Returns:
            True if processing successful
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False

        session = self.sessions[session_id]

        # Check signal quality
        signal_quality = self.processor.assess_signal_quality(eeg_data)
        session.signal_quality = signal_quality

        if signal_quality == SignalQuality.NO_SIGNAL:
            logger.warning("No EEG signal detected")
            return False

        # Filter signal
        filtered_signal = self.processor.filter_signal(eeg_data)

        # Remove artifacts
        clean_signal, _ = self.processor.remove_artifacts(filtered_signal)

        # Extract features
        features = self.processor.extract_features(clean_signal)

        # Update mental state
        self._update_mental_state(session_id, features)

        # Detect commands if in active mode
        if session.mode in [BCIMode.ACTIVE, BCIMode.HYBRID]:
            self._detect_commands(session_id, features)

        return True

    def get_mental_state(self, session_id: str) -> Optional[MentalState]:
        """
        Get current mental state

        Args:
            session_id: Session identifier

        Returns:
            Mental state or None
        """
        return self.mental_states.get(session_id)

    def get_attention_level(self, session_id: str) -> float:
        """
        Get attention level (0-1)

        Args:
            session_id: Session identifier

        Returns:
            Attention level
        """
        state = self.get_mental_state(session_id)
        return state.attention if state else 0.0

    def get_relaxation_level(self, session_id: str) -> float:
        """
        Get relaxation level (0-1)

        Args:
            session_id: Session identifier

        Returns:
            Relaxation level
        """
        state = self.get_mental_state(session_id)
        return state.relaxation if state else 0.0

    def register_command_callback(self,
                                  command: MentalCommand,
                                  callback: Callable[[str], None]) -> None:
        """
        Register callback for mental command

        Args:
            command: Mental command type
            callback: Callback function (takes session_id as parameter)
        """
        if command not in self.command_callbacks:
            self.command_callbacks[command] = []

        self.command_callbacks[command].append(callback)
        logger.info(f"Registered callback for command: {command.value}")

    def send_mental_command(self, session_id: str, command: MentalCommand) -> bool:
        """
        Manually send mental command (for testing)

        Args:
            session_id: Session identifier
            command: Mental command

        Returns:
            True if successful
        """
        if session_id not in self.sessions:
            return False

        logger.info(f"Mental command detected: {command.value}")

        # Execute callbacks
        if command in self.command_callbacks:
            for callback in self.command_callbacks[command]:
                try:
                    callback(session_id)
                except Exception as e:
                    logger.error(f"Command callback error: {e}")

        return True

    # Private methods

    def _update_mental_state(self, session_id: str, features: SignalFeatures) -> None:
        """Update mental state based on features"""
        if session_id not in self.mental_states:
            return

        state = self.mental_states[session_id]

        # Compute attention
        state.attention = self.processor.compute_attention_level(features)

        # Compute relaxation
        state.relaxation = self.processor.compute_relaxation_level(features)

        # Compute stress (simplified: high beta + low alpha)
        beta = features.band_powers.get('beta', 0.0)
        alpha = features.band_powers.get('alpha', 0.0)
        state.stress = min(1.0, beta / (alpha + 0.1))

        # Compute drowsiness (high theta + low beta)
        theta = features.band_powers.get('theta', 0.0)
        state.drowsiness = min(1.0, theta / (beta + 0.1))

        # Compute engagement
        state.engagement = (state.attention + (1.0 - state.drowsiness)) / 2.0

        logger.debug(f"Mental state updated - Attention: {state.attention:.2f}, "
                    f"Relaxation: {state.relaxation:.2f}, Stress: {state.stress:.2f}")

    def _detect_commands(self, session_id: str, features: SignalFeatures) -> None:
        """Detect mental commands from features"""
        # Simplified command detection
        # In real implementation, use machine learning classifier

        state = self.mental_states[session_id]

        # Detect focus command (high attention)
        if state.attention > self.config.command_threshold:
            self.send_mental_command(session_id, MentalCommand.FOCUS)

        # Detect select command (high engagement + spike in P300)
        # This would require ERP detection in real implementation

        # Additional command detection logic...


class BCIFeedback:
    """
    BCI Feedback System

    Provides real-time feedback to user about their mental state and signal quality.
    """

    def __init__(self):
        """Initialize feedback system"""
        self.feedback_history: List[Dict[str, Any]] = []
        logger.info("BCI Feedback System initialized")

    def provide_feedback(self,
                        mental_state: MentalState,
                        signal_quality: SignalQuality) -> Dict[str, str]:
        """
        Generate feedback for user

        Args:
            mental_state: Current mental state
            signal_quality: Current signal quality

        Returns:
            Feedback messages
        """
        feedback = {
            'signal': '',
            'attention': '',
            'relaxation': ''
        }

        # Signal quality feedback
        if signal_quality == SignalQuality.EXCELLENT:
            feedback['signal'] = "Signal quality: Excellent"
        elif signal_quality == SignalQuality.GOOD:
            feedback['signal'] = "Signal quality: Good"
        elif signal_quality == SignalQuality.FAIR:
            feedback['signal'] = "Signal quality: Fair - Check electrode contact"
        else:
            feedback['signal'] = "Signal quality: Poor - Check headset"

        # Attention feedback
        if mental_state.attention > 0.8:
            feedback['attention'] = "High focus - Great concentration!"
        elif mental_state.attention > 0.5:
            feedback['attention'] = "Moderate focus"
        else:
            feedback['attention'] = "Low focus - Try to concentrate"

        # Relaxation feedback
        if mental_state.relaxation > 0.7:
            feedback['relaxation'] = "Deeply relaxed"
        elif mental_state.relaxation > 0.4:
            feedback['relaxation'] = "Moderately relaxed"
        else:
            feedback['relaxation'] = "Tense - Try to relax"

        return feedback


__all__ = [
    'BCIInterface',
    'BCIFeedback',
    'MentalCommand',
    'BCIMode',
    'BCISession',
    'MentalState',
    'BCIConfig',
]
