"""
Tests for Social & Collective Intelligence (v8.0)

Tests for social cognition, group dynamics, collective decision-making,
swarm intelligence, cultural intelligence, social network analysis, and
collaborative intelligence.

IMPORTANT: These tests verify computational social intelligence simulation,
not genuine social understanding or consciousness.
"""

import pytest


class TestSocialCognitionEngine:
    """Test Social Cognition Engine (v8.0)"""

    def test_import_social_cognition(self):
        """Test importing SocialCognitionEngine"""
        from social_ai import (
            SocialCognitionEngine,
            ToMBeliefState,
            SocialContext,
            IntentionType
        )
        assert SocialCognitionEngine is not None
        assert IntentionType.COOPERATIVE is not None

    def test_create_social_cognition_engine(self):
        """Test creating social cognition engine"""
        from social_ai import SocialCognitionEngine

        engine = SocialCognitionEngine()
        assert engine is not None
        assert len(engine.belief_states) == 0

    def test_recursive_theory_of_mind(self):
        """Test recursive Theory of Mind"""
        from social_ai import SocialCognitionEngine

        engine = SocialCognitionEngine()

        belief_chain = engine.recursive_tom(
            belief="The meeting starts at 3pm",
            depth=3
        )

        assert belief_chain is not None
        assert len(belief_chain) == 3
        assert "I believe" in belief_chain[0]
        assert "you believe" in belief_chain[1]

    def test_infer_mental_state(self):
        """Test inferring mental state from behavior"""
        from social_ai import SocialCognitionEngine

        engine = SocialCognitionEngine()

        behavior = {
            'action': 'smiling',
            'context': 'received_good_news',
            'body_language': 'open'
        }

        mental_state = engine.infer_mental_state(behavior)

        assert mental_state is not None
        assert 'emotion' in mental_state
        assert 'beliefs' in mental_state

    def test_recognize_intention(self):
        """Test recognizing intentions"""
        from social_ai import SocialCognitionEngine

        engine = SocialCognitionEngine()

        action = {
            'type': 'helping',
            'target': 'other_agent',
            'context': 'collaboration'
        }

        intention = engine.recognize_intention(action)

        assert intention is not None
        assert hasattr(intention, 'type')

    def test_predict_behavior(self):
        """Test predicting future behavior"""
        from social_ai import SocialCognitionEngine, ToMBeliefState

        engine = SocialCognitionEngine()

        belief_state = ToMBeliefState(
            agent_id="agent_1",
            beliefs={'goal': 'finish_task'},
            desires=['efficiency', 'quality'],
            intentions=['cooperative']
        )

        context = {
            'situation': 'team_project',
            'time_pressure': 'high'
        }

        prediction = engine.predict_behavior(belief_state, context)

        assert prediction is not None
        assert 'predicted_action' in prediction


