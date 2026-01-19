"""
Comprehensive Test Suite for Emergent Intelligence Platform (v24.0)

Tests all 7 subsystems and integrated system:
1. SwarmIntelligence - Collective problem solving
2. CollectiveIntelligence - Aggregate intelligence from multiple agents
3. SelfOrganization - Spontaneous structure formation
4. EmergentBehaviorDetection - Detect unexpected patterns
5. SynergyDetection - Identify synergistic interactions
6. AdaptiveSystemEvolution - Evolve systems over time
7. HolisticSystemOptimization - System-wide optimization
8. IntegratedEmergentIntelligenceSystem - Unified workflows

Total: 48 tests
"""

import asyncio
import pytest

from src.emergent_intelligence import (
    # Core Systems
    AdaptiveSystemEvolution,
    CollectiveIntelligence,
    EmergentBehaviorDetection,
    HolisticSystemOptimization,
    IntegratedEmergentIntelligenceSystem,
    SelfOrganization,
    SwarmIntelligence,
    SynergyDetection,
    # Config
    EmergentIntelligenceConfig,
    # Singleton Getters
    get_emergent_intelligence_system,
)


class TestSwarmIntelligence:
    """Test Swarm Intelligence subsystem"""

    @pytest.mark.asyncio
    async def test_create_swarm(self):
        swarm = SwarmIntelligence()
        result = await swarm.create_swarm(num_agents=50)

        assert result is not None
        assert "swarm_id" in result
        assert result["num_agents"] == 50

    @pytest.mark.asyncio
    async def test_coordinate(self):
        swarm = SwarmIntelligence()
        coordination = await swarm.coordinate("task_1", ["agent_1", "agent_2"])

        assert coordination is not None
        assert "strategy" in coordination

    @pytest.mark.asyncio
    async def test_optimize_swarm(self):
        swarm = SwarmIntelligence()
        result = await swarm.optimize(swarm_id="test_swarm", objective="maximize_coverage")

        assert result is not None
        assert "optimization_result" in result

    @pytest.mark.asyncio
    async def test_swarm_decision_making(self):
        swarm = SwarmIntelligence()
        decision = await swarm.make_decision(swarm_id="test_swarm", options=["A", "B", "C"])

        assert decision is not None
        assert decision in ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_swarm_communication(self):
        swarm = SwarmIntelligence()
        result = await swarm.communicate(swarm_id="test_swarm", message="coordinate")

        assert result is not None
        assert "broadcast_success" in result

    @pytest.mark.asyncio
    async def test_swarm_adaptation(self):
        swarm = SwarmIntelligence()
        result = await swarm.adapt(swarm_id="test_swarm", environmental_change="resource_scarcity")

        assert result is not None
        assert "adaptation_strategy" in result


class TestCollectiveIntelligence:
    """Test Collective Intelligence subsystem"""

    @pytest.mark.asyncio
    async def test_aggregate_intelligence(self):
        collective = CollectiveIntelligence()
        result = await collective.aggregate(agent_outputs=[0.8, 0.9, 0.7, 0.85])

        assert result is not None
        assert "aggregated_value" in result
        assert 0.0 <= result["aggregated_value"] <= 1.0

    @pytest.mark.asyncio
    async def test_consensus_formation(self):
        collective = CollectiveIntelligence()
        consensus = await collective.form_consensus(opinions=[0.7, 0.8, 0.75, 0.72])

        assert consensus is not None
        assert "consensus_value" in consensus

    @pytest.mark.asyncio
    async def test_distributed_problem_solving(self):
        collective = CollectiveIntelligence()
        result = await collective.solve_distributed(problem="optimize_network", num_agents=10)

        assert result is not None
        assert "solution" in result

    @pytest.mark.asyncio
    async def test_knowledge_sharing(self):
        collective = CollectiveIntelligence()
        result = await collective.share_knowledge(source_agents=[1, 2, 3], target_agents=[4, 5, 6])

        assert result is not None
        assert "knowledge_transferred" in result

    @pytest.mark.asyncio
    async def test_collective_learning(self):
        collective = CollectiveIntelligence()
        result = await collective.collective_learn(experiences=[{"reward": 0.8}, {"reward": 0.9}])

        assert result is not None
        assert "learning_rate" in result

    @pytest.mark.asyncio
    async def test_wisdom_of_crowds(self):
        collective = CollectiveIntelligence()
        result = await collective.wisdom_of_crowds(predictions=[50, 55, 52, 48, 51])

        assert result is not None
        assert "crowd_estimate" in result


