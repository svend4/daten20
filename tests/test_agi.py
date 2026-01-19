"""
Tests for AGI Foundation (v4.5)

Tests for reasoning engine, knowledge graph, and planning system.
"""

import pytest


class TestReasoningEngine:
    """Test Reasoning Engine (v4.5)"""

    def test_import_reasoning_engine(self):
        """Test importing ReasoningEngine"""
        from agi.reasoning_engine import (
            ReasoningEngine,
            ReasoningType,
            ConfidenceLevel,
            Fact,
            Rule
        )
        assert ReasoningEngine is not None
        assert ReasoningType.DEDUCTIVE is not None
        assert ConfidenceLevel.HIGH is not None

    def test_create_reasoning_engine(self):
        """Test creating reasoning engine"""
        from agi.reasoning_engine import ReasoningEngine

        engine = ReasoningEngine()
        assert engine is not None
        assert len(engine.facts) == 0
        assert len(engine.rules) == 0

    def test_add_fact(self):
        """Test adding fact"""
        from agi.reasoning_engine import ReasoningEngine

        engine = ReasoningEngine()
        engine.add_fact("Socrates", "is_a", "human", confidence=1.0)

        assert len(engine.facts) == 1
        fact = engine.facts[0]
        assert fact.subject == "Socrates"
        assert fact.predicate == "is_a"
        assert fact.object == "human"

    def test_add_rule(self):
        """Test adding rule"""
        from agi.reasoning_engine import ReasoningEngine, Rule

        engine = ReasoningEngine()

        rule = Rule(
            rule_id="rule_mortal",
            premises=["X is_a human"],
            conclusion="X is mortal",
            confidence=1.0
        )

        engine.add_rule(rule)
        assert "rule_mortal" in engine.rules

    def test_deductive_reasoning(self):
        """Test deductive reasoning"""
        from agi.reasoning_engine import ReasoningEngine, Rule, ReasoningType

        engine = ReasoningEngine()

        # Add facts
        engine.add_fact("Socrates", "is_a", "human")
        engine.add_fact("humans", "are", "mortal")

        # Add rule
        rule = Rule(
            rule_id="mortal_rule",
            premises=["X is_a human", "humans are mortal"],
            conclusion="X is mortal",
            confidence=1.0
        )
        engine.add_rule(rule)

        # Reason
        result = engine.reason("Is Socrates mortal?", ReasoningType.DEDUCTIVE)

        assert result is not None
        assert result.reasoning_type == ReasoningType.DEDUCTIVE
        assert result.success is True

    def test_inductive_reasoning(self):
        """Test inductive reasoning"""
        from agi.reasoning_engine import ReasoningEngine, ReasoningType

        engine = ReasoningEngine()

        # Add examples
        engine.add_fact("swan1", "is_a", "swan")
        engine.add_fact("swan1", "color", "white")
        engine.add_fact("swan2", "is_a", "swan")
        engine.add_fact("swan2", "color", "white")
        engine.add_fact("swan3", "is_a", "swan")
        engine.add_fact("swan3", "color", "white")

        # Reason inductively
        result = engine.reason("What color are swans?", ReasoningType.INDUCTIVE)

        assert result is not None
        assert result.reasoning_type == ReasoningType.INDUCTIVE

    def test_abductive_reasoning(self):
        """Test abductive reasoning"""
        from agi.reasoning_engine import ReasoningEngine, ReasoningType

        engine = ReasoningEngine()

        # Add facts
        engine.add_fact("grass", "is", "wet")

        # Possible explanations
        engine.add_fact("rain", "causes", "wet_grass")
        engine.add_fact("sprinkler", "causes", "wet_grass")

        # Find best explanation
        result = engine.reason("Why is grass wet?", ReasoningType.ABDUCTIVE)

        assert result is not None
        assert result.reasoning_type == ReasoningType.ABDUCTIVE

    def test_explain_reasoning(self):
        """Test reasoning explanation"""
        from agi.reasoning_engine import ReasoningEngine, Rule, ReasoningType

        engine = ReasoningEngine()

        engine.add_fact("Socrates", "is_a", "human")

        rule = Rule(
            rule_id="mortal_rule",
            premises=["X is_a human"],
            conclusion="X is mortal",
            confidence=1.0
        )
        engine.add_rule(rule)

        result = engine.reason("Is Socrates mortal?", ReasoningType.DEDUCTIVE)
        explanation = engine.explain_reasoning(result)

        assert isinstance(explanation, str)
        assert len(explanation) > 0


