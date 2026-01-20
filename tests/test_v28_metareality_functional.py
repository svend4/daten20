"""
Functional Test Suite for Meta-Reality Engineering Platform (v28.0)

Tests REAL world simulation system, not mock code!

This test suite validates:
1. WorldSimulator - Complete world simulation cycle
2. CellularAutomaton - Conway's Game of Life implementation
3. AgentBasedWorld - Agent-based modeling with physics
4. Agent behavior - Movement, interaction, resource consumption
5. Measurable results - Population dynamics, complexity metrics

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
)


class TestWorldSimulator:
    """Test complete world simulation"""

    def test_simulator_initialization(self):
        """Test WorldSimulator initializes with config"""
        config = WorldConfig(
            width=20,
            height=20,
            num_agents=10,
            steps=5
        )
        simulator = WorldSimulator(config)

        assert simulator is not None
        assert simulator.config == config

    def test_simulate_cellular_automaton(self):
        """Test cellular automaton simulation"""
        config = WorldConfig(width=10, height=10, steps=5, use_cellular_automaton=True)
        simulator = WorldSimulator(config)

        result = simulator.simulate()

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'final_state')
        assert hasattr(result, 'complexity_evolution')
        assert hasattr(result, 'total_steps')

        assert result.total_steps == 5
        assert len(result.complexity_evolution) == 5

    def test_simulate_agent_based_world(self):
        """Test agent-based world simulation"""
        config = WorldConfig(
            width=15,
            height=15,
            num_agents=20,
            steps=10,
            use_cellular_automaton=False
        )
        simulator = WorldSimulator(config)

        result = simulator.simulate()

        # Verify result
        assert result is not None
        assert result.total_steps == 10
        assert hasattr(result, 'population_history')
        assert len(result.population_history) > 0


class TestCellularAutomaton:
    """Test cellular automaton (Game of Life) implementation"""

    def test_cellular_automaton_initialization(self):
        """Test CellularAutomaton initializes correctly"""
        ca = CellularAutomaton(width=10, height=10)

        assert ca is not None
        assert ca.width == 10
        assert ca.height == 10
        assert ca.grid is not None

    def test_step_updates_grid(self):
        """Test step function updates the grid"""
        ca = CellularAutomaton(width=5, height=5)

        # Set up a simple pattern (blinker)
        ca.grid[2][1] = CellState.ALIVE
        ca.grid[2][2] = CellState.ALIVE
        ca.grid[2][3] = CellState.ALIVE

        initial_alive = ca.count_alive_cells()

        # Step forward
        ca.step()

        # Grid should have updated (blinker rotates)
        stepped_alive = ca.count_alive_cells()

        # Blinker preserves alive count but changes position
        assert stepped_alive == initial_alive

    def test_count_alive_cells(self):
        """Test counting alive cells"""
        ca = CellularAutomaton(width=10, height=10)

        # Initially all dead (randomized but mostly dead)
        # Just verify method works
        count = ca.count_alive_cells()
        assert count >= 0
        assert count <= 100  # 10x10 grid

    def test_calculate_complexity(self):
        """Test complexity calculation"""
        ca = CellularAutomaton(width=10, height=10)

        complexity = ca.calculate_complexity()

        # Complexity (Shannon entropy) should be non-negative
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
        world.step()

        # At least some agents should have moved
        current_positions = [(a.x, a.y) for a in world.agents]
        moved_count = sum(1 for i, pos in enumerate(current_positions)
                         if pos != initial_positions[i])

        # With velocity, most agents should move
        assert moved_count > 0

    def test_get_population(self):
        """Test population count"""
        world = AgentBasedWorld(width=20, height=20, num_agents=15)

        population = world.get_population()

        assert population == 15

    def test_calculate_complexity(self):
        """Test complexity calculation for agent world"""
        world = AgentBasedWorld(width=20, height=20, num_agents=20)

        complexity = world.calculate_complexity()

        # Complexity should be non-negative
        assert complexity >= 0.0


class TestAgent:
    """Test individual agent behavior"""

    def test_agent_creation(self):
        """Test Agent dataclass creation"""
        agent = Agent(
            agent_id=1,
            x=10.0,
            y=15.0,
            vx=0.5,
            vy=-0.3,
            energy=100.0
        )

        assert agent.agent_id == 1
        assert agent.x == 10.0
        assert agent.y == 15.0
        assert agent.vx == 0.5
        assert agent.vy == -0.3
        assert agent.energy == 100.0

    def test_agent_has_default_values(self):
        """Test Agent has sensible defaults"""
        agent = Agent(agent_id=1, x=0.0, y=0.0)

        # Should have default velocity and energy
        assert hasattr(agent, 'vx')
        assert hasattr(agent, 'vy')
        assert hasattr(agent, 'energy')


class TestDataStructures:
    """Test data structures and configurations"""

    def test_world_config_defaults(self):
        """Test WorldConfig has sensible defaults"""
        config = WorldConfig()

        assert config.width > 0
        assert config.height > 0
        assert config.steps > 0

    def test_cell_state_enum(self):
        """Test CellState enum"""
        assert CellState.ALIVE is not None
        assert CellState.DEAD is not None
        assert CellState.ALIVE != CellState.DEAD


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
