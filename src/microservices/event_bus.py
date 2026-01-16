#!/usr/bin/env python3
"""
Event-Driven Architecture Module

Event bus with CQRS and Event Sourcing support for microservices.

Key Features:
- Event Sourcing (append-only event log)
- CQRS (Command Query Responsibility Segregation)
- Pub/Sub messaging
- Event replay and projection
- Saga pattern for distributed transactions
- Dead letter queue
- Event versioning
- Message deduplication

Dependencies:
- None (pure Python implementation)
"""

import json
import logging
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class EventPriority(str, Enum):
    """Event priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CommandStatus(str, Enum):
    """Command execution status"""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"


@dataclass
class Event:
    """Domain event"""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Deserialize event from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            aggregate_id=data["aggregate_id"],
            aggregate_type=data["aggregate_type"],
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data.get("version", 1),
            priority=EventPriority(data.get("priority", "normal")),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
        )


@dataclass
class Command:
    """CQRS Command"""

    command_id: str = field(default_factory=lambda: str(uuid4()))
    command_type: str = ""
    aggregate_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    status: CommandStatus = CommandStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Query:
    """CQRS Query"""

    query_id: str = field(default_factory=lambda: str(uuid4()))
    query_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


EventHandler = Callable[[Event], None]
CommandHandler = Callable[[Command], Any]
QueryHandler = Callable[[Query], Any]


class EventStore:
    """
    Event store for Event Sourcing

    Append-only log of all domain events.
    """

    def __init__(self):
        self._events: List[Event] = []
        self._streams: Dict[str, List[Event]] = defaultdict(list)
        self._lock = threading.Lock()
        self._snapshots: Dict[str, tuple[int, Dict[str, Any]]] = {}

    def append(self, event: Event):
        """
        Append event to store

        Args:
            event: Event to append
        """
        with self._lock:
            self._events.append(event)

            # Add to aggregate stream
            stream_key = f"{event.aggregate_type}:{event.aggregate_id}"
            self._streams[stream_key].append(event)

            logger.info(f"Event appended: {event.event_type} for {stream_key}")

    def get_events(self, aggregate_type: str, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """
        Get events for aggregate

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate ID
            from_version: Starting version (for snapshots)

        Returns:
            List of events
        """
        with self._lock:
            stream_key = f"{aggregate_type}:{aggregate_id}"
            events = self._streams.get(stream_key, [])

            # Filter by version if needed
            if from_version > 0:
                events = [e for e in events if e.version > from_version]

            return events.copy()

    def get_all_events(
        self, event_type: Optional[str] = None, from_timestamp: Optional[datetime] = None
    ) -> List[Event]:
        """
        Get all events, optionally filtered

        Args:
            event_type: Filter by event type
            from_timestamp: Filter events after timestamp

        Returns:
            List of events
        """
        with self._lock:
            events = self._events.copy()

            if event_type:
                events = [e for e in events if e.event_type == event_type]

            if from_timestamp:
                events = [e for e in events if e.timestamp >= from_timestamp]

            return events

    def save_snapshot(self, aggregate_type: str, aggregate_id: str, version: int, state: Dict[str, Any]):
        """
        Save aggregate snapshot

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate ID
            version: Version at snapshot
            state: Aggregate state
        """
        with self._lock:
            key = f"{aggregate_type}:{aggregate_id}"
            self._snapshots[key] = (version, state)
            logger.info(f"Snapshot saved: {key} at version {version}")

    def get_snapshot(self, aggregate_type: str, aggregate_id: str) -> Optional[tuple[int, Dict[str, Any]]]:
        """
        Get aggregate snapshot

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate ID

        Returns:
            Tuple of (version, state) or None
        """
        with self._lock:
            key = f"{aggregate_type}:{aggregate_id}"
            return self._snapshots.get(key)


class EventBus:
    """
    Event bus for Pub/Sub messaging

    Distributes events to registered handlers.
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._processed_events: Set[str] = set()  # For deduplication
        self._dead_letter_queue: List[tuple[Event, Exception]] = []
        self._lock = threading.Lock()
        self._max_retry_attempts = 3

    def subscribe(self, event_type: str, handler: EventHandler):
        """
        Subscribe to event type

        Args:
            event_type: Event type to subscribe to
            handler: Handler function
        """
        with self._lock:
            self._handlers[event_type].append(handler)
            logger.info(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: str, handler: EventHandler):
        """
        Unsubscribe from event type

        Args:
            event_type: Event type
            handler: Handler function
        """
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type].remove(handler)

    def publish(self, event: Event, retry_count: int = 0):
        """
        Publish event to subscribers

        Args:
            event: Event to publish
            retry_count: Current retry attempt
        """
        # Deduplication check
        with self._lock:
            if event.event_id in self._processed_events:
                logger.warning(f"Duplicate event ignored: {event.event_id}")
                return

            self._processed_events.add(event.event_id)

        # Get handlers
        handlers = self._handlers.get(event.event_type, []).copy()

        if not handlers:
            logger.debug(f"No handlers for event type: {event.event_type}")
            return

        # Invoke handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler failed for {event.event_type}: {e}")

                # Retry logic
                if retry_count < self._max_retry_attempts:
                    logger.info(f"Retrying event {event.event_id} (attempt {retry_count + 1})")
                    self.publish(event, retry_count + 1)
                else:
                    # Add to dead letter queue
                    with self._lock:
                        self._dead_letter_queue.append((event, e))
                    logger.error(f"Event moved to DLQ: {event.event_id}")

    def get_dead_letters(self) -> List[tuple[Event, Exception]]:
        """Get events in dead letter queue"""
        with self._lock:
            return self._dead_letter_queue.copy()


