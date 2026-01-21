"""
Example 1: Advanced Monitoring with Anomaly Detection

Demonstrates how to monitor performance metrics, detect anomalies,
analyze trends, and predict future performance.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import time
import random
from src.self_improving import (
    AdvancedMonitor,
    get_global_monitor,
)


def simulate_training_loop(monitor: AdvancedMonitor, num_epochs: int = 50):
    """Simulate a training loop with realistic metrics"""

    print(f"\nSimulating {num_epochs} training epochs...")
    print("-" * 60)

    for epoch in range(1, num_epochs + 1):
        # Simulate decreasing loss (with occasional spikes)
        base_loss = 2.0 / (epoch + 1)

        # Add occasional anomalies (spikes)
        if epoch in [15, 32]:  # Anomaly epochs
            loss = base_loss * 3.0  # Spike
        else:
            loss = base_loss + random.gauss(0, 0.05)

        # Simulate increasing accuracy
        accuracy = min(0.95, 0.5 + (epoch / num_epochs) * 0.45 + random.gauss(0, 0.02))

        # Simulate varying training speed
        samples_per_sec = 1000 + random.gauss(0, 100)

        # Record metrics
        monitor.record_metric('loss', loss)
        monitor.record_metric('accuracy', accuracy)
        monitor.record_metric('throughput', samples_per_sec)

        # Print progress every 10 epochs
        if epoch % 10 == 0 or epoch in [15, 32]:
            print(f"Epoch {epoch:3d}: Loss={loss:.4f}, Acc={accuracy:.4f}, "
                  f"Throughput={samples_per_sec:.0f} samples/s")

            # Check for anomalies
            if 'loss' in monitor.anomaly_history:
                recent_anomalies = [
                    a for a in monitor.anomaly_history['loss']
                    if epoch - 5 <= a['index'] <= epoch
                ]
                if recent_anomalies:
                    print(f"  ⚠️  ANOMALY DETECTED in last 5 epochs!")


def main():
    print("=" * 60)
    print("Self-Improving AI v24.0 - Advanced Monitoring")
    print("=" * 60)

    # Get global monitor (singleton)
    print("\n[1] Initializing Global Monitor...")
    monitor = get_global_monitor()

    print(f"Monitor initialized: {monitor is not None}")
    print(f"History size limit: {monitor.history_size}")
    print(f"Anomaly threshold (z-score): {monitor.anomaly_threshold}")

    # Simulate training with monitoring
    print("\n[2] Recording Metrics During Training")
    print("=" * 60)

    simulate_training_loop(monitor, num_epochs=50)

    # Analyze trends
    print("\n" + "=" * 60)
    print("[3] Trend Analysis")
    print("=" * 60)

    metrics_to_analyze = ['loss', 'accuracy', 'throughput']

    for metric in metrics_to_analyze:
        print(f"\n{metric.upper()}:")

        trend_result = monitor.analyze_trend(metric, window_size=20)

        print(f"  Direction: {trend_result['direction']}")
        print(f"  Slope: {trend_result['slope']:.6f}")
        print(f"  Trend strength: {trend_result['trend_strength']:.1%}")
        print(f"  Volatility: {trend_result['volatility']:.6f}")

        if trend_result['direction'] == 'decreasing':
            print(f"  ✓ {metric.capitalize()} is improving (decreasing)")
        elif trend_result['direction'] == 'increasing':
            if metric == 'accuracy' or metric == 'throughput':
                print(f"  ✓ {metric.capitalize()} is improving (increasing)")
            else:
                print(f"  ⚠️  {metric.capitalize()} is worsening (increasing)")

    # Detect anomalies
    print("\n" + "=" * 60)
    print("[4] Anomaly Detection")
    print("=" * 60)

    for metric in metrics_to_analyze:
        anomalies = monitor.detect_anomalies(metric)

        print(f"\n{metric.upper()}:")
        print(f"  Total anomalies detected: {len(anomalies)}")

        if anomalies:
            print(f"  Anomaly details:")
            for i, anomaly in enumerate(anomalies[:3], 1):  # Show first 3
                print(f"    {i}. Index {anomaly['index']}: "
                      f"Value={anomaly['value']:.4f}, "
                      f"Z-score={anomaly['z_score']:.2f}")

            if len(anomalies) > 3:
                print(f"    ... and {len(anomalies) - 3} more")
        else:
            print(f"  ✓ No anomalies detected")

    # Predict future performance
    print("\n" + "=" * 60)
    print("[5] Performance Prediction")
    print("=" * 60)

    steps_ahead = 10

    for metric in ['loss', 'accuracy']:
        print(f"\n{metric.upper()}:")

        prediction = monitor.predict_performance(metric, steps_ahead=steps_ahead)

        print(f"  Current value: {prediction['current_value']:.4f}")
        print(f"  Predicted value (in {steps_ahead} steps): {prediction['predicted_value']:.4f}")
        print(f"  Expected change: {prediction['expected_change']:.4f}")
        print(f"  Prediction confidence: {prediction['confidence']:.1%}")

        if prediction['is_improving']:
            print(f"  ✓ Metric is predicted to improve")
        else:
            print(f"  ⚠️  Metric is predicted to worsen or plateau")

    # Get metric summary
    print("\n" + "=" * 60)
    print("[6] Metric Summary")
    print("=" * 60)

    for metric in metrics_to_analyze:
        if metric in monitor.metrics:
            history = monitor.metrics[metric]

            print(f"\n{metric.upper()}:")
            print(f"  Data points: {len(history)}")
            print(f"  Current value: {history[-1]:.4f}")
            print(f"  Min: {min(history):.4f}")
            print(f"  Max: {max(history):.4f}")
            print(f"  Mean: {sum(history) / len(history):.4f}")

    # Real-time monitoring tips
    print("\n" + "=" * 60)
    print("[7] Real-Time Monitoring Tips")
    print("=" * 60)

    print("""
Key Features Demonstrated:

1. **Metric Recording**
   - Use record_metric() to track any numeric metric
   - Automatic time-series storage with configurable history
   - Thread-safe for concurrent training

2. **Anomaly Detection**
   - Statistical z-score based detection
   - Configurable sensitivity (default: 3.0)
   - Tracks anomaly history for analysis

3. **Trend Analysis**
   - Linear regression for trend direction
   - Slope and strength metrics
   - Volatility measurement

4. **Performance Prediction**
   - Extrapolates future values based on trends
   - Confidence scores based on trend strength
   - Helps predict convergence or divergence

5. **Best Practices**
   - Monitor multiple metrics simultaneously
   - Check for anomalies regularly
   - Use predictions to adjust hyperparameters
   - Analyze trends to understand training dynamics
    """)

    print("\n✓ Advanced monitoring example complete!")


if __name__ == "__main__":
    main()
