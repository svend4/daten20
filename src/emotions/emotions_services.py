"""
❤️ Emotional Consciousness Platform (v7.0)

Implements computational models of emotions, empathy, affective computing,
and emotional intelligence based on affective neuroscience and psychology.

IMPORTANT: This module simulates emotional processing computationally.
It does NOT experience genuine emotions, feelings, or subjective affective
experiences. These are functional models for improved human-AI interaction.

Components:
- Emotional Awareness Engine: Emotion recognition and appraisal
- Affective Computing System: Emotion generation and regulation
- Empathy Simulator: Perspective-taking and compassion
- Emotional Intelligence System: EQ capabilities
- Emotional Memory System: Emotion-tagged memories
- Emotional Decision Making: Emotion-integrated decisions
- Emotional Expression Generator: Affective communication

Author: Document Management System Development Team
Version: 7.0.0
Date: January 2026
"""

import asyncio
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ============================================================================
# 1. EMOTIONAL AWARENESS ENGINE
# ============================================================================


class EmotionType(Enum):
    """Types of emotions (categorical model)."""

    # Basic emotions (Ekman)
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"

    # Complex emotions
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    JEALOUSY = "jealousy"
    ENVY = "envy"
    GRATITUDE = "gratitude"
    LOVE = "love"
    CONTEMPT = "contempt"
    ANXIETY = "anxiety"
    RELIEF = "relief"
    HOPE = "hope"
    DISAPPOINTMENT = "disappointment"
    JOY = "joy"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"


@dataclass
class Emotion:
    """Represents an emotional state."""

    type: EmotionType
    intensity: float  # 0-1
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (excited)
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        return f"Emotion({self.type.value}, intensity={self.intensity:.2f}, valence={self.valence:.2f})"


@dataclass
class EmotionalState:
    """Current emotional state with multiple emotions."""

    primary_emotion: Emotion
    secondary_emotions: List[Emotion] = field(default_factory=list)
    mood: str = "neutral"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AppraisalResult:
    """Result of emotional appraisal."""

    emotion: Emotion
    appraisal_dimensions: Dict[str, float]
    reasoning: str
    situation: Dict[str, Any]