class Projection(ABC):
    """
    Base class for event projections

    Projections build read models from event streams.
    """

    def __init__(self, name: str):
        self.name = name
        self._position = 0

    @abstractmethod
    def handle_event(self, event: Event):
        """Handle event and update projection"""
        pass

    def replay(self, events: List[Event]):
        """
        Replay events to rebuild projection

        Args:
            events: Events to replay
        """
        logger.info(f"Replaying {len(events)} events for projection {self.name}")

        for event in events:
            self.handle_event(event)
            self._position += 1

        logger.info(f"Projection {self.name} rebuilt at position {self._position}")


class CommandBus:
    """
    Command bus for CQRS

    Routes commands to handlers.
    """

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._lock = threading.Lock()

    def register_handler(self, command_type: str, handler: CommandHandler):
        """
        Register command handler

        Args:
            command_type: Command type
            handler: Handler function
        """
        with self._lock:
            if command_type in self._handlers:
                raise ValueError(f"Handler already registered for {command_type}")

            self._handlers[command_type] = handler
            logger.info(f"Registered handler for command: {command_type}")

    def dispatch(self, command: Command) -> Any:
        """
        Dispatch command to handler

        Args:
            command: Command to dispatch

        Returns:
            Command result

        Raises:
            ValueError: If no handler registered
        """
        handler = self._handlers.get(command.command_type)
        if not handler:
            raise ValueError(f"No handler for command: {command.command_type}")

        try:
            command.status = CommandStatus.EXECUTING
            result = handler(command)
            command.status = CommandStatus.COMPLETED
            command.result = result
            return result

        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error = str(e)
            logger.error(f"Command failed: {command.command_type} - {e}")
            raise


class QueryBus:
    """
    Query bus for CQRS

    Routes queries to handlers.
    """

    def __init__(self):
        self._handlers: Dict[str, QueryHandler] = {}
        self._lock = threading.Lock()

    def register_handler(self, query_type: str, handler: QueryHandler):
        """
        Register query handler

        Args:
            query_type: Query type
            handler: Handler function
        """
        with self._lock:
            self._handlers[query_type] = handler
            logger.info(f"Registered handler for query: {query_type}")

    def execute(self, query: Query) -> Any:
        """
        Execute query

        Args:
            query: Query to execute

        Returns:
            Query result

        Raises:
            ValueError: If no handler registered
        """
        handler = self._handlers.get(query.query_type)
        if not handler:
            raise ValueError(f"No handler for query: {query.query_type}")

        return handler(query)


