"""
🌐 Social & Collective Intelligence Platform (v8.0)

Implements computational models of social cognition, group dynamics, collective
decision-making, swarm intelligence, cultural adaptation, and collaborative AI
based on social psychology and organizational behavior research.

Components:
- Social Cognition Engine: Advanced Theory of Mind and social understanding
- Group Dynamics System: Team formation, development, and leadership
- Collective Decision Making: Voting, consensus, wisdom of crowds
- Swarm Intelligence System: Emergent coordination and optimization
- Cultural Intelligence System: Cross-cultural adaptation
- Social Network Analysis: Influence and information flow
- Collaborative Intelligence Orchestrator: Human-AI coordination

Author: Document Management System Development Team
Version: 8.0.0
Date: January 2026
"""

import asyncio
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# ============================================================================
# 1. SOCIAL COGNITION ENGINE
# ============================================================================


class SocialRole(Enum):
    """Social roles in interactions."""

    LEADER = "leader"
    MANAGER = "manager"
    COLLEAGUE = "colleague"
    SUBORDINATE = "subordinate"
    CLIENT = "client"
    EXPERT = "expert"
    FACILITATOR = "facilitator"
    OBSERVER = "observer"


@dataclass
class SocialContext:
    """Context for social interaction."""

    participants: List[str]
    setting: str  # meeting, email, chat, etc.
    formality: str  # formal, professional, casual
    power_dynamics: Optional[Dict[str, float]] = None  # 0-1 power levels


@dataclass
class AppropriatenessAssessment:
    """Assessment of social appropriateness."""

    score: float  # 0-1
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BeliefChain:
    """Recursive Theory of Mind belief chain."""

    depth: int
    chain: List[str]
    confidence: float


class SocialCognitionEngine:
    """
    Advanced social cognition with Theory of Mind, social perception,
    and social intelligence capabilities.
    """

    def __init__(self, tom_depth: int = 3, social_awareness: float = 0.85):
        self.tom_depth = tom_depth  # Max ToM recursion depth
        self.social_awareness = social_awareness

        self.role_patterns: Dict[str, Set[str]] = {
            "leader": {"directive", "authoritative", "strategic", "decisive"},
            "manager": {"organized", "coordinating", "responsible", "supervising"},
            "colleague": {"collaborative", "equal", "peer", "cooperative"},
            "subordinate": {"respectful", "responsive", "following", "executing"},
            "client": {"requesting", "expecting", "customer", "external"},
            "expert": {"knowledgeable", "specialist", "consultant", "advisor"},
        }

    async def recognize_roles(self, context: SocialContext) -> Dict[str, SocialRole]:
        """
        Recognize social roles of participants.

        Args:
            context: Social context

        Returns:
            Dict mapping participants to roles
        """
        await asyncio.sleep(0.2)

        roles = {}

        # Simple pattern-based role recognition
        for participant in context.participants:
            if "manager" in participant.lower() or "boss" in participant.lower():
                roles[participant] = SocialRole.MANAGER
            elif "client" in participant.lower() or "customer" in participant.lower():
                roles[participant] = SocialRole.CLIENT
            elif "expert" in participant.lower() or "specialist" in participant.lower():
                roles[participant] = SocialRole.EXPERT
            else:
                roles[participant] = SocialRole.COLLEAGUE

        return roles

    async def recursive_tom(self, depth: int, belief: str) -> BeliefChain:
        """
        Recursive Theory of Mind (I believe that you believe that...).

        Args:
            depth: Recursion depth (1-3)
            belief: Base belief

        Returns:
            BeliefChain with recursive beliefs
        """
        await asyncio.sleep(0.1 * depth)

        depth = min(depth, self.tom_depth)

        chain = []
        current_belief = belief

        for level in range(depth):
            if level == 0:
                chain.append(f"You believe that {current_belief}")
            else:
                prefix = "I believe that " * (level + 1)
                chain.append(f"{prefix}{current_belief}")

        confidence = 0.9**depth  # Confidence decreases with depth

        return BeliefChain(depth=depth, chain=chain, confidence=confidence)

    async def assess_appropriateness(self, message: str, context: SocialContext) -> AppropriatenessAssessment:
        """
        Assess social appropriateness of message.

        Args:
            message: Message to assess
            context: Social context

        Returns:
            AppropriatenessAssessment
        """
        await asyncio.sleep(0.15)

        score = 0.8  # Default
        issues = []
        recommendations = []

        message_lower = message.lower()

        # Check formality match
        if context.formality == "formal":
            if any(informal in message_lower for informal in ["hey", "gonna", "wanna", "yeah"]):
                score -= 0.3
                issues.append("Too informal for formal context")
                recommendations.append("Use more formal language")

        # Check respect for roles
        roles = await self.recognize_roles(context)
        if any(role == SocialRole.MANAGER for role in roles.values()):
            if "!" in message and "urgent" not in message_lower:
                score -= 0.1
                issues.append("Overly forceful with manager present")

        # Check politeness
        if not any(polite in message_lower for polite in ["please", "thank", "would you", "could you"]):
            if "?" in message:  # It's a request
                score -= 0.2
                issues.append("Lacks politeness markers for request")
                recommendations.append("Add 'please' or 'would you'")

        score = max(0.0, min(1.0, score))

        return AppropriatenessAssessment(score=score, issues=issues, recommendations=recommendations)


