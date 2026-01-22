"""
Tests for Neuro-Symbolic AI Platform (v14.0)

Tests for Logic Tensor Networks, Neural Module Networks, Program Synthesis,
Semantic Parsing, Differentiable Reasoning, Knowledge Graph Embeddings, and
Hybrid Learning.

IMPORTANT: These tests verify neuro-symbolic AI simulation, not production-ready
systems with rigorous logical guarantees.
"""

import pytest
import numpy as np


class TestLogicTensorNetwork:
    """Test Logic Tensor Network (v14.0)"""

    def test_import_ltn(self):
        """Test importing LogicTensorNetwork"""
        from neurosymbolic import (
            LogicTensorNetwork,
            Predicate,
            LogicRule,
            LogicOperator,
            TNorm
        )
        assert LogicTensorNetwork is not None
        assert LogicOperator.AND is not None
        assert TNorm.PRODUCT is not None

    def test_create_ltn(self):
        """Test creating LTN"""
        from neurosymbolic import LogicTensorNetwork

        ltn = LogicTensorNetwork()
        assert ltn is not None
        assert len(ltn.predicates) == 0

    async def test_add_predicate(self):
        """Test adding predicate"""
        from neurosymbolic import LogicTensorNetwork

        ltn = LogicTensorNetwork()
        await ltn.add_predicate("is_red", arity=1)

        assert "is_red" in ltn.predicates

    async def test_fuzzy_operations(self):
        """Test fuzzy logic operations"""
        from neurosymbolic import LogicTensorNetwork

        ltn = LogicTensorNetwork()

        # Test AND
        result_and = await ltn.fuzzy_and(0.8, 0.6)
        assert 0.0 <= result_and <= 1.0

        # Test OR
        result_or = await ltn.fuzzy_or(0.8, 0.6)
        assert 0.0 <= result_or <= 1.0

        # Test NOT
        result_not = await ltn.fuzzy_not(0.7)
        assert abs(result_not - 0.3) < 0.01

    async def test_satisfiability(self):
        """Test knowledge base satisfiability"""
        from neurosymbolic import LogicTensorNetwork

        ltn = LogicTensorNetwork()
        await ltn.add_rule("rule_1", premise=["A", "B"], conclusion="C")

        sat = await ltn.compute_satisfiability()
        assert 0.0 <= sat <= 1.0


class TestNeuralModuleNetwork:
    """Test Neural Module Network (v14.0)"""

    def test_import_nmn(self):
        """Test importing NeuralModuleNetwork"""
        from neurosymbolic import (
            NeuralModuleNetwork,
            Module,
            ModuleType
        )
        assert NeuralModuleNetwork is not None
        assert ModuleType.FIND is not None

    def test_create_nmn(self):
        """Test creating NMN"""
        from neurosymbolic import NeuralModuleNetwork

        nmn = NeuralModuleNetwork()
        assert nmn is not None

    async def test_parse_question(self):
        """Test question parsing"""
        from neurosymbolic import NeuralModuleNetwork

        nmn = NeuralModuleNetwork()
        program = await nmn.parse_question("What is the color of the ball?")

        assert program is not None
        assert isinstance(program, list)

    async def test_answer_question(self):
        """Test end-to-end question answering"""
        from neurosymbolic import NeuralModuleNetwork

        nmn = NeuralModuleNetwork()
        image_features = np.random.randn(224, 224, 3)

        answer = await nmn.answer_question("Count the objects", image_features)
        assert answer is not None


class TestProgramSynthesisEngine:
    """Test Program Synthesis Engine (v14.0)"""

    def test_import_synthesis(self):
        """Test importing ProgramSynthesisEngine"""
        from neurosymbolic import (
            ProgramSynthesisEngine,
            Program,
            SynthesisAlgorithm
        )
        assert ProgramSynthesisEngine is not None
        assert SynthesisAlgorithm.NEURAL_GUIDED is not None

    def test_create_synthesis_engine(self):
        """Test creating synthesis engine"""
        from neurosymbolic import ProgramSynthesisEngine

        engine = ProgramSynthesisEngine()
        assert engine is not None

    async def test_synthesize_program(self):
        """Test program synthesis"""
        from neurosymbolic import ProgramSynthesisEngine, SynthesisAlgorithm

        engine = ProgramSynthesisEngine()
        examples = [("hello", "HELLO"), ("world", "WORLD")]

        program = await engine.synthesize_program(
            examples,
            algorithm=SynthesisAlgorithm.NEURAL_GUIDED,
            max_size=20
        )

        assert program is not None
        assert program.code is not None

    async def test_verify_program(self):
        """Test program verification"""
        from neurosymbolic import ProgramSynthesisEngine, Program

        engine = ProgramSynthesisEngine()
        program = Program(
            program_id="test_prog",
            code="lambda x: x.upper()",
            language="python",
            examples=[("test", "TEST")]
        )

        correctness = await engine.verify_program(program, [("new", "NEW")])
        assert 0.0 <= correctness <= 1.0


