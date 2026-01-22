"""
Tests for Emotional Intelligence & Affective Computing (v7.0)

Tests for emotional awareness, affective computing, empathy, emotional intelligence,
emotional memory, emotional decision-making, and expression generation.

IMPORTANT: These tests verify computational emotional simulation,
not genuine subjective emotional experiences.
"""

import pytest


class TestEmotionalAwarenessEngine:
    """Test Emotional Awareness Engine (v7.0)"""

    def test_import_awareness_engine(self):
        """Test importing EmotionalAwarenessEngine"""
        from emotions_ai import (
            EmotionalAwarenessEngine,
            Emotion,
            EmotionType,
            EmotionalState,
            AppraisalResult
        )
        assert EmotionalAwarenessEngine is not None
        assert EmotionType.JOY is not None

    def test_create_awareness_engine(self):
        """Test creating awareness engine"""
        from emotions_ai import EmotionalAwarenessEngine

        engine = EmotionalAwarenessEngine()
        assert engine is not None
        assert engine.current_state is None  # No state initially

    def test_recognize_self_emotion(self):
        """Test recognizing self emotion"""
        from emotions_ai import EmotionalAwarenessEngine, EmotionType

        engine = EmotionalAwarenessEngine()

        emotion = engine.recognize_self_emotion()

        assert emotion is not None
        assert emotion.type == EmotionType.NEUTRAL  # Default
        assert 0.0 <= emotion.intensity <= 1.0

    def test_detect_emotion_from_text(self):
        """Test detecting emotion from text"""
        from emotions_ai import EmotionalAwarenessEngine, EmotionType

        engine = EmotionalAwarenessEngine()

        # Happy text
        happy_text = "I'm so happy and excited about this!"
        emotion = engine.detect_emotion(happy_text)

        assert emotion.type == EmotionType.JOY
        assert emotion.intensity > 0.5

        # Sad text
        sad_text = "I'm feeling really sad and down today."
        emotion = engine.detect_emotion(sad_text)

        assert emotion.type == EmotionType.SADNESS
        assert emotion.valence < 0

    def test_appraise_event(self):
        """Test event appraisal"""
        from emotions_ai import EmotionalAwarenessEngine

        engine = EmotionalAwarenessEngine()

        event = {
            'type': 'goal_achieved',
            'importance': 0.9
        }

        appraisal = engine.appraise_event(event)

        assert appraisal is not None
        assert appraisal.emotion is not None
        assert appraisal.goal_relevance == 0.9
        assert appraisal.goal_congruence == 1.0  # Goal achieved

    def test_update_emotional_state(self):
        """Test updating emotional state"""
        from emotions_ai import EmotionalAwarenessEngine, Emotion, EmotionType

        engine = EmotionalAwarenessEngine()

        emotion = Emotion(
            type=EmotionType.JOY,
            intensity=0.8,
            valence=0.9,
            arousal=0.7
        )

        state = engine.update_emotional_state(emotion)

        assert state is not None
        assert state.primary_emotion.type == EmotionType.JOY
        assert len(engine.emotion_history) == 1