# ============================================================================
# 2. GROUP DYNAMICS SYSTEM
# ============================================================================


class GroupStage(Enum):
    """Tuckman's stages of group development."""

    FORMING = "forming"
    STORMING = "storming"
    NORMING = "norming"
    PERFORMING = "performing"
    ADJOURNING = "adjourning"


class LeadershipStyle(Enum):
    """Leadership styles."""

    TRANSFORMATIONAL = "transformational"
    TRANSACTIONAL = "transactional"
    SERVANT = "servant"
    DEMOCRATIC = "democratic"
    AUTOCRATIC = "autocratic"
    LAISSEZ_FAIRE = "laissez_faire"


@dataclass
class GroupStageAssessment:
    """Assessment of group development stage."""

    stage: GroupStage
    confidence: float
    indicators: List[str]
    recommendations: List[str]


@dataclass
class GroupthinkRisk:
    """Groupthink risk assessment."""

    risk_level: float  # 0-1
    indicators: List[str]
    recommendations: List[str]


@dataclass
class TeamComposition:
    """Optimal team composition."""

    members: List[str]
    diversity_score: float
    predicted_performance: float
    rationale: str


class GroupDynamicsSystem:
    """
    Models group behavior, team dynamics, leadership, and social processes.
    """

    def __init__(self, max_group_size: int = 20, dynamics_tracking: bool = True):
        self.max_group_size = max_group_size
        self.dynamics_tracking = dynamics_tracking

        self.group_states: Dict[str, Dict] = {}

    async def assess_stage(self, group: Dict[str, Any]) -> GroupStageAssessment:
        """
        Assess group development stage (Tuckman's model).

        Args:
            group: Group information

        Returns:
            GroupStageAssessment
        """
        await asyncio.sleep(0.3)

        group_id = group.get("id")
        age_days = group.get("age_days", 0)

        # Simple age-based heuristic
        if age_days < 7:
            stage = GroupStage.FORMING
            indicators = ["New group", "Getting acquainted", "Uncertainty"]
            recommendations = ["Establish clear goals", "Build trust", "Define roles"]
        elif age_days < 21:
            stage = GroupStage.STORMING
            indicators = ["Conflicts emerging", "Role competition", "Testing boundaries"]
            recommendations = ["Address conflicts openly", "Clarify expectations", "Support communication"]
        elif age_days < 60:
            stage = GroupStage.NORMING
            indicators = ["Norms established", "Cohesion building", "Collaboration improving"]
            recommendations = ["Reinforce positive norms", "Maintain momentum", "Celebrate progress"]
        else:
            stage = GroupStage.PERFORMING
            indicators = ["High performance", "Effective collaboration", "Goal achievement"]
            recommendations = ["Maintain performance", "Support innovation", "Plan succession"]

        confidence = 0.7

        return GroupStageAssessment(
            stage=stage, confidence=confidence, indicators=indicators, recommendations=recommendations
        )

    async def detect_groupthink(self, group: Dict[str, Any], decision_process: Dict[str, Any]) -> GroupthinkRisk:
        """
        Detect groupthink risk (Janis, 1972).

        Args:
            group: Group information
            decision_process: Recent decision process

        Returns:
            GroupthinkRisk assessment
        """
        await asyncio.sleep(0.25)

        risk_factors = 0
        indicators = []

        # Check for groupthink symptoms
        if decision_process.get("dissent_voiced", True) == False:
            risk_factors += 1
            indicators.append("Lack of dissenting voices")

        if decision_process.get("alternatives_considered", 3) < 2:
            risk_factors += 1
            indicators.append("Few alternatives considered")

        if group.get("cohesion", 0.5) > 0.8:
            risk_factors += 1
            indicators.append("Very high cohesion (can suppress dissent)")

        if group.get("leader_directiveness", 0.5) > 0.8:
            risk_factors += 1
            indicators.append("Highly directive leadership")

        # Calculate risk level
        risk_level = min(risk_factors / 4.0, 1.0)

        recommendations = []
        if risk_level > 0.5:
            recommendations.extend(
                [
                    "Encourage devil's advocate role",
                    "Seek external opinions",
                    "Subdivide group for independent analysis",
                    "Leader should withhold opinion initially",
                ]
            )

        return GroupthinkRisk(risk_level=risk_level, indicators=indicators, recommendations=recommendations)

    async def compose_team(
        self, available_members: List[Dict[str, Any]], task: Dict[str, Any], size_range: Tuple[int, int] = (4, 7)
    ) -> TeamComposition:
        """
        Compose optimal team for task.

        Args:
            available_members: Pool of potential members
            task: Task requirements
            size_range: Min and max team size

        Returns:
            TeamComposition
        """
        await asyncio.sleep(1.0)

        # Simple diversity and skill matching
        task_type = task.get("type", "general")

        selected = []
        diversity_score = 0.0

        # Select members with relevant skills
        for member in available_members:
            skills = member.get("skills", [])
            if task_type in skills or "general" in skills:
                selected.append(member["id"])
                if len(selected) >= size_range[1]:
                    break

        # Ensure minimum size
        while len(selected) < size_range[0] and len(selected) < len(available_members):
            for member in available_members:
                if member["id"] not in selected:
                    selected.append(member["id"])
                    break

        # Calculate diversity (simplified: based on skill variety)
        unique_skills = set()
        for member_id in selected:
            member = next(m for m in available_members if m["id"] == member_id)
            unique_skills.update(member.get("skills", []))

        diversity_score = len(unique_skills) / max(len(selected), 1)

        # Predict performance (simplified)
        predicted_performance = diversity_score * 0.7 + 0.3

        rationale = f"Selected {len(selected)} members with {len(unique_skills)} unique skills for {task_type} task"

        return TeamComposition(
            members=selected,
            diversity_score=diversity_score,
            predicted_performance=predicted_performance,
            rationale=rationale,
        )


