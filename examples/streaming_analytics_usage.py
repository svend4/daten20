#!/usr/bin/env python3
"""
Real-time Streaming Analytics - Usage Examples

This module demonstrates real-world applications of the Streaming Analytics system,
including:
- Time-windowed aggregations
- Real-time transaction monitoring
- User session analytics
- Fraud detection with Complex Event Processing
- IoT sensor data processing
- System metrics monitoring

Author: DMS Team
Date: 2026-01-16
"""

import time
from datetime import datetime, timedelta
from decimal import Decimal

from src.analytics.streaming_analytics import (
    StreamProcessor,
    WindowType,
    AggregationType,
    StreamEvent,
    Window,
    get_stream_processor,
)


# ============================================================================
# EXAMPLE 1: Real-time Transaction Monitoring
# ============================================================================


def example_transaction_monitoring():
    """
    Example: Monitor transactions in real-time with tumbling windows

    Use Case: E-commerce platform monitoring transaction volumes and values
    Window: 30-second tumbling windows
    Metrics: Total transactions, total value, average value
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Real-time Transaction Monitoring")
    print("=" * 80)

    # Create processor with 30-second tumbling windows
    processor = StreamProcessor(window_type=WindowType.TUMBLING, window_size=timedelta(seconds=30))

    # Statistics collector
    window_stats = []

    # Define window close handler
    def analyze_window(window: Window):
        """Analyze completed window"""
        if not window.events:
            return

        # Calculate metrics
        total_transactions = len(window.events)
        total_value = processor.aggregator.aggregate_window(window, "amount", AggregationType.SUM)
        avg_value = processor.aggregator.aggregate_window(window, "amount", AggregationType.AVG)
        max_value = processor.aggregator.aggregate_window(window, "amount", AggregationType.MAX)

        stats = {
            "window_id": window.window_id,
            "start_time": window.start_time,
            "end_time": window.end_time,
            "total_transactions": total_transactions,
            "total_value": float(total_value),
            "avg_value": avg_value,
            "max_value": max_value,
        }

        window_stats.append(stats)

        print(f"\n📊 Window Analysis:")
        print(f"   Period: {window.start_time.strftime('%H:%M:%S')} - {window.end_time.strftime('%H:%M:%S')}")
        print(f"   Total Transactions: {total_transactions}")
        print(f"   Total Value: ${total_value:,.2f}")
        print(f"   Average Value: ${avg_value:,.2f}")
        print(f"   Max Transaction: ${max_value:,.2f}")

        # Alert on high volume
        if total_transactions > 10:
            print(f"   ⚠️  HIGH VOLUME ALERT: {total_transactions} transactions in 30 seconds!")

    processor.on_window_close(analyze_window)

    # Simulate transaction stream
    print("\n📈 Simulating transaction stream...")

    base_time = datetime.now()
    transaction_values = [99.99, 45.50, 199.99, 24.99, 149.99, 89.99, 299.99, 34.99, 129.99, 59.99]

    for i, amount in enumerate(transaction_values):
        event = StreamEvent(
            event_id=f"tx-{i:04d}",
            event_type="transaction",
            timestamp=base_time + timedelta(seconds=i * 3),
            event_time=base_time + timedelta(seconds=i * 3),
            data={"amount": amount, "user_id": f"user-{i % 3}", "product_id": f"prod-{i % 5}"},
            source="payment-gateway",
        )
        processor.process_event(event)
        print(f"   Transaction {i+1}: ${amount:,.2f}")

    # Close windows
    processor.window_manager.close_expired_windows(base_time + timedelta(seconds=35))

    # Summary
    print(f"\n📋 Summary:")
    print(f"   Windows Processed: {len(window_stats)}")
    print(f"   Total Events: {processor.get_metrics().total_events}")

    return processor


# ============================================================================
# EXAMPLE 2: User Session Analytics with Session Windows
# ============================================================================


def example_user_session_analytics():
    """
    Example: Analyze user sessions with session windows

    Use Case: Website analytics tracking user behavior
    Window: Session windows with 2-minute gap
    Metrics: Pages per session, session duration, engagement
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: User Session Analytics")
    print("=" * 80)

    # Create processor with session windows (2-minute session gap)
    processor = StreamProcessor(window_type=WindowType.SESSION, window_size=timedelta(minutes=10))
    processor.window_manager = processor.window_manager.__class__(
        WindowType.SESSION, timedelta(minutes=10), session_gap=timedelta(minutes=2)
    )

    # Session analytics
    user_sessions = {}

    def analyze_session(window: Window):
        """Analyze completed user session"""
        if not window.events:
            return

        user = window.events[0].source
        page_count = len(window.events)
        duration = (window.end_time - window.start_time).total_seconds()

        # Extract pages visited
        pages = [e.data.get("page") for e in window.events if "page" in e.data]

        user_sessions[user] = {
            "session_id": window.window_id,
            "page_count": page_count,
            "duration_sec": duration,
            "pages": pages,
        }

        print(f"\n👤 Session Ended: {user}")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Pages Visited: {page_count}")
        print(f"   Path: {' → '.join(pages)}")

        # Engagement scoring
        engagement_score = (page_count * 10) + (duration / 60)
        print(f"   Engagement Score: {engagement_score:.1f}")

        if engagement_score > 50:
            print(f"   🌟 HIGH ENGAGEMENT USER!")

    processor.on_window_close(analyze_session)

    # Simulate user activity
    print("\n🖱️  Simulating user sessions...")

    base_time = datetime.now()
    users = ["user-alice", "user-bob", "user-charlie"]
    pages = ["/home", "/products", "/product/123", "/cart", "/checkout", "/confirmation"]

    for user_idx, user in enumerate(users):
        print(f"\n   {user} browsing...")
        for page_idx in range(4):
            event = StreamEvent(
                event_id=f"pageview-{user_idx}-{page_idx}",
                event_type="pageview",
                timestamp=base_time + timedelta(seconds=user_idx * 60 + page_idx * 20),
                event_time=base_time + timedelta(seconds=user_idx * 60 + page_idx * 20),
                data={"page": pages[page_idx % len(pages)], "referrer": "google.com" if page_idx == 0 else pages[page_idx - 1]},
                source=user,
            )
            processor.process_event(event)

    # Wait for sessions to timeout
    time.sleep(1)

    # Summary
    print(f"\n📋 Summary:")
    print(f"   Total Sessions: {len(user_sessions)}")
    print(f"   Total Pageviews: {processor.get_metrics().total_events}")

    return processor


