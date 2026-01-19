"""
Tests for Autonomous Systems (v5.0)

Tests for autonomous decision-making, self-learning, multi-agent coordination,
self-monitoring, self-repair, goal generation, and human-AI collaboration.
"""

import pytest


class TestAutonomousDecisionEngine:
    """Test Autonomous Decision Engine (v5.0)"""

    def test_import_decision_engine(self):
        """Test importing AutonomousDecisionEngine"""
        from autonomous import (
            AutonomousDecisionEngine,
            DecisionType,
            DecisionContext,
            DecisionResult
        )
        assert AutonomousDecisionEngine is not None
        assert DecisionType.OPERATIONAL is not None

    def test_create_decision_engine(self):
        """Test creating decision engine"""
        from autonomous import AutonomousDecisionEngine, AutonomousConfig

        config = AutonomousConfig()
        engine = AutonomousDecisionEngine(config)

        assert engine is not None
        assert engine.config is not None

    def test_make_decision(self):
        """Test making autonomous decision"""
        from autonomous import (
            AutonomousDecisionEngine,
            DecisionContext,
            DecisionType
        )

        engine = AutonomousDecisionEngine()

        context = DecisionContext(
            decision_id="decision_test_01",
            decision_type=DecisionType.OPERATIONAL,
            current_state={"system": "operational"},
            available_actions=["continue", "adjust", "stop"],
            constraints={"time": 100},
            goals=["efficiency", "safety"]
        )

        result = engine.make_decision(context)

        assert result is not None
        assert result.selected_action in context.available_actions
        assert 0.0 <= result.confidence <= 1.0

    def test_evaluate_actions(self):
        """Test action evaluation"""
        from autonomous import AutonomousDecisionEngine, DecisionContext, DecisionType

        engine = AutonomousDecisionEngine()

        context = DecisionContext(
            decision_id="eval_test",
            decision_type=DecisionType.TACTICAL,
            current_state={},
            available_actions=["A", "B", "C"],
            constraints={},
            goals=["goal1"]
        )

        scores = engine._evaluate_actions(context)

        assert isinstance(scores, dict)
        assert len(scores) == 3
        for action in context.available_actions:
            assert action in scores
            assert isinstance(scores[action], float)


class TestSelfLearningSystem:
    """Test Self-Learning System (v5.0)"""

    def test_import_learning_system(self):
        """Test importing SelfLearningSystem"""
        from autonomous import SelfLearningSystem, LearningType
        assert SelfLearningSystem is not None
        assert LearningType.REINFORCEMENT is not None

    def test_create_learning_system(self):
        """Test creating learning system"""
        from autonomous import SelfLearningSystem

        system = SelfLearningSystem()
        assert system is not None
        assert len(system.experience_buffer) == 0

    def test_learn_from_experience(self):
        """Test learning from experience"""
        from autonomous import SelfLearningSystem

        system = SelfLearningSystem()

        experience = {
            'state': {'x': 1},
            'action': 'move_forward',
            'reward': 1.0,
            'next_state': {'x': 2}
        }

        system.learn_from_experience(experience)

        assert len(system.experience_buffer) == 1
        assert system.experience_buffer[0] == experience

    def test_update_policy(self):
        """Test policy update"""
        from autonomous import SelfLearningSystem

        system = SelfLearningSystem()

        # Add multiple experiences
        for i in range(10):
            experience = {
                'state': {'step': i},
                'action': 'action_' + str(i % 3),
                'reward': float(i % 2),
                'next_state': {'step': i + 1}
            }
            system.learn_from_experience(experience)

        initial_policy_version = system.policy_version
        system._update_policy()

        # Policy should be updated
        assert system.policy_version > initial_policy_version


class TestMultiAgentCoordinator:
    """Test Multi-Agent Coordinator (v5.0)"""

    def test_import_multi_agent_coordinator(self):
        """Test importing MultiAgentCoordinator"""
        from autonomous import MultiAgentCoordinator, AgentRole
        assert MultiAgentCoordinator is not None
        assert AgentRole.COORDINATOR is not None

    def test_create_coordinator(self):
        """Test creating multi-agent coordinator"""
        from autonomous import MultiAgentCoordinator

        coordinator = MultiAgentCoordinator()
        assert coordinator is not None
        assert len(coordinator.agents) == 0

    def test_register_agent(self):
        """Test registering agent"""
        from autonomous import MultiAgentCoordinator, AgentRole

        coordinator = MultiAgentCoordinator()

        agent_id = coordinator.register_agent(
            agent_id="agent_001",
            role=AgentRole.EXECUTOR,
            capabilities=["task_A", "task_B"]
        )

        assert agent_id == "agent_001"
        assert agent_id in coordinator.agents

    def test_allocate_task(self):
        """Test task allocation"""
        from autonomous import MultiAgentCoordinator, AgentRole

        coordinator = MultiAgentCoordinator()

        # Register multiple agents
        coordinator.register_agent("agent_1", AgentRole.EXECUTOR, ["task_A"])
        coordinator.register_agent("agent_2", AgentRole.EXECUTOR, ["task_B"])

        # Allocate task
        assigned_agent = coordinator.allocate_task("task_001")

        assert assigned_agent is not None
        assert assigned_agent in coordinator.agents

    def test_coordinate_agents(self):
        """Test agent coordination"""
        from autonomous import MultiAgentCoordinator, AgentRole

        coordinator = MultiAgentCoordinator()

        # Register agents
        coordinator.register_agent("agent_1", AgentRole.EXECUTOR, ["process"])
        coordinator.register_agent("agent_2", AgentRole.EXECUTOR, ["validate"])

        # Coordinate for goal
        result = coordinator.coordinate_agents("Complete project")

        assert result is not None
        assert 'subtasks' in result
        assert 'allocations' in result


