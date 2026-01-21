"""
Tests for AGI Universal Framework v26.0

Tests all major components:
- Multi-task learning
- Meta-learning
- Reasoning chains
- Universal problem solver
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))


class TestMetaLearning:
    """Tests for meta-learning module"""

    def test_meta_learner_initialization(self):
        """Test meta-learner can be initialized"""
        from agi_universal.meta_learning import MetaLearner, MetaLearningConfig

        config = MetaLearningConfig(
            inner_learning_rate=0.01,
            outer_learning_rate=0.001,
            inner_steps=3
        )

        meta = MetaLearner(input_dim=1, output_dim=1, hidden_dim=16, config=config)

        assert meta.input_dim == 1
        assert meta.output_dim == 1
        assert meta.hidden_dim == 16
        assert meta.config.inner_steps == 3

    def test_few_shot_adaptation(self):
        """Test few-shot learning adaptation"""
        from agi_universal.meta_learning import MetaLearner, TaskSample

        meta = MetaLearner(input_dim=1, output_dim=1, hidden_dim=16)

        # Create simple task
        support_set = [([x], [x * 2]) for x in [0.1, 0.2, 0.3]]
        query_set = [([x], [x * 2]) for x in [0.4, 0.5]]

        task_sample = TaskSample(support_set=support_set, query_set=query_set)

        # Adapt to task
        result = meta.adapt_to_task(task_sample)

        assert 'adapted_params' in result
        assert 'query_loss' in result
        assert result['num_support'] == 3
        assert result['num_query'] == 2

    def test_meta_training(self):
        """Test meta-training process"""
        from agi_universal.meta_learning import (
            MetaLearner,
            MetaLearningConfig,
            sine_wave_task_generator
        )

        config = MetaLearningConfig(
            inner_learning_rate=0.01,
            outer_learning_rate=0.001,
            inner_steps=2,
            meta_batch_size=2
        )

        meta = MetaLearner(input_dim=1, output_dim=1, hidden_dim=16, config=config)

        # Meta-train for few iterations
        result = meta.meta_train(sine_wave_task_generator, num_iterations=5)

        assert 'meta_losses' in result
        assert len(result['meta_losses']) == 5
        assert 'final_loss' in result
        assert 'improvement' in result
        assert result['iterations'] == 5


class TestReasoningChains:
    """Tests for reasoning chains module"""

    def test_deductive_reasoning(self):
        """Test deductive reasoning chain"""
        from agi_universal.reasoning_chains import ChainOfThoughtReasoner, ReasoningType

        reasoner = ChainOfThoughtReasoner()

        problem = "If all humans are mortal, and Socrates is human, is Socrates mortal?"
        chain = reasoner.solve_problem(problem, ReasoningType.DEDUCTIVE)

        assert chain.problem == problem
        assert len(chain.steps) > 0
        assert chain.conclusion is not None
        assert chain.success is True
        assert all(step.reasoning_type == ReasoningType.DEDUCTIVE for step in chain.steps)

    def test_inductive_reasoning(self):
        """Test inductive reasoning chain"""
        from agi_universal.reasoning_chains import ChainOfThoughtReasoner, ReasoningType

        reasoner = ChainOfThoughtReasoner()

        problem = "The sun rose today, yesterday, and the day before. What about tomorrow?"
        chain = reasoner.solve_problem(problem, ReasoningType.INDUCTIVE)

        assert len(chain.steps) > 0
        assert chain.success is True
        assert all(step.reasoning_type == ReasoningType.INDUCTIVE for step in chain.steps)

    def test_abductive_reasoning(self):
        """Test abductive reasoning chain"""
        from agi_universal.reasoning_chains import ChainOfThoughtReasoner, ReasoningType

        reasoner = ChainOfThoughtReasoner()

        problem = "The grass is wet. What is the most likely explanation?"
        chain = reasoner.solve_problem(problem, ReasoningType.ABDUCTIVE)

        assert len(chain.steps) > 0
        assert chain.success is True
        assert all(step.reasoning_type == ReasoningType.ABDUCTIVE for step in chain.steps)

    def test_causal_reasoning(self):
        """Test causal reasoning chain"""
        from agi_universal.reasoning_chains import ChainOfThoughtReasoner, ReasoningType

        reasoner = ChainOfThoughtReasoner()

        problem = "What caused the window to break?"
        chain = reasoner.solve_problem(problem, ReasoningType.CAUSAL)

        assert len(chain.steps) > 0
        assert chain.success is True
        assert all(step.reasoning_type == ReasoningType.CAUSAL for step in chain.steps)

    def test_reasoning_step_confidence(self):
        """Test that reasoning steps have confidence scores"""
        from agi_universal.reasoning_chains import ChainOfThoughtReasoner, ReasoningType

        reasoner = ChainOfThoughtReasoner()
        chain = reasoner.solve_problem("Test problem", ReasoningType.DEDUCTIVE)

        for step in chain.steps:
            assert 0.0 <= step.confidence <= 1.0

    def test_explain_reasoning_chain(self):
        """Test reasoning chain explanation generation"""
        from agi_universal.reasoning_chains import (
            ChainOfThoughtReasoner,
            ReasoningType,
            explain_reasoning_chain
        )

        reasoner = ChainOfThoughtReasoner()
        chain = reasoner.solve_problem("Test problem", ReasoningType.DEDUCTIVE)

        explanation = explain_reasoning_chain(chain)

        assert isinstance(explanation, str)
        assert "Problem:" in explanation
        assert "Conclusion:" in explanation
        assert len(explanation) > 0


class TestUniversalProblemSolver:
    """Tests for universal problem solver"""

    def test_solver_initialization(self):
        """Test solver can be initialized"""
        from agi_universal.universal_solver import UniversalProblemSolver

        solver = UniversalProblemSolver()
        result = solver.initialize(quick_init=True)

        assert result['status'] == 'initialized'
        assert 'initialization_time' in result
        assert 'components' in result
        assert solver.initialized is True

    def test_solve_logical_problem(self):
        """Test solving logical problem"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain,
            SolutionStrategy
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        problem = Problem(
            description="If A implies B, and B implies C, does A imply C?",
            domain=ProblemDomain.LOGICAL
        )

        solution = solver.solve(problem)

        assert solution.problem == problem
        assert solution.strategy_used == SolutionStrategy.REASONING_CHAIN
        assert solution.answer is not None
        assert 0.0 <= solution.confidence <= 1.0
        assert solution.success is True

    def test_solve_mathematical_problem(self):
        """Test solving mathematical problem"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        problem = Problem(
            description="What is 5 + 3?",
            domain=ProblemDomain.MATHEMATICAL
        )

        solution = solver.solve(problem)

        assert solution.problem == problem
        assert solution.answer is not None
        assert solution.success is True

    def test_solve_with_few_shot_examples(self):
        """Test solving with few-shot examples"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain,
            SolutionStrategy
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        problem = Problem(
            description="What is the pattern?",
            domain=ProblemDomain.MATHEMATICAL,
            examples=[
                {'input': 1, 'output': 2},
                {'input': 2, 'output': 4},
                {'input': 3, 'output': 6}
            ]
        )

        solution = solver.solve(problem)

        assert solution.strategy_used == SolutionStrategy.FEW_SHOT_LEARNING
        assert solution.answer is not None
        assert solution.success is True

    def test_strategy_selection(self):
        """Test that solver selects appropriate strategy"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain,
            SolutionStrategy
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        # Logical problem should use reasoning
        logical_problem = Problem(
            description="Test logical problem",
            domain=ProblemDomain.LOGICAL
        )
        logical_solution = solver.solve(logical_problem)
        assert logical_solution.strategy_used == SolutionStrategy.REASONING_CHAIN

        # Problem with examples should use few-shot
        few_shot_problem = Problem(
            description="Test few-shot problem",
            domain=ProblemDomain.UNKNOWN,
            examples=[{'x': 1, 'y': 2}]
        )
        few_shot_solution = solver.solve(few_shot_problem)
        assert few_shot_solution.strategy_used == SolutionStrategy.FEW_SHOT_LEARNING

    def test_learn_from_feedback(self):
        """Test learning from feedback"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        problem = Problem(description="Test problem", domain=ProblemDomain.LOGICAL)
        solution = solver.solve(problem)

        # Provide feedback
        feedback = {
            'correct': False,
            'better_answer': 'The correct answer is X'
        }

        result = solver.learn_from_feedback(solution, feedback)

        assert 'feedback_id' in result
        assert result['stored'] is True
        assert 'adjustments' in result

    def test_performance_statistics(self):
        """Test performance statistics collection"""
        from agi_universal.universal_solver import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        # Solve multiple problems
        for i in range(3):
            problem = Problem(
                description=f"Test problem {i}",
                domain=ProblemDomain.LOGICAL
            )
            solver.solve(problem)

        stats = solver.get_performance_stats()

        assert stats['total_problems_solved'] == 3
        assert 'success_rate' in stats
        assert 'average_confidence' in stats
        assert 'average_execution_time' in stats
        assert 'strategies_used' in stats
        assert 'domains_covered' in stats


