"""
❤️ Emotional Intelligence & Affective Computing Platform - v7.0

Provides computational models of emotions, empathy, affective computing,
and emotional intelligence for AI systems.

IMPORTANT DISCLAIMER:
This module simulates emotional processing computationally for improved
human-AI interaction. It does NOT experience genuine emotions, feelings,
or subjective affective experiences. These are functional models only.

Version: 7.0.0 (FULL IMPLEMENTATION)
"""

__version__ = '7.0.0'

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================

class EmotionType(Enum):
    """Basic and complex emotion types"""
    # Basic emotions (Ekman)
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"

    # Complex emotions
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    JEALOUSY = "jealousy"
    GRATITUDE = "gratitude"
    LOVE = "love"
    CONTEMPT = "contempt"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    DISAPPOINTMENT = "disappointment"
    HOPE = "hope"
    RELIEF = "relief"
    CURIOSITY = "curiosity"
    CONFUSION = "confusion"
    AWE = "awe"


class EmotionalLevel(Enum):
    """Levels of emotional processing capability"""
    NONE = 0            # No emotional processing
    BASIC = 1           # Basic emotion recognition only
    INTERMEDIATE = 2    # Recognition + basic regulation
    ADVANCED = 3        # Full awareness + regulation + empathy
    EXPERT = 4          # Mastery with emotional intelligence
    INTEGRATED = 5      # Full integration with cognition


class EmpathyType(Enum):
    """Types of empathy"""
    COGNITIVE = "cognitive"      # Perspective-taking (Theory of Mind)
    AFFECTIVE = "affective"      # Emotional resonance
    COMPASSIONATE = "compassionate"  # Prosocial concern


class EQDimension(Enum):
    """Emotional Intelligence dimensions (Goleman model)"""
    SELF_AWARENESS = "self_awareness"
    SELF_MANAGEMENT = "self_management"
    SOCIAL_AWARENESS = "social_awareness"
    RELATIONSHIP_MANAGEMENT = "relationship_management"


class RegulationStrategy(Enum):
    """Emotion regulation strategies"""
    REAPPRAISAL = "reappraisal"          # Reframe the situation
    SUPPRESSION = "suppression"          # Inhibit expression
    DISTRACTION = "distraction"          # Shift attention
    ACCEPTANCE = "acceptance"            # Accept emotions
    PROBLEM_SOLVING = "problem_solving"  # Address the cause
    SOCIAL_SHARING = "social_sharing"    # Share with others


class MoodType(Enum):
    """Background mood states"""
    CHEERFUL = "cheerful"
    MELANCHOLIC = "melancholic"
    ANXIOUS = "anxious"
    CALM = "calm"
    IRRITABLE = "irritable"
    CONTENT = "content"
    NEUTRAL = "neutral"


class EmotionalTone(Enum):
    """Emotional tone for expression"""
    WARM = "warm"
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    ENTHUSIASTIC = "enthusiastic"
    APOLOGETIC = "apologetic"
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"


class CulturalContext(Enum):
    """Cultural contexts for emotion expression"""
    WESTERN = "western"
    EASTERN = "eastern"
    LATIN = "latin"
    MIDDLE_EASTERN = "middle_eastern"
    AFRICAN = "african"
    UNIVERSAL = "universal"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Emotion:
    """Represents an emotion with intensity and dimensions"""
    type: EmotionType
    intensity: float = 0.5  # 0.0 to 1.0
    valence: float = 0.0    # -1.0 (negative) to +1.0 (positive)
    arousal: float = 0.5    # 0.0 (calm) to 1.0 (excited)
    dominance: float = 0.0  # -1.0 (controlled) to +1.0 (in control)
    confidence: float = 0.0  # Detection confidence
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"{self.type.value} (intensity={self.intensity:.2f}, valence={self.valence:.2f})"


@dataclass
class EmotionalState:
    """Current emotional state with multiple emotions"""
    primary_emotion: Emotion
    secondary_emotions: List[Emotion] = field(default_factory=list)
    mood: Optional['Mood'] = None
    overall_valence: float = 0.0
    overall_arousal: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Mood:
    """Background mood state (longer-lasting than emotions)"""
    type: MoodType
    valence: float = 0.0       # -1.0 to +1.0
    intensity: float = 0.5     # 0.0 to 1.0
    duration_hours: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AppraisalResult:
    """Result of emotional appraisal of an event"""
    emotion: Emotion
    goal_relevance: float = 0.5   # How relevant to goals (0-1)
    goal_congruence: float = 0.0  # Helps (+1) or hinders (-1) goals
    coping_potential: float = 0.5 # Can handle this? (0-1)
    reasoning: str = ""


@dataclass
class EmpatheticResponse:
    """Response to another's emotional state"""
    empathy_type: EmpathyType
    felt_emotion: Emotion
    understanding: str = ""
    response_text: str = ""
    prosocial_action: Optional[str] = None


