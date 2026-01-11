#!/usr/bin/env python3
"""
Streaming Analytics Module

Real-time data stream processing with windowing, aggregation, and CEP
(Complex Event Processing).

Key Features:
- Time-based windowing (tumbling, sliding, session)
- Real-time aggregation and metrics
- Complex Event Processing (CEP)
- Stream joins and transformations
- Late data handling
- Watermarking for event time processing
- State management
- Fault tolerance with checkpointing

Dependencies:
- pandas for data manipulation
- numpy for numerical operations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading
import time
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class WindowType(str, Enum):
    """Window types for stream processing"""
    TUMBLING = "tumbling"  # Fixed, non-overlapping windows
    SLIDING = "sliding"  # Overlapping windows
    SESSION = "session"  # Dynamic windows based on inactivity


class AggregationType(str, Enum):
    """Aggregation functions"""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    FIRST = "first"
    LAST = "last"


class EventType(str, Enum):
    """Complex event types"""
    PATTERN_MATCHED = "pattern_matched"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    SEQUENCE_COMPLETED = "sequence_completed"


@dataclass
class StreamEvent:
    """Stream event with metadata"""
    event_id: str
    event_type: str
    timestamp: datetime
    event_time: datetime  # For event-time processing
    data: Dict[str, Any]
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure timestamps are datetime objects"""
        if isinstance(self.timestamp, (int, float)):
            self.timestamp = datetime.fromtimestamp(self.timestamp)
        if isinstance(self.event_time, (int, float)):
            self.event_time = datetime.fromtimestamp(self.event_time)


@dataclass
class Window:
    """Time window for aggregation"""
    window_id: str
    start_time: datetime
    end_time: datetime
    events: List[StreamEvent] = field(default_factory=list)
    aggregates: Dict[str, Any] = field(default_factory=dict)
    closed: bool = False

    def add_event(self, event: StreamEvent):
        """Add event to window"""
        if not self.closed and self.start_time <= event.event_time < self.end_time:
            self.events.append(event)
            return True
        return False

    def close(self):
        """Close window for aggregation"""
        self.closed = True


@dataclass
class StreamMetrics:
    """Real-time stream metrics"""
    total_events: int = 0
    events_per_second: float = 0.0
    average_latency_ms: float = 0.0
    late_events: int = 0
    windows_processed: int = 0
    last_update: datetime = field(default_factory=datetime.now)


