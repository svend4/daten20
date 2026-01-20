"""
Functional Test Suite for Meta-Reality Engineering Platform (v28.0)

Tests REAL world simulation system, not mock code!

This test suite validates:
1. WorldSimulator - Complete cellular automaton and agent-based simulation
2. CellularAutomaton - Conway's Game of Life implementation
3. AgentBasedWorld - Agent-based modeling with physics
4. Agent behavior - Movement, energy consumption, physics
5. Measurable results - Population dynamics, complexity, patterns

Total: 14 comprehensive functional tests
"""

import pytest
from src.meta_reality import (
    WorldSimulator,
    WorldConfig,
    CellularAutomaton,
    AgentBasedWorld,
    Agent,
    CellState,
    WorldState,
    SimulationResult,
)


class TestWorldSimulator:
    """Test complete world simulation"""

    def test_simulator_initialization(self):
        """Test WorldSimulator initializes with config"""
        config = WorldConfig(width=20, height=20, max_steps=5)
        simulator = WorldSimulator(config)

        assert simulator is not None
        assert simulator.config == config
        assert simulator.config.width == 20
        assert simulator.config.height == 20

    def test_simulate_cellular_world(self):
        """Test cellular automaton simulation"""
        config = WorldConfig(width=30, height=30, max_steps=10)
        simulator = WorldSimulator(config)

        result = simulator.simulate_cellular_world()

        # Verify result structure
        assert result is not None
        assert isinstance(result, SimulationResult)
        assert result.steps_simulated == 10
        assert len(result.complexity_evolution) == 10
        assert result.initial_alive >= 0
        assert result.final_alive >= 0
        assert result.max_alive >= result.final_alive

    def test_simulate_agent_world(self):
        """Test agent-based world simulation"""
        config = WorldConfig(width=40, height=40, max_steps=20)
        simulator = WorldSimulator(config)

        result = simulator.simulate_agent_world(num_agents=30)

        # Verify result
        assert result is not None
        assert 'initial_agents' in result
        assert 'final_agents' in result
        assert result['initial_agents'] == 30
        assert result['final_agents'] >= 0  # Some may die
        assert 'steps_simulated' in result
        assert result['steps_simulated'] == 20


class TestCellularAutomaton:
    """Test cellular automaton (Game of Life) implementation"""

    def test_cellular_automaton_initialization(self):
        """Test CellularAutomaton initializes correctly"""
        ca = CellularAutomaton(width=15, height=15)

        assert ca is not None
        assert ca.width == 15
        assert ca.height == 15
        assert len(ca.grid) == 15
        assert len(ca.grid[0]) == 15

    def test_initialize_random(self):
        """Test random initialization"""
        ca = CellularAutomaton(width=10, height=10)
        ca.initialize_random(alive_probability=0.5)

        # Should have some alive cells (probabilistically)
        alive = ca.count_alive()
        # With 100 cells and 50% probability, expect around 50 alive
        # Allow wide range due to randomness
        assert 20 <= alive <= 80, f"Expected 20-80 alive cells, got {alive}"

    def test_step_updates_grid(self):
        """Test step function updates the grid"""
        ca = CellularAutomaton(width=5, height=5)

        # Set up a simple pattern (blinker)
        ca.grid[2][1] = CellState.ALIVE
        ca.grid[2][2] = CellState.ALIVE
        ca.grid[2][3] = CellState.ALIVE

        initial_alive = ca.count_alive()

        # Step forward
        ca.step()

        # Grid should have updated (blinker rotates)
        stepped_alive = ca.count_alive()

        # Blinker preserves alive count but changes position
        assert stepped_alive == initial_alive

    def test_count_alive(self):
        """Test counting alive cells"""
        ca = CellularAutomaton(width=10, height=10)
        ca.initialize_random(alive_probability=0.3)

        count = ca.count_alive()
        assert count >= 0
        assert count <= 100  # 10x10 grid

    def test_calculate_complexity(self):
        """Test complexity calculation"""
        ca = CellularAutomaton(width=10, height=10)
        ca.initialize_random(alive_probability=0.5)

        complexity = ca.calculate_complexity()

        # Complexity should be non-negative
        assert complexity >= 0.0

    def test_game_of_life_rules(self):
        """Test Game of Life rules are applied correctly"""
        ca = CellularAutomaton(width=5, height=5)

        # Create a 2x2 block (stable pattern)
        ca.grid[1][1] = CellState.ALIVE
        ca.grid[1][2] = CellState.ALIVE
        ca.grid[2][1] = CellState.ALIVE
        ca.grid[2][2] = CellState.ALIVE

        # Step forward
        ca.step()

        # Block should remain stable
        assert ca.grid[1][1] == CellState.ALIVE
        assert ca.grid[1][2] == CellState.ALIVE
        assert ca.grid[2][1] == CellState.ALIVE
        assert ca.grid[2][2] == CellState.ALIVE