class TestKnowledgeGraph:
    """Test Knowledge Graph (v4.5)"""

    def test_import_knowledge_graph(self):
        """Test importing KnowledgeGraph"""
        from agi.knowledge_graph import (
            KnowledgeGraph,
            Node,
            Edge,
            NodeType,
            EdgeType
        )
        assert KnowledgeGraph is not None
        assert NodeType.ENTITY is not None
        assert EdgeType.IS_A is not None

    def test_create_knowledge_graph(self):
        """Test creating knowledge graph"""
        from agi.knowledge_graph import KnowledgeGraph

        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0

    def test_add_node(self):
        """Test adding node"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType

        kg = KnowledgeGraph()
        kg.add_node("person1", "John", NodeType.ENTITY)

        assert "person1" in kg.nodes
        node = kg.nodes["person1"]
        assert node.label == "John"
        assert node.node_type == NodeType.ENTITY

    def test_add_edge(self):
        """Test adding edge"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType, EdgeType

        kg = KnowledgeGraph()

        kg.add_node("person1", "John", NodeType.ENTITY)
        kg.add_node("person2", "Mary", NodeType.ENTITY)

        kg.add_edge("person1", "person2", EdgeType.KNOWS, weight=1.0)

        edge_key = ("person1", "person2")
        assert edge_key in kg.edges

    def test_find_path(self):
        """Test pathfinding"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType, EdgeType

        kg = KnowledgeGraph()

        # Create simple graph: A -> B -> C
        kg.add_node("A", "Node A", NodeType.ENTITY)
        kg.add_node("B", "Node B", NodeType.ENTITY)
        kg.add_node("C", "Node C", NodeType.ENTITY)

        kg.add_edge("A", "B", EdgeType.CUSTOM, weight=1.0)
        kg.add_edge("B", "C", EdgeType.CUSTOM, weight=1.0)

        path = kg.find_path("A", "C")

        assert path is not None
        assert path.nodes[0] == "A"
        assert path.nodes[-1] == "C"
        assert "B" in path.nodes

    def test_semantic_similarity(self):
        """Test semantic similarity"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType, EdgeType

        kg = KnowledgeGraph()

        kg.add_node("dog", "Dog", NodeType.ENTITY)
        kg.add_node("animal", "Animal", NodeType.ENTITY)
        kg.add_edge("dog", "animal", EdgeType.IS_A, weight=1.0)

        similarity = kg.find_semantic_similarity("dog", "animal")

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0  # Should have some similarity

    def test_query_subgraph(self):
        """Test subgraph query"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType, EdgeType

        kg = KnowledgeGraph()

        # Create small graph
        kg.add_node("A", "Node A", NodeType.ENTITY)
        kg.add_node("B", "Node B", NodeType.ENTITY)
        kg.add_node("C", "Node C", NodeType.ENTITY)

        kg.add_edge("A", "B", EdgeType.CUSTOM)
        kg.add_edge("B", "C", EdgeType.CUSTOM)

        subgraph = kg.query_subgraph("A", radius=2)

        assert 'nodes' in subgraph
        assert 'edges' in subgraph
        assert len(subgraph['nodes']) > 0

    def test_get_statistics(self):
        """Test graph statistics"""
        from agi.knowledge_graph import KnowledgeGraph, NodeType, EdgeType

        kg = KnowledgeGraph()

        kg.add_node("A", "Node A", NodeType.ENTITY)
        kg.add_node("B", "Node B", NodeType.ENTITY)
        kg.add_edge("A", "B", EdgeType.CUSTOM)

        stats = kg.get_statistics()

        assert 'num_nodes' in stats
        assert 'num_edges' in stats
        assert stats['num_nodes'] == 2
        assert stats['num_edges'] == 1


class TestPlanningSystem:
    """Test Planning System (v4.5)"""

    def test_import_planning_system(self):
        """Test importing PlanningSystem"""
        from agi.planning_system import (
            PlanningSystem,
            Goal,
            Action,
            Plan,
            GoalStatus,
            ActionStatus
        )
        assert PlanningSystem is not None
        assert GoalStatus.PENDING is not None
        assert ActionStatus.NOT_STARTED is not None

    def test_create_planning_system(self):
        """Test creating planning system"""
        from agi.planning_system import PlanningSystem

        planner = PlanningSystem()
        assert planner is not None
        assert len(planner.goals) == 0
        assert len(planner.actions) == 0

    def test_add_goal(self):
        """Test adding goal"""
        from agi.planning_system import PlanningSystem, Goal

        planner = PlanningSystem()

        goal = Goal(
            goal_id="goal1",
            description="Process document",
            postconditions=["document_processed"]
        )

        planner.add_goal(goal)
        assert "goal1" in planner.goals

    def test_register_action(self):
        """Test registering action"""
        from agi.planning_system import PlanningSystem, Action

        planner = PlanningSystem()

        def execute_fn():
            return True

        action = Action(
            action_id="action1",
            name="Load document",
            preconditions=["file_exists"],
            effects=["document_loaded"],
            execute_fn=execute_fn
        )

        planner.register_action(action)
        assert "action1" in planner.actions

    def test_create_plan(self):
        """Test creating plan"""
        from agi.planning_system import PlanningSystem, Goal, Action

        planner = PlanningSystem()

        # Define actions
        def load_fn():
            return True

        def process_fn():
            return True

        load_action = Action(
            action_id="load",
            name="Load document",
            preconditions=[],
            effects=["document_loaded"],
            execute_fn=load_fn
        )

        process_action = Action(
            action_id="process",
            name="Process document",
            preconditions=["document_loaded"],
            effects=["document_processed"],
            execute_fn=process_fn
        )

        planner.register_action(load_action)
        planner.register_action(process_action)

        # Define goal
        goal = Goal(
            goal_id="goal1",
            description="Process document",
            postconditions=["document_processed"]
        )

        planner.add_goal(goal)

        # Create plan
        plan = planner.plan("goal1")

        assert plan is not None
        assert len(plan.actions) > 0

    def test_execute_plan(self):
        """Test executing plan"""
        from agi.planning_system import PlanningSystem, Goal, Action

        planner = PlanningSystem()

        # Define simple action
        def simple_action():
            planner.world_state.facts.append("task_done")
            return True

        action = Action(
            action_id="action1",
            name="Do task",
            preconditions=[],
            effects=["task_done"],
            execute_fn=simple_action
        )

        planner.register_action(action)

        # Define goal
        goal = Goal(
            goal_id="goal1",
            description="Complete task",
            postconditions=["task_done"]
        )

        planner.add_goal(goal)

        # Plan and execute
        plan = planner.plan("goal1")
        if plan:
            result = planner.execute_plan(plan.plan_id)
            assert result is True

    def test_monitor_goals(self):
        """Test goal monitoring"""
        from agi.planning_system import PlanningSystem, Goal

        planner = PlanningSystem()

        goal = Goal(
            goal_id="goal1",
            description="Test goal",
            postconditions=["done"]
        )

        planner.add_goal(goal)

        status = planner.monitor_goals()

        assert 'total_goals' in status
        assert 'goals' in status
        assert status['total_goals'] == 1


class TestAGISystem:
    """Test Integrated AGI System (v4.5)"""

    def test_import_agi_system(self):
        """Test importing AGISystem"""
        from agi import AGISystem
        assert AGISystem is not None

    def test_create_agi_system(self):
        """Test creating AGI system"""
        from agi import AGISystem

        agi = AGISystem()
        assert agi is not None
        assert agi.reasoning is not None
        assert agi.knowledge is not None
        assert agi.planning is not None

    def test_add_fact_integrated(self):
        """Test adding fact (integrated)"""
        from agi import AGISystem

        agi = AGISystem()
        agi.add_fact("Socrates", "is_a", "human", confidence=1.0)

        # Should be in both reasoning and knowledge
        assert len(agi.reasoning.facts) > 0
        assert len(agi.knowledge.nodes) > 0

    def test_reason_integrated(self):
        """Test reasoning (integrated)"""
        from agi import AGISystem, ReasoningType

        agi = AGISystem()

        agi.add_fact("Socrates", "is_a", "human")
        agi.add_fact("humans", "are", "mortal")

        result = agi.reason("Is Socrates mortal?", ReasoningType.DEDUCTIVE)

        assert result is not None
        assert result.success is True

    def test_add_entity(self):
        """Test adding entity"""
        from agi import AGISystem

        agi = AGISystem()
        agi.add_entity("person1", "John", {"age": 30})

        assert "person1" in agi.knowledge.nodes

    def test_add_relation(self):
        """Test adding relation"""
        from agi import AGISystem

        agi = AGISystem()

        agi.add_entity("person1", "John")
        agi.add_entity("person2", "Mary")
        agi.add_relation("person1", "person2", "knows", weight=1.0)

        assert ("person1", "person2") in agi.knowledge.edges

    def test_find_path_integrated(self):
        """Test pathfinding (integrated)"""
        from agi import AGISystem

        agi = AGISystem()

        agi.add_entity("A", "Node A")
        agi.add_entity("B", "Node B")
        agi.add_entity("C", "Node C")

        agi.add_relation("A", "B", "connects_to")
        agi.add_relation("B", "C", "connects_to")

        path = agi.find_path("A", "C")

        assert path is not None
        assert "A" in path.nodes
        assert "C" in path.nodes

    def test_add_goal_integrated(self):
        """Test adding goal (integrated)"""
        from agi import AGISystem, Goal

        agi = AGISystem()

        goal = Goal(
            goal_id="goal1",
            description="Test goal",
            postconditions=["done"]
        )

        agi.add_goal(goal)
        assert "goal1" in agi.planning.goals

    def test_learn_from_example(self):
        """Test learning from example"""
        from agi import AGISystem

        agi = AGISystem()

        example = {
            'input': 'x=5, y=3',
            'output': 'sum=8'
        }

        agi.learn_from_example(example)

        # Should have added fact
        assert len(agi.reasoning.facts) > 0

    def test_get_system_statistics(self):
        """Test getting system statistics"""
        from agi import AGISystem

        agi = AGISystem()

        agi.add_fact("test", "is", "fact")
        agi.add_entity("entity1", "Entity")

        stats = agi.get_system_statistics()

        assert 'reasoning' in stats
        assert 'knowledge' in stats
        assert 'planning' in stats
        assert stats['reasoning']['facts'] > 0

    def test_get_agi_system_singleton(self):
        """Test getting singleton AGI system"""
        from agi import get_agi_system

        agi1 = get_agi_system()
        agi2 = get_agi_system()

        # Should be same instance
        assert agi1 is agi2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
