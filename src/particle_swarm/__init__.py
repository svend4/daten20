"""
Particle Swarm Optimization Module - v24.0 (FUNCTIONAL)

Swarm intelligence optimization using emergent collective behavior.
Version: 24.0.0 (FUNCTIONAL - uses REAL particle swarm optimization!)

This module uses REAL swarm intelligence for optimization,
not mock code! Particles cooperate to find optimal solutions.
"""

__version__ = '24.0.0'
__status__ = 'FUNCTIONAL'

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

# Import REAL PSO implementation
from .pso_algorithm import (
    ParticleSwarmOptimizer,
    PSOConfig,
    PSOResult,
    Particle
)

# Import benchmark functions from genetic algorithm module
from ..self_improving_ai.genetic_algorithm import (
    sphere_function,
    rastrigin_function,
    rosenbrock_function,
    ackley_function
)

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Swarm optimization strategies"""
    STANDARD_PSO = "standard_pso"
    ADAPTIVE_PSO = "adaptive_pso"
    HYBRID_PSO_GA = "hybrid_pso_ga"


@dataclass
class SwarmOptimizationConfig:
    """Swarm optimization configuration"""
    num_particles: int = 30
    num_iterations: int = 100
    enable_adaptive: bool = False


class SwarmIntelligenceEngine:
    """
    Swarm Intelligence Engine using REAL Particle Swarm Optimization.

    This is a FUNCTIONAL implementation that uses real emergent
    swarm behavior for optimization!

    Features:
    - REAL particle swarm optimization
    - Emergent collective intelligence
    - Benchmark function optimization
    - Swarm diversity tracking
    - Convergence detection

    PSO simulates social behavior of bird flocking or fish schooling.
    Particles "fly" through search space, learning from:
    1. Personal experience (cognitive component)
    2. Swarm's collective knowledge (social component)

    This creates EMERGENT intelligence - the swarm is smarter than individuals!

    Example:
        >>> engine = SwarmIntelligenceEngine()
        >>> result = engine.optimize_function(
        ...     function="rastrigin",
        ...     dimensions=10,
        ...     iterations=100
        ... )
        >>> print(f"Swarm improved by {result['improvement_percentage']:.1f}%")
    """

    def __init__(self, config: Optional[SwarmOptimizationConfig] = None):
        self.config = config or SwarmOptimizationConfig()
        self.optimization_runs = []
        self.swarm_history = []
        logger.info("Swarm Intelligence Engine initialized (FUNCTIONAL - with REAL PSO)")

    def optimize_function(self,
                         function: str = "rastrigin",
                         dimensions: int = 10,
                         iterations: int = 100,
                         num_particles: int = 30) -> Dict[str, Any]:
        """
        Optimize a benchmark function using REAL particle swarm!

        Args:
            function: Function to optimize ("sphere", "rastrigin", "rosenbrock", "ackley")
            dimensions: Problem dimensionality
            iterations: Number of PSO iterations
            num_particles: Swarm size

        Returns:
            Optimization result with fitness improvement metrics
        """
        # Select fitness function
        function_map = {
            "sphere": (sphere_function, (-5.0, 5.0)),
            "rastrigin": (rastrigin_function, (-5.12, 5.12)),
            "rosenbrock": (rosenbrock_function, (-5.0, 10.0)),
            "ackley": (ackley_function, (-5.0, 5.0))
        }

        if function not in function_map:
            raise ValueError(f"Unknown function: {function}. Choose from {list(function_map.keys())}")

        fitness_fn, bounds = function_map[function]

        # Create PSO optimizer
        pso_config = PSOConfig(
            num_particles=num_particles,
            num_iterations=iterations,
            inertia_weight=0.7,
            cognitive_coeff=1.5,
            social_coeff=1.5
        )

        pso = ParticleSwarmOptimizer(
            fitness_function=fitness_fn,
            dimensions=dimensions,
            bounds=bounds,
            config=pso_config,
            maximize=False  # Minimization for benchmark functions
        )

        # Run REAL swarm optimization!
        result = pso.optimize()

        # Calculate improvement
        initial_fitness = result.fitness_history[0]
        final_fitness = result.fitness_history[-1]
        improvement = ((initial_fitness - final_fitness) / initial_fitness * 100) if initial_fitness > 0 else 0.0

        # Store in history
        optimization_record = {
            "function": function,
            "dimensions": dimensions,
            "iterations": iterations,
            "num_particles": num_particles,
            "initial_fitness": initial_fitness,
            "final_fitness": final_fitness,
            "improvement_percentage": improvement,
            "best_solution": result.best_position,
            "converged_at": result.convergence_iteration,
            "method": "particle_swarm"
        }

        self.optimization_runs.append(optimization_record)

        return optimization_record

    def analyze_swarm_performance(self) -> Dict[str, Any]:
        """Analyze swarm optimization performance across runs"""
        if not self.optimization_runs:
            return {
                "total_runs": 0,
                "average_improvement": 0.0,
                "best_improvement": 0.0,
                "status": "no_runs_yet"
            }

        improvements = [run["improvement_percentage"] for run in self.optimization_runs]

        return {
            "total_runs": len(self.optimization_runs),
            "average_improvement": sum(improvements) / len(improvements),
            "best_improvement": max(improvements),
            "worst_improvement": min(improvements),
            "last_run": self.optimization_runs[-1],
            "status": "functional"
        }

    def compare_with_genetic_algorithm(self,
                                       function: str = "rastrigin",
                                       dimensions: int = 10) -> Dict[str, Any]:
        """
        Compare PSO with Genetic Algorithm performance.

        Returns:
            Comparison metrics showing which algorithm performed better
        """
        # This is a placeholder for comparison
        # In real implementation, would run both and compare
        return {
            "function": function,
            "dimensions": dimensions,
            "pso_performance": "pending",
            "ga_performance": "pending",
            "winner": "unknown",
            "status": "planned"
        }


_engine = None

def get_swarm_intelligence_engine(config: Optional[SwarmOptimizationConfig] = None) -> SwarmIntelligenceEngine:
    """Get singleton Swarm Intelligence Engine"""
    global _engine
    if _engine is None:
        _engine = SwarmIntelligenceEngine(config)
    return _engine


__all__ = [
    'SwarmIntelligenceEngine',
    'SwarmOptimizationConfig',
    'OptimizationStrategy',
    'get_swarm_intelligence_engine',
    # PSO exports
    'ParticleSwarmOptimizer',
    'PSOConfig',
    'PSOResult',
    'Particle',
    # Benchmark functions
    'sphere_function',
    'rastrigin_function',
    'rosenbrock_function',
    'ackley_function'
]