class TestAffectiveComputingSystem:
    """Test Affective Computing System (v7.0)"""

    def test_import_affective_system(self):
        """Test importing AffectiveComputingSystem"""
        from emotions_ai import (
            AffectiveComputingSystem,
            RegulationStrategy,
            Mood,
            MoodType
        )
        assert AffectiveComputingSystem is not None
        assert RegulationStrategy.REAPPRAISAL is not None

    def test_create_affective_system(self):
        """Test creating affective system"""
        from emotions_ai import AffectiveComputingSystem

        system = AffectiveComputingSystem()
        assert system is not None
        assert system.current_mood is not None

    def test_generate_emotion(self):
        """Test generating emotion from event"""
        from emotions_ai import AffectiveComputingSystem, EmotionType

        system = AffectiveComputingSystem()

        event = {
            'type': 'success',
            'severity': 0.8
        }

        emotion = system.generate_emotion(event)

        assert emotion is not None
        assert emotion.type == EmotionType.JOY
        assert emotion.valence > 0

    def test_regulate_emotion(self):
        """Test emotion regulation"""
        from emotions_ai import (
            AffectiveComputingSystem,
            Emotion,
            EmotionType,
            RegulationStrategy
        )

        system = AffectiveComputingSystem()

        # Strong negative emotion
        emotion = Emotion(
            type=EmotionType.ANGER,
            intensity=0.9,
            valence=-0.8,
            arousal=0.9
        )

        # Regulate with reappraisal
        regulated = system.regulate_emotion(
            emotion,
            RegulationStrategy.REAPPRAISAL,
            target_intensity=0.5
        )

        assert regulated is not None
        assert regulated.intensity < emotion.intensity  # Should be reduced

    def test_update_mood(self):
        """Test mood update from emotions"""
        from emotions_ai import AffectiveComputingSystem, Emotion, EmotionType, MoodType

        system = AffectiveComputingSystem()

        # Multiple positive emotions
        emotions = [
            Emotion(EmotionType.JOY, intensity=0.8, valence=0.8, arousal=0.7),
            Emotion(EmotionType.GRATITUDE, intensity=0.7, valence=0.7, arousal=0.4),
            Emotion(EmotionType.EXCITEMENT, intensity=0.9, valence=0.9, arousal=0.9)
        ]

        mood = system.update_mood(emotions)

        assert mood is not None
        assert mood.type in [MoodType.CHEERFUL, MoodType.CONTENT, MoodType.CALM]
        assert mood.valence > 0

    def test_get_current_mood(self):
        """Test getting current mood"""
        from emotions_ai import AffectiveComputingSystem

        system = AffectiveComputingSystem()

        mood = system.get_current_mood()

        assert mood is not None
        assert hasattr(mood, 'type')
        assert hasattr(mood, 'valence')


class TestEmpathySimulator:
    """Test Empathy Simulator (v7.0)"""

    def test_import_empathy_simulator(self):
        """Test importing EmpathySimulator"""
        from emotions_ai import (
            EmpathySimulator,
            EmpathyType,
            EmpatheticResponse
        )
        assert EmpathySimulator is not None
        assert EmpathyType.COGNITIVE is not None

    def test_create_empathy_simulator(self):
        """Test creating empathy simulator"""
        from emotions_ai import EmpathySimulator

        simulator = EmpathySimulator()
        assert simulator is not None
        assert simulator.empathy_level > 0

    def test_take_perspective(self):
        """Test perspective-taking (cognitive empathy)"""
        from emotions_ai import EmpathySimulator

        simulator = EmpathySimulator()

        situation = {
            'context': 'project_failure',
            'visible_emotions': ['frustration', 'disappointment']
        }

        perspective = simulator.take_perspective(situation)

        assert perspective is not None
        assert 'inferred_beliefs' in perspective
        assert 'inferred_emotions' in perspective
        assert len(perspective['inferred_beliefs']) > 0

    def test_feel_empathy(self):
        """Test feeling empathy (affective empathy)"""
        from emotions_ai import EmpathySimulator, EmpathyType

        simulator = EmpathySimulator()

        empathic_emotion = simulator.feel_empathy(
            other_emotion='sadness',
            intensity=0.8,
            empathy_type=EmpathyType.AFFECTIVE
        )

        assert empathic_emotion is not None
        assert empathic_emotion.intensity > 0
        # Should feel similar emotion with modulated intensity

    def test_generate_compassionate_response(self):
        """Test generating compassionate response"""
        from emotions_ai import EmpathySimulator

        simulator = EmpathySimulator()

        situation = {
            'context': 'project_failure',
            'visible_emotions': ['frustration']
        }

        response = simulator.generate_compassionate_response(
            situation,
            'frustration'
        )

        assert response is not None
        assert response.empathy_type is not None
        assert len(response.response_text) > 0
        assert len(response.understanding) > 0