class TestSemanticParser:
    """Test Semantic Parser (v14.0)"""

    def test_import_parser(self):
        """Test importing SemanticParser"""
        from neurosymbolic import (
            SemanticParser,
            LogicalForm
        )
        assert SemanticParser is not None
        assert LogicalForm is not None

    def test_create_parser(self):
        """Test creating parser"""
        from neurosymbolic import SemanticParser

        parser = SemanticParser()
        assert parser is not None

    async def test_parse_to_sql(self):
        """Test parsing to SQL"""
        from neurosymbolic import SemanticParser

        parser = SemanticParser()
        logical_form = await parser.parse("Count the users", target_language="sql")

        assert logical_form is not None
        assert logical_form.logical_form is not None
        assert "COUNT" in logical_form.logical_form or "count" in logical_form.logical_form.lower()

    async def test_parse_batch(self):
        """Test batch parsing"""
        from neurosymbolic import SemanticParser

        parser = SemanticParser()
        questions = ["List names", "Count items", "Find max value"]

        logical_forms = await parser.parse_batch(questions, target_language="sql")
        assert len(logical_forms) == 3


class TestDifferentiableReasoner:
    """Test Differentiable Reasoner (v14.0)"""

    def test_import_reasoner(self):
        """Test importing DifferentiableReasoner"""
        from neurosymbolic import (
            DifferentiableReasoner,
            ReasoningMode
        )
        assert DifferentiableReasoner is not None
        assert ReasoningMode.BACKWARD_CHAINING is not None

    def test_create_reasoner(self):
        """Test creating reasoner"""
        from neurosymbolic import DifferentiableReasoner

        reasoner = DifferentiableReasoner()
        assert reasoner is not None

    def test_add_facts_and_rules(self):
        """Test adding facts and rules"""
        from neurosymbolic import DifferentiableReasoner

        reasoner = DifferentiableReasoner()
        reasoner.add_fact("human(socrates)")
        reasoner.add_rule("human(X) -> mortal(X)")

        assert len(reasoner.knowledge_base["facts"]) > 0
        assert len(reasoner.knowledge_base["rules"]) > 0

    async def test_backward_chaining(self):
        """Test backward chaining"""
        from neurosymbolic import DifferentiableReasoner

        reasoner = DifferentiableReasoner()
        reasoner.add_fact("human(socrates)")

        score, proof = await reasoner.backward_chain("mortal(socrates)")
        assert 0.0 <= score <= 1.0

    async def test_multi_hop_reasoning(self):
        """Test multi-hop reasoning"""
        from neurosymbolic import DifferentiableReasoner

        reasoner = DifferentiableReasoner()
        result = await reasoner.multi_hop_reasoning("goal", num_hops=3)

        assert result is not None
        assert "reasoning_chain" in result