class TestSelfOrganization:
    """Test Self-Organization subsystem"""

    @pytest.mark.asyncio
    async def test_spontaneous_organization(self):
        org = SelfOrganization()
        result = await org.organize(agents=["a1", "a2", "a3", "a4", "a5"])

        assert result is not None
        assert "organization_structure" in result

    @pytest.mark.asyncio
    async def test_pattern_formation(self):
        org = SelfOrganization()
        pattern = await org.form_pattern(system_state={"entropy": 0.5})

        assert pattern is not None
        assert "pattern_type" in pattern

    @pytest.mark.asyncio
    async def test_structure_emergence(self):
        org = SelfOrganization()
        result = await org.emerge_structure(num_iterations=10)

        assert result is not None
        assert "final_structure" in result

    @pytest.mark.asyncio
    async def test_decentralized_coordination(self):
        org = SelfOrganization()
        result = await org.coordinate_decentralized(agents=["a1", "a2", "a3"])

        assert result is not None
        assert "coordination_success" in result

    @pytest.mark.asyncio
    async def test_local_interaction_effects(self):
        org = SelfOrganization()
        result = await org.simulate_local_interactions(num_agents=20, num_steps=50)

        assert result is not None
        assert "global_pattern" in result

    @pytest.mark.asyncio
    async def test_phase_transition(self):
        org = SelfOrganization()
        result = await org.detect_phase_transition(system_parameter=0.7)

        assert result is not None
        assert "phase_transition_detected" in result


class TestEmergentBehaviorDetection:
    """Test Emergent Behavior Detection subsystem"""

    @pytest.mark.asyncio
    async def test_detect_emergence(self):
        detector = EmergentBehaviorDetection()
        result = await detector.detect(system_state={"complexity": 0.8, "organization": 0.7})

        assert result is not None
        assert "emergence_detected" in result

    @pytest.mark.asyncio
    async def test_behavior_classification(self):
        detector = EmergentBehaviorDetection()
        result = await detector.classify_behavior(behavior_trace=[0.5, 0.6, 0.7, 0.8])

        assert result is not None
        assert "behavior_type" in result

    @pytest.mark.asyncio
    async def test_novelty_detection(self):
        detector = EmergentBehaviorDetection()
        result = await detector.detect_novelty(observed_patterns=["pattern_A", "pattern_B"])

        assert result is not None
        assert "novelty_score" in result

    @pytest.mark.asyncio
    async def test_complexity_measurement(self):
        detector = EmergentBehaviorDetection()
        complexity = await detector.measure_complexity(system_state={"agents": 100, "connections": 500})

        assert complexity is not None
        assert complexity > 0

    @pytest.mark.asyncio
    async def test_predictability_analysis(self):
        detector = EmergentBehaviorDetection()
        result = await detector.analyze_predictability(behavior_history=[0.1, 0.2, 0.3, 0.4])

        assert result is not None
        assert "predictability_score" in result

    @pytest.mark.asyncio
    async def test_emergence_tracking(self):
        detector = EmergentBehaviorDetection()
        result = await detector.track_emergence(system_id="sys_1", duration_seconds=10)

        assert result is not None
        assert "emergence_timeline" in result


class TestSynergyDetection:
    """Test Synergy Detection subsystem"""

    @pytest.mark.asyncio
    async def test_detect_synergies(self):
        synergy = SynergyDetection()
        result = await synergy.detect(components=["comp_A", "comp_B", "comp_C"])

        assert result is not None
        assert "synergies_found" in result

    @pytest.mark.asyncio
    async def test_measure_synergy_strength(self):
        synergy = SynergyDetection()
        strength = await synergy.measure_strength(component_a="A", component_b="B")

        assert strength is not None
        assert 0.0 <= strength <= 1.0

    @pytest.mark.asyncio
    async def test_identify_synergy_type(self):
        synergy = SynergyDetection()
        result = await synergy.identify_type(interaction_data={"positive_feedback": True})

        assert result is not None
        assert "synergy_type" in result

    @pytest.mark.asyncio
    async def test_optimize_synergies(self):
        synergy = SynergyDetection()
        result = await synergy.optimize(system_components=["A", "B", "C", "D"])

        assert result is not None
        assert "optimal_configuration" in result

    @pytest.mark.asyncio
    async def test_synergy_network_analysis(self):
        synergy = SynergyDetection()
        result = await synergy.analyze_network(components=["A", "B", "C"])

        assert result is not None
        assert "network_metrics" in result

    @pytest.mark.asyncio
    async def test_cascading_synergies(self):
        synergy = SynergyDetection()
        result = await synergy.detect_cascades(initial_synergy="synergy_1")

        assert result is not None
        assert "cascade_chain" in result