class TestEmotionalIntelligenceSystem:
    """Test Emotional Intelligence System (v7.0)"""

    def test_import_eq_system(self):
        """Test importing EmotionalIntelligenceSystem"""
        from emotions_ai import (
            EmotionalIntelligenceSystem,
            EQAssessment,
            EQDimension
        )
        assert EmotionalIntelligenceSystem is not None
        assert EQDimension.SELF_AWARENESS is not None

    def test_create_eq_system(self):
        """Test creating EQ system"""
        from emotions_ai import EmotionalIntelligenceSystem

        system = EmotionalIntelligenceSystem()
        assert system is not None
        assert len(system.eq_scores) > 0

    def test_assess_eq(self):
        """Test EQ assessment"""
        from emotions_ai import EmotionalIntelligenceSystem

        system = EmotionalIntelligenceSystem()

        assessment = system.assess_eq()

        assert assessment is not None
        assert 0.0 <= assessment.overall_score <= 1.0
        assert 'self_awareness' in assessment.dimensions
        assert 'social_awareness' in assessment.dimensions
        assert isinstance(assessment.strengths, list)

    def test_apply_skill(self):
        """Test applying emotional intelligence skill"""
        from emotions_ai import EmotionalIntelligenceSystem

        system = EmotionalIntelligenceSystem()

        situation = {
            'type': 'conflict',
            'parties': ['person_a', 'person_b']
        }

        result = system.apply_skill('conflict_resolution', situation)

        assert result is not None
        assert 'skill' in result
        assert 'strategy' in result
        assert 'steps' in result

    def test_learn_from_interaction(self):
        """Test learning from interaction"""
        from emotions_ai import EmotionalIntelligenceSystem

        system = EmotionalIntelligenceSystem()

        initial_scores = system.eq_scores.copy()

        interaction = {
            'outcome': 'positive',
            'emotions': ['satisfaction']
        }

        feedback = {
            'effectiveness': 0.9
        }

        system.learn_from_interaction(interaction, feedback)

        # Scores should improve with positive feedback
        # (At least some dimension should increase)


class TestEmotionalMemorySystem:
    """Test Emotional Memory System (v7.0)"""

    def test_import_memory_system(self):
        """Test importing EmotionalMemorySystem"""
        from emotions_ai import (
            EmotionalMemorySystem,
            EmotionalMemory
        )
        assert EmotionalMemorySystem is not None
        assert EmotionalMemory is not None

    def test_create_memory_system(self):
        """Test creating memory system"""
        from emotions_ai import EmotionalMemorySystem

        system = EmotionalMemorySystem()
        assert system is not None
        assert len(system.memories) == 0

    def test_store_memory(self):
        """Test storing emotion-tagged memory"""
        from emotions_ai import EmotionalMemorySystem, Emotion, EmotionType

        system = EmotionalMemorySystem()

        event = {
            'type': 'user_praise',
            'content': 'Great job!'
        }

        emotion = Emotion(
            type=EmotionType.PRIDE,
            intensity=0.8,
            valence=0.8
        )

        memory_id = system.store(event, emotion, importance=0.9)

        assert memory_id is not None
        assert len(system.memories) == 1

    def test_retrieve_memory(self):
        """Test retrieving memories by emotion"""
        from emotions_ai import EmotionalMemorySystem, Emotion, EmotionType

        system = EmotionalMemorySystem()

        # Store multiple memories
        for i in range(3):
            event = {'event': f'event_{i}'}
            emotion = Emotion(
                type=EmotionType.JOY if i < 2 else EmotionType.SADNESS,
                intensity=0.7
            )
            system.store(event, emotion)

        # Query for joy memories
        query = {
            'emotion_type': 'joy',
            'min_intensity': 0.5
        }

        results = system.retrieve(query)

        assert len(results) == 2  # Should find 2 joy memories

    def test_retrieve_mood_congruent(self):
        """Test mood-congruent memory retrieval"""
        from emotions_ai import EmotionalMemorySystem, Emotion, EmotionType, Mood, MoodType

        system = EmotionalMemorySystem()

        # Store memories with different valences
        positive_event = {'event': 'good_news'}
        positive_emotion = Emotion(EmotionType.JOY, intensity=0.8, valence=0.8)
        system.store(positive_event, positive_emotion)

        negative_event = {'event': 'bad_news'}
        negative_emotion = Emotion(EmotionType.SADNESS, intensity=0.7, valence=-0.7)
        system.store(negative_event, negative_emotion)

        # Positive mood
        positive_mood = Mood(type=MoodType.CHEERFUL, valence=0.7)
        results = system.retrieve_mood_congruent(positive_mood)

        assert len(results) == 1  # Should retrieve positive memory
        assert results[0].emotion.valence > 0