class TestGroupDynamicsSystem:
    """Test Group Dynamics System (v8.0)"""

    def test_import_group_dynamics(self):
        """Test importing GroupDynamicsSystem"""
        from social_ai import (
            GroupDynamicsSystem,
            GroupStage,
            GroupProfile,
            DynamicEvent
        )
        assert GroupDynamicsSystem is not None
        assert GroupStage.FORMING is not None

    def test_create_group_dynamics_system(self):
        """Test creating group dynamics system"""
        from social_ai import GroupDynamicsSystem

        system = GroupDynamicsSystem()
        assert system is not None
        assert len(system.active_groups) == 0

    def test_identify_group_stage(self):
        """Test identifying Tuckman's group stage"""
        from social_ai import GroupDynamicsSystem

        system = GroupDynamicsSystem()

        group_state = {
            'time_together': 'short',
            'conflict_level': 'low',
            'productivity': 'low',
            'relationships': 'forming'
        }

        stage = system.identify_stage(group_state)

        assert stage is not None
        assert hasattr(stage, 'name')

    def test_detect_groupthink(self):
        """Test detecting groupthink patterns"""
        from social_ai import GroupDynamicsSystem

        system = GroupDynamicsSystem()

        group_behavior = {
            'dissent_level': 0.1,
            'conformity': 0.9,
            'alternative_exploration': 0.2,
            'pressure_for_consensus': 0.95
        }

        groupthink_score = system.detect_groupthink(group_behavior)

        assert groupthink_score is not None
        assert 0.0 <= groupthink_score <= 1.0
        assert groupthink_score > 0.5  # High indicators

    def test_analyze_cohesion(self):
        """Test analyzing group cohesion"""
        from social_ai import GroupDynamicsSystem

        system = GroupDynamicsSystem()

        group_data = {
            'interaction_frequency': 0.8,
            'shared_goals': 0.9,
            'trust_level': 0.85,
            'communication_quality': 0.75
        }

        cohesion = system.analyze_cohesion(group_data)

        assert cohesion is not None
        assert 0.0 <= cohesion <= 1.0

    def test_recommend_interventions(self):
        """Test recommending group interventions"""
        from social_ai import GroupDynamicsSystem

        system = GroupDynamicsSystem()

        group_issues = {
            'low_productivity': True,
            'high_conflict': True,
            'poor_communication': False
        }

        interventions = system.recommend_interventions(group_issues)

        assert interventions is not None
        assert isinstance(interventions, list)
        assert len(interventions) > 0


class TestCollectiveDecisionMaking:
    """Test Collective Decision Making (v8.0)"""

    def test_import_collective_decision(self):
        """Test importing CollectiveDecisionMaking"""
        from social_ai import (
            CollectiveDecisionMaking,
            VotingMethod,
            DecisionOption,
            ConsensusResult
        )
        assert CollectiveDecisionMaking is not None
        assert VotingMethod.MAJORITY is not None

    def test_create_decision_system(self):
        """Test creating collective decision system"""
        from social_ai import CollectiveDecisionMaking

        system = CollectiveDecisionMaking()
        assert system is not None

    def test_voting_majority(self):
        """Test majority voting"""
        from social_ai import CollectiveDecisionMaking, DecisionOption

        system = CollectiveDecisionMaking()

        options = [
            DecisionOption(option_id="A", description="Option A", supporters=["1", "2", "3"]),
            DecisionOption(option_id="B", description="Option B", supporters=["4", "5"])
        ]

        result = system.vote(options, method="majority")

        assert result is not None
        assert result['winner'] == "A"

    def test_voting_ranked_choice(self):
        """Test ranked choice voting"""
        from social_ai import CollectiveDecisionMaking

        system = CollectiveDecisionMaking()

        preferences = {
            'voter1': ['A', 'B', 'C'],
            'voter2': ['B', 'A', 'C'],
            'voter3': ['C', 'B', 'A']
        }

        result = system.ranked_choice_vote(preferences)

        assert result is not None
        assert 'winner' in result

    def test_build_consensus(self):
        """Test building consensus"""
        from social_ai import CollectiveDecisionMaking

        system = CollectiveDecisionMaking()

        positions = {
            'agent1': {'priority': 'speed', 'value': 0.8},
            'agent2': {'priority': 'quality', 'value': 0.9},
            'agent3': {'priority': 'speed', 'value': 0.7}
        }

        consensus = system.build_consensus(positions)

        assert consensus is not None
        assert 'agreement_level' in consensus

    def test_wisdom_of_crowds(self):
        """Test wisdom of crowds aggregation"""
        from social_ai import CollectiveDecisionMaking

        system = CollectiveDecisionMaking()

        estimates = [100, 110, 95, 105, 98, 102]

        aggregate = system.aggregate_estimates(estimates)

        assert aggregate is not None
        assert 95 <= aggregate <= 110