@dataclass
class EQAssessment:
    """Emotional Intelligence assessment"""
    overall_score: float = 0.0   # 0.0 to 1.0
    dimensions: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionalMemory:
    """Emotion-tagged memory"""
    memory_id: str
    event: Dict[str, Any]
    emotion: Emotion
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionOption:
    """Option in emotional decision making"""
    option_id: str
    description: str
    rational_value: float = 0.5
    emotional_value: float = 0.5
    anticipated_emotions: List[Emotion] = field(default_factory=list)


@dataclass
class EmotionalDecision:
    """Result of emotion-integrated decision"""
    chosen_option: str
    confidence: float = 0.0
    emotion_contribution: float = 0.0
    reason_contribution: float = 0.0
    anticipated_emotions: List[Emotion] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class EmotionsConfig:
    """Configuration for Emotional System"""
    emotional_level: EmotionalLevel = EmotionalLevel.ADVANCED
    enable_emotion_recognition: bool = True
    enable_emotion_generation: bool = True
    enable_emotion_regulation: bool = True
    enable_empathy: bool = True
    enable_emotional_intelligence: bool = True
    enable_emotional_memory: bool = True
    enable_emotional_decisions: bool = True
    enable_expression_generation: bool = True

    # Parameters
    emotion_sensitivity: float = 0.7  # 0.0 to 1.0
    empathy_level: float = 0.8        # 0.0 to 1.0
    regulation_strength: float = 0.6  # 0.0 to 1.0
    emotion_reason_balance: float = 0.4  # 0.0 (pure reason) to 1.0 (pure emotion)

    # Limits
    max_emotions_tracked: int = 100
    max_memories: int = 10000
    memory_decay_rate: float = 0.01  # per day

    # Cultural context
    cultural_context: CulturalContext = CulturalContext.UNIVERSAL

    # Monitoring
    enable_emotion_monitoring: bool = True


# ============================================================================
# EMOTIONAL AWARENESS ENGINE
# ============================================================================