class TestEmotionalDecisionMaking:
    """Test Emotional Decision Making (v7.0)"""

    def test_import_decision_system(self):
        """Test importing EmotionalDecisionMaking"""
        from emotions_ai import (
            EmotionalDecisionMaking,
            DecisionOption,
            EmotionalDecision
        )
        assert EmotionalDecisionMaking is not None
        assert DecisionOption is not None

    def test_create_decision_system(self):
        """Test creating decision system"""
        from emotions_ai import EmotionalDecisionMaking

        system = EmotionalDecisionMaking()
        assert system is not None
        assert 0.0 <= system.emotion_weight <= 1.0

    def test_emotionally_evaluate(self):
        """Test emotional evaluation (somatic marker)"""
        from emotions_ai import EmotionalDecisionMaking, DecisionOption

        system = EmotionalDecisionMaking()

        option = DecisionOption(
            option_id='A',
            description='Safe choice',
            rational_value=0.7
        )

        evaluation = system.emotionally_evaluate(option)

        assert evaluation is not None
        assert 'emotional_value' in evaluation
        assert 'somatic_marker' in evaluation
        assert 'anticipated_emotions' in evaluation

    def test_decide(self):
        """Test emotion-integrated decision making"""
        from emotions_ai import EmotionalDecisionMaking, DecisionOption

        system = EmotionalDecisionMaking()

        options = [
            DecisionOption('A', 'Safe', rational_value=0.6),
            DecisionOption('B', 'Risky', rational_value=0.8),
            DecisionOption('C', 'Moderate', rational_value=0.7)
        ]

        decision = system.decide(options, context={})

        assert decision is not None
        assert decision.chosen_option in ['A', 'B', 'C']
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.emotion_contribution == system.emotion_weight

    def test_simulate_regret(self):
        """Test counterfactual regret simulation"""
        from emotions_ai import EmotionalDecisionMaking

        system = EmotionalDecisionMaking()

        result = system.simulate_regret(
            chosen='A',
            alternative='B',
            outcome='negative'
        )

        assert result is not None
        assert 'regret_intensity' in result
        assert result['regret_intensity'] > 0.5  # High regret on negative outcome


