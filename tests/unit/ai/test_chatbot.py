"""
Comprehensive tests for ai/chatbot.py module

Tests organized by size:
- Small: Enums, dataclasses
- Medium: NLP engine, chatbot handlers
- Large: Full conversation workflows

Test coverage: ~80% target
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.ai.chatbot import (
    ChatbotEngine,
    Conversation,
    Entity,
    EntityType,
    Intent,
    IntentType,
    Message,
    NLPEngine,
    configure_chatbot,
    get_chatbot,
)

# ============================================================================
# SMALL TESTS - Enums, Dataclasses
# ============================================================================

pytestmark = [pytest.mark.small, pytest.mark.unit]


class TestIntentType:
    """Test IntentType enum."""

    def test_all_intent_types_defined(self):
        """Test all intent types are defined."""
        intents = [i for i in IntentType]
        assert len(intents) >= 11

        assert IntentType.GREETING in intents
        assert IntentType.SEARCH_SERVICE in intents
        assert IntentType.CREATE_SERVICE in intents
        assert IntentType.HELP in intents
        assert IntentType.GOODBYE in intents
        assert IntentType.UNKNOWN in intents

    def test_intent_type_values(self):
        """Test intent type enum values."""
        assert IntentType.GREETING.value == "greeting"
        assert IntentType.SEARCH_SERVICE.value == "search_service"
        assert IntentType.CALCULATE_COST.value == "calculate_cost"


class TestEntityType:
    """Test EntityType enum."""

    def test_all_entity_types_defined(self):
        """Test all entity types are defined."""
        entities = [e for e in EntityType]
        assert len(entities) >= 6

        assert EntityType.SERVICE_NAME in entities
        assert EntityType.REGION in entities
        assert EntityType.RATE in entities
        assert EntityType.HOURS in entities

    def test_entity_type_values(self):
        """Test entity type enum values."""
        assert EntityType.REGION.value == "region"
        assert EntityType.RATE.value == "rate"
        assert EntityType.NUMBER.value == "number"


class TestEntityDataclass:
    """Test Entity dataclass."""

    def test_entity_creation(self):
        """Test creating entity."""
        entity = Entity(
            type=EntityType.REGION,
            value="Bavaria",
            confidence=0.9,
            start=10,
            end=17
        )

        assert entity.type == EntityType.REGION
        assert entity.value == "Bavaria"
        assert entity.confidence == 0.9
        assert entity.start == 10
        assert entity.end == 17


class TestIntentDataclass:
    """Test Intent dataclass."""

    def test_intent_creation(self):
        """Test creating intent."""
        entity = Entity(EntityType.REGION, "Bavaria", 0.9, 0, 7)
        intent = Intent(
            type=IntentType.SEARCH_SERVICE,
            confidence=0.85,
            entities=[entity]
        )

        assert intent.type == IntentType.SEARCH_SERVICE
        assert intent.confidence == 0.85
        assert len(intent.entities) == 1

    def test_intent_without_entities(self):
        """Test intent without entities."""
        intent = Intent(type=IntentType.GREETING, confidence=0.9)

        assert intent.entities == []


class TestMessageDataclass:
    """Test Message dataclass."""

    def test_message_creation(self):
        """Test creating message."""
        msg = Message(
            id="msg_1",
            content="Hello",
            sender="user",
            timestamp=datetime.now()
        )

        assert msg.id == "msg_1"
        assert msg.content == "Hello"
        assert msg.sender == "user"
        assert msg.intent is None

    def test_message_with_intent(self):
        """Test message with intent."""
        intent = Intent(IntentType.GREETING, 0.9)
        msg = Message(
            id="msg_1",
            content="Hi there",
            sender="user",
            timestamp=datetime.now(),
            intent=intent
        )

        assert msg.intent.type == IntentType.GREETING


class TestConversationDataclass:
    """Test Conversation dataclass."""

    def test_conversation_creation(self):
        """Test creating conversation."""
        conv = Conversation(id="conv_1", user_id=123)

        assert conv.id == "conv_1"
        assert conv.user_id == 123
        assert conv.messages == []
        assert conv.context == {}

    def test_conversation_with_messages(self):
        """Test conversation with messages."""
        msg = Message("msg_1", "Hello", "user", datetime.now())
        conv = Conversation(id="conv_1", user_id=123, messages=[msg])

        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"


# ============================================================================
# MEDIUM TESTS - NLP Engine, Chatbot Handlers
# ============================================================================


@pytest.mark.medium
@pytest.mark.integration
class TestNLPEngine:
    """Test NLPEngine class."""

    def test_nlp_engine_initialization(self):
        """Test creating NLP engine."""
        nlp = NLPEngine()

        assert nlp.intent_patterns is not None
        assert len(nlp.intent_patterns) > 0

    def test_detect_greeting_intent(self):
        """Test detecting greeting intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("Hello, how are you?")

        assert intent.type == IntentType.GREETING
        assert intent.confidence > 0

    def test_detect_search_service_intent(self):
        """Test detecting search service intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("Show me all services in Bavaria")

        assert intent.type == IntentType.SEARCH_SERVICE

    def test_detect_calculate_cost_intent(self):
        """Test detecting calculate cost intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("How much does 10 hours at 50€/h cost?")

        assert intent.type == IntentType.CALCULATE_COST

    def test_detect_help_intent(self):
        """Test detecting help intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("Can you help me?")

        assert intent.type == IntentType.HELP

    def test_detect_goodbye_intent(self):
        """Test detecting goodbye intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("Goodbye, see you later")

        assert intent.type == IntentType.GOODBYE

    def test_detect_unknown_intent(self):
        """Test detecting unknown intent."""
        nlp = NLPEngine()

        intent = nlp.detect_intent("xyzabc random gibberish")

        assert intent.type == IntentType.UNKNOWN

    def test_extract_region_entity(self):
        """Test extracting region entity."""
        nlp = NLPEngine()

        entities = nlp.extract_entities("Services in Bavaria")

        region_entities = [e for e in entities if e.type == EntityType.REGION]
        assert len(region_entities) > 0
        assert region_entities[0].value == "Bavaria"

    def test_extract_rate_entity(self):
        """Test extracting rate entity."""
        nlp = NLPEngine()

        entities = nlp.extract_entities("The rate is 50€ per hour")

        rate_entities = [e for e in entities if e.type == EntityType.RATE]
        assert len(rate_entities) > 0
        assert "50" in rate_entities[0].value

    def test_extract_hours_entity(self):
        """Test extracting hours entity."""
        nlp = NLPEngine()

        entities = nlp.extract_entities("I worked 8 hours")

        hours_entities = [e for e in entities if e.type == EntityType.HOURS]
        assert len(hours_entities) > 0
        assert hours_entities[0].value == "8"

    def test_extract_multiple_entities(self):
        """Test extracting multiple entities."""
        nlp = NLPEngine()

        text = "Calculate 10 hours at 50€ in Bavaria"
        entities = nlp.extract_entities(text)

        # Should find hours, rate, and region
        types = {e.type for e in entities}
        assert EntityType.HOURS in types or EntityType.NUMBER in types
        assert EntityType.RATE in types
        assert EntityType.REGION in types