class TestAGIUniversalIntegration:
    """Integration tests for complete AGI framework"""

    def test_complete_agi_workflow(self):
        """Test complete AGI workflow from initialization to problem solving"""
        from agi_universal import (
            UniversalProblemSolver,
            Problem,
            ProblemDomain
        )

        # Initialize
        solver = UniversalProblemSolver()
        init_result = solver.initialize(quick_init=True)
        assert init_result['status'] == 'initialized'

        # Solve problems
        problems = [
            Problem("Logical problem", ProblemDomain.LOGICAL),
            Problem("Math problem", ProblemDomain.MATHEMATICAL),
            Problem("Causal problem", ProblemDomain.CAUSAL)
        ]

        solutions = [solver.solve(p) for p in problems]

        # Verify all solved
        assert all(s.success for s in solutions)
        assert len(solutions) == 3

        # Check stats
        stats = solver.get_performance_stats()
        assert stats['total_problems_solved'] == 3

    def test_multi_task_and_meta_learning_integration(self):
        """Test integration of multi-task and meta-learning"""
        from agi_universal import (
            MultiTaskLearner,
            MultiTaskConfig,
            MetaLearner,
            MetaLearningConfig
        )

        # Multi-task learner
        mtl_config = MultiTaskConfig(shared_hidden_dim=16, num_epochs=10)
        mtl = MultiTaskLearner(input_dim=2, config=mtl_config)
        assert mtl is not None

        # Meta-learner
        meta_config = MetaLearningConfig(inner_steps=2)
        meta = MetaLearner(input_dim=1, output_dim=1, config=meta_config)
        assert meta is not None

        # Both can coexist
        assert mtl.input_dim == 2
        assert meta.input_dim == 1

    def test_reasoning_with_problem_solver(self):
        """Test reasoning chains integrated with problem solver"""
        from agi_universal import (
            UniversalProblemSolver,
            ChainOfThoughtReasoner,
            Problem,
            ProblemDomain,
            ReasoningType
        )

        solver = UniversalProblemSolver()
        solver.initialize(quick_init=True)

        # Solve via problem solver
        problem = Problem("Test problem", ProblemDomain.LOGICAL)
        solution = solver.solve(problem)

        # Also test reasoner directly
        reasoner = ChainOfThoughtReasoner()
        chain = reasoner.solve_problem("Test problem", ReasoningType.DEDUCTIVE)

        # Both should work
        assert solution.success
        assert chain.success


# Run with: pytest tests/unit/agi_universal/test_agi_universal_framework.py -v
