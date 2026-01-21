"""
Continuous Improvement Orchestrator

Orchestrates autonomous continuous improvement:
- Monitors system performance
- Identifies optimization opportunities
- Applies improvements automatically
- Validates improvements
- Rolls back if necessary
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from .advanced_monitoring import (
    AdvancedMonitor, MetricType, get_advanced_monitor
)
from .bottleneck_analyzer import (
    BottleneckAnalyzer, get_bottleneck_analyzer
)
from .adaptive_learning import (
    AdaptiveLearningController, LRScheduleConfig,
    get_adaptive_lr_controller
)


class ImprovementPhase(Enum):
    """Phases of improvement cycle"""
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    ROLLBACK = "rollback"


class ImprovementStatus(Enum):
    """Status of improvement"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ImprovementAction:
    """Action to improve system"""
    action_id: str
    action_type: str  # "optimize_lr", "fix_bottleneck", "adjust_architecture", etc.
    target_component: str
    parameters: Dict[str, Any]
    expected_impact: float
    priority: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImprovementResult:
    """Result of an improvement action"""
    action: ImprovementAction
    status: ImprovementStatus
    actual_impact: float
    performance_before: float
    performance_after: float
    execution_time: float
    validation_passed: bool
    rollback_performed: bool
    timestamp: float


@dataclass
class ContinuousImprovementConfig:
    """Configuration for continuous improvement"""
    # Monitoring
    monitoring_interval: float = 10.0  # seconds
    performance_threshold: float = 0.95

    # Analysis
    analysis_window: int = 100
    min_samples_for_analysis: int = 10

    # Optimization
    max_improvements_per_cycle: int = 3
    improvement_cooldown: float = 30.0  # seconds

    # Validation
    validation_trials: int = 5
    improvement_threshold: float = 0.02  # 2% minimum improvement

    # Safety
    enable_auto_rollback: bool = True
    rollback_threshold: float = -0.05  # -5% performance drop triggers rollback
    max_rollbacks: int = 3


