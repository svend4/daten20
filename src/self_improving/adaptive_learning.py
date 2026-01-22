"""
Adaptive Learning Rate Controller

Intelligent learning rate scheduling with:
- Performance-driven adaptation
- Plateau detection
- Warmup and cooldown strategies
- Cyclical learning rates
- Adaptive momentum
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from collections import deque


class LRScheduleType(Enum):
    """Learning rate schedule types"""
    CONSTANT = "constant"
    STEP_DECAY = "step_decay"
    EXPONENTIAL = "exponential"
    COSINE_ANNEALING = "cosine_annealing"
    CYCLICAL = "cyclical"
    REDUCE_ON_PLATEAU = "reduce_on_plateau"
    ADAPTIVE_PERFORMANCE = "adaptive_performance"


class PlateauState(Enum):
    """Performance plateau states"""
    IMPROVING = "improving"
    PLATEAU = "plateau"
    DEGRADING = "degrading"


@dataclass
class LRScheduleConfig:
    """Configuration for learning rate schedule"""
    schedule_type: LRScheduleType = LRScheduleType.ADAPTIVE_PERFORMANCE
    initial_lr: float = 0.001
    min_lr: float = 1e-6
    max_lr: float = 0.1
    warmup_steps: int = 0
    decay_rate: float = 0.5
    decay_steps: int = 100
    plateau_patience: int = 10
    plateau_threshold: float = 0.001
    cooldown_steps: int = 0


@dataclass
class LRState:
    """Current learning rate state"""
    current_lr: float
    step: int
    plateau_counter: int
    plateau_state: PlateauState
    best_performance: float
    performance_history: List[float]


class AdaptiveLearningController:
    """
    Adaptive learning rate controller.

    Automatically adjusts learning rate based on:
    - Training performance
    - Plateau detection
    - Step count
    """

    def __init__(self, config: Optional[LRScheduleConfig] = None):
        """
        Initialize adaptive learning controller.

        Args:
            config: Learning rate schedule configuration
        """
        self.config = config or LRScheduleConfig()

        # State
        self.state = LRState(
            current_lr=self.config.initial_lr,
            step=0,
            plateau_counter=0,
            plateau_state=PlateauState.IMPROVING,
            best_performance=float('-inf'),
            performance_history=[]
        )

        # Performance tracking
        self.performance_window = deque(maxlen=self.config.plateau_patience)

    def step(self, performance: Optional[float] = None) -> float:
        """
        Update learning rate for one step.

        Args:
            performance: Current performance metric (higher is better)

        Returns:
            Updated learning rate
        """
        self.state.step += 1

        # Update performance history
        if performance is not None:
            self.state.performance_history.append(performance)
            self.performance_window.append(performance)

        # Apply schedule
        if self.config.schedule_type == LRScheduleType.CONSTANT:
            lr = self._constant_schedule()
        elif self.config.schedule_type == LRScheduleType.STEP_DECAY:
            lr = self._step_decay_schedule()
        elif self.config.schedule_type == LRScheduleType.EXPONENTIAL:
            lr = self._exponential_schedule()
        elif self.config.schedule_type == LRScheduleType.COSINE_ANNEALING:
            lr = self._cosine_annealing_schedule()
        elif self.config.schedule_type == LRScheduleType.CYCLICAL:
            lr = self._cyclical_schedule()
        elif self.config.schedule_type == LRScheduleType.REDUCE_ON_PLATEAU:
            lr = self._reduce_on_plateau_schedule(performance)
        elif self.config.schedule_type == LRScheduleType.ADAPTIVE_PERFORMANCE:
            lr = self._adaptive_performance_schedule(performance)
        else:
            lr = self.config.initial_lr

        # Apply warmup
        if self.state.step <= self.config.warmup_steps:
            warmup_factor = self.state.step / self.config.warmup_steps
            lr = lr * warmup_factor

        # Clip to bounds
        lr = max(self.config.min_lr, min(self.config.max_lr, lr))

        self.state.current_lr = lr
        return lr

    def _constant_schedule(self) -> float:
        """Constant learning rate"""
        return self.config.initial_lr

    def _step_decay_schedule(self) -> float:
        """Step decay schedule"""
        decay_factor = (self.state.step // self.config.decay_steps)
        return self.config.initial_lr * (self.config.decay_rate ** decay_factor)

    def _exponential_schedule(self) -> float:
        """Exponential decay schedule"""
        return self.config.initial_lr * math.exp(-self.config.decay_rate * self.state.step)

    def _cosine_annealing_schedule(self) -> float:
        """Cosine annealing schedule"""
        if self.config.decay_steps == 0:
            return self.config.initial_lr

        progress = (self.state.step % self.config.decay_steps) / self.config.decay_steps
        cosine_factor = 0.5 * (1 + math.cos(math.pi * progress))

        return self.config.min_lr + (self.config.initial_lr - self.config.min_lr) * cosine_factor

    def _cyclical_schedule(self) -> float:
        """Cyclical learning rate (triangular policy)"""
        if self.config.decay_steps == 0:
            return self.config.initial_lr

        cycle = math.floor(1 + self.state.step / (2 * self.config.decay_steps))
        x = abs(self.state.step / self.config.decay_steps - 2 * cycle + 1)

        return self.config.min_lr + (self.config.max_lr - self.config.min_lr) * max(0, (1 - x))

    def _reduce_on_plateau_schedule(self, performance: Optional[float]) -> float:
        """Reduce learning rate on plateau"""
        if performance is None:
            return self.state.current_lr

        # Update best performance
        if performance > self.state.best_performance:
            self.state.best_performance = performance
            self.state.plateau_counter = 0
        else:
            self.state.plateau_counter += 1

        # Check for plateau
        if self.state.plateau_counter >= self.config.plateau_patience:
            # Reduce learning rate
            new_lr = self.state.current_lr * self.config.decay_rate
            self.state.plateau_counter = 0  # Reset counter
            return max(self.config.min_lr, new_lr)

        return self.state.current_lr

    def _adaptive_performance_schedule(self, performance: Optional[float]) -> float:
        """
        Adaptive schedule based on performance trends.

        Increases LR when improving, decreases when plateauing.
        """
        if performance is None or len(self.performance_window) < 3:
            return self.state.current_lr

        # Analyze recent performance
        recent = list(self.performance_window)

        # Calculate trend
        if len(recent) >= 2:
            recent_improvement = recent[-1] - recent[-2]

            # Moving average of improvements
            if len(recent) >= 3:
                avg_improvement = sum(recent[i] - recent[i-1] for i in range(1, len(recent))) / (len(recent) - 1)
            else:
                avg_improvement = recent_improvement

            # Detect plateau state
            if abs(avg_improvement) < self.config.plateau_threshold:
                self.state.plateau_state = PlateauState.PLATEAU
                # Reduce LR on plateau
                new_lr = self.state.current_lr * 0.9
            elif avg_improvement > 0:
                self.state.plateau_state = PlateauState.IMPROVING
                # Slightly increase LR when improving
                new_lr = self.state.current_lr * 1.05
            else:
                self.state.plateau_state = PlateauState.DEGRADING
                # Reduce LR when degrading
                new_lr = self.state.current_lr * 0.8

            return new_lr

        return self.state.current_lr

    def reset(self, new_initial_lr: Optional[float] = None):
        """
        Reset learning rate state.

        Args:
            new_initial_lr: Optional new initial learning rate
        """
        if new_initial_lr is not None:
            self.config.initial_lr = new_initial_lr

        self.state = LRState(
            current_lr=self.config.initial_lr,
            step=0,
            plateau_counter=0,
            plateau_state=PlateauState.IMPROVING,
            best_performance=float('-inf'),
            performance_history=[]
        )
        self.performance_window.clear()

    def get_current_lr(self) -> float:
        """Get current learning rate"""
        return self.state.current_lr

    def get_state_info(self) -> dict:
        """Get current state information"""
        return {
            "current_lr": self.state.current_lr,
            "step": self.state.step,
            "plateau_state": self.state.plateau_state.value,
            "plateau_counter": self.state.plateau_counter,
            "best_performance": self.state.best_performance,
            "schedule_type": self.config.schedule_type.value
        }

    def get_performance_summary(self) -> dict:
        """Get performance summary"""
        if not self.state.performance_history:
            return {
                "status": "no_data",
                "num_steps": 0
            }

        history = self.state.performance_history

        # Calculate statistics
        improvements = [history[i] - history[i-1] for i in range(1, len(history))]

        return {
            "status": "active",
            "num_steps": len(history),
            "initial_performance": history[0],
            "current_performance": history[-1],
            "best_performance": max(history),
            "total_improvement": history[-1] - history[0],
            "average_improvement_per_step": sum(improvements) / len(improvements) if improvements else 0.0,
            "plateau_state": self.state.plateau_state.value
        }


class AdaptiveMomentumController:
    """
    Adaptive momentum controller.

    Adjusts momentum based on training dynamics.
    """

    def __init__(self,
                 initial_momentum: float = 0.9,
                 min_momentum: float = 0.5,
                 max_momentum: float = 0.99):
        """
        Initialize adaptive momentum controller.

        Args:
            initial_momentum: Initial momentum value
            min_momentum: Minimum momentum
            max_momentum: Maximum momentum
        """
        self.initial_momentum = initial_momentum
        self.min_momentum = min_momentum
        self.max_momentum = max_momentum

        self.current_momentum = initial_momentum
        self.gradient_history: deque = deque(maxlen=100)

    def update(self, gradient_norm: float) -> float:
        """
        Update momentum based on gradient norm.

        Args:
            gradient_norm: Current gradient norm

        Returns:
            Updated momentum value
        """
        self.gradient_history.append(gradient_norm)

        if len(self.gradient_history) < 10:
            return self.current_momentum

        # Calculate gradient variance
        recent_grads = list(self.gradient_history)[-10:]
        mean_grad = sum(recent_grads) / len(recent_grads)
        variance = sum((g - mean_grad) ** 2 for g in recent_grads) / len(recent_grads)

        # Normalize variance
        normalized_variance = variance / (mean_grad ** 2 + 1e-8)

        # Adjust momentum based on variance
        # High variance -> lower momentum for stability
        # Low variance -> higher momentum for acceleration
        if normalized_variance > 0.5:
            # High variance: reduce momentum
            self.current_momentum = max(
                self.min_momentum,
                self.current_momentum * 0.95
            )
        elif normalized_variance < 0.1:
            # Low variance: increase momentum
            self.current_momentum = min(
                self.max_momentum,
                self.current_momentum * 1.02
            )

        return self.current_momentum

    def get_momentum(self) -> float:
        """Get current momentum"""
        return self.current_momentum

    def reset(self):
        """Reset momentum state"""
        self.current_momentum = self.initial_momentum
        self.gradient_history.clear()


# Singletons
_lr_controller_instance = None
_momentum_controller_instance = None


def get_adaptive_lr_controller(config: Optional[LRScheduleConfig] = None) -> AdaptiveLearningController:
    """Get singleton instance of AdaptiveLearningController"""
    global _lr_controller_instance
    if _lr_controller_instance is None:
        _lr_controller_instance = AdaptiveLearningController(config)
    return _lr_controller_instance


def get_adaptive_momentum_controller() -> AdaptiveMomentumController:
    """Get singleton instance of AdaptiveMomentumController"""
    global _momentum_controller_instance
    if _momentum_controller_instance is None:
        _momentum_controller_instance = AdaptiveMomentumController()
    return _momentum_controller_instance