class Saga:
    """
    Saga pattern for distributed transactions

    Coordinates multi-step business processes across services.
    """

    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[tuple[CommandHandler, CommandHandler]] = []  # (action, compensation)
        self.completed_steps: List[int] = []
        self.status = CommandStatus.PENDING

    def add_step(self, action: CommandHandler, compensation: CommandHandler):
        """
        Add step to saga

        Args:
            action: Forward action
            compensation: Compensating action
        """
        self.steps.append((action, compensation))

    def execute(self, context: Dict[str, Any]) -> bool:
        """
        Execute saga

        Args:
            context: Saga context data

        Returns:
            True if successful, False if compensated
        """
        self.status = CommandStatus.EXECUTING

        try:
            # Execute forward actions
            for i, (action, _) in enumerate(self.steps):
                logger.info(f"Executing saga step {i+1}/{len(self.steps)}")
                action(context)
                self.completed_steps.append(i)

            self.status = CommandStatus.COMPLETED
            logger.info(f"Saga {self.saga_id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Saga {self.saga_id} failed: {e}")
            self.status = CommandStatus.COMPENSATING

            # Execute compensating actions in reverse order
            for step_index in reversed(self.completed_steps):
                _, compensation = self.steps[step_index]
                try:
                    logger.info(f"Compensating saga step {step_index+1}")
                    compensation(context)
                except Exception as comp_error:
                    logger.error(f"Compensation failed for step {step_index}: {comp_error}")

            self.status = CommandStatus.FAILED
            logger.info(f"Saga {self.saga_id} compensated")
            return False


class EventSourcingRepository:
    """
    Repository for event-sourced aggregates

    Loads and saves aggregates using event store.
    """

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def load(self, aggregate_type: str, aggregate_id: str, aggregate_class: type) -> Any:
        """
        Load aggregate from event store

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate ID
            aggregate_class: Aggregate class

        Returns:
            Reconstructed aggregate
        """
        # Try to load from snapshot
        snapshot = self.event_store.get_snapshot(aggregate_type, aggregate_id)

        if snapshot:
            version, state = snapshot
            aggregate = aggregate_class.from_snapshot(state)
            from_version = version
        else:
            aggregate = aggregate_class(aggregate_id)
            from_version = 0

        # Load events after snapshot
        events = self.event_store.get_events(aggregate_type, aggregate_id, from_version)

        # Replay events
        for event in events:
            aggregate.apply(event)

        return aggregate

    def save(self, aggregate: Any, events: List[Event]):
        """
        Save aggregate events

        Args:
            aggregate: Aggregate instance
            events: New events to save
        """
        for event in events:
            self.event_store.append(event)


# Singleton instances
_event_store_instance = None
_event_bus_instance = None
_command_bus_instance = None
_query_bus_instance = None
_instance_lock = threading.Lock()


def get_event_store() -> EventStore:
    """Get singleton Event Store instance"""
    global _event_store_instance
    if _event_store_instance is None:
        with _instance_lock:
            if _event_store_instance is None:
                _event_store_instance = EventStore()
    return _event_store_instance


def get_event_bus() -> EventBus:
    """Get singleton Event Bus instance"""
    global _event_bus_instance
    if _event_bus_instance is None:
        with _instance_lock:
            if _event_bus_instance is None:
                _event_bus_instance = EventBus()
    return _event_bus_instance


def get_command_bus() -> CommandBus:
    """Get singleton Command Bus instance"""
    global _command_bus_instance
    if _command_bus_instance is None:
        with _instance_lock:
            if _command_bus_instance is None:
                _command_bus_instance = CommandBus()
    return _command_bus_instance


def get_query_bus() -> QueryBus:
    """Get singleton Query Bus instance"""
    global _query_bus_instance
    if _query_bus_instance is None:
        with _instance_lock:
            if _query_bus_instance is None:
                _query_bus_instance = QueryBus()
    return _query_bus_instance


if __name__ == "__main__":
    # Example usage
    event_store = get_event_store()
    event_bus = get_event_bus()
    command_bus = get_command_bus()

    # Create and store event
    event = Event(
        event_type="UserCreated",
        aggregate_type="User",
        aggregate_id="user-123",
        data={"email": "user@example.com", "name": "John Doe"},
    )

    event_store.append(event)
    print(f"Event stored: {event.event_id}")

    # Subscribe to event
    def handle_user_created(event: Event):
        print(f"Handler received: {event.event_type} - {event.data}")

    event_bus.subscribe("UserCreated", handle_user_created)

    # Publish event
    event_bus.publish(event)

    # Register command handler
    def handle_create_user(command: Command) -> str:
        print(f"Creating user: {command.data}")
        return f"user-{uuid4()}"

    command_bus.register_handler("CreateUser", handle_create_user)

    # Dispatch command
    command = Command(command_type="CreateUser", data={"email": "newuser@example.com"})

    user_id = command_bus.dispatch(command)
    print(f"Command result: {user_id}")

    print("\nEvent-Driven Architecture module loaded successfully!")
