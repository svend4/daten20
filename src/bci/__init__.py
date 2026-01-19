"""
Brain-Computer Interface (BCI) Module - v4.4

Advanced BCI for hands-free document management and interaction.

Features:
- EEG signal processing and artifact rejection
- Mental state monitoring (attention, relaxation, stress)
- Mental command detection (select, scroll, navigate)
- Event-related potential (ERP) detection (P300)
- Real-time feedback system
- Adaptive user calibration

Version: 4.4.0 (FULL IMPLEMENTATION)
"""

__version__ = '4.4.0'

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable
import logging
import numpy as np

# Import from submodules
from bci.signal_processing import (
    SignalProcessor,
    ERPDetector,
    BandPower,
    SignalQuality,
    EEGChannel,
    SignalFeatures,
    SignalProcessingConfig,
)

from bci.bci_interface import (
    BCIInterface,
    BCIFeedback,
    MentalCommand,
    BCIMode,
    BCISession,
    MentalState,
    BCIConfig,
)

logger = logging.getLogger(__name__)


class BCIManager:
    """
    BCI Manager - Unified brain-computer interface management

    Integrates:
    - Signal processing
    - Mental state monitoring
    - Command detection
    - User feedback

    Example:
        >>> from bci import BCIManager, MentalCommand
        >>> manager = BCIManager()
        >>> session_id = manager.start_session("user123")
        >>> manager.calibrate(session_id)
        >>>
        >>> # Register command callback
        >>> def on_select(session_id):
        ...     print("User selected document!")
        >>> manager.register_command(MentalCommand.SELECT, on_select)
        >>>
        >>> # Process EEG data
        >>> eeg_data = np.random.randn(8, 256)  # 8 channels, 256 samples
        >>> manager.process(session_id, eeg_data)
        >>>
        >>> # Get mental state
        >>> state = manager.get_mental_state(session_id)
        >>> print(f"Attention: {state.attention:.2f}")
    """

    def __init__(self, config: Optional[BCIConfig] = None):
        """
        Initialize BCI Manager

        Args:
            config: BCI configuration
        """
        self.config = config or BCIConfig()
        self.bci = BCIInterface(config)
        self.feedback = BCIFeedback()

        logger.info(f"BCI Manager initialized - Mode: {self.config.mode.value}")

    def start_session(self, user_id: str, mode: Optional[BCIMode] = None) -> str:
        """
        Start BCI session

        Args:
            user_id: User identifier
            mode: Optional BCI mode

        Returns:
            Session ID
        """
        return self.bci.start_session(user_id, mode)

    def stop_session(self, session_id: str) -> bool:
        """
        Stop BCI session

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        return self.bci.stop_session(session_id)

    def calibrate(self, session_id: str, calibration_data: Optional[np.ndarray] = None) -> bool:
        """
        Calibrate BCI for user

        Args:
            session_id: Session identifier
            calibration_data: Optional calibration EEG data

        Returns:
            True if successful
        """
        return self.bci.calibrate(session_id, calibration_data)

    def process(self, session_id: str, eeg_data: np.ndarray) -> bool:
        """
        Process EEG signal

        Args:
            session_id: Session identifier
            eeg_data: Raw EEG data (channels x samples)

        Returns:
            True if successful
        """
        return self.bci.process_signal(session_id, eeg_data)

    def get_mental_state(self, session_id: str) -> Optional[MentalState]:
        """
        Get current mental state

        Args:
            session_id: Session identifier

        Returns:
            Mental state or None
        """
        return self.bci.get_mental_state(session_id)

    def get_attention_level(self, session_id: str) -> float:
        """Get attention level (0-1)"""
        return self.bci.get_attention_level(session_id)

    def get_relaxation_level(self, session_id: str) -> float:
        """Get relaxation level (0-1)"""
        return self.bci.get_relaxation_level(session_id)

    def register_command(self,
                        command: MentalCommand,
                        callback: Callable[[str], None]) -> None:
        """
        Register callback for mental command

        Args:
            command: Mental command type
            callback: Callback function
        """
        self.bci.register_command_callback(command, callback)

    def get_feedback(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Get feedback for user

        Args:
            session_id: Session identifier

        Returns:
            Feedback messages or None
        """
        mental_state = self.bci.get_mental_state(session_id)
        if not mental_state:
            return None

        session = self.bci.sessions.get(session_id)
        if not session:
            return None

        return self.feedback.provide_feedback(mental_state, session.signal_quality)


# Singleton instance
_manager = None

def get_bci_manager(config: Optional[BCIConfig] = None) -> BCIManager:
    """
    Get singleton BCI Manager instance

    Args:
        config: Optional BCI configuration

    Returns:
        BCIManager instance
    """
    global _manager
    if _manager is None:
        _manager = BCIManager(config)
    return _manager


__all__ = [
    # Main manager
    'BCIManager',
    'get_bci_manager',

    # Configuration and types
    'BCIConfig',
    'BCIMode',
    'BCISession',
    'MentalState',
    'MentalCommand',

    # Signal processing
    'SignalProcessor',
    'ERPDetector',
    'BandPower',
    'SignalQuality',
    'EEGChannel',
    'SignalFeatures',
    'SignalProcessingConfig',

    # Interface
    'BCIInterface',
    'BCIFeedback',
]