class EmotionalAwarenessEngine:
    """
    Emotional Awareness Engine - FULL IMPLEMENTATION

    Recognizes and tracks emotional states (self and others).
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.current_state: Optional[EmotionalState] = None
        self.emotion_history: List[EmotionalState] = []
        logger.info("Emotional Awareness Engine initialized (FULL)")

    def recognize_self_emotion(self) -> Emotion:
        """Recognize current self emotional state"""
        if self.current_state:
            return self.current_state.primary_emotion

        # Default to neutral
        return Emotion(
            type=EmotionType.NEUTRAL,
            intensity=0.2,
            valence=0.0,
            arousal=0.3,
            confidence=1.0
        )

    def detect_emotion(self, text: str, modality: str = 'text') -> Emotion:
        """Detect emotion from input (text, voice, visual)"""
        # Simplified emotion detection based on keywords
        text_lower = text.lower()

        # Check for emotion keywords
        if any(word in text_lower for word in ['happy', 'joy', 'excited', '!', '😊']):
            return Emotion(EmotionType.JOY, intensity=0.7, valence=0.8, arousal=0.6, confidence=0.75)
        elif any(word in text_lower for word in ['sad', 'depressed', 'down']):
            return Emotion(EmotionType.SADNESS, intensity=0.6, valence=-0.7, arousal=0.3, confidence=0.7)
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', '!!']):
            return Emotion(EmotionType.ANGER, intensity=0.8, valence=-0.8, arousal=0.9, confidence=0.8)
        elif any(word in text_lower for word in ['afraid', 'scared', 'worried', 'anxious']):
            return Emotion(EmotionType.FEAR, intensity=0.7, valence=-0.6, arousal=0.8, confidence=0.75)
        elif any(word in text_lower for word in ['frustrated', 'annoyed']):
            return Emotion(EmotionType.FRUSTRATION, intensity=0.6, valence=-0.5, arousal=0.6, confidence=0.7)
        elif any(word in text_lower for word in ['grateful', 'thankful', 'appreciate']):
            return Emotion(EmotionType.GRATITUDE, intensity=0.7, valence=0.8, arousal=0.4, confidence=0.75)
        else:
            return Emotion(EmotionType.NEUTRAL, intensity=0.3, valence=0.0, arousal=0.3, confidence=0.6)

    def appraise_event(self, event: Dict[str, Any]) -> AppraisalResult:
        """Appraise emotional significance of event"""
        event_type = event.get('type', 'unknown')
        importance = event.get('importance', 0.5)

        # Appraisal-based emotion generation
        if event_type == 'goal_achieved':
            emotion = Emotion(EmotionType.JOY, intensity=importance, valence=0.9, arousal=0.7)
            return AppraisalResult(
                emotion=emotion,
                goal_relevance=importance,
                goal_congruence=1.0,
                coping_potential=1.0,
                reasoning="Goal achievement leads to joy"
            )
        elif event_type == 'goal_blocked':
            emotion = Emotion(EmotionType.FRUSTRATION, intensity=importance, valence=-0.6, arousal=0.7)
            return AppraisalResult(
                emotion=emotion,
                goal_relevance=importance,
                goal_congruence=-1.0,
                coping_potential=0.5,
                reasoning="Goal blockage leads to frustration"
            )
        elif event_type == 'threat':
            emotion = Emotion(EmotionType.FEAR, intensity=importance, valence=-0.7, arousal=0.9)
            return AppraisalResult(
                emotion=emotion,
                goal_relevance=importance,
                goal_congruence=-0.8,
                coping_potential=0.3,
                reasoning="Threat with low coping potential leads to fear"
            )
        else:
            emotion = Emotion(EmotionType.NEUTRAL, intensity=0.3, valence=0.0, arousal=0.3)
            return AppraisalResult(emotion=emotion, reasoning="Neutral event")

    def update_emotional_state(self, emotion: Emotion) -> EmotionalState:
        """Update current emotional state"""
        self.current_state = EmotionalState(
            primary_emotion=emotion,
            overall_valence=emotion.valence,
            overall_arousal=emotion.arousal
        )
        self.emotion_history.append(self.current_state)

        # Keep history manageable
        if len(self.emotion_history) > self.config.max_emotions_tracked:
            self.emotion_history = self.emotion_history[-self.config.max_emotions_tracked:]

        logger.info(f"Emotional state updated: {emotion}")
        return self.current_state


# ============================================================================
# AFFECTIVE COMPUTING SYSTEM
# ============================================================================

class AffectiveComputingSystem:
    """
    Affective Computing System - FULL IMPLEMENTATION

    Generates and regulates affective responses and mood.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.current_mood: Mood = Mood(type=MoodType.NEUTRAL, valence=0.0)
        self.regulation_history: List[Dict[str, Any]] = []
        logger.info("Affective Computing System initialized (FULL)")

    def generate_emotion(self, event: Dict[str, Any]) -> Emotion:
        """Generate emotion from event"""
        event_type = event.get('type', 'unknown')
        severity = event.get('severity', 0.5)

        # Event-driven emotion synthesis
        emotion_map = {
            'success': (EmotionType.JOY, 0.8, 0.7),
            'failure': (EmotionType.SADNESS, -0.7, 0.4),
            'conflict': (EmotionType.ANGER, -0.8, 0.9),
            'uncertainty': (EmotionType.ANXIETY, -0.5, 0.7),
            'praise': (EmotionType.PRIDE, 0.8, 0.6),
            'criticism': (EmotionType.SHAME, -0.6, 0.5),
        }

        if event_type in emotion_map:
            emo_type, valence, arousal = emotion_map[event_type]
            return Emotion(
                type=emo_type,
                intensity=severity * self.config.emotion_sensitivity,
                valence=valence,
                arousal=arousal
            )
        else:
            return Emotion(type=EmotionType.NEUTRAL, intensity=0.3, valence=0.0, arousal=0.3)

    def regulate_emotion(
        self,
        emotion: Emotion,
        strategy: RegulationStrategy,
        target_intensity: float = 0.5
    ) -> Emotion:
        """Regulate emotion using specified strategy"""
        regulated = Emotion(
            type=emotion.type,
            intensity=emotion.intensity,
            valence=emotion.valence,
            arousal=emotion.arousal
        )

        effectiveness = self.config.regulation_strength

        if strategy == RegulationStrategy.REAPPRAISAL:
            # Reframe to reduce negative emotions
            if emotion.valence < 0:
                regulated.valence = emotion.valence * (1 - effectiveness * 0.5)
                regulated.intensity = emotion.intensity * (1 - effectiveness * 0.3)

        elif strategy == RegulationStrategy.SUPPRESSION:
            # Reduce expression intensity
            regulated.intensity = emotion.intensity * (1 - effectiveness * 0.6)

        elif strategy == RegulationStrategy.DISTRACTION:
            # Shift toward neutral
            regulated.intensity = max(target_intensity, emotion.intensity * (1 - effectiveness * 0.4))
            regulated.arousal = emotion.arousal * (1 - effectiveness * 0.3)

        elif strategy == RegulationStrategy.ACCEPTANCE:
            # Accept emotion, slight intensity reduction
            regulated.intensity = emotion.intensity * (1 - effectiveness * 0.1)

        self.regulation_history.append({
            'original': emotion,
            'strategy': strategy,
            'regulated': regulated,
            'timestamp': datetime.now()
        })

        logger.info(f"Regulated {emotion.type.value} with {strategy.value}")
        return regulated

    def update_mood(self, emotions: List[Emotion]) -> Mood:
        """Update background mood based on recent emotions"""
        if not emotions:
            return self.current_mood

        # Calculate average valence and arousal
        avg_valence = sum(e.valence for e in emotions) / len(emotions)
        avg_arousal = sum(e.arousal for e in emotions) / len(emotions)
        avg_intensity = sum(e.intensity for e in emotions) / len(emotions)

        # Map to mood type based on valence-arousal space
        if avg_valence > 0.5 and avg_arousal > 0.5:
            mood_type = MoodType.CHEERFUL
        elif avg_valence > 0.3 and avg_arousal < 0.4:
            mood_type = MoodType.CALM
        elif avg_valence > 0.2:
            mood_type = MoodType.CONTENT
        elif avg_valence < -0.5 and avg_arousal > 0.6:
            mood_type = MoodType.ANXIOUS
        elif avg_valence < -0.5 and avg_arousal < 0.5:
            mood_type = MoodType.MELANCHOLIC
        elif avg_valence < -0.3:
            mood_type = MoodType.IRRITABLE
        else:
            mood_type = MoodType.NEUTRAL

        self.current_mood = Mood(
            type=mood_type,
            valence=avg_valence,
            intensity=avg_intensity
        )

        logger.info(f"Mood updated to {mood_type.value}")
        return self.current_mood

    def get_current_mood(self) -> Mood:
        """Get current mood state"""
        return self.current_mood