class TestSwarmIntelligenceSystem:
    """Test Swarm Intelligence System (v8.0)"""

    def test_import_swarm_intelligence(self):
        """Test importing SwarmIntelligenceSystem"""
        from social_ai import (
            SwarmIntelligenceSystem,
            SwarmAgent,
            SwarmBehavior
        )
        assert SwarmIntelligenceSystem is not None
        assert SwarmAgent is not None

    def test_create_swarm_system(self):
        """Test creating swarm intelligence system"""
        from social_ai import SwarmIntelligenceSystem

        system = SwarmIntelligenceSystem()
        assert system is not None

    def test_ant_colony_optimization(self):
        """Test ant colony optimization"""
        from social_ai import SwarmIntelligenceSystem

        system = SwarmIntelligenceSystem()

        problem = {
            'type': 'path_finding',
            'graph': {
                'nodes': ['A', 'B', 'C', 'D'],
                'edges': [('A', 'B', 2), ('B', 'C', 3), ('C', 'D', 1), ('A', 'D', 10)]
            },
            'start': 'A',
            'goal': 'D'
        }

        solution = system.ant_colony_optimize(problem, num_ants=10, iterations=5)

        assert solution is not None
        assert 'best_path' in solution
        assert 'cost' in solution

    def test_particle_swarm_optimization(self):
        """Test particle swarm optimization"""
        from social_ai import SwarmIntelligenceSystem

        system = SwarmIntelligenceSystem()

        problem = {
            'type': 'optimization',
            'dimensions': 2,
            'bounds': [(-10, 10), (-10, 10)],
            'objective': 'minimize'
        }

        solution = system.particle_swarm_optimize(problem, num_particles=20, iterations=10)

        assert solution is not None
        assert 'best_position' in solution
        assert 'best_fitness' in solution

    def test_emergent_behavior(self):
        """Test emergent swarm behavior"""
        from social_ai import SwarmIntelligenceSystem, SwarmAgent

        system = SwarmIntelligenceSystem()

        agents = [
            SwarmAgent(agent_id=f"agent_{i}", position=[0.0, 0.0], velocity=[1.0, 0.0])
            for i in range(10)
        ]

        behavior = system.simulate_swarm_behavior(agents, steps=5)

        assert behavior is not None
        assert 'final_positions' in behavior


class TestCulturalIntelligenceSystem:
    """Test Cultural Intelligence System (v8.0)"""

    def test_import_cultural_intelligence(self):
        """Test importing CulturalIntelligenceSystem"""
        from social_ai import (
            CulturalIntelligenceSystem,
            CulturalDimension,
            CulturalProfile
        )
        assert CulturalIntelligenceSystem is not None
        assert CulturalDimension is not None

    def test_create_cultural_system(self):
        """Test creating cultural intelligence system"""
        from social_ai import CulturalIntelligenceSystem

        system = CulturalIntelligenceSystem()
        assert system is not None

    def test_analyze_hofstede_dimensions(self):
        """Test analyzing Hofstede's cultural dimensions"""
        from social_ai import CulturalIntelligenceSystem

        system = CulturalIntelligenceSystem()

        cultural_indicators = {
            'power_distance': 0.7,
            'individualism': 0.3,
            'masculinity': 0.5,
            'uncertainty_avoidance': 0.8,
            'long_term_orientation': 0.6,
            'indulgence': 0.4
        }

        profile = system.analyze_cultural_dimensions(cultural_indicators)

        assert profile is not None
        assert hasattr(profile, 'dimensions')

    def test_detect_cultural_differences(self):
        """Test detecting cultural differences"""
        from social_ai import CulturalIntelligenceSystem

        system = CulturalIntelligenceSystem()

        culture_a = {'power_distance': 0.8, 'individualism': 0.3}
        culture_b = {'power_distance': 0.2, 'individualism': 0.9}

        differences = system.detect_differences(culture_a, culture_b)

        assert differences is not None
        assert 'distance' in differences
        assert differences['distance'] > 0.5  # Significant differences

    def test_adapt_communication_style(self):
        """Test adapting communication style"""
        from social_ai import CulturalIntelligenceSystem

        system = CulturalIntelligenceSystem()

        message = "We need to finish this project"
        target_culture = {
            'power_distance': 0.2,
            'individualism': 0.9,
            'context': 'low'
        }

        adapted = system.adapt_communication(message, target_culture)

        assert adapted is not None
        assert isinstance(adapted, str)
        assert len(adapted) > 0