@pytest.mark.medium
@pytest.mark.integration
class TestChatbotEngine:
    """Test ChatbotEngine class."""

    def test_chatbot_engine_initialization(self):
        """Test creating chatbot engine."""
        bot = ChatbotEngine()

        assert bot.nlp is not None
        assert bot.conversations == {}

    def test_get_or_create_conversation(self):
        """Test getting or creating conversation."""
        bot = ChatbotEngine()

        conv1 = bot.get_or_create_conversation(user_id=123)
        conv2 = bot.get_or_create_conversation(user_id=123)

        # Should return same conversation
        assert conv1 is conv2
        assert conv1.user_id == 123

    def test_process_greeting_message(self):
        """Test processing greeting message."""
        bot = ChatbotEngine()

        response = bot.process_message(user_id=1, message="Hello!")

        assert isinstance(response, str)
        assert len(response) > 0
        # Should be a greeting response
        assert any(word in response.lower() for word in ["hello", "hi", "greetings"])

    def test_process_help_message(self):
        """Test processing help message."""
        bot = ChatbotEngine()

        response = bot.process_message(user_id=1, message="Help me please")

        assert isinstance(response, str)
        assert "help" in response.lower() or "can" in response.lower()

    def test_process_goodbye_message(self):
        """Test processing goodbye message."""
        bot = ChatbotEngine()

        response = bot.process_message(user_id=1, message="Goodbye")

        assert isinstance(response, str)
        assert any(word in response.lower() for word in ["goodbye", "bye", "see you"])

    def test_handle_calculate_cost(self):
        """Test calculating cost."""
        bot = ChatbotEngine()

        response = bot.process_message(user_id=1, message="How much for 10 hours at 50 euro")

        assert isinstance(response, str)
        # Should mention the total (500) or ask for more info
        assert "500" in response or "total" in response.lower() or "provide" in response.lower()

    def test_handle_search_service_without_database(self):
        """Test search service without database."""
        bot = ChatbotEngine(database=None)

        response = bot.process_message(user_id=1, message="Find services")

        assert "database" in response.lower() or "not available" in response.lower()

    def test_handle_get_statistics_without_database(self):
        """Test statistics without database."""
        bot = ChatbotEngine(database=None)

        response = bot.process_message(user_id=1, message="Show statistics")

        assert "statistics" in response.lower() or "not available" in response.lower()

    def test_conversation_history(self):
        """Test getting conversation history."""
        bot = ChatbotEngine()

        bot.process_message(user_id=1, message="Hello")
        bot.process_message(user_id=1, message="Help")

        history = bot.get_conversation_history(user_id=1)

        # Should have 4 messages (2 user + 2 bot)
        assert len(history) == 4
        assert history[0].sender == "user"
        assert history[1].sender == "bot"

    def test_clear_conversation(self):
        """Test clearing conversation."""
        bot = ChatbotEngine()

        bot.process_message(user_id=1, message="Hello")
        bot.clear_conversation(user_id=1)

        history = bot.get_conversation_history(user_id=1)

        # Should be empty (new conversation)
        assert len(history) == 0