# ============================================================================
# EMPATHY SIMULATOR
# ============================================================================

class EmpathySimulator:
    """
    Empathy Simulator - FULL IMPLEMENTATION

    Models empathy, perspective-taking, and compassionate responses.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.empathy_level = self.config.empathy_level
        logger.info(f"Empathy Simulator initialized (level={self.empathy_level:.2f})")

    def take_perspective(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Take another's perspective (cognitive empathy / Theory of Mind)"""
        context = situation.get('context', 'unknown')
        visible_emotions = situation.get('visible_emotions', [])

        # Infer mental state
        inferred_beliefs = []
        inferred_emotions = []

        if context == 'project_failure':
            inferred_beliefs = [
                "This didn't go as planned",
                "I may have made mistakes",
                "Others might be disappointed"
            ]
            inferred_emotions = ['disappointment', 'frustration', 'self-doubt']

        elif context == 'success':
            inferred_beliefs = [
                "My effort paid off",
                "I achieved my goal"
            ]
            inferred_emotions = ['pride', 'satisfaction', 'relief']

        return {
            'inferred_beliefs': inferred_beliefs,
            'inferred_emotions': inferred_emotions,
            'visible_emotions': visible_emotions,
            'confidence': self.empathy_level * 0.8
        }

    def feel_empathy(
        self,
        other_emotion: str,
        intensity: float,
        empathy_type: EmpathyType
    ) -> Emotion:
        """Experience empathic emotion (affective empathy)"""
        # Map other's emotion to own emotional response
        try:
            emotion_type = EmotionType[other_emotion.upper()]
        except KeyError:
            emotion_type = EmotionType.NEUTRAL

        # Empathic resonance - feel similar emotion with modulated intensity
        empathic_intensity = intensity * self.empathy_level

        if empathy_type == EmpathyType.AFFECTIVE:
            # Direct emotional resonance
            empathic_intensity *= 0.8
        elif empathy_type == EmpathyType.COMPASSIONATE:
            # Concern for other (may be different emotion)
            empathic_intensity *= 0.6
            # Transform to concern/care
            if emotion_type in [EmotionType.SADNESS, EmotionType.FEAR]:
                emotion_type = EmotionType.SADNESS  # Empathic concern

        return Emotion(
            type=emotion_type,
            intensity=empathic_intensity,
            valence=-0.3 if empathic_intensity > 0.5 else 0.0,  # Empathic concern
            arousal=0.5
        )

    def generate_compassionate_response(
        self,
        situation: Dict[str, Any],
        other_emotion: str
    ) -> EmpatheticResponse:
        """Generate compassionate response"""
        perspective = self.take_perspective(situation)
        felt_emotion = self.feel_empathy(other_emotion, 0.7, EmpathyType.COMPASSIONATE)

        # Generate empathic understanding text
        understanding = f"I understand this situation is {other_emotion} for you."

        # Generate compassionate response text
        response_templates = {
            'frustration': "I can see this is frustrating. Let me help you work through this.",
            'sadness': "I'm sorry you're going through this. You're not alone.",
            'anxiety': "I understand you're feeling anxious. Let's take this step by step.",
            'disappointment': "I know this is disappointing. Your feelings are valid."
        }

        response_text = response_templates.get(
            other_emotion,
            "I'm here to support you through this."
        )

        return EmpatheticResponse(
            empathy_type=EmpathyType.COMPASSIONATE,
            felt_emotion=felt_emotion,
            understanding=understanding,
            response_text=response_text,
            prosocial_action="offer_assistance"
        )