class TestKnowledgeGraphEmbedder:
    """Test Knowledge Graph Embedder (v14.0)"""

    def test_import_kg_embedder(self):
        """Test importing KnowledgeGraphEmbedder"""
        from neurosymbolic import (
            KnowledgeGraphEmbedder,
            Triple,
            EmbeddingModel
        )
        assert KnowledgeGraphEmbedder is not None
        assert EmbeddingModel.TRANSE is not None

    def test_create_kg_embedder(self):
        """Test creating KG embedder"""
        from neurosymbolic import KnowledgeGraphEmbedder

        embedder = KnowledgeGraphEmbedder(embedding_dim=50)
        assert embedder is not None
        assert embedder.embedding_dim == 50

    async def test_add_triple(self):
        """Test adding triple"""
        from neurosymbolic import KnowledgeGraphEmbedder

        embedder = KnowledgeGraphEmbedder()
        await embedder.add_triple("Paris", "capital_of", "France")

        assert len(embedder.triples) > 0
        assert "Paris" in embedder.entity_embeddings

    async def test_score_triple(self):
        """Test triple scoring with TransE"""
        from neurosymbolic import KnowledgeGraphEmbedder

        embedder = KnowledgeGraphEmbedder()
        await embedder.add_triple("Paris", "capital_of", "France")

        score = await embedder.score_triple_transe("Paris", "capital_of", "France")
        assert isinstance(score, float)

    async def test_link_prediction(self):
        """Test link prediction"""
        from neurosymbolic import KnowledgeGraphEmbedder, Triple

        embedder = KnowledgeGraphEmbedder()
        await embedder.add_triple("A", "rel", "B")
        await embedder.add_triple("B", "rel", "C")

        test_triples = [Triple("A", "rel", "B")]
        metrics = await embedder.link_prediction(test_triples)

        assert "hits@10" in metrics
        assert "mrr" in metrics


class TestHybridLearningSystem:
    """Test Hybrid Learning System (v14.0)"""

    def test_import_hybrid(self):
        """Test importing HybridLearningSystem"""
        from neurosymbolic import HybridLearningSystem
        assert HybridLearningSystem is not None

    def test_create_hybrid_system(self):
        """Test creating hybrid system"""
        from neurosymbolic import HybridLearningSystem

        system = HybridLearningSystem()
        assert system is not None

    async def test_add_constraint(self):
        """Test adding constraint"""
        from neurosymbolic import HybridLearningSystem

        system = HybridLearningSystem()
        await system.add_constraint("constraint_1", "forall x: P(x) -> Q(x)", weight=1.0)

        assert len(system.symbolic_kb["constraints"]) > 0

    async def test_train_hybrid(self):
        """Test hybrid training"""
        from neurosymbolic import HybridLearningSystem

        system = HybridLearningSystem()
        await system.add_constraint("c1", "constraint", weight=1.0)

        data = [(np.random.randn(10), 0) for _ in range(20)]
        history = await system.train_hybrid(data, num_epochs=10)

        assert "total_loss" in history
        assert len(history["total_loss"]) == 10

    async def test_extract_rules(self):
        """Test rule extraction"""
        from neurosymbolic import HybridLearningSystem

        system = HybridLearningSystem()
        rules = await system.extract_rules(num_rules=5)

        assert len(rules) == 5


class TestIntegratedSystem:
    """Test Integrated Neuro-Symbolic System (v14.0)"""

    def test_import_integrated(self):
        """Test importing integrated system"""
        from neurosymbolic import (
            IntegratedNeurosymbolicSystem,
            NeurosymbolicConfig,
            get_neurosymbolic_system
        )
        assert IntegratedNeurosymbolicSystem is not None
        assert NeurosymbolicConfig is not None
        assert get_neurosymbolic_system is not None

    def test_create_integrated_system(self):
        """Test creating integrated system"""
        from neurosymbolic import IntegratedNeurosymbolicSystem, NeurosymbolicConfig

        config = NeurosymbolicConfig()
        system = IntegratedNeurosymbolicSystem(config)

        assert system is not None
        assert system.ltn is not None
        assert system.nmn is not None
        assert system.synthesis is not None

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        from neurosymbolic import get_neurosymbolic_system

        system1 = get_neurosymbolic_system()
        system2 = get_neurosymbolic_system()

        assert system1 is system2

    def test_system_status(self):
        """Test system status"""
        from neurosymbolic import IntegratedNeurosymbolicSystem

        system = IntegratedNeurosymbolicSystem()
        status = system.get_system_status()

        assert "ltn_enabled" in status
        assert "nmn_enabled" in status
        assert "synthesis_enabled" in status

    async def test_compositional_reasoning(self):
        """Test compositional reasoning"""
        from neurosymbolic import IntegratedNeurosymbolicSystem

        system = IntegratedNeurosymbolicSystem()
        image = np.random.randn(224, 224, 3)

        result = await system.compositional_reasoning(
            question="What color is the object?",
            image_features=image
        )

        assert result is not None
        assert "combined_answer" in result