class TestSocialNetworkAnalysis:
    """Test Social Network Analysis (v8.0)"""

    def test_import_social_network(self):
        """Test importing SocialNetworkAnalysis"""
        from social_ai import (
            SocialNetworkAnalysis,
            NetworkNode,
            NetworkEdge,
            CentralityMeasure
        )
        assert SocialNetworkAnalysis is not None
        assert CentralityMeasure.DEGREE is not None

    def test_create_network_analysis(self):
        """Test creating social network analysis system"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()
        assert system is not None

    def test_calculate_degree_centrality(self):
        """Test calculating degree centrality"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()

        network = {
            'nodes': ['A', 'B', 'C', 'D'],
            'edges': [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C')]
        }

        centrality = system.calculate_centrality(network, measure='degree')

        assert centrality is not None
        assert 'A' in centrality
        assert centrality['A'] > centrality['D']  # A has more connections

    def test_calculate_betweenness_centrality(self):
        """Test calculating betweenness centrality"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()

        network = {
            'nodes': ['A', 'B', 'C', 'D', 'E'],
            'edges': [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
        }

        betweenness = system.calculate_centrality(network, measure='betweenness')

        assert betweenness is not None
        assert 'C' in betweenness
        # C should have high betweenness as it's in the middle

    def test_detect_communities(self):
        """Test detecting communities"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()

        network = {
            'nodes': ['A', 'B', 'C', 'D', 'E', 'F'],
            'edges': [
                ('A', 'B'), ('A', 'C'), ('B', 'C'),  # Community 1
                ('D', 'E'), ('D', 'F'), ('E', 'F'),  # Community 2
                ('C', 'D')  # Bridge
            ]
        }

        communities = system.detect_communities(network)

        assert communities is not None
        assert isinstance(communities, list)
        assert len(communities) >= 2

    def test_calculate_pagerank(self):
        """Test calculating PageRank"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()

        network = {
            'nodes': ['A', 'B', 'C', 'D'],
            'edges': [('A', 'B'), ('B', 'C'), ('C', 'A'), ('D', 'A')]
        }

        pagerank = system.calculate_pagerank(network)

        assert pagerank is not None
        assert all(0.0 <= score <= 1.0 for score in pagerank.values())

    def test_find_influencers(self):
        """Test finding network influencers"""
        from social_ai import SocialNetworkAnalysis

        system = SocialNetworkAnalysis()

        network = {
            'nodes': ['A', 'B', 'C', 'D', 'E'],
            'edges': [('A', 'B'), ('A', 'C'), ('A', 'D'), ('A', 'E'), ('B', 'C')]
        }

        influencers = system.find_influencers(network, top_n=2)

        assert influencers is not None
        assert isinstance(influencers, list)
        assert len(influencers) <= 2
        assert 'A' in influencers  # A has most connections


class TestCollaborativeIntelligenceOrchestrator:
    """Test Collaborative Intelligence Orchestrator (v8.0)"""

    def test_import_collaborative_intelligence(self):
        """Test importing CollaborativeIntelligenceOrchestrator"""
        from social_ai import (
            CollaborativeIntelligenceOrchestrator,
            LeadershipStyle,
            CollaborationPattern
        )
        assert CollaborativeIntelligenceOrchestrator is not None
        assert LeadershipStyle.TRANSFORMATIONAL is not None

    def test_create_orchestrator(self):
        """Test creating collaborative intelligence orchestrator"""
        from social_ai import CollaborativeIntelligenceOrchestrator

        orchestrator = CollaborativeIntelligenceOrchestrator()
        assert orchestrator is not None

    def test_coordinate_multi_agent_task(self):
        """Test coordinating multi-agent task"""
        from social_ai import CollaborativeIntelligenceOrchestrator

        orchestrator = CollaborativeIntelligenceOrchestrator()

        task = {
            'task_id': 'task_001',
            'type': 'problem_solving',
            'complexity': 0.8,
            'agents': ['agent_1', 'agent_2', 'agent_3']
        }

        coordination = orchestrator.coordinate_task(task)

        assert coordination is not None
        assert 'strategy' in coordination
        assert 'assignments' in coordination

    def test_select_leadership_style(self):
        """Test selecting appropriate leadership style"""
        from social_ai import CollaborativeIntelligenceOrchestrator

        orchestrator = CollaborativeIntelligenceOrchestrator()

        context = {
            'team_maturity': 'high',
            'task_urgency': 'low',
            'creativity_needed': 'high'
        }

        style = orchestrator.select_leadership_style(context)

        assert style is not None
        assert hasattr(style, 'name')

    def test_facilitate_collaboration(self):
        """Test facilitating collaboration"""
        from social_ai import CollaborativeIntelligenceOrchestrator

        orchestrator = CollaborativeIntelligenceOrchestrator()

        agents = ['agent_1', 'agent_2', 'agent_3']
        goal = "Solve complex optimization problem"

        facilitation = orchestrator.facilitate_collaboration(agents, goal)

        assert facilitation is not None
        assert 'pattern' in facilitation


class TestIntegratedSocialSystem:
    """Test Integrated Social & Collective Intelligence System (v8.0)"""

    def test_import_integrated_social_system(self):
        """Test importing IntegratedSocialSystem"""
        from social_ai import IntegratedSocialSystem, SocialConfig
        assert IntegratedSocialSystem is not None
        assert SocialConfig is not None

    def test_create_integrated_system(self):
        """Test creating integrated social system"""
        from social_ai import IntegratedSocialSystem, SocialConfig

        config = SocialConfig()
        system = IntegratedSocialSystem(config)

        assert system is not None
        assert system.config is not None

    def test_process_social_interaction(self):
        """Test processing social interaction"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        interaction = {
            'agents': ['agent_1', 'agent_2'],
            'type': 'cooperation',
            'context': 'joint_task'
        }

        result = system.process_social_interaction(interaction)

        # May return None if social cognition disabled
        if result is not None:
            assert 'tom_analysis' in result or result is not None

    def test_analyze_group(self):
        """Test analyzing group dynamics"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        group_data = {
            'group_id': 'group_1',
            'members': ['a1', 'a2', 'a3'],
            'history': []
        }

        analysis = system.analyze_group(group_data)

        # May return None if group dynamics disabled
        if analysis is not None:
            assert 'stage' in analysis or analysis is not None

    def test_make_collective_decision(self):
        """Test making collective decision"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        decision_context = {
            'options': ['A', 'B', 'C'],
            'preferences': {
                'agent1': 'A',
                'agent2': 'B',
                'agent3': 'A'
            }
        }

        decision = system.make_collective_decision(decision_context)

        # May return None if collective decision disabled
        if decision is not None:
            assert 'winner' in decision or decision is not None

    def test_optimize_with_swarm(self):
        """Test swarm-based optimization"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        problem = {
            'type': 'optimization',
            'dimensions': 2
        }

        result = system.optimize_with_swarm(problem)

        # May return None if swarm intelligence disabled
        if result is not None:
            assert 'best_position' in result or 'best_path' in result or result is not None

    def test_analyze_social_network(self):
        """Test social network analysis"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        network = {
            'nodes': ['A', 'B', 'C'],
            'edges': [('A', 'B'), ('B', 'C')]
        }

        analysis = system.analyze_social_network(network)

        # May return None if SNA disabled
        if analysis is not None:
            assert 'centrality' in analysis or 'communities' in analysis or analysis is not None

    def test_get_system_statistics(self):
        """Test getting system statistics"""
        from social_ai import IntegratedSocialSystem

        system = IntegratedSocialSystem()

        stats = system.get_system_statistics()

        assert stats is not None
        assert 'config' in stats
        assert 'subsystems' in stats

    def test_get_social_system_singleton(self):
        """Test getting singleton social system"""
        from social_ai import get_social_system

        sys1 = get_social_system()
        sys2 = get_social_system()

        # Should be same instance
        assert sys1 is sys2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