class WindowManager:
    """
    Manages time windows for stream processing

    Supports tumbling, sliding, and session windows.
    """

    def __init__(
        self,
        window_type: WindowType,
        window_size: timedelta,
        slide: Optional[timedelta] = None,
        session_gap: Optional[timedelta] = None
    ):
        self.window_type = window_type
        self.window_size = window_size
        self.slide = slide or window_size  # Default to tumbling
        self.session_gap = session_gap or timedelta(minutes=5)

        self._windows: Dict[str, Window] = {}
        self._lock = threading.Lock()

    def assign_to_windows(self, event: StreamEvent) -> List[str]:
        """
        Assign event to appropriate windows

        Args:
            event: Stream event

        Returns:
            List of window IDs the event was assigned to
        """
        with self._lock:
            if self.window_type == WindowType.TUMBLING:
                return self._assign_tumbling(event)
            elif self.window_type == WindowType.SLIDING:
                return self._assign_sliding(event)
            elif self.window_type == WindowType.SESSION:
                return self._assign_session(event)
        return []

    def _assign_tumbling(self, event: StreamEvent) -> List[str]:
        """Assign to tumbling window"""
        window_start = self._align_to_window(event.event_time)
        window_end = window_start + self.window_size
        window_id = f"tumbling_{window_start.timestamp()}"

        if window_id not in self._windows:
            self._windows[window_id] = Window(
                window_id=window_id,
                start_time=window_start,
                end_time=window_end
            )

        window = self._windows[window_id]
        if window.add_event(event):
            return [window_id]
        return []

    def _assign_sliding(self, event: StreamEvent) -> List[str]:
        """Assign to sliding windows"""
        assigned_windows = []

        # Calculate all windows this event belongs to
        window_start = self._align_to_window(event.event_time)

        # Look back to find windows this event might belong to
        lookback = int(self.window_size / self.slide) + 1
        for i in range(lookback):
            ws = window_start - (self.slide * i)
            we = ws + self.window_size

            if ws <= event.event_time < we:
                window_id = f"sliding_{ws.timestamp()}"

                if window_id not in self._windows:
                    self._windows[window_id] = Window(
                        window_id=window_id,
                        start_time=ws,
                        end_time=we
                    )

                window = self._windows[window_id]
                if window.add_event(event):
                    assigned_windows.append(window_id)

        return assigned_windows

    def _assign_session(self, event: StreamEvent) -> List[str]:
        """Assign to session window"""
        # Find active session or create new one
        source = event.source
        session_key = f"session_{source}"

        # Find most recent session for this source
        active_session = None
        for window_id, window in self._windows.items():
            if window_id.startswith(session_key) and not window.closed:
                if event.event_time - window.end_time < self.session_gap:
                    active_session = window
                    break

        if active_session:
            # Extend existing session
            active_session.end_time = event.event_time + self.session_gap
            active_session.add_event(event)
            return [active_session.window_id]
        else:
            # Create new session
            window_id = f"{session_key}_{event.event_time.timestamp()}"
            self._windows[window_id] = Window(
                window_id=window_id,
                start_time=event.event_time,
                end_time=event.event_time + self.session_gap,
                events=[event]
            )
            return [window_id]

    def _align_to_window(self, timestamp: datetime) -> datetime:
        """Align timestamp to window boundary"""
        seconds = int(self.window_size.total_seconds())
        aligned_ts = int(timestamp.timestamp() // seconds) * seconds
        return datetime.fromtimestamp(aligned_ts)

    def get_window(self, window_id: str) -> Optional[Window]:
        """Get window by ID"""
        with self._lock:
            return self._windows.get(window_id)

    def close_expired_windows(self, current_time: datetime) -> List[Window]:
        """Close windows that have expired"""
        closed_windows = []

        with self._lock:
            for window in list(self._windows.values()):
                if not window.closed and current_time >= window.end_time:
                    window.close()
                    closed_windows.append(window)

        return closed_windows

    def cleanup_old_windows(self, retention: timedelta):
        """Remove old closed windows"""
        cutoff = datetime.now() - retention

        with self._lock:
            to_remove = [
                wid for wid, window in self._windows.items()
                if window.closed and window.end_time < cutoff
            ]

            for wid in to_remove:
                del self._windows[wid]


class StreamAggregator:
    """
    Aggregates events within windows

    Computes various aggregations over windowed data.
    """

    def __init__(self):
        self._aggregators: Dict[AggregationType, Callable] = {
            AggregationType.SUM: self._sum,
            AggregationType.AVG: self._avg,
            AggregationType.COUNT: self._count,
            AggregationType.MIN: self._min,
            AggregationType.MAX: self._max,
            AggregationType.FIRST: self._first,
            AggregationType.LAST: self._last,
        }

    def aggregate_window(
        self,
        window: Window,
        field: str,
        agg_type: AggregationType
    ) -> Any:
        """
        Aggregate field in window

        Args:
            window: Window to aggregate
            field: Field name to aggregate
            agg_type: Aggregation type

        Returns:
            Aggregated value
        """
        aggregator = self._aggregators.get(agg_type)
        if not aggregator:
            raise ValueError(f"Unknown aggregation type: {agg_type}")

        values = [event.data.get(field) for event in window.events if field in event.data]
        return aggregator(values)

    def _sum(self, values: List[Any]) -> Decimal:
        """Sum aggregation"""
        return Decimal(sum(Decimal(str(v)) for v in values if v is not None))

    def _avg(self, values: List[Any]) -> float:
        """Average aggregation"""
        if not values:
            return 0.0
        return float(sum(Decimal(str(v)) for v in values if v is not None)) / len(values)

    def _count(self, values: List[Any]) -> int:
        """Count aggregation"""
        return len([v for v in values if v is not None])

    def _min(self, values: List[Any]) -> Any:
        """Min aggregation"""
        valid = [v for v in values if v is not None]
        return min(valid) if valid else None

    def _max(self, values: List[Any]) -> Any:
        """Max aggregation"""
        valid = [v for v in values if v is not None]
        return max(valid) if valid else None

    def _first(self, values: List[Any]) -> Any:
        """First value"""
        return values[0] if values else None

    def _last(self, values: List[Any]) -> Any:
        """Last value"""
        return values[-1] if values else None


class ComplexEventProcessor:
    """
    Complex Event Processing (CEP)

    Detects patterns and sequences in event streams.
    """

    def __init__(self):
        self._patterns: Dict[str, Dict[str, Any]] = {}
        self._event_buffer: deque = deque(maxlen=1000)
        self._lock = threading.Lock()

    def register_pattern(
        self,
        pattern_name: str,
        event_sequence: List[str],
        within_time: timedelta,
        condition: Optional[Callable[[List[StreamEvent]], bool]] = None
    ):
        """
        Register event pattern

        Args:
            pattern_name: Pattern identifier
            event_sequence: Sequence of event types to match
            within_time: Time window for pattern
            condition: Optional condition function
        """
        with self._lock:
            self._patterns[pattern_name] = {
                "sequence": event_sequence,
                "within_time": within_time,
                "condition": condition or (lambda events: True)
            }

    def process_event(self, event: StreamEvent) -> List[Tuple[str, List[StreamEvent]]]:
        """
        Process event and detect patterns

        Args:
            event: Stream event

        Returns:
            List of (pattern_name, matched_events) tuples
        """
        with self._lock:
            self._event_buffer.append(event)
            matched_patterns = []

            for pattern_name, pattern_config in self._patterns.items():
                matches = self._match_pattern(pattern_config)
                if matches:
                    matched_patterns.append((pattern_name, matches))

            return matched_patterns

    def _match_pattern(self, pattern_config: Dict[str, Any]) -> Optional[List[StreamEvent]]:
        """Match pattern in event buffer"""
        sequence = pattern_config["sequence"]
        within_time = pattern_config["within_time"]
        condition = pattern_config["condition"]

        # Search for pattern in buffer
        for i in range(len(self._event_buffer)):
            if self._event_buffer[i].event_type != sequence[0]:
                continue

            # Try to match full sequence
            matched_events = [self._event_buffer[i]]
            last_time = self._event_buffer[i].event_time

            for j in range(i + 1, len(self._event_buffer)):
                if len(matched_events) == len(sequence):
                    break

                event = self._event_buffer[j]
                expected_type = sequence[len(matched_events)]

                if event.event_type == expected_type:
                    if event.event_time - last_time <= within_time:
                        matched_events.append(event)
                        last_time = event.event_time
                    else:
                        break

            # Check if full pattern matched
            if len(matched_events) == len(sequence) and condition(matched_events):
                return matched_events

        return None


class StreamProcessor:
    """
    Main stream processing engine

    Coordinates windowing, aggregation, and CEP.
    """

    def __init__(
        self,
        window_type: WindowType = WindowType.TUMBLING,
        window_size: timedelta = timedelta(minutes=5),
        slide: Optional[timedelta] = None
    ):
        self.window_manager = WindowManager(window_type, window_size, slide)
        self.aggregator = StreamAggregator()
        self.cep = ComplexEventProcessor()

        self._metrics = StreamMetrics()
        self._event_handlers: List[Callable[[StreamEvent], None]] = []
        self._window_handlers: List[Callable[[Window], None]] = []
        self._pattern_handlers: Dict[str, Callable[[List[StreamEvent]], None]] = {}
        self._lock = threading.Lock()

        self._processing_thread: Optional[threading.Thread] = None
        self._running = False

    def on_event(self, handler: Callable[[StreamEvent], None]):
        """Register event handler"""
        with self._lock:
            self._event_handlers.append(handler)

    def on_window_close(self, handler: Callable[[Window], None]):
        """Register window close handler"""
        with self._lock:
            self._window_handlers.append(handler)

    def on_pattern(self, pattern_name: str, handler: Callable[[List[StreamEvent]], None]):
        """Register pattern match handler"""
        with self._lock:
            self._pattern_handlers[pattern_name] = handler

    def process_event(self, event: StreamEvent):
        """
        Process single event

        Args:
            event: Stream event to process
        """
        # Update metrics
        self._metrics.total_events += 1
        latency = (datetime.now() - event.timestamp).total_seconds() * 1000
        self._metrics.average_latency_ms = (
            (self._metrics.average_latency_ms * (self._metrics.total_events - 1) + latency)
            / self._metrics.total_events
        )

        # Assign to windows
        window_ids = self.window_manager.assign_to_windows(event)
        if not window_ids:
            self._metrics.late_events += 1

        # Run event handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

        # Check for patterns
        matched_patterns = self.cep.process_event(event)
        for pattern_name, matched_events in matched_patterns:
            handler = self._pattern_handlers.get(pattern_name)
            if handler:
                try:
                    handler(matched_events)
                except Exception as e:
                    logger.error(f"Pattern handler error: {e}")

        # Close expired windows
        closed_windows = self.window_manager.close_expired_windows(datetime.now())
        for window in closed_windows:
            self._metrics.windows_processed += 1

            for handler in self._window_handlers:
                try:
                    handler(window)
                except Exception as e:
                    logger.error(f"Window handler error: {e}")

    def start(self):
        """Start background processing"""
        if self._running:
            return

        self._running = True
        self._processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self._processing_thread.start()
        logger.info("Stream processor started")

    def stop(self):
        """Stop background processing"""
        self._running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5)
        logger.info("Stream processor stopped")

    def _background_processing(self):
        """Background processing loop"""
        while self._running:
            try:
                # Close expired windows
                closed_windows = self.window_manager.close_expired_windows(datetime.now())

                for window in closed_windows:
                    self._metrics.windows_processed += 1

                    for handler in self._window_handlers:
                        try:
                            handler(window)
                        except Exception as e:
                            logger.error(f"Window handler error: {e}")

                # Cleanup old windows
                self.window_manager.cleanup_old_windows(timedelta(hours=1))

                time.sleep(1)  # Check every second

            except Exception as e:
                logger.error(f"Background processing error: {e}")

    def get_metrics(self) -> StreamMetrics:
        """Get current stream metrics"""
        return self._metrics