class TestSelfMonitoringSystem:
    """Test Self-Monitoring System (v5.0)"""

    def test_import_monitoring_system(self):
        """Test importing SelfMonitoringSystem"""
        from autonomous import SelfMonitoringSystem, HealthStatus
        assert SelfMonitoringSystem is not None
        assert HealthStatus.HEALTHY is not None

    def test_create_monitoring_system(self):
        """Test creating monitoring system"""
        from autonomous import SelfMonitoringSystem

        monitor = SelfMonitoringSystem()
        assert monitor is not None

    def test_perform_health_check(self):
        """Test health check"""
        from autonomous import SelfMonitoringSystem

        monitor = SelfMonitoringSystem()
        health = monitor.perform_health_check()

        assert health is not None
        assert 'status' in health
        assert 'checks' in health
        assert 'timestamp' in health

    def test_detect_anomalies(self):
        """Test anomaly detection"""
        from autonomous import SelfMonitoringSystem

        monitor = SelfMonitoringSystem()

        metrics = {
            'cpu_usage': 0.95,  # High
            'memory_usage': 0.50,
            'error_rate': 0.02
        }

        anomalies = monitor.detect_anomalies(metrics)

        assert isinstance(anomalies, list)
        # Should detect high CPU usage
        assert any('cpu' in str(a).lower() for a in anomalies)


class TestSelfRepairSystem:
    """Test Self-Repair System (v5.0)"""

    def test_import_repair_system(self):
        """Test importing SelfRepairSystem"""
        from autonomous import SelfRepairSystem, RepairStrategy
        assert SelfRepairSystem is not None
        assert RepairStrategy.RESTART is not None

    def test_create_repair_system(self):
        """Test creating repair system"""
        from autonomous import SelfRepairSystem

        repair = SelfRepairSystem()
        assert repair is not None

    def test_diagnose_issue(self):
        """Test issue diagnosis"""
        from autonomous import SelfRepairSystem

        repair = SelfRepairSystem()

        issue = {
            'type': 'high_error_rate',
            'severity': 0.8,
            'component': 'data_processor'
        }

        diagnosis = repair.diagnose_issue(issue)

        assert diagnosis is not None
        assert 'cause' in diagnosis
        assert 'recommended_action' in diagnosis

    def test_attempt_repair(self):
        """Test repair attempt"""
        from autonomous import SelfRepairSystem, RepairStrategy

        repair = SelfRepairSystem()

        issue = {
            'type': 'connection_lost',
            'component': 'network'
        }

        result = repair.attempt_repair(issue, RepairStrategy.RECONNECT)

        assert result is not None
        assert 'success' in result
        assert isinstance(result['success'], bool)


class TestAutonomousGoalGenerator:
    """Test Autonomous Goal Generator (v5.0)"""

    def test_import_goal_generator(self):
        """Test importing AutonomousGoalGenerator"""
        from autonomous import AutonomousGoalGenerator, GoalPriority
        assert AutonomousGoalGenerator is not None
        assert GoalPriority.HIGH is not None

    def test_create_goal_generator(self):
        """Test creating goal generator"""
        from autonomous import AutonomousGoalGenerator

        generator = AutonomousGoalGenerator()
        assert generator is not None

    def test_generate_goal(self):
        """Test goal generation"""
        from autonomous import AutonomousGoalGenerator

        generator = AutonomousGoalGenerator()

        context = {
            'current_performance': 0.7,
            'user_needs': ['efficiency', 'accuracy']
        }

        goal = generator.generate_goal(context)

        assert goal is not None
        assert 'goal_id' in goal
        assert 'description' in goal
        assert 'priority' in goal

    def test_evaluate_goal_achievement(self):
        """Test goal achievement evaluation"""
        from autonomous import AutonomousGoalGenerator

        generator = AutonomousGoalGenerator()

        goal = {
            'goal_id': 'goal_001',
            'target_metric': 'accuracy',
            'target_value': 0.9
        }

        current_state = {
            'accuracy': 0.92
        }

        result = generator.evaluate_goal_achievement(goal, current_state)

        assert result is not None
        assert 'achieved' in result
        assert result['achieved'] is True  # 0.92 >= 0.9


