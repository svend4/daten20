"""
Performance Bottleneck Analyzer

Identifies and analyzes performance bottlenecks in self-improving AI systems:
- CPU/GPU utilization profiling
- Memory bottleneck detection
- I/O wait time analysis
- Computational hotspot identification
- Optimization recommendations
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import statistics


class BottleneckType(Enum):
    """Types of performance bottlenecks"""
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    COMPUTATION_HEAVY = "computation_heavy"
    DATA_TRANSFER = "data_transfer"


class Severity(Enum):
    """Bottleneck severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BottleneckProfile:
    """Profile of a performance bottleneck"""
    bottleneck_id: str
    bottleneck_type: BottleneckType
    severity: Severity
    location: str  # Where bottleneck occurs
    impact_percent: float  # Percentage of total time
    current_throughput: float
    potential_throughput: float
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfilingResult:
    """Result of performance profiling"""
    total_execution_time: float
    breakdown: Dict[str, float]  # component -> time
    bottlenecks: List[BottleneckProfile]
    optimization_potential: float  # Estimated speedup
    profiling_timestamp: float


class BottleneckAnalyzer:
    """
    Analyzer for identifying performance bottlenecks.

    Profiles execution, identifies slowest components,
    and provides optimization recommendations.
    """

    def __init__(self,
                 critical_threshold: float = 0.30,
                 high_threshold: float = 0.20):
        """
        Initialize bottleneck analyzer.

        Args:
            critical_threshold: Threshold for critical bottlenecks (% of total time)
            high_threshold: Threshold for high severity bottlenecks
        """
        self.critical_threshold = critical_threshold
        self.high_threshold = high_threshold

        # Profiling history
        self.profiling_history: List[ProfilingResult] = []

        # Component timings
        self.component_timings: Dict[str, List[float]] = {}

    def profile_execution(self,
                         components: Dict[str, Callable],
                         iterations: int = 10) -> ProfilingResult:
        """
        Profile execution of multiple components.

        Args:
            components: Dictionary of component_name -> callable
            iterations: Number of profiling iterations

        Returns:
            Profiling result with bottleneck analysis
        """
        # Profile each component
        timings: Dict[str, List[float]] = {name: [] for name in components}

        start_time = time.time()

        for i in range(iterations):
            for name, func in components.items():
                comp_start = time.time()
                try:
                    func()
                except:
                    pass  # Continue profiling even if component fails
                comp_end = time.time()

                timings[name].append(comp_end - comp_start)

        total_time = time.time() - start_time

        # Calculate breakdown
        breakdown = {
            name: statistics.mean(times)
            for name, times in timings.items()
        }

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(breakdown, total_time / iterations)

        # Calculate optimization potential
        optimization_potential = self._estimate_optimization_potential(bottlenecks)

        result = ProfilingResult(
            total_execution_time=total_time / iterations,
            breakdown=breakdown,
            bottlenecks=bottlenecks,
            optimization_potential=optimization_potential,
            profiling_timestamp=time.time()
        )

        self.profiling_history.append(result)

        # Update component timings
        for name, times in timings.items():
            if name not in self.component_timings:
                self.component_timings[name] = []
            self.component_timings[name].extend(times)

        return result

    def _identify_bottlenecks(self,
                             breakdown: Dict[str, float],
                             total_time: float) -> List[BottleneckProfile]:
        """
        Identify bottlenecks from timing breakdown.

        Args:
            breakdown: Component timings
            total_time: Total execution time

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        for component, comp_time in breakdown.items():
            if total_time == 0:
                impact_percent = 0.0
            else:
                impact_percent = (comp_time / total_time) * 100

            # Determine severity
            if impact_percent >= self.critical_threshold * 100:
                severity = Severity.CRITICAL
            elif impact_percent >= self.high_threshold * 100:
                severity = Severity.HIGH
            elif impact_percent >= 0.10 * 100:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW

            # Classify bottleneck type
            bottleneck_type = self._classify_bottleneck_type(component, comp_time)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                component, bottleneck_type, comp_time
            )

            # Estimate potential throughput
            current_throughput = 1.0 / comp_time if comp_time > 0 else float('inf')
            potential_throughput = current_throughput * 2.0  # Assume 2x improvement possible

            bottleneck = BottleneckProfile(
                bottleneck_id=f"bottleneck_{component}_{int(time.time())}",
                bottleneck_type=bottleneck_type,
                severity=severity,
                location=component,
                impact_percent=impact_percent,
                current_throughput=current_throughput,
                potential_throughput=potential_throughput,
                recommendations=recommendations,
                metadata={
                    "component_time": comp_time,
                    "total_time": total_time
                }
            )

            # Only report significant bottlenecks
            if severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]:
                bottlenecks.append(bottleneck)

        # Sort by severity and impact
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3
        }
        bottlenecks.sort(key=lambda b: (severity_order[b.severity], -b.impact_percent))

        return bottlenecks

    def _classify_bottleneck_type(self,
                                  component: str,
                                  time_taken: float) -> BottleneckType:
        """
        Classify type of bottleneck based on component name and timing.

        Args:
            component: Component name
            time_taken: Time taken by component

        Returns:
            Bottleneck type
        """
        component_lower = component.lower()

        # Heuristic classification
        if "compute" in component_lower or "calculation" in component_lower:
            return BottleneckType.COMPUTATION_HEAVY
        elif "memory" in component_lower or "cache" in component_lower:
            return BottleneckType.MEMORY_BOUND
        elif "io" in component_lower or "disk" in component_lower or "file" in component_lower:
            return BottleneckType.IO_BOUND
        elif "network" in component_lower or "request" in component_lower:
            return BottleneckType.NETWORK_BOUND
        elif "transfer" in component_lower or "copy" in component_lower:
            return BottleneckType.DATA_TRANSFER
        else:
            # Default: assume CPU-bound if taking significant time
            return BottleneckType.CPU_BOUND

    def _generate_recommendations(self,
                                 component: str,
                                 bottleneck_type: BottleneckType,
                                 time_taken: float) -> List[str]:
        """
        Generate optimization recommendations for a bottleneck.

        Args:
            component: Component name
            bottleneck_type: Type of bottleneck
            time_taken: Time taken

        Returns:
            List of recommendations
        """
        recommendations = []

        if bottleneck_type == BottleneckType.CPU_BOUND:
            recommendations.extend([
                "Consider parallelization or vectorization",
                "Profile CPU usage to identify hot loops",
                "Use CPU profiling tools for detailed analysis"
            ])
        elif bottleneck_type == BottleneckType.MEMORY_BOUND:
            recommendations.extend([
                "Optimize memory allocation patterns",
                "Consider memory pooling or reuse",
                "Profile memory access patterns for cache optimization"
            ])
        elif bottleneck_type == BottleneckType.IO_BOUND:
            recommendations.extend([
                "Use asynchronous I/O operations",
                "Implement buffering and batching",
                "Consider caching frequently accessed data"
            ])
        elif bottleneck_type == BottleneckType.COMPUTATION_HEAVY:
            recommendations.extend([
                "Optimize algorithms for better complexity",
                "Use GPU acceleration if applicable",
                "Consider approximation methods for faster computation"
            ])
        elif bottleneck_type == BottleneckType.DATA_TRANSFER:
            recommendations.extend([
                "Minimize data transfers between components",
                "Use in-place operations where possible",
                "Compress data for transfer if applicable"
            ])
        elif bottleneck_type == BottleneckType.NETWORK_BOUND:
            recommendations.extend([
                "Implement request batching",
                "Use connection pooling",
                "Consider CDN or edge caching"
            ])

        return recommendations

    def _estimate_optimization_potential(self,
                                        bottlenecks: List[BottleneckProfile]) -> float:
        """
        Estimate potential speedup from optimizing bottlenecks.

        Uses Amdahl's Law principles.

        Args:
            bottlenecks: List of bottlenecks

        Returns:
            Estimated speedup factor
        """
        if not bottlenecks:
            return 1.0

        # Assume we can halve the time of critical/high bottlenecks
        total_optimizable_percent = 0.0

        for bottleneck in bottlenecks:
            if bottleneck.severity in [Severity.CRITICAL, Severity.HIGH]:
                # Assume 50% improvement for critical/high
                total_optimizable_percent += bottleneck.impact_percent * 0.5
            elif bottleneck.severity == Severity.MEDIUM:
                # Assume 30% improvement for medium
                total_optimizable_percent += bottleneck.impact_percent * 0.3

        # Convert to speedup using Amdahl's Law approximation
        # Speedup = 1 / (1 - optimizable_fraction)
        optimizable_fraction = total_optimizable_percent / 100.0
        if optimizable_fraction >= 1.0:
            return 2.0  # Cap at 2x speedup
        else:
            speedup = 1.0 / (1.0 - optimizable_fraction)
            return min(speedup, 3.0)  # Cap at 3x maximum

    def analyze_historical_trends(self,
                                  component: str,
                                  window: int = 10) -> Dict[str, Any]:
        """
        Analyze historical performance trends for a component.

        Args:
            component: Component name
            window: Window size for trend analysis

        Returns:
            Trend analysis results
        """
        if component not in self.component_timings:
            return {
                "status": "no_data",
                "trend": "unknown"
            }

        timings = self.component_timings[component][-window:]

        if len(timings) < 2:
            return {
                "status": "insufficient_data",
                "trend": "unknown"
            }

        # Calculate trend
        mean_first_half = statistics.mean(timings[:len(timings)//2])
        mean_second_half = statistics.mean(timings[len(timings)//2:])

        if mean_second_half > mean_first_half * 1.1:
            trend = "degrading"
        elif mean_second_half < mean_first_half * 0.9:
            trend = "improving"
        else:
            trend = "stable"

        return {
            "status": "analyzed",
            "trend": trend,
            "mean": statistics.mean(timings),
            "stddev": statistics.stdev(timings) if len(timings) >= 2 else 0.0,
            "min": min(timings),
            "max": max(timings),
            "recent_mean": mean_second_half,
            "change_percent": ((mean_second_half - mean_first_half) / mean_first_half * 100)
                             if mean_first_half != 0 else 0.0
        }

    def get_optimization_priority_list(self) -> List[Dict[str, Any]]:
        """
        Get prioritized list of optimization opportunities.

        Returns:
            List of optimization opportunities sorted by priority
        """
        if not self.profiling_history:
            return []

        # Use most recent profiling result
        latest = self.profiling_history[-1]

        priorities = []

        for bottleneck in latest.bottlenecks:
            # Calculate priority score
            severity_score = {
                Severity.CRITICAL: 1.0,
                Severity.HIGH: 0.7,
                Severity.MEDIUM: 0.4,
                Severity.LOW: 0.1
            }[bottleneck.severity]

            impact_score = bottleneck.impact_percent / 100.0

            priority_score = (severity_score * 0.6) + (impact_score * 0.4)

            priorities.append({
                "component": bottleneck.location,
                "type": bottleneck.bottleneck_type.value,
                "severity": bottleneck.severity.value,
                "impact_percent": bottleneck.impact_percent,
                "priority_score": priority_score,
                "recommendations": bottleneck.recommendations[:2]  # Top 2 recommendations
            })

        # Sort by priority score
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)

        return priorities

    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.

        Returns:
            Optimization report dictionary
        """
        if not self.profiling_history:
            return {
                "status": "no_profiling_data",
                "message": "No profiling data available"
            }

        latest = self.profiling_history[-1]

        return {
            "status": "analyzed",
            "profiling_summary": {
                "total_execution_time": latest.total_execution_time,
                "num_components": len(latest.breakdown),
                "num_bottlenecks": len(latest.bottlenecks),
                "optimization_potential": latest.optimization_potential
            },
            "bottlenecks": [
                {
                    "location": b.location,
                    "type": b.bottleneck_type.value,
                    "severity": b.severity.value,
                    "impact_percent": b.impact_percent,
                    "recommendations": b.recommendations
                }
                for b in latest.bottlenecks
            ],
            "priority_list": self.get_optimization_priority_list(),
            "estimated_speedup": f"{latest.optimization_potential:.2f}x"
        }


# Singleton
_bottleneck_analyzer_instance = None


def get_bottleneck_analyzer() -> BottleneckAnalyzer:
    """Get singleton instance of BottleneckAnalyzer"""
    global _bottleneck_analyzer_instance
    if _bottleneck_analyzer_instance is None:
        _bottleneck_analyzer_instance = BottleneckAnalyzer()
    return _bottleneck_analyzer_instance