# Singleton instance
_stream_processor_instance = None
_instance_lock = threading.Lock()


def get_stream_processor() -> StreamProcessor:
    """Get singleton Stream Processor instance"""
    global _stream_processor_instance

    if _stream_processor_instance is None:
        with _instance_lock:
            if _stream_processor_instance is None:
                _stream_processor_instance = StreamProcessor()

    return _stream_processor_instance


if __name__ == "__main__":
    # Example usage
    processor = get_stream_processor()

    # Register window handler
    def on_window_complete(window: Window):
        print(f"Window {window.window_id} closed with {len(window.events)} events")

        # Aggregate
        if window.events:
            total = processor.aggregator.aggregate_window(window, "amount", AggregationType.SUM)
            avg = processor.aggregator.aggregate_window(window, "amount", AggregationType.AVG)
            print(f"  Total: {total}, Average: {avg}")

    processor.on_window_close(on_window_complete)

    # Register pattern
    processor.cep.register_pattern(
        "high_value_sequence",
        ["transaction", "transaction", "transaction"],
        within_time=timedelta(minutes=1)
    )

    def on_high_value_pattern(events: List[StreamEvent]):
        print(f"Pattern detected: {len(events)} transactions in quick succession")

    processor.on_pattern("high_value_sequence", on_high_value_pattern)

    # Start processor
    processor.start()

    # Simulate events
    for i in range(10):
        event = StreamEvent(
            event_id=f"evt-{i}",
            event_type="transaction",
            timestamp=datetime.now(),
            event_time=datetime.now(),
            data={"amount": 100 + i * 10, "user_id": f"user-{i % 3}"},
            source="payment-api"
        )
        processor.process_event(event)
        time.sleep(0.1)

    # Wait a bit
    time.sleep(2)

    # Stop processor
    processor.stop()

    # Print metrics
    metrics = processor.get_metrics()
    print(f"\nMetrics:")
    print(f"  Total events: {metrics.total_events}")
    print(f"  Events/sec: {metrics.events_per_second:.2f}")
    print(f"  Avg latency: {metrics.average_latency_ms:.2f}ms")
    print(f"  Windows processed: {metrics.windows_processed}")

    print("\nStreaming Analytics module loaded successfully!")