# ============================================================================
# LARGE TESTS - Full Conversation Workflows
# ============================================================================


@pytest.mark.large
@pytest.mark.e2e
class TestChatbotConversationFlows:
    """Test complete chatbot conversation flows."""

    def test_full_conversation_flow(self):
        """Test complete multi-turn conversation."""
        bot = ChatbotEngine()
        user_id = 100

        # Turn 1: Greeting
        response1 = bot.process_message(user_id, "Hi there")
        assert "hello" in response1.lower() or "hi" in response1.lower()

        # Turn 2: Help
        response2 = bot.process_message(user_id, "What can you do?")
        assert len(response2) > 0

        # Turn 3: Calculate
        response3 = bot.process_message(user_id, "How much is 5 hours at 100 euro")
        assert "500" in response3 or "provide" in response3.lower()

        # Turn 4: Goodbye
        response4 = bot.process_message(user_id, "Goodbye")
        assert any(word in response4.lower() for word in ["goodbye", "bye", "see you"])

        # Check conversation history
        history = bot.get_conversation_history(user_id)
        assert len(history) == 8  # 4 user + 4 bot messages

    def test_context_preservation_across_turns(self):
        """Test context preservation in conversation."""
        bot = ChatbotEngine()
        user_id = 200

        # Send multiple messages
        bot.process_message(user_id, "Hello")
        bot.process_message(user_id, "Help me")
        bot.process_message(user_id, "Thanks")

        # Get conversation
        conv = bot.get_or_create_conversation(user_id)

        # Context should be maintained
        assert len(conv.messages) > 0
        assert conv.user_id == user_id

    def test_multiple_users_separate_conversations(self):
        """Test separate conversations for different users."""
        bot = ChatbotEngine()

        # User 1
        bot.process_message(user_id=1, message="Hello from user 1")
        history1 = bot.get_conversation_history(user_id=1)

        # User 2
        bot.process_message(user_id=2, message="Hello from user 2")
        history2 = bot.get_conversation_history(user_id=2)

        # Histories should be different
        assert history1 != history2
        assert "user 1" in history1[0].content
        assert "user 2" in history2[0].content

    def test_get_chatbot_singleton(self):
        """Test get_chatbot() function."""
        bot1 = get_chatbot()
        bot2 = get_chatbot()

        # Should return same instance
        assert bot1 is bot2

    def test_configure_chatbot(self):
        """Test configure_chatbot() function."""
        mock_db = MagicMock()

        configure_chatbot(database=mock_db, llm_enabled=True)
        bot = get_chatbot()

        assert bot.database is mock_db
        assert bot.llm_enabled is True

    def test_conversation_with_create_service_request(self):
        """Test conversation for creating service."""
        bot = ChatbotEngine()

        response = bot.process_message(
            user_id=1,
            message="Create a new service in Bavaria at 75€ for 8 hours"
        )

        # Should acknowledge service creation
        assert isinstance(response, str)
        assert len(response) > 0