class TestAdaptiveSystemEvolution:
    """Test Adaptive System Evolution subsystem"""

    @pytest.mark.asyncio
    async def test_evolve_system(self):
        evolution = AdaptiveSystemEvolution()
        result = await evolution.evolve(system_id="sys_1", generations=10)

        assert result is not None
        assert "evolved_system" in result

    @pytest.mark.asyncio
    async def test_fitness_evaluation(self):
        evolution = AdaptiveSystemEvolution()
        fitness = await evolution.evaluate_fitness(system_state={"performance": 0.8})

        assert fitness is not None
        assert fitness > 0

    @pytest.mark.asyncio
    async def test_mutation_application(self):
        evolution = AdaptiveSystemEvolution()
        result = await evolution.mutate(system_config={"param_1": 0.5}, mutation_rate=0.1)

        assert result is not None
        assert "mutated_config" in result

    @pytest.mark.asyncio
    async def test_selection_pressure(self):
        evolution = AdaptiveSystemEvolution()
        result = await evolution.apply_selection(population=[{"fitness": 0.8}, {"fitness": 0.6}])

        assert result is not None
        assert "selected_systems" in result

    @pytest.mark.asyncio
    async def test_adaptation_speed(self):
        evolution = AdaptiveSystemEvolution()
        result = await evolution.measure_adaptation_speed(evolution_history=[0.5, 0.6, 0.7, 0.8])

        assert result is not None
        assert "adaptation_rate" in result

    @pytest.mark.asyncio
    async def test_evolutionary_trajectory(self):
        evolution = AdaptiveSystemEvolution()
        result = await evolution.track_trajectory(system_id="sys_1", num_generations=20)

        assert result is not None
        assert "trajectory" in result


class TestHolisticSystemOptimization:
    """Test Holistic System Optimization subsystem"""

    @pytest.mark.asyncio
    async def test_optimize_holistically(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.optimize(system_components=["A", "B", "C"])

        assert result is not None
        assert "optimized_system" in result

    @pytest.mark.asyncio
    async def test_system_wide_objective(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.define_objective(goals=["efficiency", "robustness"])

        assert result is not None
        assert "objective_function" in result

    @pytest.mark.asyncio
    async def test_constraint_satisfaction(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.satisfy_constraints(constraints=["resource < 100", "latency < 50"])

        assert result is not None
        assert "constraints_satisfied" in result

    @pytest.mark.asyncio
    async def test_pareto_optimization(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.pareto_optimize(objectives=["cost", "performance"])

        assert result is not None
        assert "pareto_front" in result

    @pytest.mark.asyncio
    async def test_system_balance(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.balance_system(subsystems=["A", "B", "C"])

        assert result is not None
        assert "balance_achieved" in result

    @pytest.mark.asyncio
    async def test_global_optimum_search(self):
        optimizer = HolisticSystemOptimization()
        result = await optimizer.search_global_optimum(search_space_size=1000)

        assert result is not None
        assert "optimum_found" in result


class TestIntegratedEmergentIntelligenceSystem:
    """Test Integrated Emergent Intelligence System"""

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        config = EmergentIntelligenceConfig(
            num_agents_per_swarm=50, synergy_detection_threshold=0.5, adaptation_time_hours=0.8
        )

        system = IntegratedEmergentIntelligenceSystem(config)
        assert system.swarm is not None
        assert system.collective is not None
        assert system.self_org is not None

    @pytest.mark.asyncio
    async def test_emergent_collective_problem_solving(self):
        system = IntegratedEmergentIntelligenceSystem()

        result = await system.emergent_collective_problem_solving(
            problem_description="optimize distributed network", num_swarms=3, systems_to_integrate=["routing", "caching"]
        )

        assert result is not None
        assert "num_swarms_created" in result
        assert "systems_integrated" in result
        assert "synergies_detected" in result
        assert "emergent_performance" in result

    @pytest.mark.asyncio
    async def test_self_organizing_adaptive_system(self):
        system = IntegratedEmergentIntelligenceSystem()

        result = await system.self_organizing_adaptive_system(
            initial_agents=["a1", "a2", "a3", "a4", "a5"], environmental_changes=["resource_change", "demand_spike"], optimization_cycles=5
        )

        assert result is not None
        assert "organization_structure" in result
        assert "adaptations_applied" in result
        assert "optimization_improvement" in result

    @pytest.mark.asyncio
    async def test_multi_system_emergence(self):
        system = IntegratedEmergentIntelligenceSystem()

        result = await system.multi_system_emergence(systems=["system_A", "system_B"], create_swarm=True)

        assert result is not None
        assert "integrated_systems" in result
        assert "emergent_behaviors" in result

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        system = IntegratedEmergentIntelligenceSystem()
        status = system.get_system_status()

        assert status is not None
        assert "swarm_intelligence_enabled" in status

    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        system = IntegratedEmergentIntelligenceSystem()
        benchmarks = await system.benchmark_performance()

        assert benchmarks is not None
        assert len(benchmarks) > 0

    @pytest.mark.asyncio
    async def test_singleton_accessor(self):
        system1 = get_emergent_intelligence_system()
        system2 = get_emergent_intelligence_system()

        assert system1 is system2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