# ============================================================================
# EXAMPLE 3: Fraud Detection with Complex Event Processing
# ============================================================================


def example_fraud_detection():
    """
    Example: Detect suspicious patterns using CEP

    Use Case: Financial fraud detection
    Pattern: Multiple high-value transactions from same source in short time
    Alert: Potential fraudulent activity
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Fraud Detection with CEP")
    print("=" * 80)

    processor = StreamProcessor()

    # Fraud alerts
    fraud_alerts = []

    # Define fraud pattern: 3 transactions > $1000 within 30 seconds
    def high_value_condition(events):
        """Check if all transactions are high-value"""
        return all(e.data.get("amount", 0) >= 1000 for e in events)

    processor.cep.register_pattern(
        pattern_name="rapid_high_value",
        event_sequence=["transaction", "transaction", "transaction"],
        within_time=timedelta(seconds=30),
        condition=high_value_condition,
    )

    # Pattern handler
    def fraud_alert_handler(events):
        """Handle potential fraud detection"""
        user = events[0].data.get("user_id", "unknown")
        amounts = [e.data.get("amount", 0) for e in events]
        total = sum(amounts)

        alert = {
            "user_id": user,
            "event_count": len(events),
            "total_amount": total,
            "amounts": amounts,
            "time_span": (events[-1].event_time - events[0].event_time).total_seconds(),
        }
        fraud_alerts.append(alert)

        print(f"\n🚨 FRAUD ALERT!")
        print(f"   User: {user}")
        print(f"   Transactions: {len(events)} high-value transactions in {alert['time_span']:.1f} seconds")
        print(f"   Amounts: {', '.join([f'${a:,.2f}' for a in amounts])}")
        print(f"   Total: ${total:,.2f}")
        print(f"   ⚠️  RECOMMENDED ACTION: Flag account for review")

    processor.on_pattern("rapid_high_value", fraud_alert_handler)

    # Simulate normal and suspicious activity
    print("\n💳 Simulating transaction activity...")

    base_time = datetime.now()

    # Normal user
    print("\n   Normal user activity:")
    for i in range(3):
        event = StreamEvent(
            event_id=f"tx-normal-{i}",
            event_type="transaction",
            timestamp=base_time + timedelta(seconds=i * 60),
            event_time=base_time + timedelta(seconds=i * 60),
            data={"amount": 50.0 + i * 10, "user_id": "user-normal", "merchant": f"shop-{i}"},
            source="normal-terminal",
        )
        processor.process_event(event)
        print(f"      Transaction {i+1}: ${event.data['amount']:.2f}")

    # Suspicious user
    print("\n   Suspicious user activity:")
    for i in range(3):
        event = StreamEvent(
            event_id=f"tx-suspicious-{i}",
            event_type="transaction",
            timestamp=base_time + timedelta(seconds=100 + i * 5),
            event_time=base_time + timedelta(seconds=100 + i * 5),
            data={"amount": 1500.0 + i * 200, "user_id": "user-suspicious", "merchant": f"online-{i}"},
            source="suspicious-terminal",
        )
        processor.process_event(event)
        print(f"      Transaction {i+1}: ${event.data['amount']:.2f} 🚩")

    time.sleep(0.5)

    # Summary
    print(f"\n📋 Summary:")
    print(f"   Total Transactions: {processor.get_metrics().total_events}")
    print(f"   Fraud Alerts: {len(fraud_alerts)}")

    if fraud_alerts:
        print(f"\n   ⚠️  {len(fraud_alerts)} suspicious pattern(s) detected!")

    return processor


# ============================================================================
# EXAMPLE 4: Sliding Window Metrics
# ============================================================================


def example_sliding_window_metrics():
    """
    Example: Compute moving averages with sliding windows

    Use Case: Real-time system metrics monitoring
    Window: 1-minute sliding window with 10-second slide
    Metrics: Moving average of response times, throughput
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Sliding Window Metrics")
    print("=" * 80)

    # Create processor with sliding windows
    processor = StreamProcessor(
        window_type=WindowType.SLIDING, window_size=timedelta(seconds=60), slide=timedelta(seconds=10)
    )

    # Metrics tracking
    metrics_history = []

    def calculate_metrics(window: Window):
        """Calculate metrics for window"""
        if not window.events:
            return

        avg_response = processor.aggregator.aggregate_window(window, "response_time", AggregationType.AVG)
        throughput = len(window.events)

        metrics = {
            "window_start": window.start_time,
            "avg_response_ms": avg_response,
            "throughput": throughput,
        }
        metrics_history.append(metrics)

        print(f"\n📊 Window Metrics [{window.start_time.strftime('%H:%M:%S')}]:")
        print(f"   Avg Response Time: {avg_response:.2f}ms")
        print(f"   Throughput: {throughput} requests/minute")

        # Alert on high response times
        if avg_response > 500:
            print(f"   ⚠️  HIGH LATENCY WARNING!")

    processor.on_window_close(calculate_metrics)

    # Simulate API requests
    print("\n🌐 Simulating API request stream...")

    base_time = datetime.now()

    for i in range(20):
        # Simulate varying response times
        response_time = 100 + (i % 5) * 50 + (i // 10) * 100

        event = StreamEvent(
            event_id=f"req-{i:04d}",
            event_type="api_request",
            timestamp=base_time + timedelta(seconds=i * 5),
            event_time=base_time + timedelta(seconds=i * 5),
            data={"response_time": response_time, "endpoint": f"/api/v1/endpoint-{i % 3}", "status": 200},
            source="api-server",
        )
        processor.process_event(event)

    # Close windows
    processor.window_manager.close_expired_windows(base_time + timedelta(seconds=150))

    # Summary
    print(f"\n📋 Summary:")
    print(f"   Total Requests: {processor.get_metrics().total_events}")
    print(f"   Windows Analyzed: {len(metrics_history)}")

    if metrics_history:
        avg_of_avgs = sum(m["avg_response_ms"] for m in metrics_history) / len(metrics_history)
        print(f"   Overall Avg Response: {avg_of_avgs:.2f}ms")

    return processor


# ============================================================================
# EXAMPLE 5: IoT Sensor Data Processing
# ============================================================================


def example_iot_sensor_processing():
    """
    Example: Process IoT sensor data in real-time

    Use Case: Smart building temperature monitoring
    Window: 1-minute tumbling windows
    Metrics: Min, max, average temperature per room
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: IoT Sensor Data Processing")
    print("=" * 80)

    processor = StreamProcessor(window_type=WindowType.TUMBLING, window_size=timedelta(seconds=60))

    # Room temperature tracking
    room_analytics = {}

    def analyze_temperature_data(window: Window):
        """Analyze temperature data per room"""
        if not window.events:
            return

        # Group by room
        rooms = {}
        for event in window.events:
            room = event.source
            temp = event.data.get("temperature", 0)

            if room not in rooms:
                rooms[room] = []
            rooms[room].append(temp)

        print(f"\n🌡️  Temperature Analysis [{window.start_time.strftime('%H:%M:%S')}]:")

        for room, temps in rooms.items():
            avg_temp = sum(temps) / len(temps)
            min_temp = min(temps)
            max_temp = max(temps)

            room_analytics[room] = {"avg": avg_temp, "min": min_temp, "max": max_temp, "readings": len(temps)}

            print(f"\n   {room}:")
            print(f"      Readings: {len(temps)}")
            print(f"      Avg: {avg_temp:.1f}°C")
            print(f"      Min: {min_temp:.1f}°C")
            print(f"      Max: {max_temp:.1f}°C")

            # Alerts
            if avg_temp > 28:
                print(f"      ⚠️  HIGH TEMPERATURE ALERT!")
            elif avg_temp < 18:
                print(f"      ❄️  LOW TEMPERATURE ALERT!")

    processor.on_window_close(analyze_temperature_data)

    # Simulate sensor data
    print("\n📡 Simulating IoT sensor stream...")

    base_time = datetime.now()
    rooms = ["room-a", "room-b", "room-c"]
    base_temps = [22.0, 24.0, 21.5]

    for i in range(30):
        room_idx = i % len(rooms)
        room = rooms[room_idx]
        # Simulate temperature fluctuation
        temp = base_temps[room_idx] + (i % 10) * 0.5 - 2

        event = StreamEvent(
            event_id=f"sensor-{i:04d}",
            event_type="temperature_reading",
            timestamp=base_time + timedelta(seconds=i * 3),
            event_time=base_time + timedelta(seconds=i * 3),
            data={"temperature": temp, "humidity": 45 + (i % 5) * 2, "sensor_id": f"sensor-{room_idx}"},
            source=room,
        )
        processor.process_event(event)

    # Close windows
    processor.window_manager.close_expired_windows(base_time + timedelta(seconds=120))

    # Summary
    print(f"\n📋 Summary:")
    print(f"   Total Readings: {processor.get_metrics().total_events}")
    print(f"   Rooms Monitored: {len(room_analytics)}")

    return processor


# ============================================================================
# EXAMPLE 6: Stream Metrics and Monitoring
# ============================================================================


def example_stream_metrics():
    """
    Example: Monitor stream processing metrics

    Use Case: System health monitoring
    Metrics: Events per second, latency, windows processed
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Stream Metrics and Monitoring")
    print("=" * 80)

    processor = StreamProcessor(window_type=WindowType.TUMBLING, window_size=timedelta(seconds=10))

    print("\n📊 Processing event stream...")

    base_time = datetime.now()

    # Send burst of events
    for i in range(100):
        event = StreamEvent(
            event_id=f"evt-{i:04d}",
            event_type="metric_event",
            timestamp=base_time + timedelta(milliseconds=i * 50),
            event_time=base_time + timedelta(milliseconds=i * 50),
            data={"value": i, "metric": "request_count"},
            source="app-server",
        )
        processor.process_event(event)

        if (i + 1) % 20 == 0:
            print(f"   Processed {i + 1} events...")

    # Get metrics
    metrics = processor.get_metrics()

    print(f"\n📈 Stream Processing Metrics:")
    print(f"   Total Events Processed: {metrics.total_events}")
    print(f"   Average Latency: {metrics.average_latency_ms:.2f}ms")
    print(f"   Late Events: {metrics.late_events}")
    print(f"   Windows Processed: {metrics.windows_processed}")

    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if metrics.average_latency_ms < 10:
        print(f"   ✅ Excellent - Very low latency")
    elif metrics.average_latency_ms < 50:
        print(f"   ✅ Good - Acceptable latency")
    elif metrics.average_latency_ms < 100:
        print(f"   ⚠️  Fair - Moderate latency")
    else:
        print(f"   ❌ Poor - High latency")

    return processor


# ============================================================================
# MAIN: Run All Examples
# ============================================================================


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("REAL-TIME STREAMING ANALYTICS - USAGE EXAMPLES")
    print("=" * 80)
    print("\nDemonstrating comprehensive streaming analytics capabilities:")
    print("  1. Real-time transaction monitoring")
    print("  2. User session analytics")
    print("  3. Fraud detection with CEP")
    print("  4. Sliding window metrics")
    print("  5. IoT sensor data processing")
    print("  6. Stream metrics and monitoring")

    try:
        # Run examples
        example_transaction_monitoring()
        example_user_session_analytics()
        example_fraud_detection()
        example_sliding_window_metrics()
        example_iot_sensor_processing()
        example_stream_metrics()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY! ✅")
        print("=" * 80)
        print("\n💡 Key Takeaways:")
        print("   • Tumbling windows for fixed-time aggregations")
        print("   • Sliding windows for moving averages")
        print("   • Session windows for user behavior analysis")
        print("   • CEP for complex pattern detection")
        print("   • Real-time metrics for system monitoring")
        print("   • Multiple aggregation types (sum, avg, count, min, max)")
        print("\n📚 For more information, see:")
        print("   • src/analytics/streaming_analytics.py")
        print("   • tests/unit/analytics/test_streaming_analytics.py")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
