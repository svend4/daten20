"""
Simple CartPole Environment (Pure Python, Zero Dependencies)

A simplified version of the classic CartPole-v1 environment for testing
world models. This is a REAL physics simulation!

CartPole: Balance a pole on a cart by moving left/right.
- State: [x, x_dot, theta, theta_dot] (cart position, velocity, pole angle, angular velocity)
- Action: 0 (left) or 1 (right)
- Reward: +1 for each timestep the pole stays upright
- Done: pole angle > 12 degrees or cart position > 2.4

This transforms v22 from using random data to using REAL physics!
"""

import math
import random
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class CartPoleConfig:
    """Configuration for CartPole environment."""
    gravity: float = 9.8
    mass_cart: float = 1.0
    mass_pole: float = 0.1
    pole_length: float = 0.5  # Half-length of pole
    force_mag: float = 10.0
    tau: float = 0.02  # Timestep (20ms)
    theta_threshold: float = 12.0 * (2 * math.pi / 360)  # 12 degrees
    x_threshold: float = 2.4


class CartPoleEnvironment:
    """
    Simple CartPole physics simulation.

    This is a REAL environment with REAL physics equations!
    Not a mockup - actual Newtonian mechanics.

    The cart-pole system is modeled using the equations:
        x_ddot = (force + pole_mass * pole_length * theta_dot^2 * sin(theta) -
                  pole_mass * gravity * sin(theta) * cos(theta)) / total_mass
        theta_ddot = (gravity * sin(theta) - cos(theta) * x_ddot) / pole_length

    Example:
        >>> env = CartPoleEnvironment()
        >>> state = env.reset()
        >>> next_state, reward, done = env.step(action=1)  # Move right
        >>> # Physics is REAL - state changes according to Newton's laws!
    """

    def __init__(self, config: CartPoleConfig = None):
        """Initialize CartPole environment."""
        self.config = config or CartPoleConfig()

        # State: [x, x_dot, theta, theta_dot]
        self.state = [0.0, 0.0, 0.0, 0.0]
        self.steps = 0
        self.done = False

        # Total mass
        self.total_mass = self.config.mass_cart + self.config.mass_pole
        self.polemass_length = self.config.mass_pole * self.config.pole_length

    def reset(self) -> List[float]:
        """
        Reset environment to initial state.

        Returns:
            Initial state vector [x, x_dot, theta, theta_dot]
        """
        # Random initial state (small perturbation)
        self.state = [
            random.uniform(-0.05, 0.05),  # x
            random.uniform(-0.05, 0.05),  # x_dot
            random.uniform(-0.05, 0.05),  # theta (radians)
            random.uniform(-0.05, 0.05)   # theta_dot
        ]
        self.steps = 0
        self.done = False
        return self.state.copy()

    def step(self, action: int) -> Tuple[List[float], float, bool]:
        """
        Take one step in the environment using REAL physics!

        Args:
            action: 0 (push left) or 1 (push right)

        Returns:
            Tuple of (next_state, reward, done)
        """
        if self.done:
            return self.state.copy(), 0.0, True

        # Extract current state
        x, x_dot, theta, theta_dot = self.state

        # Apply force
        force = self.config.force_mag if action == 1 else -self.config.force_mag

        # Physics calculation (REAL Newtonian mechanics!)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        # Temporary variable for calculation
        temp = (force + self.polemass_length * theta_dot**2 * sin_theta) / self.total_mass

        # Angular acceleration (theta_ddot)
        theta_acc = (self.config.gravity * sin_theta - cos_theta * temp) / (
            self.config.pole_length * (4.0/3.0 - self.config.mass_pole * cos_theta**2 / self.total_mass)
        )

        # Linear acceleration (x_ddot)
        x_acc = temp - self.polemass_length * theta_acc * cos_theta / self.total_mass

        # Euler integration (semi-implicit)
        x_dot = x_dot + self.config.tau * x_acc
        x = x + self.config.tau * x_dot
        theta_dot = theta_dot + self.config.tau * theta_acc
        theta = theta + self.config.tau * theta_dot

        # Update state
        self.state = [x, x_dot, theta, theta_dot]
        self.steps += 1

        # Check termination conditions
        done = bool(
            x < -self.config.x_threshold or
            x > self.config.x_threshold or
            theta < -self.config.theta_threshold or
            theta > self.config.theta_threshold
        )

        self.done = done

        # Reward: +1 for staying alive
        reward = 1.0 if not done else 0.0

        return self.state.copy(), reward, done

    def sample_action(self) -> int:
        """Sample random action (for exploration)."""
        return random.randint(0, 1)

    def get_state_dim(self) -> int:
        """Get state dimensionality."""
        return 4

    def get_action_dim(self) -> int:
        """Get number of actions."""
        return 2