class ContinuousImprovementOrchestrator:
    """
    Orchestrator for continuous autonomous improvement.

    Coordinates monitoring, analysis, optimization, and validation
    to continuously improve system performance.
    """

    def __init__(self, config: Optional[ContinuousImprovementConfig] = None):
        """
        Initialize continuous improvement orchestrator.

        Args:
            config: Configuration for continuous improvement
        """
        self.config = config or ContinuousImprovementConfig()

        # Components
        self.monitor = get_advanced_monitor()
        self.analyzer = get_bottleneck_analyzer()
        self.lr_controller = get_adaptive_lr_controller()

        # State
        self.current_phase = ImprovementPhase.MONITORING
        self.improvement_history: List[ImprovementResult] = []
        self.pending_actions: List[ImprovementAction] = []
        self.baseline_performance: Optional[float] = None
        self.current_performance: float = 0.0

        # Metrics
        self.cycle_count = 0
        self.total_improvements = 0
        self.successful_improvements = 0
        self.rollback_count = 0

        # Cooldown tracking
        self.last_improvement_time = 0.0

    def run_improvement_cycle(self,
                             performance_metric: float,
                             components: Optional[Dict[str, Callable]] = None) -> Dict[str, Any]:
        """
        Run one complete improvement cycle.

        Args:
            performance_metric: Current performance metric value
            components: Optional dictionary of components to profile

        Returns:
            Cycle results
        """
        self.cycle_count += 1
        cycle_start = time.time()

        # Update performance
        self.current_performance = performance_metric

        # Set baseline if not set
        if self.baseline_performance is None:
            self.baseline_performance = performance_metric

        # Phase 1: Monitoring
        self.current_phase = ImprovementPhase.MONITORING
        monitoring_results = self._monitor_system(performance_metric)

        # Phase 2: Analysis
        self.current_phase = ImprovementPhase.ANALYSIS
        analysis_results = self._analyze_system(components)

        # Phase 3: Optimization (if needed and not in cooldown)
        self.current_phase = ImprovementPhase.OPTIMIZATION
        optimization_results = self._optimize_system()

        # Phase 4: Validation
        self.current_phase = ImprovementPhase.VALIDATION
        validation_results = self._validate_improvements()

        cycle_time = time.time() - cycle_start

        return {
            "cycle": self.cycle_count,
            "cycle_time": cycle_time,
            "current_performance": self.current_performance,
            "baseline_performance": self.baseline_performance,
            "improvement_over_baseline": (
                (self.current_performance - self.baseline_performance) / self.baseline_performance * 100
                if self.baseline_performance != 0 else 0.0
            ),
            "phase": self.current_phase.value,
            "monitoring": monitoring_results,
            "analysis": analysis_results,
            "optimization": optimization_results,
            "validation": validation_results,
            "total_improvements": self.total_improvements,
            "success_rate": (
                self.successful_improvements / self.total_improvements * 100
                if self.total_improvements > 0 else 0.0
            )
        }

    def _monitor_system(self, performance_metric: float) -> Dict[str, Any]:
        """Monitor system performance"""
        # Record metrics
        self.monitor.record_metric(MetricType.PERFORMANCE, performance_metric)

        # Get monitoring report
        report = self.monitor.get_monitoring_report()

        # Analyze trends
        trend = self.monitor.analyze_trend(MetricType.PERFORMANCE)

        return {
            "performance": performance_metric,
            "trend": trend.trend_direction,
            "anomalies_detected": len(self.monitor.get_recent_anomalies(5)),
            "predictions": self.monitor.predict_performance(MetricType.PERFORMANCE, steps_ahead=5)
        }

    def _analyze_system(self, components: Optional[Dict[str, Callable]]) -> Dict[str, Any]:
        """Analyze system for optimization opportunities"""
        if components is None or len(components) == 0:
            return {
                "status": "skipped",
                "reason": "no_components_provided"
            }

        # Profile components
        profiling_result = self.analyzer.profile_execution(components, iterations=5)

        # Get optimization priorities
        priorities = self.analyzer.get_optimization_priority_list()

        # Generate improvement actions
        self.pending_actions = []
        for priority in priorities[:self.config.max_improvements_per_cycle]:
            action = ImprovementAction(
                action_id=f"action_{self.cycle_count}_{len(self.pending_actions)}",
                action_type="optimize_bottleneck",
                target_component=priority["component"],
                parameters={"priority": priority["priority_score"]},
                expected_impact=priority["impact_percent"] / 100.0,
                priority=priority["priority_score"],
                metadata=priority
            )
            self.pending_actions.append(action)

        return {
            "status": "completed",
            "bottlenecks_found": len(profiling_result.bottlenecks),
            "optimization_potential": profiling_result.optimization_potential,
            "actions_proposed": len(self.pending_actions)
        }

    def _optimize_system(self) -> Dict[str, Any]:
        """Apply optimization improvements"""
        # Check cooldown
        time_since_last = time.time() - self.last_improvement_time
        if time_since_last < self.config.improvement_cooldown:
            return {
                "status": "cooldown",
                "time_remaining": self.config.improvement_cooldown - time_since_last
            }

        if not self.pending_actions:
            return {
                "status": "no_actions",
                "reason": "no_pending_improvements"
            }

        # Apply improvements
        applied_actions = []
        performance_before = self.current_performance

        for action in self.pending_actions[:self.config.max_improvements_per_cycle]:
            # Simulate applying improvement
            # In real implementation, this would actually modify system
            improvement_applied = self._apply_improvement_action(action)

            if improvement_applied:
                applied_actions.append(action)
                self.total_improvements += 1

        self.last_improvement_time = time.time()

        return {
            "status": "applied",
            "actions_applied": len(applied_actions),
            "performance_before": performance_before
        }

    def _apply_improvement_action(self, action: ImprovementAction) -> bool:
        """
        Apply a specific improvement action.

        Args:
            action: Improvement action to apply

        Returns:
            True if successfully applied
        """
        try:
            if action.action_type == "optimize_lr":
                # Adjust learning rate
                self.lr_controller.step(self.current_performance)
                return True
            elif action.action_type == "optimize_bottleneck":
                # Mark bottleneck for optimization (simulated)
                return True
            else:
                return False
        except Exception:
            return False

    def _validate_improvements(self) -> Dict[str, Any]:
        """Validate applied improvements"""
        if not self.improvement_history:
            return {
                "status": "no_improvements_to_validate"
            }

        # Get recent improvement
        recent = self.improvement_history[-1]

        # Check if improvement was successful
        if recent.actual_impact >= self.config.improvement_threshold:
            self.successful_improvements += 1
            return {
                "status": "validated",
                "improvement": recent.actual_impact,
                "validation_passed": True
            }
        elif recent.actual_impact < self.config.rollback_threshold:
            # Performance degraded significantly
            if self.config.enable_auto_rollback:
                self._rollback_improvement(recent)
                return {
                    "status": "rolled_back",
                    "reason": "performance_degradation",
                    "impact": recent.actual_impact
                }

        return {
            "status": "validated",
            "improvement": recent.actual_impact if self.improvement_history else 0.0,
            "validation_passed": recent.validation_passed if self.improvement_history else False
        }

    def _rollback_improvement(self, improvement: ImprovementResult):
        """Rollback a failed improvement"""
        self.rollback_count += 1
        improvement.rollback_performed = True
        improvement.status = ImprovementStatus.ROLLED_BACK

        # In real implementation, this would revert system changes
        # For now, just mark as rolled back

    def get_improvement_statistics(self) -> Dict[str, Any]:
        """Get statistics about improvements"""
        return {
            "total_cycles": self.cycle_count,
            "total_improvements": self.total_improvements,
            "successful_improvements": self.successful_improvements,
            "failed_improvements": self.total_improvements - self.successful_improvements,
            "rollbacks": self.rollback_count,
            "success_rate": (
                self.successful_improvements / self.total_improvements * 100
                if self.total_improvements > 0 else 0.0
            ),
            "baseline_performance": self.baseline_performance,
            "current_performance": self.current_performance,
            "total_improvement": (
                (self.current_performance - self.baseline_performance) / self.baseline_performance * 100
                if self.baseline_performance and self.baseline_performance != 0 else 0.0
            )
        }

    def get_optimization_roadmap(self) -> Dict[str, Any]:
        """Get optimization roadmap with recommendations"""
        # Get analyzer recommendations
        report = self.analyzer.generate_optimization_report()

        # Get monitoring insights
        monitoring_report = self.monitor.get_monitoring_report()

        # Get LR controller status
        lr_status = self.lr_controller.get_state_info()

        return {
            "current_status": {
                "phase": self.current_phase.value,
                "performance": self.current_performance,
                "cycle": self.cycle_count
            },
            "optimization_opportunities": report.get("priority_list", []),
            "monitoring_insights": {
                "anomalies": monitoring_report.get("anomalies", {}),
                "metrics_summary": monitoring_report.get("metrics", {})
            },
            "learning_dynamics": {
                "current_lr": lr_status["current_lr"],
                "plateau_state": lr_status["plateau_state"]
            },
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check performance trend
        trend = self.monitor.analyze_trend(MetricType.PERFORMANCE)
        if trend.trend_direction == "degrading":
            recommendations.append("Performance is degrading - consider investigating recent changes")
        elif trend.trend_direction == "stable":
            recommendations.append("Performance is stable - consider exploring new optimization strategies")

        # Check for anomalies
        recent_anomalies = self.monitor.get_recent_anomalies(3)
        if len(recent_anomalies) > 0:
            recommendations.append(f"Detected {len(recent_anomalies)} recent anomalies - review system stability")

        # Check learning rate
        lr_status = self.lr_controller.get_state_info()
        if lr_status["plateau_state"] == "plateau":
            recommendations.append("Learning has plateaued - consider adjusting learning rate or architecture")

        # Check success rate
        if self.total_improvements > 10:
            success_rate = self.successful_improvements / self.total_improvements
            if success_rate < 0.5:
                recommendations.append(
                    f"Low improvement success rate ({success_rate*100:.1f}%) - review improvement strategies"
                )

        return recommendations


# Singleton
_orchestrator_instance = None


def get_continuous_improvement_orchestrator(
    config: Optional[ContinuousImprovementConfig] = None
) -> ContinuousImprovementOrchestrator:
    """Get singleton instance of ContinuousImprovementOrchestrator"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ContinuousImprovementOrchestrator(config)
    return _orchestrator_instance
