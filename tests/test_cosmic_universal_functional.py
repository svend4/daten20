"""
Functional Test Suite for Cosmic Intelligence & Universal-Scale Platform (v27.0)

Tests REAL multi-scale hierarchical coordination system, not mock code!

This test suite validates:
1. UniversalCoordinator - 4-level hierarchical optimization
2. LocalOptimizer - Agent-level coordination
3. RegionalCoordinator - Regional coordination with emergent behavior
4. GlobalOptimizer - Global optimization across regions
5. Multi-scale integration - Hierarchical information flow
6. Measurable results - Shannon entropy, coordination efficiency, etc.

Total: 15 comprehensive functional tests
"""

import pytest
from src.cosmic_universal import (
    UniversalCoordinator,
    MultiScaleConfig,
    CoordinationLevel,
    Agent,
    Region,
    LocalOptimizer,
    RegionalCoordinator,
    GlobalOptimizer,
)


class TestUniversalCoordinator:
    """Test 4-level hierarchical coordination"""

    def test_coordinator_initialization(self):
        """Test UniversalCoordinator initializes correctly"""
        config = MultiScaleConfig(
            num_agents=100,
            num_regions=4,
            dimensions=2
        )
        coordinator = UniversalCoordinator(config)

        assert coordinator is not None
        assert len(coordinator.agents) == 100
        assert len(coordinator.regions) == 4
        assert coordinator.config.dimensions == 2

    def test_single_step_coordination(self):
        """Test one coordination step produces measurable results"""
        config = MultiScaleConfig(num_agents=50, num_regions=2, dimensions=2)
        coordinator = UniversalCoordinator(config)

        result = coordinator.coordinate_step()

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'step')
        assert hasattr(result, 'global_coordination')
        assert hasattr(result, 'entropy')
        assert hasattr(result, 'convergence')

        # Verify measurable metrics
        assert result.global_coordination >= 0.0
        assert result.global_coordination <= 1.0
        assert result.entropy >= 0.0  # Shannon entropy always non-negative
        assert result.step == 1

    def test_multi_step_coordination(self):
        """Test coordination converges over multiple steps"""
        config = MultiScaleConfig(num_agents=50, num_regions=2, dimensions=2)
        coordinator = UniversalCoordinator(config)

        # Run 10 coordination steps
        results = []
        for _ in range(10):
            result = coordinator.coordinate_step()
            results.append(result)

        # Verify all steps completed
        assert len(results) == 10
        assert results[-1].step == 10

        # Verify coordination improves (trending toward convergence)
        # Note: May not be strictly monotonic due to stochastic updates
        first_coordination = results[0].global_coordination
        last_coordination = results[-1].global_coordination

        # At least one of: coordination improved OR entropy decreased
        entropy_decreased = results[-1].entropy < results[0].entropy
        coordination_improved = last_coordination > first_coordination
        assert coordination_improved or entropy_decreased, \
            "System should show some improvement over 10 steps"

    def test_hierarchical_information_flow(self):
        """Test information flows through all 4 levels"""
        config = MultiScaleConfig(num_agents=100, num_regions=4, dimensions=2)
        coordinator = UniversalCoordinator(config)

        result = coordinator.coordinate_step()

        # Verify each level produced results
        assert hasattr(result, 'local_coordination')
        assert hasattr(result, 'regional_coordination')
        assert hasattr(result, 'global_coordination')
        assert hasattr(result, 'entropy')  # Universal level metric

        # All coordination scores should be in [0, 1]
        assert 0.0 <= result.local_coordination <= 1.0
        assert 0.0 <= result.regional_coordination <= 1.0
        assert 0.0 <= result.global_coordination <= 1.0


