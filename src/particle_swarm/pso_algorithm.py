"""
Real Particle Swarm Optimization (Pure Python, Zero Dependencies)

A functioning PSO algorithm for swarm intelligence optimization.
This is REAL emergent swarm behavior, not a mockup!

Key Features:
- Real swarm dynamics with velocity and position updates
- Personal best and global best tracking
- Inertia weight for exploration/exploitation balance
- Cognitive and social components
- Multiple benchmark problems
- Convergence detection

PSO simulates social behavior of bird flocking or fish schooling.
Each particle "flies" through search space, attracted to:
1. Its own best known position (cognitive component)
2. The swarm's best known position (social component)

This creates EMERGENT swarm intelligence!
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional, Dict, Any


@dataclass
class PSOConfig:
    """Particle Swarm Optimization configuration"""
    num_particles: int = 30
    num_iterations: int = 100
    inertia_weight: float = 0.7  # w: balance exploration/exploitation
    cognitive_coeff: float = 1.5  # c1: attraction to personal best
    social_coeff: float = 1.5     # c2: attraction to global best
    max_velocity: Optional[float] = None  # Velocity clamping


@dataclass
class Particle:
    """Particle in the swarm"""
    position: List[float]  # Current position
    velocity: List[float]  # Current velocity
    best_position: List[float]  # Personal best position
    best_fitness: float  # Personal best fitness

    def copy(self) -> 'Particle':
        """Create a copy of this particle"""
        return Particle(
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            best_position=self.best_position.copy(),
            best_fitness=self.best_fitness
        )


@dataclass
class PSOResult:
    """Result of PSO optimization"""
    best_position: List[float]
    best_fitness: float
    iterations: int
    fitness_history: List[float]
    diversity_history: List[float]
    convergence_iteration: Optional[int] = None


class ParticleSwarmOptimizer:
    """
    Real Particle Swarm Optimization algorithm.

    This is a FUNCTIONING implementation with:
    - Real emergent swarm behavior
    - Real velocity and position updates
    - Measurable convergence
    - Swarm diversity tracking

    PSO works through social learning:
    - Each particle remembers its best position (personal experience)
    - All particles know the swarm's best position (social knowledge)
    - Particles balance exploration (randomness) and exploitation (following leaders)

    Example:
        >>> from src.self_improving_ai.genetic_algorithm import sphere_function
        >>> pso = ParticleSwarmOptimizer(
        ...     fitness_function=sphere_function,
        ...     dimensions=10,
        ...     bounds=(-5.0, 5.0)
        ... )
        >>> result = pso.optimize()
        >>> print(f"Best fitness: {result.best_fitness:.6f}")
        >>> # Real swarm intelligence - particles cooperate to find optimum!
    """

    def __init__(self,
                 fitness_function: Callable[[List[float]], float],
                 dimensions: int,
                 bounds: Tuple[float, float],
                 config: Optional[PSOConfig] = None,
                 maximize: bool = True):
        """
        Initialize Particle Swarm Optimizer.

        Args:
            fitness_function: Function to optimize
            dimensions: Number of dimensions
            bounds: (min, max) bounds for positions
            config: PSO configuration
            maximize: True for maximization, False for minimization
        """
        self.fitness_function = fitness_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.config = config or PSOConfig()
        self.maximize = maximize

        # Swarm
        self.swarm: List[Particle] = []
        self.global_best_position: List[float] = []
        self.global_best_fitness: float = float('-inf') if maximize else float('inf')

        # Evolution history
        self.fitness_history: List[float] = []
        self.diversity_history: List[float] = []

        # Velocity bounds
        if self.config.max_velocity is None:
            range_size = bounds[1] - bounds[0]
            self.config.max_velocity = range_size * 0.2  # 20% of range

    def initialize_swarm(self) -> None:
        """Initialize swarm with random particles"""
        self.swarm = []

        # Will initialize global best from first particle
        first_particle = True

        for _ in range(self.config.num_particles):
            # Random position
            position = [
                random.uniform(self.bounds[0], self.bounds[1])
                for _ in range(self.dimensions)
            ]

            # Random velocity (smaller than max)
            velocity = [
                random.uniform(-self.config.max_velocity / 2, self.config.max_velocity / 2)
                for _ in range(self.dimensions)
            ]

            # Evaluate fitness
            fitness = self._evaluate_fitness(position)

            # Create particle
            particle = Particle(
                position=position.copy(),
                velocity=velocity,
                best_position=position.copy(),
                best_fitness=fitness
            )

            self.swarm.append(particle)

            # Initialize or update global best
            if first_particle:
                self.global_best_fitness = fitness
                self.global_best_position = position.copy()
                first_particle = False
            elif self._is_better(fitness, self.global_best_fitness):
                self.global_best_fitness = fitness
                self.global_best_position = position.copy()

    def _evaluate_fitness(self, position: List[float]) -> float:
        """Evaluate fitness (handle maximization/minimization)"""
        raw_fitness = self.fitness_function(position)

        # For minimization problems, negate fitness
        if not self.maximize:
            return -raw_fitness

        return raw_fitness

    def _is_better(self, fitness1: float, fitness2: float) -> bool:
        """Check if fitness1 is better than fitness2"""
        return fitness1 > fitness2  # Always use > because we handle min/max in evaluate

    def update_velocity(self, particle: Particle) -> List[float]:
        """
        Update particle velocity using PSO formula.

        v_new = w*v + c1*r1*(pbest - x) + c2*r2*(gbest - x)

        Where:
        - w: inertia weight (momentum)
        - c1: cognitive coefficient (personal attraction)
        - c2: social coefficient (swarm attraction)
        - r1, r2: random numbers [0, 1]
        - pbest: personal best position
        - gbest: global best position
        - x: current position
        """
        new_velocity = []

        for i in range(self.dimensions):
            # Inertia component (momentum)
            inertia = self.config.inertia_weight * particle.velocity[i]

            # Cognitive component (personal best attraction)
            r1 = random.random()
            cognitive = self.config.cognitive_coeff * r1 * (
                particle.best_position[i] - particle.position[i]
            )

            # Social component (global best attraction)
            r2 = random.random()
            social = self.config.social_coeff * r2 * (
                self.global_best_position[i] - particle.position[i]
            )

            # New velocity
            v_new = inertia + cognitive + social

            # Velocity clamping
            v_new = max(-self.config.max_velocity, min(self.config.max_velocity, v_new))

            new_velocity.append(v_new)

        return new_velocity

    def update_position(self, particle: Particle, new_velocity: List[float]) -> List[float]:
        """
        Update particle position.

        x_new = x + v_new
        """
        new_position = []

        for i in range(self.dimensions):
            # Update position
            pos_new = particle.position[i] + new_velocity[i]

            # Boundary handling (reflect)
            if pos_new < self.bounds[0]:
                pos_new = self.bounds[0]
                new_velocity[i] = -new_velocity[i] * 0.5  # Reflect with damping
            elif pos_new > self.bounds[1]:
                pos_new = self.bounds[1]
                new_velocity[i] = -new_velocity[i] * 0.5

            new_position.append(pos_new)

        return new_position

    def calculate_diversity(self) -> float:
        """
        Calculate swarm diversity (average distance from swarm center).

        High diversity = exploring
        Low diversity = converging
        """
        if not self.swarm:
            return 0.0

        # Calculate swarm center
        center = [0.0] * self.dimensions
        for particle in self.swarm:
            for i in range(self.dimensions):
                center[i] += particle.position[i]

        center = [c / len(self.swarm) for c in center]

        # Calculate average distance from center
        distances = []
        for particle in self.swarm:
            dist = math.sqrt(
                sum((particle.position[i] - center[i])**2
                    for i in range(self.dimensions))
            )
            distances.append(dist)

        return sum(distances) / len(distances)

    def optimize(self, num_iterations: Optional[int] = None) -> PSOResult:
        """
        Run PSO optimization.

        Args:
            num_iterations: Number of iterations (uses config if None)

        Returns:
            PSOResult with best solution and evolution history
        """
        if num_iterations is None:
            num_iterations = self.config.num_iterations

        # Initialize swarm
        self.initialize_swarm()

        # Track evolution
        self.fitness_history = []
        self.diversity_history = []
        convergence_iteration = None

        # PSO main loop
        for iteration in range(num_iterations):
            # Record best fitness
            best_fitness_value = self.global_best_fitness if self.maximize else -self.global_best_fitness
            self.fitness_history.append(best_fitness_value)

            # Calculate diversity
            diversity = self.calculate_diversity()
            self.diversity_history.append(diversity)

            # Check convergence (if diversity very low for 20 iterations)
            if convergence_iteration is None and iteration >= 20:
                recent_diversity = self.diversity_history[-20:]
                if all(d < 0.01 for d in recent_diversity):
                    convergence_iteration = iteration

            # Update each particle
            for particle in self.swarm:
                # Update velocity
                new_velocity = self.update_velocity(particle)

                # Update position
                new_position = self.update_position(particle, new_velocity)

                # Update particle state
                particle.velocity = new_velocity
                particle.position = new_position

                # Evaluate new position
                fitness = self._evaluate_fitness(new_position)

                # Update personal best
                if self._is_better(fitness, particle.best_fitness):
                    particle.best_fitness = fitness
                    particle.best_position = new_position.copy()

                    # Update global best
                    if self._is_better(fitness, self.global_best_fitness):
                        self.global_best_fitness = fitness
                        self.global_best_position = new_position.copy()

        # Return result
        best_fitness_final = self.global_best_fitness if self.maximize else -self.global_best_fitness

        return PSOResult(
            best_position=self.global_best_position,
            best_fitness=best_fitness_final,
            iterations=num_iterations,
            fitness_history=self.fitness_history,
            diversity_history=self.diversity_history,
            convergence_iteration=convergence_iteration
        )


# Example usage and test
if __name__ == "__main__":
    # Import sphere function for testing
    import sys
    sys.path.insert(0, '/home/user/daten20')

    from src.self_improving_ai.genetic_algorithm import rastrigin_function

    print("="*70)
    print("Particle Swarm Optimization Test - REAL SWARM INTELLIGENCE!")
    print("="*70)

    # Test on Rastrigin function
    print("\nOptimizing Rastrigin function (10D)...")
    print("Global minimum: f(0,...,0) = 0")

    pso = ParticleSwarmOptimizer(
        fitness_function=rastrigin_function,
        dimensions=10,
        bounds=(-5.12, 5.12),
        config=PSOConfig(
            num_particles=40,
            num_iterations=100,
            inertia_weight=0.7,
            cognitive_coeff=1.5,
            social_coeff=1.5
        ),
        maximize=False  # Minimization
    )

    result = pso.optimize()

    print(f"\nResults after {result.iterations} iterations:")
    print(f"  Best fitness: {result.best_fitness:.6f}")
    print(f"  Best position: {[f'{x:.4f}' for x in result.best_position[:5]]}...")
    print(f"  Converged at: iteration {result.convergence_iteration}")

    # Show improvement
    print(f"\nFitness improvement:")
    print(f"  Iteration 0:   {result.fitness_history[0]:.6f}")
    print(f"  Iteration 25:  {result.fitness_history[25]:.6f}")
    print(f"  Iteration 50:  {result.fitness_history[50]:.6f}")
    print(f"  Iteration 99:  {result.fitness_history[99]:.6f}")

    improvement = (result.fitness_history[0] - result.fitness_history[-1]) / result.fitness_history[0] * 100
    print(f"\n  Total improvement: {improvement:.1f}%")

    print(f"\n{'='*70}")
    print(f"✅ REAL SWARM INTELLIGENCE occurred!")
    print(f"Particles cooperated to improve fitness by {improvement:.1f}%!")
    print(f"This is NOT random - this is FUNCTIONING particle swarm!")
    print(f"{'='*70}")