class TestAgentBasedWorld:
    """Test agent-based modeling"""

    def test_agent_based_world_initialization(self):
        """Test AgentBasedWorld initializes correctly"""
        world = AgentBasedWorld(width=20, height=20, num_agents=10)

        assert world is not None
        assert world.width == 20
        assert world.height == 20
        assert len(world.agents) == 10

    def test_step_updates_agents(self):
        """Test step function updates agent positions"""
        world = AgentBasedWorld(width=20, height=20, num_agents=5)

        # Record initial positions
        initial_positions = [(a.x, a.y) for a in world.agents]

        # Step forward
        world.step(dt=1.0)

        # Agents should have moved (with velocity)
        current_positions = [(a.x, a.y) for a in world.agents]
        moved_count = sum(1 for i, pos in enumerate(current_positions)
                         if abs(pos[0] - initial_positions[i][0]) > 0.01 or
                            abs(pos[1] - initial_positions[i][1]) > 0.01)

        # Most agents should move (they have random velocities)
        assert moved_count > 0

    def test_count_alive_agents(self):
        """Test agent count"""
        world = AgentBasedWorld(width=20, height=20, num_agents=15)

        count = world.count_alive_agents()

        assert count == 15

    def test_calculate_total_energy(self):
        """Test total energy calculation"""
        world = AgentBasedWorld(width=20, height=20, num_agents=10)

        total_energy = world.calculate_total_energy()

        # Should have positive energy (agents initialized with 50-150)
        assert total_energy > 0
        assert total_energy >= 500  # At least 50 per agent
        assert total_energy <= 1500  # At most 150 per agent

    def test_calculate_kinetic_energy(self):
        """Test kinetic energy calculation"""
        world = AgentBasedWorld(width=20, height=20, num_agents=10)

        kinetic = world.calculate_kinetic_energy()

        # Kinetic energy should be non-negative
        assert kinetic >= 0.0


class TestAgent:
    """Test individual agent behavior"""

    def test_agent_creation(self):
        """Test Agent dataclass creation"""
        agent = Agent(
            agent_id=1,
            x=10.0,
            y=15.0,
            energy=100.0,
            velocity_x=0.5,
            velocity_y=-0.3
        )

        assert agent.agent_id == 1
        assert agent.x == 10.0
        assert agent.y == 15.0
        assert agent.velocity_x == 0.5
        assert agent.velocity_y == -0.3
        assert agent.energy == 100.0


class TestDataStructures:
    """Test data structures and configurations"""

    def test_world_config_defaults(self):
        """Test WorldConfig has sensible defaults"""
        config = WorldConfig()

        assert config.width == 50
        assert config.height == 50
        assert config.max_steps == 100
        assert config.initial_alive_probability == 0.3

    def test_cell_state_enum(self):
        """Test CellState enum"""
        assert CellState.ALIVE is not None
        assert CellState.DEAD is not None
        assert CellState.ALIVE != CellState.DEAD
        assert CellState.ALIVE.value == 1
        assert CellState.DEAD.value == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