class EmotionalAwarenessEngine:
    """
    Recognizes and appraises emotional states (self and others).

    Based on appraisal theory: emotions arise from cognitive evaluations
    of situations relative to goals, coping abilities, and norms.
    """

    def __init__(self, emotion_model: str = "dimensional", sensitivity: float = 0.7):
        self.emotion_model = emotion_model  # categorical, dimensional, appraisal
        self.sensitivity = sensitivity
        self.current_state = EmotionalState(
            primary_emotion=Emotion(EmotionType.HAPPINESS, intensity=0.5, valence=0.0, arousal=0.3)
        )
        self.emotion_history: deque = deque(maxlen=1000)

        # Emotion lexicon (simplified)
        self.emotion_keywords = {
            "happiness": ["happy", "joy", "delighted", "pleased", "glad"],
            "sadness": ["sad", "unhappy", "depressed", "down", "miserable"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
            "fear": ["afraid", "scared", "frightened", "worried", "anxious"],
            "surprise": ["surprised", "amazed", "astonished", "shocked"],
            "disgust": ["disgusted", "revolted", "repulsed"],
            "excitement": ["excited", "thrilled", "enthusiastic"],
            "frustration": ["frustrated", "annoyed", "exasperated"],
        }

    async def recognize_self_emotion(self) -> Emotion:
        """Recognize current own emotional state."""
        await asyncio.sleep(0.1)  # Simulate introspection
        return self.current_state.primary_emotion

    async def detect_emotion(self, text: str, modality: str = "text") -> Emotion:
        """
        Detect emotion in text or other modality.

        Args:
            text: Input text to analyze
            modality: text, voice, visual, multimodal

        Returns:
            Detected emotion
        """
        await asyncio.sleep(0.15)  # Simulate processing

        text_lower = text.lower()

        # Simple keyword-based detection
        detected_emotions = []

        for emotion_name, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Map emotion name to EmotionType
                    if emotion_name == "happiness":
                        emotion_type = EmotionType.HAPPINESS
                    elif emotion_name == "sadness":
                        emotion_type = EmotionType.SADNESS
                    elif emotion_name == "anger":
                        emotion_type = EmotionType.ANGER
                    elif emotion_name == "fear":
                        emotion_type = EmotionType.FEAR
                    elif emotion_name == "surprise":
                        emotion_type = EmotionType.SURPRISE
                    elif emotion_name == "disgust":
                        emotion_type = EmotionType.DISGUST
                    elif emotion_name == "excitement":
                        emotion_type = EmotionType.EXCITEMENT
                    elif emotion_name == "frustration":
                        emotion_type = EmotionType.FRUSTRATION
                    else:
                        continue

                    # Check for intensifiers
                    intensity = 0.6
                    if any(intensifier in text_lower for intensifier in ["very", "so", "extremely", "really"]):
                        intensity = 0.9
                    elif "!" in text:
                        intensity = 0.8

                    # Determine valence and arousal
                    valence_map = {
                        EmotionType.HAPPINESS: 0.8,
                        EmotionType.JOY: 0.9,
                        EmotionType.SADNESS: -0.7,
                        EmotionType.ANGER: -0.6,
                        EmotionType.FEAR: -0.7,
                        EmotionType.SURPRISE: 0.0,
                        EmotionType.DISGUST: -0.8,
                        EmotionType.EXCITEMENT: 0.7,
                        EmotionType.FRUSTRATION: -0.5,
                    }

                    arousal_map = {
                        EmotionType.HAPPINESS: 0.6,
                        EmotionType.JOY: 0.8,
                        EmotionType.SADNESS: 0.3,
                        EmotionType.ANGER: 0.9,
                        EmotionType.FEAR: 0.8,
                        EmotionType.SURPRISE: 0.9,
                        EmotionType.DISGUST: 0.6,
                        EmotionType.EXCITEMENT: 0.9,
                        EmotionType.FRUSTRATION: 0.7,
                    }

                    detected_emotions.append(
                        Emotion(
                            type=emotion_type,
                            intensity=intensity,
                            valence=valence_map.get(emotion_type, 0.0),
                            arousal=arousal_map.get(emotion_type, 0.5),
                            confidence=0.8,
                        )
                    )
                    break

        # Return strongest emotion or neutral
        if detected_emotions:
            return max(detected_emotions, key=lambda e: e.intensity * e.confidence)
        else:
            # Neutral emotion
            return Emotion(type=EmotionType.HAPPINESS, intensity=0.3, valence=0.0, arousal=0.3, confidence=0.5)

    async def appraise_event(self, event: Dict[str, Any]) -> AppraisalResult:
        """
        Appraise emotional significance of event.

        Uses appraisal theory dimensions:
        - Goal relevance: Is this important?
        - Goal congruence: Does this help or hinder goals?
        - Coping potential: Can I handle this?

        Args:
            event: Event to appraise

        Returns:
            AppraisalResult with generated emotion
        """
        await asyncio.sleep(0.2)  # Simulate appraisal

        event_type = event.get("type", "unknown")
        importance = event.get("importance", 0.5)

        # Appraisal dimensions
        goal_relevance = importance
        goal_congruence = 0.0
        coping_potential = 0.7

        # Determine goal congruence and emotion type
        if event_type == "goal_achieved":
            goal_congruence = 1.0
            emotion_type = EmotionType.JOY
            valence = 0.9
            arousal = 0.8
            reasoning = "Goal achievement leads to joy"

        elif event_type == "goal_blocked":
            goal_congruence = -1.0
            emotion_type = EmotionType.FRUSTRATION
            valence = -0.6
            arousal = 0.7
            reasoning = "Goal blockage leads to frustration"

        elif event_type == "threat":
            goal_congruence = -0.9
            coping_potential = event.get("coping_potential", 0.3)
            if coping_potential < 0.5:
                emotion_type = EmotionType.FEAR
                valence = -0.8
                arousal = 0.9
                reasoning = "Threat with low coping leads to fear"
            else:
                emotion_type = EmotionType.ANGER
                valence = -0.6
                arousal = 0.9
                reasoning = "Threat with coping potential leads to anger"

        elif event_type == "loss":
            goal_congruence = -0.8
            emotion_type = EmotionType.SADNESS
            valence = -0.7
            arousal = 0.3
            reasoning = "Loss leads to sadness"

        elif event_type == "surprise":
            goal_congruence = 0.0
            emotion_type = EmotionType.SURPRISE
            valence = 0.0
            arousal = 0.9
            reasoning = "Unexpected event leads to surprise"

        elif event_type == "user_praise":
            goal_congruence = 0.8
            emotion_type = EmotionType.PRIDE
            valence = 0.8
            arousal = 0.6
            reasoning = "Praise leads to pride"

        else:
            # Neutral
            goal_congruence = 0.0
            emotion_type = EmotionType.HAPPINESS
            valence = 0.0
            arousal = 0.3
            reasoning = "Neutral event"

        # Calculate intensity from appraisal dimensions
        intensity = goal_relevance * abs(goal_congruence)
        intensity = max(0.0, min(1.0, intensity))

        emotion = Emotion(type=emotion_type, intensity=intensity, valence=valence, arousal=arousal, confidence=0.85)

        appraisal_dimensions = {
            "goal_relevance": goal_relevance,
            "goal_congruence": goal_congruence,
            "coping_potential": coping_potential,
        }

        return AppraisalResult(
            emotion=emotion, appraisal_dimensions=appraisal_dimensions, reasoning=reasoning, situation=event
        )

    async def update_emotional_state(self, emotion: Emotion):
        """Update current emotional state."""
        self.current_state.primary_emotion = emotion
        self.emotion_history.append((datetime.now(), emotion))


# ============================================================================
# 2. AFFECTIVE COMPUTING SYSTEM
# ============================================================================


class EmotionRegulationStrategy(Enum):
    """Emotion regulation strategies."""

    REAPPRAISAL = "reappraisal"  # Change interpretation
    SUPPRESSION = "suppression"  # Inhibit expression
    DISTRACTION = "distraction"  # Shift attention
    SITUATION_MODIFICATION = "situation_modification"  # Change situation
    ACCEPTANCE = "acceptance"  # Accept emotion as is


@dataclass
class Mood:
    """Background mood state (longer-lasting than emotions)."""

    type: str  # happy, sad, anxious, calm, etc.
    valence: float  # -1 to +1
    intensity: float  # 0-1
    duration: float = 0.0  # hours
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AffectiveResponse:
    """Generated affective response."""

    text: str
    emotion: Emotion
    tone: str
    appropriateness: float  # 0-1


class AffectiveComputingSystem:
    """
    Generates and regulates emotional responses and tracks mood.

    Implements emotion generation, regulation strategies, and mood dynamics.
    """

    def __init__(self, default_mood: str = "neutral", regulation_enabled: bool = True):
        self.default_mood = default_mood
        self.regulation_enabled = regulation_enabled

        self.current_mood = Mood(type=default_mood, valence=0.0, intensity=0.5)

        self.regulation_history: deque = deque(maxlen=500)
        self.lock = threading.Lock()

    async def generate_emotion(self, event: Dict[str, Any]) -> Emotion:
        """
        Generate emotion from event.

        Args:
            event: Event to generate emotion from

        Returns:
            Generated emotion
        """
        await asyncio.sleep(0.05)

        event_type = event.get("type", "neutral")
        severity = event.get("severity", 0.5)

        # Simple event-to-emotion mapping
        emotion_map = {
            "user_complaint": (EmotionType.CONCERN, -0.5, 0.6),
            "success": (EmotionType.JOY, 0.8, 0.7),
            "error": (EmotionType.FRUSTRATION, -0.6, 0.7),
            "user_praise": (EmotionType.GRATITUDE, 0.8, 0.5),
            "uncertainty": (EmotionType.ANXIETY, -0.4, 0.7),
            "completion": (EmotionType.SATISFACTION, 0.7, 0.4),
        }

        if event_type in emotion_map:
            emotion_type_str, valence, arousal = emotion_map[event_type]
            # Map string to EmotionType
            try:
                emotion_type = EmotionType[emotion_type_str.upper()]
            except:
                emotion_type = EmotionType.HAPPINESS

            intensity = severity
        else:
            emotion_type = EmotionType.HAPPINESS
            valence = 0.0
            arousal = 0.3
            intensity = 0.3

        return Emotion(type=emotion_type, intensity=intensity, valence=valence, arousal=arousal)

    async def regulate_emotion(
        self, emotion: Emotion, strategy: EmotionRegulationStrategy, target_intensity: Optional[float] = None
    ) -> Emotion:
        """
        Regulate emotion using specified strategy.

        Args:
            emotion: Emotion to regulate
            strategy: Regulation strategy to use
            target_intensity: Desired intensity (optional)

        Returns:
            Regulated emotion
        """
        await asyncio.sleep(0.1)

        if not self.regulation_enabled:
            return emotion

        with self.lock:
            regulated = Emotion(
                type=emotion.type, intensity=emotion.intensity, valence=emotion.valence, arousal=emotion.arousal
            )

            if strategy == EmotionRegulationStrategy.REAPPRAISAL:
                # Change interpretation to reduce intensity
                regulated.intensity *= 0.6
                regulated.valence *= 0.7  # Less extreme valence

            elif strategy == EmotionRegulationStrategy.SUPPRESSION:
                # Reduce intensity but emotion remains
                regulated.intensity *= 0.4

            elif strategy == EmotionRegulationStrategy.DISTRACTION:
                # Shift to less intense neutral-ish emotion
                regulated.intensity *= 0.5
                regulated.arousal *= 0.6

            elif strategy == EmotionRegulationStrategy.ACCEPTANCE:
                # Accept as is, slight intensity reduction from acceptance
                regulated.intensity *= 0.9

            # Apply target intensity if specified
            if target_intensity is not None:
                regulated.intensity = target_intensity

            # Clamp values
            regulated.intensity = max(0.0, min(1.0, regulated.intensity))
            regulated.valence = max(-1.0, min(1.0, regulated.valence))
            regulated.arousal = max(0.0, min(1.0, regulated.arousal))

            self.regulation_history.append(
                {"original": emotion, "regulated": regulated, "strategy": strategy, "timestamp": datetime.now()}
            )

            return regulated

    async def get_current_mood(self) -> Mood:
        """Get current background mood."""
        return self.current_mood

    async def update_mood(self, emotion: Emotion):
        """Update mood based on recent emotions."""
        # Mood is slower-changing than emotion
        # Average recent emotional valence
        mood_update_rate = 0.1  # Slow update

        new_valence = self.current_mood.valence * (1 - mood_update_rate) + emotion.valence * mood_update_rate

        self.current_mood.valence = new_valence

        # Update mood type based on valence
        if new_valence > 0.5:
            self.current_mood.type = "happy"
        elif new_valence > 0.2:
            self.current_mood.type = "content"
        elif new_valence > -0.2:
            self.current_mood.type = "neutral"
        elif new_valence > -0.5:
            self.current_mood.type = "melancholic"
        else:
            self.current_mood.type = "sad"

    async def generate_response(self, emotion: Emotion, context: Dict[str, Any]) -> AffectiveResponse:
        """
        Generate emotionally appropriate response.

        Args:
            emotion: Emotion to express
            context: Situational context

        Returns:
            AffectiveResponse
        """
        await asyncio.sleep(0.3)

        # Generate response based on emotion and context
        emotion_type = emotion.type

        if emotion_type == EmotionType.JOY:
            text = "I'm delighted with this outcome!"
            tone = "enthusiastic"
        elif emotion_type == EmotionType.GRATITUDE:
            text = "Thank you for your feedback!"
            tone = "appreciative"
        elif emotion_type in [EmotionType.FRUSTRATION, EmotionType.ANGER]:
            text = "I understand this is frustrating. Let me help resolve this."
            tone = "empathetic"
        elif emotion_type == EmotionType.SADNESS:
            text = "I appreciate your patience with this situation."
            tone = "understanding"
        else:
            text = "I'm here to help."
            tone = "neutral"

        return AffectiveResponse(text=text, emotion=emotion, tone=tone, appropriateness=0.85)


# ============================================================================
# 3. EMPATHY SIMULATOR
# ============================================================================


class EmpathyType(Enum):
    """Types of empathy."""

    COGNITIVE = "cognitive"  # Understanding perspective
    AFFECTIVE = "affective"  # Feeling with others
    COMPASSIONATE = "compassionate"  # Motivated to help


@dataclass
class PerspectiveTaking:
    """Result of taking another's perspective."""

    beliefs: List[str]
    emotions: List[Emotion]
    desires: List[str]
    intentions: List[str]
    confidence: float


@dataclass
class EmpatheticResponse:
    """Empathetic response to situation."""

    text: str
    empathic_emotion: Emotion
    helping_behavior: Optional[str]
    appropriateness: float


class EmpathySimulator:
    """
    Models empathy: cognitive, affective, and compassionate.

    Enables perspective-taking, emotional resonance, and prosocial responses.
    """

    def __init__(self, empathy_level: float = 0.8, cognitive_empathy: bool = True, affective_empathy: bool = True):
        self.empathy_level = empathy_level  # 0-1
        self.cognitive_empathy = cognitive_empathy
        self.affective_empathy = affective_empathy

        self.empathy_history: deque = deque(maxlen=500)

    async def take_perspective(self, situation: Dict[str, Any]) -> PerspectiveTaking:
        """
        Take another person's perspective (Theory of Mind).

        Args:
            situation: Situation to model

        Returns:
            PerspectiveTaking result
        """
        await asyncio.sleep(0.3)

        if not self.cognitive_empathy:
            return PerspectiveTaking(beliefs=[], emotions=[], desires=[], intentions=[], confidence=0.0)

        context = situation.get("context", "")
        visible_emotions = situation.get("visible_emotions", [])

        # Infer mental states (simplified)
        if "failure" in context or "problem" in context:
            beliefs = ["Things didn't go as planned", "I need help"]
            emotions = [Emotion(EmotionType.FRUSTRATION, 0.7, -0.6, 0.7)]
            desires = ["Fix the problem", "Get support"]
            intentions = ["Seek help", "Express frustration"]
        elif "success" in context or "achievement" in context:
            beliefs = ["I achieved my goal", "Things are going well"]
            emotions = [Emotion(EmotionType.JOY, 0.8, 0.8, 0.7)]
            desires = ["Share success", "Continue progress"]
            intentions = ["Celebrate", "Plan next steps"]
        else:
            beliefs = ["Situation is neutral"]
            emotions = [Emotion(EmotionType.HAPPINESS, 0.5, 0.0, 0.3)]
            desires = ["Continue normally"]
            intentions = ["Proceed with task"]

        return PerspectiveTaking(
            beliefs=beliefs, emotions=emotions, desires=desires, intentions=intentions, confidence=0.7
        )

    async def feel_empathy(self, other_emotion: str, intensity: float, empathy_type: EmpathyType) -> Emotion:
        """
        Feel empathy for another's emotion.

        Args:
            other_emotion: Emotion of the other person
            intensity: Intensity of their emotion
            empathy_type: Type of empathy to engage

        Returns:
            Empathic emotion
        """
        await asyncio.sleep(0.2)

        if not self.affective_empathy:
            # No affective empathy, return neutral
            return Emotion(EmotionType.HAPPINESS, 0.3, 0.0, 0.3)

        # Emotional contagion / resonance
        # Feel a portion of the other's emotion
        empathy_coefficient = self.empathy_level * 0.6  # Feel 60% of intensity

        empathic_intensity = intensity * empathy_coefficient

        # Map emotion string to EmotionType
        emotion_map = {
            "sadness": EmotionType.SADNESS,
            "joy": EmotionType.JOY,
            "anger": EmotionType.ANGER,
            "fear": EmotionType.FEAR,
            "frustration": EmotionType.FRUSTRATION,
        }

        emotion_type = emotion_map.get(other_emotion.lower(), EmotionType.HAPPINESS)

        # Determine valence and arousal
        if emotion_type == EmotionType.SADNESS:
            valence, arousal = -0.7, 0.3
        elif emotion_type == EmotionType.JOY:
            valence, arousal = 0.8, 0.7
        elif emotion_type == EmotionType.ANGER:
            valence, arousal = -0.6, 0.9
        elif emotion_type == EmotionType.FEAR:
            valence, arousal = -0.8, 0.9
        elif emotion_type == EmotionType.FRUSTRATION:
            valence, arousal = -0.5, 0.7
        else:
            valence, arousal = 0.0, 0.3

        return Emotion(type=emotion_type, intensity=empathic_intensity, valence=valence, arousal=arousal)

    async def generate_compassionate_response(
        self, situation: Dict[str, Any], other_emotion: str
    ) -> EmpatheticResponse:
        """
        Generate compassionate, helping response.

        Args:
            situation: Situation context
            other_emotion: Other person's emotion

        Returns:
            EmpatheticResponse
        """
        await asyncio.sleep(0.3)

        # Take perspective
        perspective = await self.take_perspective(situation)

        # Feel empathy
        empathic_emotion = await self.feel_empathy(
            other_emotion=other_emotion, intensity=0.7, empathy_type=EmpathyType.COMPASSIONATE
        )

        # Generate compassionate response
        if other_emotion.lower() in ["sadness", "frustration", "anger"]:
            text = "I understand this is difficult. I'm here to support you and help find a solution."
            helping_behavior = "offer_support"
        elif other_emotion.lower() in ["joy", "happiness"]:
            text = "That's wonderful! I'm glad things are going well for you."
            helping_behavior = "celebrate_with"
        elif other_emotion.lower() == "fear":
            text = "I can see this is concerning. Let's work through this together step by step."
            helping_behavior = "provide_reassurance"
        else:
            text = "I'm here to help however I can."
            helping_behavior = "offer_assistance"

        self.empathy_history.append(
            {"situation": situation, "other_emotion": other_emotion, "response": text, "timestamp": datetime.now()}
        )

        return EmpatheticResponse(
            text=text, empathic_emotion=empathic_emotion, helping_behavior=helping_behavior, appropriateness=0.85
        )


# ============================================================================
# 4. EMOTIONAL INTELLIGENCE SYSTEM
# ============================================================================


class EmotionalSkill(Enum):
    """Emotional intelligence skills."""

    CONFLICT_RESOLUTION = "conflict_resolution"
    INSPIRATIONAL_COMMUNICATION = "inspirational_communication"
    INFLUENCE = "influence"
    EMOTIONAL_COACHING = "emotional_coaching"
    ADAPTABILITY = "adaptability"
    TEAMWORK = "teamwork"


@dataclass
class EQAssessment:
    """Emotional intelligence assessment."""

    overall_score: float  # 0-1
    dimensions: Dict[str, float]
    strengths: List[str]
    areas_for_growth: List[str]


@dataclass
class SkillApplication:
    """Result of applying emotional skill."""

    skill: EmotionalSkill
    strategy: str
    actions: List[str]
    expected_outcome: str


class EmotionalIntelligenceSystem:
    """
    Implements emotional intelligence (EQ) capabilities.

    Four dimensions: Self-awareness, Self-management,
    Social awareness, Relationship management.
    """

    def __init__(self, self_awareness_level: float = 0.8, social_awareness_level: float = 0.75):
        self.self_awareness_level = self_awareness_level
        self.social_awareness_level = social_awareness_level
        self.self_management_level = 0.75
        self.relationship_management_level = 0.7

        self.eq_learning_history: deque = deque(maxlen=500)

    async def assess_eq(self) -> EQAssessment:
        """
        Assess emotional intelligence across dimensions.

        Returns:
            EQAssessment
        """
        await asyncio.sleep(1.0)

        dimensions = {
            "self_awareness": self.self_awareness_level,
            "self_management": self.self_management_level,
            "social_awareness": self.social_awareness_level,
            "relationship_management": self.relationship_management_level,
        }

        overall_score = np.mean(list(dimensions.values()))

        # Identify strengths and areas for growth
        strengths = [k for k, v in dimensions.items() if v > 0.75]
        areas_for_growth = [k for k, v in dimensions.items() if v < 0.7]

        return EQAssessment(
            overall_score=overall_score, dimensions=dimensions, strengths=strengths, areas_for_growth=areas_for_growth
        )

    async def apply_skill(self, skill: EmotionalSkill, situation: Dict[str, Any]) -> SkillApplication:
        """
        Apply emotional intelligence skill to situation.

        Args:
            skill: Skill to apply
            situation: Situation context

        Returns:
            SkillApplication
        """
        await asyncio.sleep(0.3)

        if skill == EmotionalSkill.CONFLICT_RESOLUTION:
            strategy = "Empathize with both parties, find common ground, propose win-win solution"
            actions = [
                "Listen to both perspectives",
                "Acknowledge emotions of all parties",
                "Identify shared interests",
                "Brainstorm mutually beneficial solutions",
                "Facilitate agreement",
            ]
            expected_outcome = "Reduced conflict, restored cooperation"

        elif skill == EmotionalSkill.INSPIRATIONAL_COMMUNICATION:
            strategy = "Connect to values, paint vivid future, express confidence"
            actions = [
                "Identify team's core values",
                "Create compelling vision",
                "Express genuine enthusiasm",
                "Highlight potential and capabilities",
                "Call to action with confidence",
            ]
            expected_outcome = "Increased motivation and engagement"

        elif skill == EmotionalSkill.INFLUENCE:
            strategy = "Build rapport, understand needs, align with interests"
            actions = [
                "Establish emotional connection",
                "Understand other's perspective and needs",
                "Frame message to align with their interests",
                "Use emotional appeals appropriately",
                "Provide rational support",
            ]
            expected_outcome = "Increased buy-in and cooperation"

        else:
            strategy = "Apply emotional intelligence"
            actions = ["Assess situation", "Respond appropriately"]
            expected_outcome = "Positive emotional outcome"

        return SkillApplication(skill=skill, strategy=strategy, actions=actions, expected_outcome=expected_outcome)

    async def learn_from_interaction(self, interaction: Dict[str, Any], feedback: Dict[str, Any]):
        """
        Learn and improve EQ from interaction feedback.

        Args:
            interaction: Interaction details
            feedback: Outcome and effectiveness feedback
        """
        await asyncio.sleep(0.1)

        effectiveness = feedback.get("effectiveness", 0.5)

        # Update EQ dimensions based on feedback
        if effectiveness > 0.8:
            # Successful interaction, reinforce
            self.relationship_management_level = min(1.0, self.relationship_management_level * 1.02)
        elif effectiveness < 0.5:
            # Need improvement
            # Identify which dimension needs work (simplified)
            # In real system, would analyze what went wrong
            pass

        self.eq_learning_history.append({"interaction": interaction, "feedback": feedback, "timestamp": datetime.now()})


# ============================================================================
# 5. EMOTIONAL MEMORY SYSTEM
# ============================================================================


@dataclass
class EmotionalMemory:
    """Memory tagged with emotion."""

    event: Dict[str, Any]
    emotion: Emotion
    importance: float  # 0-1
    retrieval_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    created: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryQuery:
    """Query for emotional memories."""

    emotion_type: Optional[str] = None
    min_intensity: float = 0.0
    valence_range: Optional[Tuple[float, float]] = None
    time_range: Optional[str] = None  # 'last_day', 'last_week', etc.
    min_importance: float = 0.0


class EmotionalMemorySystem:
    """
    Stores and retrieves emotion-tagged memories.

    Implements mood-congruent memory and emotional learning.
    """

    def __init__(self, capacity: int = 10000, decay_rate: float = 0.01):  # per day
        self.capacity = capacity
        self.decay_rate = decay_rate

        self.memories: List[EmotionalMemory] = []
        self.memory_count = 0
        self.lock = threading.Lock()

    async def store(self, event: Dict[str, Any], emotion: Emotion, importance: float):
        """
        Store emotion-tagged memory.

        Args:
            event: Event to remember
            emotion: Associated emotion
            importance: Memory importance (0-1)
        """
        await asyncio.sleep(0.03)

        with self.lock:
            memory = EmotionalMemory(event=event, emotion=emotion, importance=importance)

            self.memories.append(memory)
            self.memory_count += 1

            # Enforce capacity limit
            if len(self.memories) > self.capacity:
                # Remove least important, least accessed memories
                self.memories.sort(key=lambda m: m.importance * (1 + m.retrieval_count), reverse=True)
                self.memories = self.memories[: self.capacity]

    async def retrieve(self, query: MemoryQuery) -> List[EmotionalMemory]:
        """
        Retrieve memories matching query.

        Args:
            query: Memory query

        Returns:
            List of matching memories
        """
        await asyncio.sleep(0.1)

        with self.lock:
            matching = []

            for memory in self.memories:
                # Filter by emotion type
                if query.emotion_type:
                    if memory.emotion.type.value != query.emotion_type.lower():
                        continue

                # Filter by intensity
                if memory.emotion.intensity < query.min_intensity:
                    continue

                # Filter by valence range
                if query.valence_range:
                    min_val, max_val = query.valence_range
                    if not (min_val <= memory.emotion.valence <= max_val):
                        continue

                # Filter by time range
                if query.time_range:
                    now = datetime.now()
                    if query.time_range == "last_day":
                        cutoff = now - timedelta(days=1)
                    elif query.time_range == "last_week":
                        cutoff = now - timedelta(weeks=1)
                    elif query.time_range == "last_month":
                        cutoff = now - timedelta(days=30)
                    else:
                        cutoff = datetime.min

                    if memory.created < cutoff:
                        continue

                # Filter by importance
                if memory.importance < query.min_importance:
                    continue

                matching.append(memory)
                memory.retrieval_count += 1
                memory.last_accessed = datetime.now()

            # Sort by importance and recency
            matching.sort(key=lambda m: m.importance * (1 + np.log1p(m.retrieval_count)), reverse=True)

            return matching[:100]  # Limit results

    async def retrieve_mood_congruent(self, current_mood: Mood) -> List[EmotionalMemory]:
        """
        Retrieve memories congruent with current mood.

        Args:
            current_mood: Current mood state

        Returns:
            Mood-congruent memories
        """
        # Memories with similar valence to mood
        query = MemoryQuery(valence_range=(current_mood.valence - 0.3, current_mood.valence + 0.3), min_importance=0.3)

        return await self.retrieve(query)


# ============================================================================
# 6. EMOTIONAL DECISION MAKING
# ============================================================================


@dataclass
class DecisionOption:
    """Option in a decision."""

    id: str
    description: str
    rational_value: float  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmotionalValuation:
    """Emotional valuation of option."""

    option_id: str
    value: float  # 0-1
    anticipated_emotions: Dict[str, float]
    somatic_marker: float  # "Gut feeling" -1 to +1


@dataclass
class EmotionalDecision:
    """Decision made with emotional input."""

    choice: str
    confidence: float
    emotion_contribution: float  # How much emotion influenced (0-1)
    reasoning: str


class EmotionalDecisionMaking:
    """
    Integrates emotions into decision-making.

    Implements somatic marker hypothesis: emotions guide decisions
    through "gut feelings" based on past emotional experiences.
    """

    def __init__(self, emotion_weight: float = 0.4, use_somatic_markers: bool = True):
        self.emotion_weight = emotion_weight  # 0-1 (emotion vs reason)
        self.use_somatic_markers = use_somatic_markers

        self.decision_history: deque = deque(maxlen=500)

    async def emotionally_evaluate(self, option: DecisionOption) -> EmotionalValuation:
        """
        Evaluate option emotionally (somatic marker).

        Args:
            option: Option to evaluate

        Returns:
            EmotionalValuation
        """
        await asyncio.sleep(0.15)

        # Simulate "gut feeling" based on option properties
        description_lower = option.description.lower()

        # Positive markers
        if any(word in description_lower for word in ["safe", "certain", "proven", "stable"]):
            somatic_marker = 0.6
            anticipated_emotions = {"relief": 0.7, "satisfaction": 0.6}
        elif any(word in description_lower for word in ["exciting", "innovative", "opportunity"]):
            somatic_marker = 0.4
            anticipated_emotions = {"excitement": 0.8, "anxiety": 0.3}
        elif any(word in description_lower for word in ["risky", "uncertain", "challenging"]):
            somatic_marker = -0.3
            anticipated_emotions = {"anxiety": 0.7, "excitement": 0.4}
        else:
            somatic_marker = 0.2
            anticipated_emotions = {"neutral": 0.5}

        # Emotional value combines somatic marker and anticipated emotions
        emotional_value = (somatic_marker + 1.0) / 2.0  # Map to 0-1

        return EmotionalValuation(
            option_id=option.id,
            value=emotional_value,
            anticipated_emotions=anticipated_emotions,
            somatic_marker=somatic_marker,
        )

    async def decide(self, options: List[DecisionOption], context: Dict[str, Any]) -> EmotionalDecision:
        """
        Make decision integrating emotion and reason.

        Args:
            options: Decision options
            context: Decision context

        Returns:
            EmotionalDecision
        """
        await asyncio.sleep(0.3)

        option_scores = {}

        for option in options:
            # Get emotional valuation
            emotional = await self.emotionally_evaluate(option)

            # Combine rational and emotional values
            combined_value = self.emotion_weight * emotional.value + (1 - self.emotion_weight) * option.rational_value

            option_scores[option.id] = {
                "combined": combined_value,
                "emotional": emotional.value,
                "rational": option.rational_value,
                "option": option,
            }

        # Choose best option
        best_id = max(option_scores, key=lambda k: option_scores[k]["combined"])
        best = option_scores[best_id]

        confidence = best["combined"]

        reasoning = (
            f"Chose option {best_id} with combined score {best['combined']:.2f} "
            f"(emotional: {best['emotional']:.2f}, rational: {best['rational']:.2f})"
        )

        decision = EmotionalDecision(
            choice=best_id, confidence=confidence, emotion_contribution=self.emotion_weight, reasoning=reasoning
        )

        self.decision_history.append({"decision": decision, "options": options, "timestamp": datetime.now()})

        return decision

    async def simulate_regret(self, chosen: str, alternative: str, outcome: str) -> Dict[str, Any]:
        """
        Simulate anticipated regret/relief.

        Args:
            chosen: Chosen option ID
            alternative: Alternative option ID
            outcome: Outcome (success, failure)

        Returns:
            Dict with regret/relief emotions
        """
        await asyncio.sleep(0.2)

        if outcome == "success":
            # Relief, no regret
            regret_intensity = 0.1
            relief_intensity = 0.8
        else:
            # Failure, possible regret
            regret_intensity = 0.7
            relief_intensity = 0.2

        return {
            "regret_intensity": regret_intensity,
            "relief_intensity": relief_intensity,
            "counterfactual_emotion": "regret" if regret_intensity > 0.5 else "relief",
        }


# ============================================================================
# 7. EMOTIONAL EXPRESSION GENERATOR
# ============================================================================


class EmotionalTone(Enum):
    """Tone for emotional expression."""

    ENTHUSIASTIC = "enthusiastic"
    APOLOGETIC = "apologetic"
    SUPPORTIVE = "supportive"
    INSPIRATIONAL = "inspirational"
    CALM = "calm"
    CONCERNED = "concerned"


class CulturalContext(Enum):
    """Cultural context for emotion expression."""

    WESTERN = "western"
    EASTERN = "eastern"
    NEUTRAL = "neutral"


@dataclass
class FacialExpression:
    """Facial expression (FACS codes)."""

    action_units: List[str]  # FACS Action Units
    intensity: float
    emotion: str


class EmotionalExpressionGenerator:
    """
    Generates emotionally appropriate expressions and communication.

    Implements emotional language, nonverbal codes, and cultural adaptation.
    """

    def __init__(self, modalities: List[str], cultural_context: CulturalContext = CulturalContext.WESTERN):
        self.modalities = modalities  # text, voice, visual
        self.cultural_context = cultural_context

    async def generate_text(self, message: str, emotion: Emotion, tone: EmotionalTone) -> str:
        """
        Generate emotionally expressive text.

        Args:
            message: Base message
            emotion: Emotion to express
            tone: Tone to use

        Returns:
            Emotionally colored text
        """
        await asyncio.sleep(0.2)

        text = message

        # Add emotional coloring based on emotion and tone
        if emotion.type == EmotionType.JOY and emotion.intensity > 0.7:
            if tone == EmotionalTone.ENTHUSIASTIC:
                text = text + "! I'm so excited!"
            else:
                text = text + "! That's wonderful!"

        elif emotion.type == EmotionType.GRATITUDE:
            text = "Thank you! " + text

        elif emotion.type in [EmotionType.FRUSTRATION, EmotionType.ANGER]:
            if tone == EmotionalTone.APOLOGETIC:
                text = "I apologize for the inconvenience. " + text
            elif tone == EmotionalTone.SUPPORTIVE:
                text = "I understand this is frustrating. " + text

        elif emotion.type == EmotionType.SADNESS:
            text = "I appreciate your patience. " + text

        # Add tone-specific elements
        if tone == EmotionalTone.INSPIRATIONAL:
            text = text + " Together, we can achieve great things!"
        elif tone == EmotionalTone.CONCERNED:
            text = text + " Please let me know if you need any support."

        return text

    async def generate_facial_expression(self, emotion: str, intensity: float) -> FacialExpression:
        """
        Generate facial expression (FACS action units).

        Args:
            emotion: Emotion to express
            intensity: Expression intensity

        Returns:
            FacialExpression with FACS codes
        """
        await asyncio.sleep(0.05)

        # Map emotions to FACS Action Units (simplified)
        if emotion.lower() == "happiness":
            action_units = ["AU6", "AU12"]  # Cheek raiser, Lip corner puller
        elif emotion.lower() == "sadness":
            action_units = ["AU1", "AU4", "AU15"]  # Inner brow raiser, frown
        elif emotion.lower() == "anger":
            action_units = ["AU4", "AU5", "AU7", "AU23"]  # Brow lower, upper lid raise
        elif emotion.lower() == "fear":
            action_units = ["AU1", "AU2", "AU5", "AU20"]  # Brow raise, eyes wide
        elif emotion.lower() == "surprise":
            action_units = ["AU1", "AU2", "AU5", "AU26"]  # Brows up, jaw drop
        elif emotion.lower() == "disgust":
            action_units = ["AU9", "AU15", "AU16"]  # Nose wrinkle, lip depression
        else:
            action_units = []

        return FacialExpression(action_units=action_units, intensity=intensity, emotion=emotion)

    async def adapt_to_culture(self, emotion: str, context: CulturalContext) -> Dict[str, Any]:
        """
        Adapt emotional expression to cultural norms.

        Args:
            emotion: Emotion to adapt
            context: Cultural context

        Returns:
            Culturally adapted expression
        """
        await asyncio.sleep(0.1)

        # Cultural display rules (simplified)
        if context == CulturalContext.EASTERN:
            # More restrained emotional expression
            if emotion.lower() in ["anger", "pride"]:
                expression = "subtle_expression"
                intensity_modifier = 0.6
            else:
                expression = "moderate_expression"
                intensity_modifier = 0.8
        elif context == CulturalContext.WESTERN:
            # More expressive
            expression = "full_expression"
            intensity_modifier = 1.0
        else:
            expression = "balanced_expression"
            intensity_modifier = 0.9

        return {"expression": expression, "intensity_modifier": intensity_modifier, "cultural_appropriateness": 0.9}


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_emotional_awareness_engine: Optional[EmotionalAwarenessEngine] = None
_affective_system: Optional[AffectiveComputingSystem] = None
_empathy_simulator: Optional[EmpathySimulator] = None
_eq_system: Optional[EmotionalIntelligenceSystem] = None
_emotional_memory: Optional[EmotionalMemorySystem] = None
_emotional_decision_system: Optional[EmotionalDecisionMaking] = None
_expression_generator: Optional[EmotionalExpressionGenerator] = None

_lock = threading.Lock()


def get_emotional_awareness_engine(**kwargs) -> EmotionalAwarenessEngine:
    """Get or create singleton Emotional Awareness Engine."""
    global _emotional_awareness_engine
    with _lock:
        if _emotional_awareness_engine is None:
            _emotional_awareness_engine = EmotionalAwarenessEngine(**kwargs)
        return _emotional_awareness_engine


def get_affective_system(**kwargs) -> AffectiveComputingSystem:
    """Get or create singleton Affective Computing System."""
    global _affective_system
    with _lock:
        if _affective_system is None:
            _affective_system = AffectiveComputingSystem(**kwargs)
        return _affective_system


def get_empathy_simulator(**kwargs) -> EmpathySimulator:
    """Get or create singleton Empathy Simulator."""
    global _empathy_simulator
    with _lock:
        if _empathy_simulator is None:
            _empathy_simulator = EmpathySimulator(**kwargs)
        return _empathy_simulator


def get_eq_system(**kwargs) -> EmotionalIntelligenceSystem:
    """Get or create singleton Emotional Intelligence System."""
    global _eq_system
    with _lock:
        if _eq_system is None:
            _eq_system = EmotionalIntelligenceSystem(**kwargs)
        return _eq_system


def get_emotional_memory(**kwargs) -> EmotionalMemorySystem:
    """Get or create singleton Emotional Memory System."""
    global _emotional_memory
    with _lock:
        if _emotional_memory is None:
            _emotional_memory = EmotionalMemorySystem(**kwargs)
        return _emotional_memory


def get_emotional_decision_system(**kwargs) -> EmotionalDecisionMaking:
    """Get or create singleton Emotional Decision Making."""
    global _emotional_decision_system
    with _lock:
        if _emotional_decision_system is None:
            _emotional_decision_system = EmotionalDecisionMaking(**kwargs)
        return _emotional_decision_system


def get_expression_generator(**kwargs) -> EmotionalExpressionGenerator:
    """Get or create singleton Expression Generator."""
    global _expression_generator
    with _lock:
        if _expression_generator is None:
            _expression_generator = EmotionalExpressionGenerator(**kwargs)
        return _expression_generator