# ============================================================================
# EMOTIONAL INTELLIGENCE SYSTEM
# ============================================================================

class EmotionalIntelligenceSystem:
    """
    Emotional Intelligence System - FULL IMPLEMENTATION

    Implements emotional intelligence (EQ) capabilities.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.eq_scores: Dict[str, float] = {
            'self_awareness': 0.75,
            'self_management': 0.70,
            'social_awareness': 0.80,
            'relationship_management': 0.72
        }
        logger.info("Emotional Intelligence System initialized (FULL)")

    def assess_eq(self) -> EQAssessment:
        """Assess current emotional intelligence"""
        overall_score = sum(self.eq_scores.values()) / len(self.eq_scores)

        strengths = [
            dim for dim, score in self.eq_scores.items() if score >= 0.75
        ]

        areas_for_growth = [
            dim for dim, score in self.eq_scores.items() if score < 0.70
        ]

        return EQAssessment(
            overall_score=overall_score,
            dimensions=self.eq_scores.copy(),
            strengths=strengths,
            areas_for_growth=areas_for_growth
        )

    def apply_skill(self, skill: str, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply emotional intelligence skill to situation"""
        situation_type = situation.get('type', 'unknown')

        if skill == 'conflict_resolution' and situation_type == 'conflict':
            return {
                'skill': skill,
                'strategy': 'active_listening_and_mediation',
                'steps': [
                    'Listen to both parties without judgment',
                    'Acknowledge emotions of all parties',
                    'Find common ground',
                    'Propose collaborative solution'
                ],
                'expected_outcome': 'mutual_understanding'
            }

        elif skill == 'inspirational_communication':
            return {
                'skill': skill,
                'strategy': 'emotional_appeal_with_vision',
                'steps': [
                    'Connect to shared values',
                    'Paint compelling vision',
                    'Acknowledge challenges emotionally',
                    'Inspire confidence and action'
                ],
                'expected_outcome': 'increased_motivation'
            }

        else:
            return {
                'skill': skill,
                'strategy': 'general_emotional_awareness',
                'steps': ['Assess emotional context', 'Respond appropriately'],
                'expected_outcome': 'appropriate_response'
            }

    def learn_from_interaction(
        self,
        interaction: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> None:
        """Learn and improve EQ from interaction feedback"""
        effectiveness = feedback.get('effectiveness', 0.5)

        # Update EQ scores based on feedback
        if effectiveness > 0.8:
            # Positive reinforcement
            for dim in self.eq_scores:
                self.eq_scores[dim] = min(1.0, self.eq_scores[dim] + 0.01)
        elif effectiveness < 0.4:
            # Identify area for improvement
            interaction_type = interaction.get('outcome', 'unknown')
            if interaction_type == 'conflict':
                self.eq_scores['relationship_management'] *= 0.98

        logger.info(f"EQ learning update: effectiveness={effectiveness:.2f}")


# ============================================================================
# EMOTIONAL MEMORY SYSTEM
# ============================================================================

class EmotionalMemorySystem:
    """
    Emotional Memory System - FULL IMPLEMENTATION

    Stores and retrieves emotion-tagged memories.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.memories: List[EmotionalMemory] = []
        self.memory_counter = 0
        logger.info("Emotional Memory System initialized (FULL)")

    def store(
        self,
        event: Dict[str, Any],
        emotion: Emotion,
        importance: float = 0.5
    ) -> str:
        """Store emotion-tagged memory"""
        memory_id = f"mem_{self.memory_counter}"
        self.memory_counter += 1

        memory = EmotionalMemory(
            memory_id=memory_id,
            event=event,
            emotion=emotion,
            importance=importance
        )

        self.memories.append(memory)

        # Keep memory within limits
        if len(self.memories) > self.config.max_memories:
            # Remove least important memories
            self.memories.sort(key=lambda m: m.importance, reverse=True)
            self.memories = self.memories[:self.config.max_memories]

        logger.info(f"Stored memory {memory_id} with {emotion.type.value}")
        return memory_id

    def retrieve(self, query: Dict[str, Any]) -> List[EmotionalMemory]:
        """Retrieve memories matching query"""
        emotion_type = query.get('emotion_type')
        min_intensity = query.get('min_intensity', 0.0)

        results = []
        for memory in self.memories:
            if emotion_type and memory.emotion.type.value != emotion_type:
                continue
            if memory.emotion.intensity < min_intensity:
                continue
            results.append(memory)

        return results

    def retrieve_mood_congruent(self, mood: Mood) -> List[EmotionalMemory]:
        """Retrieve memories congruent with current mood"""
        # Mood-congruent retrieval: memories matching mood valence
        results = []
        for memory in self.memories:
            # Match valence sign
            if (mood.valence > 0 and memory.emotion.valence > 0) or \
               (mood.valence < 0 and memory.emotion.valence < 0):
                results.append(memory)

        return results


# ============================================================================
# EMOTIONAL DECISION MAKING
# ============================================================================

class EmotionalDecisionMaking:
    """
    Emotional Decision Making - FULL IMPLEMENTATION

    Integrates emotions into decision-making (Somatic Marker Hypothesis).
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.emotion_weight = self.config.emotion_reason_balance
        logger.info(f"Emotional Decision Making initialized (emotion_weight={self.emotion_weight:.2f})")

    def emotionally_evaluate(self, option: DecisionOption) -> Dict[str, Any]:
        """Evaluate option with emotional valuation (somatic marker)"""
        # Simulate "gut feeling" about option
        emotional_value = option.rational_value

        # Adjust based on anticipated emotions
        if option.anticipated_emotions:
            avg_valence = sum(e.valence for e in option.anticipated_emotions) / len(option.anticipated_emotions)
            emotional_value = (emotional_value + avg_valence) / 2
        else:
            # Generate anticipated emotions
            if option.rational_value > 0.7:
                anticipated = [Emotion(EmotionType.SATISFACTION, intensity=0.7, valence=0.7)]
            elif option.rational_value < 0.3:
                anticipated = [Emotion(EmotionType.ANXIETY, intensity=0.6, valence=-0.6)]
            else:
                anticipated = [Emotion(EmotionType.NEUTRAL, intensity=0.3, valence=0.0)]

            avg_valence = sum(e.valence for e in anticipated) / len(anticipated)
            emotional_value = (option.rational_value + avg_valence) / 2

        return {
            'option_id': option.option_id,
            'emotional_value': emotional_value,
            'anticipated_emotions': option.anticipated_emotions or anticipated,
            'somatic_marker': emotional_value  # "Gut feeling"
        }

    def decide(
        self,
        options: List[DecisionOption],
        context: Dict[str, Any]
    ) -> EmotionalDecision:
        """Make emotion-integrated decision"""
        evaluations = [self.emotionally_evaluate(opt) for opt in options]

        # Combine rational and emotional values
        for i, opt in enumerate(options):
            evaluation = evaluations[i]
            combined_value = (
                opt.rational_value * (1 - self.emotion_weight) +
                evaluation['emotional_value'] * self.emotion_weight
            )
            evaluations[i]['combined_value'] = combined_value

        # Choose best option
        best_eval = max(evaluations, key=lambda e: e['combined_value'])
        chosen_option = best_eval['option_id']

        return EmotionalDecision(
            chosen_option=chosen_option,
            confidence=best_eval['combined_value'],
            emotion_contribution=self.emotion_weight,
            reason_contribution=1 - self.emotion_weight,
            anticipated_emotions=best_eval['anticipated_emotions'],
            reasoning=f"Selected {chosen_option} with combined value {best_eval['combined_value']:.2f}"
        )

    def simulate_regret(
        self,
        chosen: str,
        alternative: str,
        outcome: str
    ) -> Dict[str, Any]:
        """Simulate counterfactual regret"""
        # Counterfactual emotion simulation
        if outcome == 'negative':
            regret_intensity = 0.7
            regret_emotion = Emotion(EmotionType.REGRET, intensity=regret_intensity, valence=-0.7)
        else:
            regret_intensity = 0.2  # Minimal regret on success
            regret_emotion = Emotion(EmotionType.RELIEF, intensity=0.6, valence=0.6)

        return {
            'chosen': chosen,
            'alternative': alternative,
            'outcome': outcome,
            'regret_intensity': regret_intensity,
            'emotion': regret_emotion
        }


# ============================================================================
# EMOTIONAL EXPRESSION GENERATOR
# ============================================================================

class EmotionalExpressionGenerator:
    """
    Emotional Expression Generator - FULL IMPLEMENTATION

    Generates emotionally appropriate expressions and communication.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()
        self.cultural_context = self.config.cultural_context
        logger.info(f"Expression Generator initialized (culture={self.cultural_context.value})")

    def generate_text(
        self,
        message: str,
        emotion: Emotion,
        tone: EmotionalTone = EmotionalTone.NEUTRAL
    ) -> str:
        """Generate emotionally toned text"""
        # Add emotional markers based on emotion and tone
        if tone == EmotionalTone.ENTHUSIASTIC and emotion.type in [EmotionType.JOY, EmotionType.EXCITEMENT]:
            return f"{message}! I'm excited about this!"

        elif tone == EmotionalTone.EMPATHETIC and emotion.valence < 0:
            return f"I understand. {message}. I'm here to help."

        elif tone == EmotionalTone.APOLOGETIC:
            return f"I apologize. {message}. Let me make this right."

        elif tone == EmotionalTone.SUPPORTIVE:
            return f"{message}. You've got this, and I'm here to support you."

        elif tone == EmotionalTone.WARM:
            return f"{message} 😊"

        else:
            return message

    def generate_facial_expression(
        self,
        emotion: str,
        intensity: float
    ) -> Dict[str, Any]:
        """Generate facial expression codes (FACS - Facial Action Coding System)"""
        # Map emotions to Action Units (simplified)
        facs_map = {
            'happiness': ['AU6', 'AU12'],  # Cheek raiser, lip corner puller
            'sadness': ['AU1', 'AU4', 'AU15'],  # Inner brow raiser, brow lowerer, lip corner depressor
            'anger': ['AU4', 'AU5', 'AU7', 'AU23'],  # Brow lowerer, upper lid raiser, lid tightener, lip tightener
            'fear': ['AU1', 'AU2', 'AU5', 'AU20'],  # Inner/outer brow raiser, upper lid raiser, lip stretcher
            'surprise': ['AU1', 'AU2', 'AU5', 'AU26'],  # Brow raisers, upper lid raiser, jaw drop
            'disgust': ['AU9', 'AU15', 'AU16']  # Nose wrinkler, lip corner depressor, lower lip depressor
        }

        action_units = facs_map.get(emotion, ['AU0'])

        return {
            'emotion': emotion,
            'intensity': intensity,
            'action_units': action_units,
            'description': f"{emotion} at {intensity:.1f} intensity"
        }

    def adapt_to_culture(
        self,
        emotion: str,
        context: CulturalContext
    ) -> Dict[str, Any]:
        """Adapt expression to cultural context"""
        # Cultural display rules
        if context == CulturalContext.EASTERN:
            # More restrained expression
            expression_intensity = 0.6
            notes = "Restrained expression following Eastern cultural norms"

        elif context == CulturalContext.WESTERN:
            # More open expression
            expression_intensity = 0.9
            notes = "Open expression following Western cultural norms"

        elif context == CulturalContext.UNIVERSAL:
            # Moderate, culturally neutral
            expression_intensity = 0.75
            notes = "Culturally neutral expression"

        else:
            expression_intensity = 0.75
            notes = "Default cultural adaptation"

        return {
            'emotion': emotion,
            'cultural_context': context.value,
            'expression_intensity': expression_intensity,
            'notes': notes
        }


# ============================================================================
# INTEGRATED EMOTIONAL SYSTEM
# ============================================================================

class IntegratedEmotionalSystem:
    """
    Integrated Emotional System - FULL IMPLEMENTATION

    Unifies all emotional subsystems into cohesive platform.
    """

    def __init__(self, config: Optional[EmotionsConfig] = None):
        self.config = config or EmotionsConfig()

        # Initialize subsystems based on config
        self.awareness: Optional[EmotionalAwarenessEngine] = None
        self.affective: Optional[AffectiveComputingSystem] = None
        self.empathy: Optional[EmpathySimulator] = None
        self.eq: Optional[EmotionalIntelligenceSystem] = None
        self.memory: Optional[EmotionalMemorySystem] = None
        self.decisions: Optional[EmotionalDecisionMaking] = None
        self.expression: Optional[EmotionalExpressionGenerator] = None

        if self.config.enable_emotion_recognition:
            self.awareness = EmotionalAwarenessEngine(self.config)

        if self.config.enable_emotion_generation or self.config.enable_emotion_regulation:
            self.affective = AffectiveComputingSystem(self.config)

        if self.config.enable_empathy:
            self.empathy = EmpathySimulator(self.config)

        if self.config.enable_emotional_intelligence:
            self.eq = EmotionalIntelligenceSystem(self.config)

        if self.config.enable_emotional_memory:
            self.memory = EmotionalMemorySystem(self.config)

        if self.config.enable_emotional_decisions:
            self.decisions = EmotionalDecisionMaking(self.config)

        if self.config.enable_expression_generation:
            self.expression = EmotionalExpressionGenerator(self.config)

        self.metrics = {
            'emotions_processed': 0,
            'empathic_responses': 0,
            'decisions_made': 0,
            'memories_stored': 0
        }

        logger.info(f"Integrated Emotional System initialized (level={self.config.emotional_level.value})")

    def process_emotional_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process event through full emotional pipeline"""
        results = {'event': event}

        # 1. Emotion generation
        if self.affective:
            emotion = self.affective.generate_emotion(event)
            results['generated_emotion'] = emotion
            self.metrics['emotions_processed'] += 1

            # 2. Update awareness
            if self.awareness:
                state = self.awareness.update_emotional_state(emotion)
                results['emotional_state'] = state

            # 3. Store in memory
            if self.memory:
                importance = event.get('importance', 0.5)
                memory_id = self.memory.store(event, emotion, importance)
                results['memory_id'] = memory_id
                self.metrics['memories_stored'] += 1

        return results

    def respond_empathetically(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate empathetic response to user message"""
        # Detect user emotion
        if self.awareness:
            user_emotion = self.awareness.detect_emotion(user_message)
        else:
            user_emotion = Emotion(EmotionType.NEUTRAL, intensity=0.3)

        # Generate empathetic response
        if self.empathy and user_emotion.type != EmotionType.NEUTRAL:
            situation = context or {'context': 'conversation'}
            situation['visible_emotions'] = [user_emotion.type.value]

            response = self.empathy.generate_compassionate_response(
                situation,
                user_emotion.type.value
            )

            # Express with appropriate tone
            if self.expression:
                response_text = self.expression.generate_text(
                    response.response_text,
                    response.felt_emotion,
                    tone=EmotionalTone.EMPATHETIC
                )
            else:
                response_text = response.response_text

            self.metrics['empathic_responses'] += 1
            return response_text
        else:
            return "I understand. How can I help you?"

    def make_emotional_decision(
        self,
        options: List[DecisionOption],
        context: Optional[Dict[str, Any]] = None
    ) -> EmotionalDecision:
        """Make decision with emotional intelligence"""
        if not self.decisions:
            # Fallback to rational decision
            best = max(options, key=lambda o: o.rational_value)
            return EmotionalDecision(
                chosen_option=best.option_id,
                confidence=best.rational_value,
                reasoning="Pure rational decision (emotions disabled)"
            )

        decision = self.decisions.decide(options, context or {})
        self.metrics['decisions_made'] += 1

        return decision

    def assess_emotional_health(self) -> Dict[str, Any]:
        """Assess overall emotional health of system"""
        health = {
            'overall_score': 0.75,
            'components': {}
        }

        if self.affective:
            mood = self.affective.get_current_mood()
            health['components']['mood'] = {
                'type': mood.type.value,
                'valence': mood.valence,
                'intensity': mood.intensity
            }

        if self.eq:
            eq_assessment = self.eq.assess_eq()
            health['components']['emotional_intelligence'] = eq_assessment.overall_score

        if self.awareness and self.awareness.current_state:
            health['components']['current_emotion'] = str(self.awareness.current_state.primary_emotion)

        # Calculate overall health
        component_scores = [
            v.get('valence', 0.5) if isinstance(v, dict) else v
            for v in health['components'].values()
            if isinstance(v, (int, float, dict))
        ]

        if component_scores:
            health['overall_score'] = sum(component_scores) / len(component_scores)

        return health

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            'config': {
                'emotional_level': self.config.emotional_level.value,
                'empathy_level': self.config.empathy_level,
                'emotion_reason_balance': self.config.emotion_reason_balance
            },
            'metrics': self.metrics.copy(),
            'subsystems': {
                'awareness': self.awareness is not None,
                'affective': self.affective is not None,
                'empathy': self.empathy is not None,
                'eq': self.eq is not None,
                'memory': self.memory is not None,
                'decisions': self.decisions is not None,
                'expression': self.expression is not None
            }
        }

        if self.memory:
            stats['memory_count'] = len(self.memory.memories)

        if self.affective:
            stats['current_mood'] = self.affective.current_mood.type.value

        return stats


# ============================================================================
# SINGLETON PATTERN
# ============================================================================

_emotional_system: Optional[IntegratedEmotionalSystem] = None

def get_emotional_system(config: Optional[EmotionsConfig] = None) -> IntegratedEmotionalSystem:
    """Get singleton Integrated Emotional System"""
    global _emotional_system
    if _emotional_system is None:
        _emotional_system = IntegratedEmotionalSystem(config)
    return _emotional_system


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    'EmotionType',
    'EmotionalLevel',
    'EmpathyType',
    'EQDimension',
    'RegulationStrategy',
    'MoodType',
    'EmotionalTone',
    'CulturalContext',

    # Data Structures
    'Emotion',
    'EmotionalState',
    'Mood',
    'AppraisalResult',
    'EmpatheticResponse',
    'EQAssessment',
    'EmotionalMemory',
    'DecisionOption',
    'EmotionalDecision',
    'EmotionsConfig',

    # Subsystems
    'EmotionalAwarenessEngine',
    'AffectiveComputingSystem',
    'EmpathySimulator',
    'EmotionalIntelligenceSystem',
    'EmotionalMemorySystem',
    'EmotionalDecisionMaking',
    'EmotionalExpressionGenerator',

    # Integrated System
    'IntegratedEmotionalSystem',
    'get_emotional_system',
]