def collect_random_transitions(env: CartPoleEnvironment,
                              num_episodes: int = 10,
                              max_steps: int = 200) -> List[Tuple[List[float], int, List[float], float, bool]]:
    """
    Collect random transitions for training world model.

    Args:
        env: CartPole environment
        num_episodes: Number of episodes to collect
        max_steps: Max steps per episode

    Returns:
        List of transitions (state, action, next_state, reward, done)
    """
    transitions = []

    for episode in range(num_episodes):
        state = env.reset()

        for step in range(max_steps):
            action = env.sample_action()
            next_state, reward, done = env.step(action)

            transitions.append((
                state.copy(),
                action,
                next_state.copy(),
                reward,
                done
            ))

            state = next_state

            if done:
                break

    return transitions


# Example usage and test
if __name__ == "__main__":
    print("="*60)
    print("CartPole Environment Test - REAL PHYSICS!")
    print("="*60)

    # Create environment
    env = CartPoleEnvironment()

    print(f"\nEnvironment configuration:")
    print(f"  State dim: {env.get_state_dim()} [x, x_dot, theta, theta_dot]")
    print(f"  Action dim: {env.get_action_dim()} [left=0, right=1]")
    print(f"  Gravity: {env.config.gravity} m/s^2")
    print(f"  Pole length: {env.config.pole_length*2} m")
    print(f"  Timestep: {env.config.tau} sec")

    # Run one episode
    print(f"\nRunning one episode with random policy...")
    print(f"Step | x      | x_dot  | theta  | theta_dot | Reward")
    print("-" * 60)

    state = env.reset()
    total_reward = 0.0

    for step in range(100):
        action = env.sample_action()
        next_state, reward, done = env.step(action)
        total_reward += reward

        if step % 10 == 0:
            x, x_dot, theta, theta_dot = next_state
            print(f"{step:4d} | {x:6.3f} | {x_dot:6.3f} | {theta:6.3f} | {theta_dot:9.3f} | {reward:.1f}")

        if done:
            print(f"\nEpisode ended at step {step+1}")
            break

    print(f"\nTotal reward: {total_reward:.1f}")

    # Collect dataset
    print(f"\n{'='*60}")
    print("Collecting dataset for world model training...")
    transitions = collect_random_transitions(env, num_episodes=10, max_steps=200)
    print(f"Collected {len(transitions)} transitions")

    # Analyze transitions
    avg_reward = sum(t[3] for t in transitions) / len(transitions)
    num_terminal = sum(1 for t in transitions if t[4])

    print(f"\nDataset statistics:")
    print(f"  Total transitions: {len(transitions)}")
    print(f"  Average reward: {avg_reward:.3f}")
    print(f"  Terminal states: {num_terminal}")

    print(f"\n{'='*60}")
    print("✅ CartPole environment is FUNCTIONING!")
    print("Physics is REAL - governed by Newton's laws!")
    print("This is NOT a mockup - this is a REAL benchmark!")
    print("="*60)