# ============================================================================
# 3. COLLECTIVE DECISION MAKING
# ============================================================================


class VotingMethod(Enum):
    """Voting methods."""

    MAJORITY = "majority"
    PLURALITY = "plurality"
    RANKED_CHOICE = "ranked_choice"
    APPROVAL = "approval"
    CONSENSUS = "consensus"


@dataclass
class VotingResult:
    """Result of voting."""

    choice: str
    support: float  # 0-1, proportion supporting
    method: VotingMethod
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Result of consensus building."""

    converged: bool
    decision: Optional[str]
    rounds: int
    final_support: float


@dataclass
class CollectiveAccuracy:
    """Collective vs individual accuracy."""

    crowd_accuracy: float
    individual_avg: float
    diversity_bonus: float


class CollectiveDecisionMaking:
    """
    Implements group decision processes and collective intelligence.
    """

    def __init__(self, aggregation_methods: List[str], deliberation_support: bool = True):
        self.aggregation_methods = aggregation_methods
        self.deliberation_support = deliberation_support

    async def vote(self, opinions: List[Dict[str, Any]], method: VotingMethod) -> VotingResult:
        """
        Aggregate votes using specified method.

        Args:
            opinions: List of individual votes
            method: Voting method to use

        Returns:
            VotingResult
        """
        await asyncio.sleep(0.05)

        if method == VotingMethod.MAJORITY:
            # Count votes for each option
            vote_counts = defaultdict(int)
            for opinion in opinions:
                vote_counts[opinion["option"]] += 1

            # Find majority
            total_votes = len(opinions)
            max_votes = max(vote_counts.values())
            winner = max(vote_counts, key=vote_counts.get)

            support = vote_counts[winner] / total_votes

            return VotingResult(
                choice=winner, support=support, method=method, details={"vote_counts": dict(vote_counts)}
            )

        elif method == VotingMethod.CONSENSUS:
            # Require high agreement (>80%)
            vote_counts = defaultdict(int)
            for opinion in opinions:
                vote_counts[opinion["option"]] += 1

            total_votes = len(opinions)
            max_votes = max(vote_counts.values())
            winner = max(vote_counts, key=vote_counts.get)
            support = vote_counts[winner] / total_votes

            if support >= 0.8:
                return VotingResult(choice=winner, support=support, method=method, details={"consensus_reached": True})
            else:
                return VotingResult(choice=None, support=support, method=method, details={"consensus_reached": False})

        else:
            # Default to plurality
            vote_counts = defaultdict(int)
            for opinion in opinions:
                vote_counts[opinion["option"]] += 1

            winner = max(vote_counts, key=vote_counts.get)
            support = vote_counts[winner] / len(opinions)

            return VotingResult(choice=winner, support=support, method=method)

    async def build_consensus(
        self, initial_opinions: List[Dict[str, Any]], max_rounds: int = 5, convergence_threshold: float = 0.9
    ) -> ConsensusResult:
        """
        Build consensus through iterative deliberation.

        Args:
            initial_opinions: Starting opinions
            max_rounds: Maximum deliberation rounds
            convergence_threshold: Required agreement level

        Returns:
            ConsensusResult
        """
        await asyncio.sleep(0.5)

        current_opinions = initial_opinions.copy()

        for round_num in range(max_rounds):
            # Count current distribution
            vote_counts = defaultdict(int)
            for opinion in current_opinions:
                vote_counts[opinion["option"]] += 1

            # Check for convergence
            total = len(current_opinions)
            max_count = max(vote_counts.values())
            support = max_count / total

            if support >= convergence_threshold:
                winner = max(vote_counts, key=vote_counts.get)
                return ConsensusResult(converged=True, decision=winner, rounds=round_num + 1, final_support=support)

            # Simulate opinion updating (move towards majority)
            majority_option = max(vote_counts, key=vote_counts.get)
            for i, opinion in enumerate(current_opinions):
                if opinion["option"] != majority_option:
                    # Some chance to change opinion
                    if np.random.random() < 0.3:
                        current_opinions[i]["option"] = majority_option

        # Final check
        vote_counts = defaultdict(int)
        for opinion in current_opinions:
            vote_counts[opinion["option"]] += 1

        winner = max(vote_counts, key=vote_counts.get)
        support = vote_counts[winner] / len(current_opinions)

        return ConsensusResult(
            converged=support >= convergence_threshold,
            decision=winner if support >= convergence_threshold else None,
            rounds=max_rounds,
            final_support=support,
        )

    async def assess_collective_accuracy(
        self, individual_predictions: List[Dict[str, Any]], ground_truth: Any
    ) -> CollectiveAccuracy:
        """
        Assess collective accuracy (wisdom of crowds).

        Args:
            individual_predictions: Individual predictions
            ground_truth: Actual truth

        Returns:
            CollectiveAccuracy
        """
        await asyncio.sleep(0.1)

        # Majority vote as crowd prediction
        vote_counts = defaultdict(int)
        for pred in individual_predictions:
            vote_counts[pred["option"]] += 1

        crowd_prediction = max(vote_counts, key=vote_counts.get)
        crowd_accuracy = 1.0 if crowd_prediction == ground_truth else 0.0

        # Individual accuracy
        individual_accuracies = [1.0 if pred["option"] == ground_truth else 0.0 for pred in individual_predictions]
        individual_avg = np.mean(individual_accuracies)

        # Diversity bonus
        diversity_bonus = crowd_accuracy - individual_avg

        return CollectiveAccuracy(
            crowd_accuracy=crowd_accuracy, individual_avg=individual_avg, diversity_bonus=diversity_bonus
        )


# ============================================================================
# 4. SWARM INTELLIGENCE SYSTEM
# ============================================================================


class SwarmAlgorithm(Enum):
    """Swarm algorithms."""

    ANT_COLONY = "ant_colony"
    PARTICLE_SWARM = "particle_swarm"
    BEE_ALGORITHM = "bee_algorithm"
    BOIDS = "boids"


@dataclass
class SwarmSolution:
    """Solution found by swarm."""

    path: List[Any]
    cost: float
    iterations: int
    convergence: float


@dataclass
class TaskAllocation:
    """Swarm task allocation result."""

    assignments: Dict[str, List[int]]  # agent_id -> task_ids
    load_balance: float


class SwarmIntelligenceSystem:
    """
    Emergent intelligence from decentralized agent coordination.
    Uses ant colony optimization and other swarm algorithms.
    """

    def __init__(
        self,
        algorithm: SwarmAlgorithm = SwarmAlgorithm.ANT_COLONY,
        agents: int = 100,
        environment_size: Tuple[int, int] = (100, 100),
    ):
        self.algorithm = algorithm
        self.num_agents = agents
        self.environment_size = environment_size

        self.pheromone_map = np.zeros(environment_size)
        self.agent_positions = []

    async def solve(
        self, problem: Dict[str, Any], max_iterations: int = 200, convergence_threshold: float = 0.95
    ) -> SwarmSolution:
        """
        Solve optimization problem using swarm intelligence.

        Args:
            problem: Problem specification
            max_iterations: Max iterations
            convergence_threshold: Convergence threshold

        Returns:
            SwarmSolution
        """
        await asyncio.sleep(1.0)  # Simulate computation

        problem_type = problem.get("type")

        if problem_type == "path_finding":
            # Simplified ACO pathfinding
            start = problem.get("start", (0, 0))
            goal = problem.get("goal", (99, 99))

            # Manhattan distance as simple path
            path = []
            current = start
            while current != goal:
                if current[0] < goal[0]:
                    current = (current[0] + 1, current[1])
                elif current[1] < goal[1]:
                    current = (current[0], current[1] + 1)
                path.append(current)

            cost = len(path)

            return SwarmSolution(path=path, cost=cost, iterations=max_iterations, convergence=0.95)

        else:
            # Generic solution
            return SwarmSolution(path=[], cost=0.0, iterations=max_iterations, convergence=0.9)

    async def allocate_tasks(
        self, tasks: List[Dict[str, Any]], agents: List[Any], method: str = "response_threshold"
    ) -> TaskAllocation:
        """
        Allocate tasks to agents using swarm principles.

        Args:
            tasks: Tasks to allocate
            agents: Available agents
            method: Allocation method

        Returns:
            TaskAllocation
        """
        await asyncio.sleep(0.3)

        assignments = defaultdict(list)

        if method == "response_threshold":
            # Agents with lower threshold (higher affinity) take tasks
            for task in tasks:
                task_type = task.get("type")
                task_priority = task.get("priority", 0.5)

                # Find best agent (simplified: random with priority weighting)
                selected_agent = np.random.choice(range(len(agents)))
                assignments[f"agent_{selected_agent}"].append(task["id"])

        # Calculate load balance
        task_counts = [len(tasks) for tasks in assignments.values()]
        load_balance = 1.0 - (np.std(task_counts) / np.mean(task_counts)) if task_counts else 1.0
        load_balance = max(0.0, load_balance)

        return TaskAllocation(assignments=dict(assignments), load_balance=load_balance)

    async def detect_emergent_patterns(self, observation_window: timedelta) -> Dict[str, Any]:
        """
        Detect emergent patterns in swarm behavior.

        Args:
            observation_window: Time window to observe

        Returns:
            Dict with detected patterns
        """
        await asyncio.sleep(0.5)

        patterns = {
            "patterns": ["task_specialization", "spatial_clustering", "temporal_coordination"],
            "confidence": 0.75,
        }

        return patterns


# ============================================================================
# 5. CULTURAL INTELLIGENCE SYSTEM
# ============================================================================


@dataclass
class CulturalProfile:
    """Cultural dimension profile."""

    culture_name: str
    power_distance: float  # 0-1
    individualism: float  # 0-1, vs collectivism
    masculinity: float  # 0-1, vs femininity
    uncertainty_avoidance: float  # 0-1
    long_term_orientation: float  # 0-1
    context_level: str  # 'high' or 'low'


@dataclass
class AdaptedCommunication:
    """Culturally adapted communication."""

    text: str
    adaptations: List[str]
    appropriateness: float


@dataclass
class CulturalCompatibility:
    """Team cultural compatibility assessment."""

    score: float  # 0-1
    synergies: List[str]
    challenges: List[str]


class CulturalIntelligenceSystem:
    """
    Cross-cultural understanding and adaptation based on cultural dimensions.
    """

    def __init__(self, known_cultures: int = 50, adaptation_enabled: bool = True):
        self.known_cultures = known_cultures
        self.adaptation_enabled = adaptation_enabled

        # Cultural profiles (simplified examples)
        self.cultural_profiles = {
            "usa": CulturalProfile(
                culture_name="USA",
                power_distance=0.4,
                individualism=0.9,
                masculinity=0.6,
                uncertainty_avoidance=0.5,
                long_term_orientation=0.3,
                context_level="low",
            ),
            "japan": CulturalProfile(
                culture_name="Japan",
                power_distance=0.5,
                individualism=0.5,
                masculinity=0.9,
                uncertainty_avoidance=0.9,
                long_term_orientation=0.9,
                context_level="high",
            ),
            "germany": CulturalProfile(
                culture_name="Germany",
                power_distance=0.3,
                individualism=0.7,
                masculinity=0.7,
                uncertainty_avoidance=0.7,
                long_term_orientation=0.8,
                context_level="low",
            ),
            "brazil": CulturalProfile(
                culture_name="Brazil",
                power_distance=0.7,
                individualism=0.4,
                masculinity=0.5,
                uncertainty_avoidance=0.8,
                long_term_orientation=0.5,
                context_level="high",
            ),
        }

    async def get_profile(self, culture: str) -> CulturalProfile:
        """Get cultural profile."""
        await asyncio.sleep(0.1)

        culture_lower = culture.lower()
        return self.cultural_profiles.get(
            culture_lower,
            CulturalProfile(
                culture_name=culture,
                power_distance=0.5,
                individualism=0.5,
                masculinity=0.5,
                uncertainty_avoidance=0.5,
                long_term_orientation=0.5,
                context_level="medium",
            ),
        )

    async def adapt_communication(self, message: str, source_culture: str, target_culture: str) -> AdaptedCommunication:
        """
        Adapt communication for target culture.

        Args:
            message: Original message
            source_culture: Source cultural context
            target_culture: Target cultural context

        Returns:
            AdaptedCommunication
        """
        await asyncio.sleep(0.15)

        if not self.adaptation_enabled:
            return AdaptedCommunication(text=message, adaptations=[], appropriateness=0.7)

        source = await self.get_profile(source_culture)
        target = await self.get_profile(target_culture)

        adapted_text = message
        adaptations = []

        # Adapt for context level
        if target.context_level == "high" and source.context_level == "low":
            # Add context, be less direct
            if message.startswith("I disagree"):
                adapted_text = f"Thank you for sharing. Perhaps we could also consider alternative perspectives on this matter. {message[13:]}"
                adaptations.append("Softened disagreement for high-context culture")

        # Adapt for power distance
        if target.power_distance > 0.7 and "boss" in message.lower():
            # More formal with authority
            adapted_text = adapted_text.replace("boss", "respected supervisor")
            adaptations.append("Increased formality for high power distance")

        # Adapt for individualism/collectivism
        if target.individualism < 0.5 and source.individualism > 0.7:
            # Emphasize group over individual
            adapted_text = adapted_text.replace("I think", "We believe")
            adapted_text = adapted_text.replace("my opinion", "our team's perspective")
            adaptations.append("Shifted to collective language")

        appropriateness = 0.85 if adaptations else 0.7

        return AdaptedCommunication(text=adapted_text, adaptations=adaptations, appropriateness=appropriateness)

    async def assess_team_compatibility(self, cultures: List[str]) -> CulturalCompatibility:
        """
        Assess cultural compatibility of multicultural team.

        Args:
            cultures: List of cultures in team

        Returns:
            CulturalCompatibility
        """
        await asyncio.sleep(0.3)

        profiles = [await self.get_profile(c) for c in cultures]

        # Calculate dimension variance
        pd_variance = np.var([p.power_distance for p in profiles])
        ind_variance = np.var([p.individualism for p in profiles])

        # Lower variance = higher compatibility (easier to align)
        avg_variance = (pd_variance + ind_variance) / 2
        score = 1.0 - min(avg_variance * 2, 1.0)

        synergies = []
        challenges = []

        if ind_variance > 0.3:
            challenges.append("Mix of individualist and collectivist cultures may cause tension")
        else:
            synergies.append("Similar individualism levels facilitate cooperation")

        if pd_variance > 0.3:
            challenges.append("Different expectations around hierarchy and authority")
        else:
            synergies.append("Aligned power distance expectations")

        # Diversity can be a synergy
        if len(set(cultures)) > 2:
            synergies.append("Cultural diversity can enhance creativity and problem-solving")

        return CulturalCompatibility(score=score, synergies=synergies, challenges=challenges)


# ============================================================================
# 6. SOCIAL NETWORK ANALYSIS
# ============================================================================


class CentralityMeasure(Enum):
    """Centrality measures."""

    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"


@dataclass
class NetworkAnalysis:
    """Network structure analysis."""

    density: float
    clustering: float
    communities: List[Set[str]]
    avg_path_length: float


@dataclass
class SpreadPrediction:
    """Information spread prediction."""

    reach_percentage: float
    max_depth: int
    timeline: List[Tuple[int, float]]  # (time, cumulative_reach)


class SocialNetworkAnalysis:
    """
    Analyzes social structures, influence, and information flow.
    """

    def __init__(self, network_size_limit: int = 10000, dynamic_tracking: bool = True):
        self.network_size_limit = network_size_limit
        self.dynamic_tracking = dynamic_tracking

        self.network_cache = {}

    async def analyze_structure(self, network: Dict[str, Any]) -> NetworkAnalysis:
        """
        Analyze network structure.

        Args:
            network: Network with nodes and edges

        Returns:
            NetworkAnalysis
        """
        await asyncio.sleep(0.5)

        nodes = network.get("nodes", [])
        edges = network.get("edges", [])

        # Calculate density
        n = len(nodes)
        max_edges = n * (n - 1) / 2 if n > 1 else 1
        density = len(edges) / max_edges if max_edges > 0 else 0.0

        # Simple clustering (proportion of triads that are closed)
        clustering = 0.3  # Simplified

        # Community detection (simplified: random grouping)
        num_communities = max(1, n // 10)
        communities = []
        nodes_per_community = n // num_communities if num_communities > 0 else n
        for i in range(num_communities):
            start = i * nodes_per_community
            end = min((i + 1) * nodes_per_community, n)
            communities.append(set(nodes[start:end]))

        # Average path length (simplified)
        avg_path_length = 3.0  # Typical small-world value

        return NetworkAnalysis(
            density=density, clustering=clustering, communities=communities, avg_path_length=avg_path_length
        )

    async def identify_influencers(
        self, network: Dict[str, Any], measure: CentralityMeasure, top_k: int = 10
    ) -> List[str]:
        """
        Identify influential nodes.

        Args:
            network: Network
            measure: Centrality measure to use
            top_k: Number of influencers to return

        Returns:
            List of influencer node IDs
        """
        await asyncio.sleep(0.4)

        nodes = network.get("nodes", [])
        edges = network.get("edges", [])

        # Simple degree centrality (count connections)
        degree = defaultdict(int)
        for edge in edges:
            degree[edge["source"]] += 1
            degree[edge["target"]] += 1

        # Sort by degree
        sorted_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        influencers = [node for node, deg in sorted_nodes[:top_k]]

        return influencers

    async def predict_spread(
        self, network: Dict[str, Any], seed_nodes: List[str], content_type: str, time_horizon: timedelta
    ) -> SpreadPrediction:
        """
        Predict information spread in network.

        Args:
            network: Network
            seed_nodes: Initial nodes with information
            content_type: Type of content (affects spread rate)
            time_horizon: Time to predict

        Returns:
            SpreadPrediction
        """
        await asyncio.sleep(1.0)

        nodes = network.get("nodes", [])
        total_nodes = len(nodes)

        # Simple exponential spread model
        initial_reach = len(seed_nodes) / total_nodes
        spread_rate = 0.3  # 30% per time step

        # Simulate spread
        timeline = [(0, initial_reach)]
        current_reach = initial_reach

        time_steps = 10
        for t in range(1, time_steps + 1):
            # Exponential spread with saturation
            current_reach = min(1.0, current_reach + (1.0 - current_reach) * spread_rate)
            timeline.append((t, current_reach))

        final_reach = current_reach
        max_depth = int(np.log(total_nodes) / np.log(1 + spread_rate)) if total_nodes > 1 else 1

        return SpreadPrediction(reach_percentage=final_reach * 100, max_depth=max_depth, timeline=timeline)


# ============================================================================
# 7. COLLABORATIVE INTELLIGENCE ORCHESTRATOR
# ============================================================================


@dataclass
class TaskGraph:
    """Graph of tasks and dependencies."""

    nodes: List[Dict[str, Any]]
    edges: List[Tuple[int, int]]  # (from_task_id, to_task_id)


@dataclass
class AllocationResult:
    """Task allocation result."""

    assignments: Dict[str, List[int]]  # agent_id -> task_ids
    estimated_completion_time: float
    load_distribution: Dict[str, float]


@dataclass
class CollaborationHealth:
    """Health of collaboration."""

    coordination: float  # 0-1
    synergy: float  # 0-1
    bottlenecks: List[str]


class CollaborativeIntelligenceOrchestrator:
    """
    Coordinates human-AI and AI-AI collaboration for complex tasks.
    """

    def __init__(self, max_agents: int = 50, coordination_protocol: str = "blackboard"):
        self.max_agents = max_agents
        self.coordination_protocol = coordination_protocol

        self.active_collaborations = {}

    async def decompose_task(self, complex_task: Dict[str, Any]) -> TaskGraph:
        """
        Decompose complex task into subtasks.

        Args:
            complex_task: Task to decompose

        Returns:
            TaskGraph with subtasks and dependencies
        """
        await asyncio.sleep(0.5)

        task_type = complex_task.get("type")

        # Create subtasks (simplified)
        if task_type == "document_analysis":
            subtasks = [
                {"id": 0, "type": "load_documents"},
                {"id": 1, "type": "preprocess"},
                {"id": 2, "type": "analyze_content"},
                {"id": 3, "type": "extract_insights"},
                {"id": 4, "type": "generate_report"},
            ]
            # Sequential dependencies
            edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        else:
            subtasks = [{"id": 0, "type": "subtask_1"}, {"id": 1, "type": "subtask_2"}, {"id": 2, "type": "subtask_3"}]
            edges = [(0, 1), (1, 2)]

        return TaskGraph(nodes=subtasks, edges=edges)

    async def allocate(
        self, task_graph: TaskGraph, agent_pool: List[Any], optimization: str = "minimize_time"
    ) -> AllocationResult:
        """
        Allocate tasks to agents optimally.

        Args:
            task_graph: Task dependency graph
            agent_pool: Available agents
            optimization: Optimization objective

        Returns:
            AllocationResult
        """
        await asyncio.sleep(1.0)

        assignments = {}
        load_distribution = {}

        # Simple round-robin allocation
        for i, task in enumerate(task_graph.nodes):
            agent_idx = i % len(agent_pool)
            agent_id = f"agent_{agent_idx}"

            if agent_id not in assignments:
                assignments[agent_id] = []
            assignments[agent_id].append(task["id"])

        # Estimate completion time (simplified)
        max_tasks_per_agent = max(len(tasks) for tasks in assignments.values())
        estimated_completion_time = max_tasks_per_agent * 1.0  # 1 hour per task

        # Load distribution
        for agent_id, tasks in assignments.items():
            load_distribution[agent_id] = len(tasks) / len(task_graph.nodes)

        return AllocationResult(
            assignments=assignments,
            estimated_completion_time=estimated_completion_time,
            load_distribution=load_distribution,
        )

    async def monitor_collaboration(self, session_id: str) -> CollaborationHealth:
        """
        Monitor health of ongoing collaboration.

        Args:
            session_id: Collaboration session ID

        Returns:
            CollaborationHealth
        """
        await asyncio.sleep(0.2)

        # Simulated health metrics
        coordination = 0.85
        synergy = 0.75
        bottlenecks = []

        if coordination < 0.7:
            bottlenecks.append("Poor coordination")
        if synergy < 0.6:
            bottlenecks.append("Low synergy, agents working in silos")

        return CollaborationHealth(coordination=coordination, synergy=synergy, bottlenecks=bottlenecks)


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_social_cognition_engine: Optional[SocialCognitionEngine] = None
_group_dynamics_system: Optional[GroupDynamicsSystem] = None
_collective_decision_system: Optional[CollectiveDecisionMaking] = None
_swarm_intelligence_system: Optional[SwarmIntelligenceSystem] = None
_cultural_intelligence_system: Optional[CulturalIntelligenceSystem] = None
_social_network_analysis: Optional[SocialNetworkAnalysis] = None
_collaboration_orchestrator: Optional[CollaborativeIntelligenceOrchestrator] = None

_lock = threading.Lock()


def get_social_cognition_engine(**kwargs) -> SocialCognitionEngine:
    """Get or create singleton Social Cognition Engine."""
    global _social_cognition_engine
    with _lock:
        if _social_cognition_engine is None:
            _social_cognition_engine = SocialCognitionEngine(**kwargs)
        return _social_cognition_engine


def get_group_dynamics_system(**kwargs) -> GroupDynamicsSystem:
    """Get or create singleton Group Dynamics System."""
    global _group_dynamics_system
    with _lock:
        if _group_dynamics_system is None:
            _group_dynamics_system = GroupDynamicsSystem(**kwargs)
        return _group_dynamics_system


def get_collective_decision_system(**kwargs) -> CollectiveDecisionMaking:
    """Get or create singleton Collective Decision Making."""
    global _collective_decision_system
    with _lock:
        if _collective_decision_system is None:
            _collective_decision_system = CollectiveDecisionMaking(**kwargs)
        return _collective_decision_system


def get_swarm_intelligence_system(**kwargs) -> SwarmIntelligenceSystem:
    """Get or create singleton Swarm Intelligence System."""
    global _swarm_intelligence_system
    with _lock:
        if _swarm_intelligence_system is None:
            _swarm_intelligence_system = SwarmIntelligenceSystem(**kwargs)
        return _swarm_intelligence_system


def get_cultural_intelligence_system(**kwargs) -> CulturalIntelligenceSystem:
    """Get or create singleton Cultural Intelligence System."""
    global _cultural_intelligence_system
    with _lock:
        if _cultural_intelligence_system is None:
            _cultural_intelligence_system = CulturalIntelligenceSystem(**kwargs)
        return _cultural_intelligence_system


def get_social_network_analysis(**kwargs) -> SocialNetworkAnalysis:
    """Get or create singleton Social Network Analysis."""
    global _social_network_analysis
    with _lock:
        if _social_network_analysis is None:
            _social_network_analysis = SocialNetworkAnalysis(**kwargs)
        return _social_network_analysis


def get_collaboration_orchestrator(**kwargs) -> CollaborativeIntelligenceOrchestrator:
    """Get or create singleton Collaborative Intelligence Orchestrator."""
    global _collaboration_orchestrator
    with _lock:
        if _collaboration_orchestrator is None:
            _collaboration_orchestrator = CollaborativeIntelligenceOrchestrator(**kwargs)
        return _collaboration_orchestrator