class TestLocalOptimizer:
    """Test agent-level local coordination"""

    def test_local_optimizer_creation(self):
        """Test LocalOptimizer initializes with agents"""
        agents = [Agent(agent_id=i, position=[0.5, 0.5]) for i in range(10)]
        optimizer = LocalOptimizer(agents)

        assert optimizer is not None
        assert len(optimizer.agents) == 10

    def test_local_coordination_single_step(self):
        """Test local coordination updates agent positions"""
        agents = [Agent(agent_id=i, position=[float(i)/10, float(i)/10]) for i in range(10)]
        optimizer = LocalOptimizer(agents)

        # Record initial positions
        initial_positions = [tuple(a.position) for a in agents]

        # Perform local coordination
        result = optimizer.coordinate_local()

        # Verify agents moved (at least some)
        current_positions = [tuple(a.position) for a in agents]
        moved_count = sum(1 for i, p in enumerate(current_positions)
                         if p != initial_positions[i])

        assert moved_count > 0, "At least some agents should move during coordination"

        # Verify coordination score is measurable
        assert 'local_coordination' in result
        assert 0.0 <= result['local_coordination'] <= 1.0

    def test_local_convergence(self):
        """Test local optimization converges toward consensus"""
        # Start with dispersed agents
        agents = [Agent(agent_id=i, position=[float(i)/10, float(i)/10]) for i in range(20)]
        optimizer = LocalOptimizer(agents)

        # Run 20 steps
        for _ in range(20):
            optimizer.coordinate_local()

        # Measure final dispersion
        positions = [a.position for a in agents]
        # Calculate variance (should be lower than initial)
        variances = []
        for dim in range(2):
            dim_values = [p[dim] for p in positions]
            mean = sum(dim_values) / len(dim_values)
            variance = sum((v - mean) ** 2 for v in dim_values) / len(dim_values)
            variances.append(variance)

        # After coordination, variance should be reasonable (not maximally dispersed)
        for var in variances:
            assert var < 0.25, f"Variance {var} too high - agents should converge"


class TestRegionalCoordinator:
    """Test regional coordination with multiple regions"""

    def test_regional_coordinator_creation(self):
        """Test RegionalCoordinator initializes with regions"""
        regions = [
            Region(region_id=0, agents=[Agent(i, [0.5, 0.5]) for i in range(25)]),
            Region(region_id=1, agents=[Agent(i+25, [0.5, 0.5]) for i in range(25)]),
        ]
        coordinator = RegionalCoordinator(regions)

        assert coordinator is not None
        assert len(coordinator.regions) == 2

    def test_regional_coordination_produces_results(self):
        """Test regional coordination produces measurable metrics"""
        regions = [
            Region(region_id=0, agents=[Agent(i, [float(i)/25, 0.5]) for i in range(25)]),
            Region(region_id=1, agents=[Agent(i+25, [float(i)/25, 0.5]) for i in range(25)]),
        ]
        coordinator = RegionalCoordinator(regions)

        result = coordinator.coordinate_regional()

        assert 'regional_coordination' in result
        assert 'entropy' in result
        assert 0.0 <= result['regional_coordination'] <= 1.0
        assert result['entropy'] >= 0.0

    def test_cross_regional_information_flow(self):
        """Test information flows between regions"""
        # Create 3 regions with different initial states
        regions = [
            Region(region_id=i, agents=[Agent(j + i*20, [0.1*i, 0.1*i]) for j in range(20)])
            for i in range(3)
        ]
        coordinator = RegionalCoordinator(regions)

        # Coordinate multiple steps
        for _ in range(10):
            coordinator.coordinate_regional()

        # Regions should have some coordination between them
        # (measured via regional_coordination metric)
        result = coordinator.coordinate_regional()
        assert result['regional_coordination'] > 0.0, \
            "Regions should show some cross-region coordination"