class TestHumanAICollaborator:
    """Test Human-AI Collaborator (v5.0)"""

    def test_import_collaborator(self):
        """Test importing HumanAICollaborator"""
        from autonomous import HumanAICollaborator, CollaborationMode
        assert HumanAICollaborator is not None
        assert CollaborationMode.SHARED_CONTROL is not None

    def test_create_collaborator(self):
        """Test creating collaborator"""
        from autonomous import HumanAICollaborator

        collaborator = HumanAICollaborator()
        assert collaborator is not None

    def test_request_human_input(self):
        """Test requesting human input"""
        from autonomous import HumanAICollaborator

        collaborator = HumanAICollaborator()

        decision = {
            'decision_id': 'dec_001',
            'options': ['A', 'B', 'C'],
            'ai_recommendation': 'B'
        }

        request = collaborator.request_human_input(decision)

        assert request is not None
        assert 'request_id' in request
        assert 'message' in request

    def test_integrate_feedback(self):
        """Test integrating human feedback"""
        from autonomous import HumanAICollaborator

        collaborator = HumanAICollaborator()

        feedback = {
            'request_id': 'req_001',
            'human_choice': 'A',
            'rationale': 'Better for long-term'
        }

        result = collaborator.integrate_feedback(feedback)

        assert result is True


class TestAutonomousSystem:
    """Test Integrated Autonomous System (v5.0)"""

    def test_import_autonomous_system(self):
        """Test importing AutonomousSystem"""
        from autonomous import AutonomousSystem
        assert AutonomousSystem is not None

    def test_create_autonomous_system(self):
        """Test creating autonomous system"""
        from autonomous import AutonomousSystem, AutonomousConfig

        config = AutonomousConfig()
        system = AutonomousSystem(config)

        assert system is not None
        assert system.decision_engine is not None
        assert system.learning_system is not None
        assert system.coordinator is not None

    def test_make_autonomous_decision(self):
        """Test making autonomous decision (integrated)"""
        from autonomous import AutonomousSystem, DecisionContext, DecisionType

        system = AutonomousSystem()

        context = DecisionContext(
            decision_id="integrated_decision",
            decision_type=DecisionType.OPERATIONAL,
            current_state={},
            available_actions=["action_A", "action_B"],
            constraints={},
            goals=["optimize"]
        )

        decision = system.make_autonomous_decision(context)

        assert decision is not None
        assert decision.selected_action in context.available_actions

    def test_coordinate_multi_agent_task(self):
        """Test multi-agent task coordination (integrated)"""
        from autonomous import AutonomousSystem, AgentRole

        system = AutonomousSystem()

        # Register agents
        system.coordinator.register_agent("agent_1", AgentRole.EXECUTOR, ["task"])
        system.coordinator.register_agent("agent_2", AgentRole.EXECUTOR, ["task"])

        # Coordinate
        result = system.coordinate_multi_agent_task("Complete mission")

        assert result is not None

    def test_self_monitor_and_repair(self):
        """Test self-monitoring and repair cycle"""
        from autonomous import AutonomousSystem

        system = AutonomousSystem()

        # Perform health check
        health = system.monitoring.perform_health_check()
        assert health is not None

        # If issues detected, attempt repair
        if health['status'] != 'HEALTHY':
            issue = {'type': 'performance_degradation'}
            repair_result = system.repair_system.diagnose_issue(issue)
            assert repair_result is not None

    def test_generate_and_pursue_goal(self):
        """Test autonomous goal generation and pursuit"""
        from autonomous import AutonomousSystem

        system = AutonomousSystem()

        context = {'current_state': 'operational'}
        goal = system.goal_generator.generate_goal(context)

        assert goal is not None
        assert 'goal_id' in goal

    def test_get_system_statistics(self):
        """Test getting system statistics"""
        from autonomous import AutonomousSystem

        system = AutonomousSystem()

        stats = system.get_system_statistics()

        assert stats is not None
        assert 'config' in stats
        assert 'metrics' in stats
        assert 'subsystems' in stats

    def test_get_autonomous_system_singleton(self):
        """Test getting singleton autonomous system"""
        from autonomous import get_autonomous_system

        sys1 = get_autonomous_system()
        sys2 = get_autonomous_system()

        # Should be same instance
        assert sys1 is sys2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