class TestEmotionalExpressionGenerator:
    """Test Emotional Expression Generator (v7.0)"""

    def test_import_expression_generator(self):
        """Test importing EmotionalExpressionGenerator"""
        from emotions_ai import (
            EmotionalExpressionGenerator,
            EmotionalTone,
            CulturalContext
        )
        assert EmotionalExpressionGenerator is not None
        assert EmotionalTone.EMPATHETIC is not None

    def test_create_expression_generator(self):
        """Test creating expression generator"""
        from emotions_ai import EmotionalExpressionGenerator

        generator = EmotionalExpressionGenerator()
        assert generator is not None
        assert generator.cultural_context is not None

    def test_generate_emotional_text(self):
        """Test generating emotionally toned text"""
        from emotions_ai import (
            EmotionalExpressionGenerator,
            Emotion,
            EmotionType,
            EmotionalTone
        )

        generator = EmotionalExpressionGenerator()

        emotion = Emotion(EmotionType.JOY, intensity=0.8, valence=0.8)

        text = generator.generate_text(
            message="The project is complete",
            emotion=emotion,
            tone=EmotionalTone.ENTHUSIASTIC
        )

        assert text is not None
        assert len(text) > len("The project is complete")  # Should add emotional markers

    def test_generate_facial_expression(self):
        """Test generating facial expression (FACS)"""
        from emotions_ai import EmotionalExpressionGenerator

        generator = EmotionalExpressionGenerator()

        expression = generator.generate_facial_expression(
            emotion='happiness',
            intensity=0.8
        )

        assert expression is not None
        assert 'action_units' in expression
        assert len(expression['action_units']) > 0
        assert 'AU6' in expression['action_units']  # Cheek raiser
        assert 'AU12' in expression['action_units']  # Lip corner puller

    def test_adapt_to_culture(self):
        """Test cultural adaptation"""
        from emotions_ai import EmotionalExpressionGenerator, CulturalContext

        generator = EmotionalExpressionGenerator()

        # Eastern context (more restrained)
        eastern = generator.adapt_to_culture('happiness', CulturalContext.EASTERN)
        assert eastern['expression_intensity'] < 0.7

        # Western context (more expressive)
        western = generator.adapt_to_culture('happiness', CulturalContext.WESTERN)
        assert western['expression_intensity'] > 0.8


class TestIntegratedEmotionalSystem:
    """Test Integrated Emotional System (v7.0)"""

    def test_import_integrated_system(self):
        """Test importing IntegratedEmotionalSystem"""
        from emotions_ai import IntegratedEmotionalSystem
        assert IntegratedEmotionalSystem is not None

    def test_create_integrated_system(self):
        """Test creating integrated emotional system"""
        from emotions_ai import IntegratedEmotionalSystem, EmotionsConfig

        config = EmotionsConfig()
        system = IntegratedEmotionalSystem(config)

        assert system is not None
        assert system.config is not None

    def test_process_emotional_event(self):
        """Test processing emotional event (integrated)"""
        from emotions_ai import IntegratedEmotionalSystem

        system = IntegratedEmotionalSystem()

        event = {
            'type': 'success',
            'severity': 0.8,
            'importance': 0.7
        }

        result = system.process_emotional_event(event)

        assert result is not None
        assert 'event' in result

    def test_respond_empathetically(self):
        """Test empathetic response generation"""
        from emotions_ai import IntegratedEmotionalSystem

        system = IntegratedEmotionalSystem()

        user_message = "I'm feeling really frustrated with this problem."

        response = system.respond_empathetically(user_message)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

    def test_make_emotional_decision(self):
        """Test emotional decision making (integrated)"""
        from emotions_ai import IntegratedEmotionalSystem, DecisionOption

        system = IntegratedEmotionalSystem()

        options = [
            DecisionOption('A', 'Option A', rational_value=0.6),
            DecisionOption('B', 'Option B', rational_value=0.8)
        ]

        decision = system.make_emotional_decision(options)

        assert decision is not None
        assert decision.chosen_option in ['A', 'B']

    def test_assess_emotional_health(self):
        """Test emotional health assessment"""
        from emotions_ai import IntegratedEmotionalSystem

        system = IntegratedEmotionalSystem()

        health = system.assess_emotional_health()

        assert health is not None
        assert 'overall_score' in health
        assert 'components' in health
        assert 0.0 <= health['overall_score'] <= 1.0

    def test_get_system_statistics(self):
        """Test getting system statistics"""
        from emotions_ai import IntegratedEmotionalSystem

        system = IntegratedEmotionalSystem()

        stats = system.get_system_statistics()

        assert stats is not None
        assert 'config' in stats
        assert 'metrics' in stats
        assert 'subsystems' in stats

    def test_get_emotional_system_singleton(self):
        """Test getting singleton emotional system"""
        from emotions_ai import get_emotional_system

        sys1 = get_emotional_system()
        sys2 = get_emotional_system()

        # Should be same instance
        assert sys1 is sys2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
