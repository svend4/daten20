"""
AI Chatbot Engine

Provides intelligent conversational interface with NLP and LLM integration.
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re


class IntentType(str, Enum):
    """Chat intent types"""
    GREETING = "greeting"
    SEARCH_SERVICE = "search_service"
    CREATE_SERVICE = "create_service"
    UPDATE_SERVICE = "update_service"
    DELETE_SERVICE = "delete_service"
    CALCULATE_COST = "calculate_cost"
    GENERATE_REPORT = "generate_report"
    EXPORT_DATA = "export_data"
    GET_STATISTICS = "get_statistics"
    HELP = "help"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Entity types for extraction"""
    SERVICE_NAME = "service_name"
    REGION = "region"
    RATE = "rate"
    HOURS = "hours"
    DATE = "date"
    NUMBER = "number"


@dataclass
class Entity:
    """Extracted entity"""
    type: EntityType
    value: Any
    confidence: float
    start: int
    end: int


@dataclass
class Intent:
    """Detected intent"""
    type: IntentType
    confidence: float
    entities: List[Entity] = field(default_factory=list)


@dataclass
class Message:
    """Chat message"""
    id: str
    content: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime
    intent: Optional[Intent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Conversation context"""
    id: str
    user_id: int
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


class NLPEngine:
    """Natural Language Processing engine"""

    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            IntentType.GREETING: [
                r'\b(hi|hello|hey|greetings)\b',
                r'\b(good morning|good afternoon|good evening)\b',
            ],
            IntentType.SEARCH_SERVICE: [
                r'\b(find|search|look for|show me)\b.*\b(service|services)\b',
                r'\b(what|which)\b.*\b(service|services)\b',
                r'\blist.*\b(service|services)\b',
            ],
            IntentType.CREATE_SERVICE: [
                r'\b(create|add|new)\b.*\b(service)\b',
                r'\bregister.*\b(service)\b',
            ],
            IntentType.CALCULATE_COST: [
                r'\b(calculate|compute|estimate)\b.*\b(cost|price|rate)\b',
                r'\bhow much\b',
            ],
            IntentType.GET_STATISTICS: [
                r'\b(statistics|stats|analytics|metrics)\b',
                r'\b(how many|count)\b.*\b(service|services)\b',
            ],
            IntentType.HELP: [
                r'\b(help|assist|support)\b',
                r'\bwhat can you do\b',
            ],
            IntentType.GOODBYE: [
                r'\b(bye|goodbye|see you|exit|quit)\b',
            ],
        }

        # Entity extraction patterns
        self.entity_patterns = {
            EntityType.REGION: r'\b(Bavaria|Berlin|Hamburg|Saxony|Bremen|Brandenburg)\b',
            EntityType.RATE: r'(\d+(?:\.\d+)?)\s*(?:€|EUR|euro)',
            EntityType.HOURS: r'(\d+)\s*(?:hours?|hrs?)',
            EntityType.NUMBER: r'\b(\d+)\b',
        }

    def detect_intent(self, text: str) -> Intent:
        """Detect intent from user message"""
        text_lower = text.lower()

        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    confidence = 0.8  # Base confidence
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type

        return Intent(type=best_intent, confidence=best_confidence)

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        entities = []

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    type=entity_type,
                    value=match.group(1) if match.groups() else match.group(0),
                    confidence=0.9,
                    start=match.start(),
                    end=match.end()
                ))

        return entities


class ChatbotEngine:
    """Main chatbot engine"""

    def __init__(self, database=None, llm_enabled: bool = False):
        self.database = database
        self.llm_enabled = llm_enabled
        self.nlp = NLPEngine()

        # Active conversations
        self.conversations: Dict[str, Conversation] = {}

        # Response templates
        self.templates = {
            IntentType.GREETING: [
                "Hello! I'm your DMS assistant. How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! I'm here to help with your document management needs.",
            ],
            IntentType.HELP: [
                "I can help you with:\n"
                "- Search and manage services\n"
                "- Calculate costs\n"
                "- Generate reports\n"
                "- Export data\n"
                "- View statistics\n\n"
                "What would you like to do?",
            ],
            IntentType.GOODBYE: [
                "Goodbye! Feel free to return if you need help.",
                "See you later! Have a great day!",
            ],
            IntentType.UNKNOWN: [
                "I'm not sure I understand. Could you rephrase that?",
                "I didn't quite get that. Can you try asking differently?",
            ],
        }

    def get_or_create_conversation(self, user_id: int) -> Conversation:
        """Get or create conversation for user"""
        conv_id = f"conv_{user_id}"

        if conv_id not in self.conversations:
            self.conversations[conv_id] = Conversation(
                id=conv_id,
                user_id=user_id
            )

        return self.conversations[conv_id]

    def process_message(self, user_id: int, message: str) -> str:
        """Process user message and generate response"""
        conversation = self.get_or_create_conversation(user_id)
        conversation.last_active = datetime.now()

        # Create message
        user_message = Message(
            id=f"msg_{len(conversation.messages)}",
            content=message,
            sender="user",
            timestamp=datetime.now()
        )

        # Detect intent
        intent = self.nlp.detect_intent(message)
        intent.entities = self.nlp.extract_entities(message)
        user_message.intent = intent

        # Add to conversation
        conversation.messages.append(user_message)

        # Generate response
        response = self._generate_response(conversation, intent)

        # Create bot message
        bot_message = Message(
            id=f"msg_{len(conversation.messages)}",
            content=response,
            sender="bot",
            timestamp=datetime.now()
        )

        conversation.messages.append(bot_message)

        return response

    def _generate_response(self, conversation: Conversation, intent: Intent) -> str:
        """Generate response based on intent"""

        if intent.type == IntentType.SEARCH_SERVICE:
            return self._handle_search_service(intent)

        elif intent.type == IntentType.CREATE_SERVICE:
            return self._handle_create_service(conversation, intent)

        elif intent.type == IntentType.CALCULATE_COST:
            return self._handle_calculate_cost(intent)

        elif intent.type == IntentType.GET_STATISTICS:
            return self._handle_get_statistics()

        elif intent.type in self.templates:
            return self.templates[intent.type][0]

        else:
            return self.templates[IntentType.UNKNOWN][0]

    def _handle_search_service(self, intent: Intent) -> str:
        """Handle service search"""
        if not self.database:
            return "Database not available. Please try again later."

        # Extract search criteria
        region = None
        for entity in intent.entities:
            if entity.type == EntityType.REGION:
                region = entity.value

        # Query database
        cursor = self.database.conn.cursor()

        if region:
            cursor.execute(
                "SELECT service_name, region, brutto_rate FROM services WHERE region LIKE ? LIMIT 5",
                (f"%{region}%",)
            )
        else:
            cursor.execute(
                "SELECT service_name, region, brutto_rate FROM services LIMIT 5"
            )

        results = cursor.fetchall()

        if not results:
            return f"No services found{' in ' + region if region else ''}."

        response = f"Found {len(results)} services:\n\n"
        for name, reg, rate in results:
            response += f"• {name} ({reg}) - {rate}€/h\n"

        return response

    def _handle_create_service(self, conversation: Conversation, intent: Intent) -> str:
        """Handle service creation"""
        # Check if we have all required info
        required = ['service_name', 'region', 'rate', 'hours']
        missing = []

        # Extract entities
        extracted = {}
        for entity in intent.entities:
            if entity.type == EntityType.REGION:
                extracted['region'] = entity.value
            elif entity.type == EntityType.RATE:
                extracted['rate'] = float(entity.value)
            elif entity.type == EntityType.HOURS:
                extracted['hours'] = int(entity.value)

        # Check what's missing
        for req in required:
            if req not in extracted and req not in conversation.context:
                missing.append(req)

        if missing:
            conversation.context['pending_action'] = 'create_service'
            conversation.context['extracted'] = extracted
            return f"To create a service, I need: {', '.join(missing)}. Please provide them."

        # Create service
        return "Service creation initiated! Please confirm the details to proceed."

    def _handle_calculate_cost(self, intent: Intent) -> str:
        """Handle cost calculation"""
        # Extract rate and hours
        rate = None
        hours = None

        for entity in intent.entities:
            if entity.type == EntityType.RATE:
                rate = float(entity.value)
            elif entity.type == EntityType.HOURS:
                hours = int(entity.value)

        if rate and hours:
            total = rate * hours
            return f"For {hours} hours at {rate}€/h, the total cost is {total}€."
        else:
            return "Please provide both hourly rate and number of hours for calculation."

    def _handle_get_statistics(self) -> str:
        """Handle statistics request"""
        if not self.database:
            return "Statistics not available. Database not connected."

        cursor = self.database.conn.cursor()

        # Total services
        cursor.execute("SELECT COUNT(*) FROM services")
        total = cursor.fetchone()[0]

        # Services by region
        cursor.execute("""
            SELECT region, COUNT(*) as count
            FROM services
            GROUP BY region
            ORDER BY count DESC
            LIMIT 3
        """)
        regions = cursor.fetchall()

        response = f"📊 System Statistics:\n\n"
        response += f"Total Services: {total}\n\n"
        response += "Top Regions:\n"
        for region, count in regions:
            response += f"• {region}: {count} services\n"

        return response

    def get_conversation_history(self, user_id: int) -> List[Message]:
        """Get conversation history for user"""
        conversation = self.get_or_create_conversation(user_id)
        return conversation.messages

    def clear_conversation(self, user_id: int):
        """Clear conversation for user"""
        conv_id = f"conv_{user_id}"
        if conv_id in self.conversations:
            del self.conversations[conv_id]


# Chat UI HTML template
CHAT_UI_HTML = """
<div id="chat-container">
    <div id="chat-header">
        <h3>DMS Assistant</h3>
        <button id="chat-minimize">_</button>
    </div>
    <div id="chat-messages"></div>
    <div id="chat-input-container">
        <input type="text" id="chat-input" placeholder="Type your message...">
        <button id="chat-send">Send</button>
    </div>
</div>

<style>
#chat-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
}

#chat-header {
    background: #0d6efd;
    color: white;
    padding: 15px;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
}

.message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    max-width: 80%;
}

.message.user {
    background: #e3f2fd;
    margin-left: auto;
}

.message.bot {
    background: #f5f5f5;
}

#chat-input-container {
    display: flex;
    padding: 10px;
    border-top: 1px solid #ddd;
}

#chat-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

#chat-send {
    margin-left: 10px;
    padding: 10px 20px;
    background: #0d6efd;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
</style>

<script>
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
const chatMessages = document.getElementById('chat-messages');

function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    chatInput.value = '';

    // Send to backend
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    });

    const data = await response.json();
    addMessage(data.response, 'bot');
}

chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
</script>
"""


# Global instance
_chatbot: Optional[ChatbotEngine] = None


def get_chatbot() -> ChatbotEngine:
    """Get global chatbot instance"""
    global _chatbot

    if _chatbot is None:
        _chatbot = ChatbotEngine()

    return _chatbot


def configure_chatbot(database=None, llm_enabled: bool = False):
    """Configure chatbot"""
    global _chatbot
    _chatbot = ChatbotEngine(database, llm_enabled)