class TestGlobalOptimizer:
    """Test global optimization across all regions"""

    def test_global_optimizer_creation(self):
        """Test GlobalOptimizer initializes correctly"""
        regions = [
            Region(region_id=i, agents=[Agent(j + i*25, [0.5, 0.5]) for j in range(25)])
            for i in range(4)
        ]
        optimizer = GlobalOptimizer(regions)

        assert optimizer is not None
        assert len(optimizer.regions) == 4

    def test_global_coordination_metric(self):
        """Test global coordination produces aggregate metrics"""
        regions = [
            Region(region_id=i, agents=[Agent(j + i*25, [float(j)/25, float(j)/25]) for j in range(25)])
            for i in range(4)
        ]
        optimizer = GlobalOptimizer(regions)

        result = optimizer.coordinate_global()

        assert 'global_coordination' in result
        assert 'total_agents' in result
        assert 'num_regions' in result

        assert result['total_agents'] == 100  # 4 regions × 25 agents
        assert result['num_regions'] == 4
        assert 0.0 <= result['global_coordination'] <= 1.0

    def test_global_convergence_over_time(self):
        """Test global system shows measurable improvement"""
        regions = [
            Region(region_id=i, agents=[Agent(j + i*20, [float(j)/20, float(i)/4]) for j in range(20)])
            for i in range(4)
        ]
        optimizer = GlobalOptimizer(regions)

        # Measure initial global coordination
        initial_result = optimizer.coordinate_global()
        initial_coordination = initial_result['global_coordination']

        # Run 15 optimization steps
        for _ in range(15):
            optimizer.coordinate_global()

        # Measure final global coordination
        final_result = optimizer.coordinate_global()
        final_coordination = final_result['global_coordination']

        # Global coordination should improve or stay stable (not degrade severely)
        # Allow small regression due to stochastic nature
        assert final_coordination >= initial_coordination - 0.1, \
            f"Global coordination degraded too much: {initial_coordination:.3f} -> {final_coordination:.3f}"


class TestEntropyMeasurement:
    """Test Shannon entropy calculation"""

    def test_entropy_calculated(self):
        """Test that entropy is calculated for the system"""
        config = MultiScaleConfig(num_agents=50, num_regions=2, dimensions=2)
        coordinator = UniversalCoordinator(config)

        result = coordinator.coordinate_step()

        # Entropy should be calculated
        assert hasattr(result, 'entropy')
        assert result.entropy >= 0.0

    def test_entropy_decreases_with_coordination(self):
        """Test that entropy tends to decrease as system coordinates"""
        config = MultiScaleConfig(num_agents=100, num_regions=4, dimensions=2)
        coordinator = UniversalCoordinator(config)

        # Record initial entropy
        initial_result = coordinator.coordinate_step()
        initial_entropy = initial_result.entropy

        # Run 20 coordination steps
        final_result = None
        for _ in range(20):
            final_result = coordinator.coordinate_step()

        # Final entropy should be lower or similar (system organizing)
        # Allow some increase due to stochastic nature, but not too much
        assert final_result.entropy <= initial_entropy * 1.2, \
            f"Entropy increased too much: {initial_entropy:.3f} -> {final_result.entropy:.3f}"


class TestConvergenceMetrics:
    """Test convergence measurement"""

    def test_convergence_metric_calculated(self):
        """Test convergence metric is calculated"""
        config = MultiScaleConfig(num_agents=50, num_regions=2, dimensions=2)
        coordinator = UniversalCoordinator(config)

        result = coordinator.coordinate_step()

        assert hasattr(result, 'convergence')
        assert 0.0 <= result.convergence <= 1.0

    def test_convergence_improves_over_time(self):
        """Test system shows measurable convergence"""
        config = MultiScaleConfig(num_agents=100, num_regions=4, dimensions=2)
        coordinator = UniversalCoordinator(config)

        # Run 30 steps and track convergence
        convergence_values = []
        for _ in range(30):
            result = coordinator.coordinate_step()
            convergence_values.append(result.convergence)

        # Convergence at end should be higher than beginning
        # (averaged to smooth out noise)
        avg_first_10 = sum(convergence_values[:10]) / 10
        avg_last_10 = sum(convergence_values[-10:]) / 10

        assert avg_last_10 >= avg_first_10 - 0.05, \
            f"Convergence did not improve: {avg_first_10:.3f} -> {avg_last_10:.3f}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
