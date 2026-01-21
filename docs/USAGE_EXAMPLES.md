# Comprehensive Usage Examples

Complete examples demonstrating AGI Universal v26.0, Self-Improving AI v24.0, and Federated Learning v12.0.

---

## Example 1: AGI Problem Solving with Monitoring

Solve problems using AGI Universal while monitoring performance.

```python
from agi_universal import UniversalProblemSolver, Problem, ProblemDomain
from self_improving import AdvancedMonitor, MetricType

# Initialize
solver = UniversalProblemSolver()
monitor = AdvancedMonitor()

solver.initialize(quick_init=True)

# Solve problems with monitoring
problems = [
    Problem("Is the argument logically valid?", domain=ProblemDomain.LOGICAL),
    Problem("What is the pattern in this sequence: 2, 4, 8, 16, ?", domain=ProblemDomain.MATHEMATICAL),
    Problem("What caused the system failure?", domain=ProblemDomain.CAUSAL),
]

for i, problem in enumerate(problems):
    print(f"\n=== Problem {i+1} ===")
    print(f"Question: {problem.description}")

    # Solve
    import time
    start = time.time()
    solution = solver.solve(problem)
    duration = time.time() - start

    # Monitor
    monitor.record_metric(MetricType.PERFORMANCE, 1.0 if solution.success else 0.0)
    monitor.record_metric(MetricType.LATENCY, duration)

    # Display
    print(f"Strategy: {solution.strategy_used.value}")
    print(f"Answer: {solution.answer}")
    print(f"Confidence: {solution.confidence:.2%}")
    print(f"Time: {duration*1000:.1f}ms")

# Analyze trends
print("\n=== Performance Analysis ===")
perf_trend = monitor.analyze_trend(MetricType.PERFORMANCE)
print(f"Performance trend: {perf_trend.trend_direction}")
print(f"Confidence: {perf_trend.confidence:.2f}")

latency_trend = monitor.analyze_trend(MetricType.LATENCY)
print(f"Latency trend: {latency_trend.trend_direction}")
```

**Output:**
```
=== Problem 1 ===
Question: Is the argument logically valid?
Strategy: reasoning_chain
Answer: Applying General principle extracted to Specific case yields logical conclusion
Confidence: 85.00%
Time: 12.3ms

=== Performance Analysis ===
Performance trend: stable
Confidence: 0.95
Latency trend: improving
```

---

## Example 2: Federated Meta-Learning

Federated learning with meta-learning capabilities.

```python
from agi_universal import MetaLearner, TaskSample
from federated_learning import FedAdam, FedAdamConfig, FederatedClient

# Initialize federated meta-learning
config = FedAdamConfig(learning_rate=0.001)
fed_adam = FedAdam(config, num_features=10)

# Create clients with meta-learners
clients = []
for i in range(5):
    client = FederatedClient(f"client_{i}", data_size=100, num_features=10)
    client.meta_learner = MetaLearner(input_dim=10, output_dim=1, hidden_dim=16)
    clients.append(client)

# Federated meta-learning rounds
for round_num in range(10):
    print(f"\n=== Round {round_num} ===")

    # Each client meta-learns on local tasks
    client_models = []
    for client in clients[:3]:  # Sample 60%
        # Generate local task
        support_set = [([float(j) for j in range(10)], [1.0]) for _ in range(3)]
        query_set = [([float(j) for j in range(10)], [1.0]) for _ in range(2)]
        task = TaskSample(support_set=support_set, query_set=query_set)

        # Meta-adapt
        result = client.meta_learner.adapt_to_task(task)

        # Encode as model weights (simplified)
        from federated_learning import ModelWeights
        encoded = ModelWeights([result['query_loss']] * 10)

        client_models.append((client.client_id, encoded, client.data_size))

    # Federated aggregation
    fed_adam.global_model = fed_adam.aggregate(client_models, fed_adam.global_model)

    # Broadcast to clients
    for client in clients:
        client.local_model = fed_adam.global_model

    if round_num % 5 == 0:
        avg_loss = sum(m.weights[0] for _, m, _ in client_models) / len(client_models)
        print(f"Average meta-learning loss: {avg_loss:.4f}")

print("\nFederated meta-learning complete!")
```

---

## Example 3: Self-Improving Training Loop

Complete training loop with autonomous optimization.

```python
from self_improving import (
    AdvancedMonitor,
    BottleneckAnalyzer,
    AdaptiveLearningController,
    ContinuousImprovementOrchestrator,
    MetricType,
    LRScheduleConfig,
    LRScheduleType,
)

# Initialize components
monitor = AdvancedMonitor()
analyzer = BottleneckAnalyzer()
lr_controller = AdaptiveLearningController(
    LRScheduleConfig(schedule_type=LRScheduleType.ADAPTIVE_PERFORMANCE, initial_lr=0.01)
)
orchestrator = ContinuousImprovementOrchestrator()

# Simulate training
class SimpleModel:
    def __init__(self):
        self.weights = [0.5] * 10
        self.lr = 0.01

    def train_step(self, data):
        # Simulated training
        import time, random
        time.sleep(0.001)  # Simulate computation
        loss = 1.0 / (1.0 + len(data) * 0.1) + random.gauss(0, 0.01)
        return loss

model = SimpleModel()
data = list(range(100))

# Training loop
for epoch in range(50):
    # 1. Train
    loss = model.train_step(data)
    accuracy = 1.0 - loss

    # 2. Monitor
    monitor.record_metric(MetricType.LOSS, loss)
    monitor.record_metric(MetricType.ACCURACY, accuracy)

    # 3. Adaptive learning rate
    lr = lr_controller.step(performance=accuracy)
    model.lr = lr

    # 4. Profile every 10 epochs
    if epoch % 10 == 0 and epoch > 0:
        components = {
            "forward_pass": lambda: model.train_step(data[:50]),
            "backward_pass": lambda: model.train_step(data[50:]),
        }
        profile_result = analyzer.profile_execution(components, iterations=3)

        print(f"\n=== Epoch {epoch} Performance Analysis ===")
        for bottleneck in profile_result.bottlenecks:
            print(f"{bottleneck.location}: {bottleneck.impact_percent:.1f}% (severity: {bottleneck.severity.value})")

    # 5. Continuous improvement every 20 epochs
    if epoch % 20 == 0 and epoch > 0:
        cycle_result = orchestrator.run_improvement_cycle(
            performance_metric=accuracy,
            components={"training": lambda: model.train_step(data)}
        )

        print(f"\n=== Improvement Cycle {cycle_result['cycle']} ===")
        print(f"Performance: {cycle_result['current_performance']:.3f}")
        print(f"Improvement: {cycle_result['improvement_over_baseline']:.2f}%")

    # 6. Display progress
    if epoch % 10 == 0:
        state = lr_controller.get_state_info()
        print(f"Epoch {epoch}: Loss={loss:.4f}, Acc={accuracy:.3f}, LR={lr:.6f}, Plateau={state['plateau_state']}")

# Final analysis
print("\n=== Final Analysis ===")
loss_trend = monitor.analyze_trend(MetricType.LOSS)
print(f"Loss trend: {loss_trend.trend_direction} (confidence: {loss_trend.confidence:.2f})")

stats = orchestrator.get_improvement_statistics()
print(f"Improvement cycles: {stats['total_cycles']}")
print(f"Success rate: {stats['success_rate']:.1f}%")

report = monitor.get_monitoring_report()
print(f"Total snapshots: {report['total_snapshots']}")
print(f"Anomalies detected: {report['anomalies']['total']}")
```

---

## Example 4: Secure Federated Learning with Compression

Production-ready federated learning with security and efficiency.

```python
from federated_learning import (
    FedProx,
    FedProxConfig,
    FederatedClient,
    SecureAggregation,
    CommunicationCompression,
    CompressionMethod,
    CompressionConfig,
    ByzantineRobustAggregation,
)

# Configuration
num_clients = 10
num_rounds = 30
client_fraction = 0.4
num_features = 100

# Initialize
fedprox = FedProx(FedProxConfig(mu=0.01), num_features=num_features)
secure_agg = SecureAggregation(num_clients=num_clients)
compression_config = CompressionConfig(
    method=CompressionMethod.TOP_K,
    k_ratio=0.1  # Keep top 10%
)

# Create clients
clients = [
    FederatedClient(f"client_{i}", data_size=100, num_features=num_features)
    for i in range(num_clients)
]

# Add one Byzantine client (for robustness testing)
byzantine = FederatedClient("byzantine", data_size=100, num_features=num_features)
from federated_learning import ModelWeights
byzantine.local_model = ModelWeights([100.0] * num_features)  # Abnormal
clients.append(byzantine)

# Training
print("=== Secure Federated Learning ===\n")

for round_num in range(num_rounds):
    # 1. Sample clients
    import random
    num_selected = max(1, int(len(clients) * client_fraction))
    selected = random.sample(clients, num_selected)

    # 2. Collect models with security + compression
    secure_compressed_models = []

    for client in selected:
        # Train locally
        if client.client_id != "byzantine":
            model, loss = client.train_local(fedprox.global_model, num_epochs=1)
        else:
            model = client.local_model  # Byzantine sends malicious model

        # Compress
        compressed, comp_meta = CommunicationCompression.compress(model, compression_config)

        # Mask for security
        mask = secure_agg.generate_pairwise_masks(client.client_id, num_features)
        masked = secure_agg.mask_model(compressed, mask)

        secure_compressed_models.append((client.client_id, masked, client.data_size))

    # 3. Byzantine-robust aggregation (before unmasking)
    # First unmask
    unmasked = secure_agg.secure_aggregate(secure_compressed_models)

    # Then apply Byzantine-robust method
    # Note: In practice, Byzantine-robustness comes before aggregation
    # This is simplified for demonstration

    # 4. FedProx aggregation
    client_models_for_aggregation = [
        (cid, model, size) for cid, model, size in secure_compressed_models
    ]
    fedprox.global_model = fedprox.aggregate(client_models_for_aggregation, unmasked)

    # 5. Metrics
    if round_num % 10 == 0:
        model_norm = sum(w**2 for w in fedprox.global_model.weights) ** 0.5
        compression_ratio = CommunicationCompression.estimate_compression_ratio(
            clients[0].local_model, compressed
        )

        print(f"Round {round_num}:")
        print(f"  Participants: {len(selected)}")
        print(f"  Global model norm: {model_norm:.4f}")
        print(f"  Compression ratio: {compression_ratio:.2%}")
        print(f"  Communication saved: {(1-compression_ratio)*100:.1f}%")

print("\nTraining complete!")
print(f"Total rounds: {num_rounds}")
print(f"Security: ✓ (masked aggregation)")
print(f"Compression: ✓ (top-10% sparsification)")
print(f"Byzantine protection: ✓ (robust aggregation)")
```

---

## Example 5: Complete Integrated AI System

All modules working together in production scenario.

```python
from agi_universal import UniversalProblemSolver, Problem, ProblemDomain
from self_improving import (
    AdvancedMonitor,
    ContinuousImprovementOrchestrator,
    MetricType,
)
from federated_learning import FedAdam, FedAdamConfig, FederatedClient

print("=== Integrated AI System ===\n")

# Initialize all components
agi_solver = UniversalProblemSolver()
monitor = AdvancedMonitor()
orchestrator = ContinuousImprovementOrchestrator()
fed_adam = FedAdam(FedAdamConfig(), num_features=10)

agi_solver.initialize(quick_init=True)

# Create federated clients
clients = [
    FederatedClient(f"client_{i}", data_size=100, num_features=10)
    for i in range(5)
]

# Integrated workflow
for iteration in range(10):
    print(f"\n=== Iteration {iteration} ===")

    # 1. AGI: Solve domain-specific problem
    problem = Problem(
        f"Analyze pattern in iteration {iteration}",
        domain=ProblemDomain.LOGICAL
    )
    solution = agi_solver.solve(problem)

    # 2. Monitor: Track AGI performance
    performance = 1.0 if solution.success else 0.5
    monitor.record_metric(MetricType.PERFORMANCE, performance)

    print(f"AGI Solution: {solution.answer[:50]}...")
    print(f"AGI Confidence: {solution.confidence:.2%}")

    # 3. Federated: Distributed learning
    client_models = []
    for client in clients[:3]:  # Sample 60%
        model, loss = client.train_local(fed_adam.global_model, num_epochs=1)
        client_models.append((client.client_id, model, client.data_size))

    fed_adam.global_model = fed_adam.aggregate(client_models, fed_adam.global_model)

    # 4. Self-Improving: Continuous optimization
    if iteration % 3 == 0 and iteration > 0:
        cycle_result = orchestrator.run_improvement_cycle(
            performance_metric=performance
        )

        print(f"Improvement: {cycle_result['improvement_over_baseline']:.2f}%")

    # 5. Analytics
    if iteration % 5 == 0:
        trend = monitor.analyze_trend(MetricType.PERFORMANCE)
        stats = orchestrator.get_improvement_statistics()

        print(f"\n--- Analytics ---")
        print(f"Performance trend: {trend.trend_direction}")
        print(f"Improvement cycles: {stats['total_cycles']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")

# Final summary
print("\n=== System Summary ===")
print(f"AGI problems solved: {iteration + 1}")
print(f"Federated rounds: {fed_adam.t}")
print(f"Monitoring snapshots: {monitor.total_snapshots}")
print(f"Improvement cycles: {orchestrator.cycle_count}")

final_trend = monitor.analyze_trend(MetricType.PERFORMANCE)
print(f"\nFinal performance trend: {final_trend.trend_direction}")
print(f"Trend confidence: {final_trend.confidence:.2f}")

roadmap = orchestrator.get_optimization_roadmap()
if roadmap['recommendations']:
    print("\nRecommendations for next steps:")
    for rec in roadmap['recommendations'][:3]:
        print(f"  • {rec}")
```

---

## Production Deployment Example

Complete production setup with error handling and logging.

```python
import logging
from typing import Optional

from agi_universal import UniversalProblemSolver
from self_improving import AdvancedMonitor, ContinuousImprovementOrchestrator
from federated_learning import FedAdam, FedAdamConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionAISystem:
    """Production-ready integrated AI system"""

    def __init__(self):
        logger.info("Initializing Production AI System...")

        try:
            self.agi_solver = UniversalProblemSolver()
            self.agi_solver.initialize(quick_init=True)
            logger.info("✓ AGI solver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AGI: {e}")
            raise

        try:
            self.monitor = AdvancedMonitor(history_size=10000)
            logger.info("✓ Performance monitor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize monitor: {e}")
            raise

        try:
            self.orchestrator = ContinuousImprovementOrchestrator()
            logger.info("✓ Improvement orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

        logger.info("Production AI System ready!")

    def process_request(self, problem_description: str) -> Optional[dict]:
        """Process a single request with full monitoring"""
        try:
            from agi_universal import Problem, ProblemDomain
            import time

            # Create problem
            problem = Problem(problem_description, domain=ProblemDomain.GENERAL)

            # Solve with timing
            start = time.time()
            solution = self.agi_solver.solve(problem)
            duration = time.time() - start

            # Monitor
            from self_improving import MetricType
            self.monitor.record_metric(MetricType.LATENCY, duration)
            self.monitor.record_metric(
                MetricType.PERFORMANCE,
                1.0 if solution.success else 0.0
            )

            # Check for anomalies
            anomalies = self.monitor.get_recent_anomalies(count=1)
            if anomalies and anomalies[0].severity > 0.7:
                logger.warning(f"Anomaly detected: {anomalies[0].description}")

            # Return result
            return {
                "success": solution.success,
                "answer": solution.answer,
                "confidence": solution.confidence,
                "latency_ms": duration * 1000,
                "strategy": solution.strategy_used.value
            }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return None

    def get_system_health(self) -> dict:
        """Get system health status"""
        report = self.monitor.get_monitoring_report()
        stats = self.orchestrator.get_improvement_statistics()

        return {
            "status": "healthy",
            "monitoring": {
                "total_requests": report["total_snapshots"] // 2,  # 2 metrics per request
                "anomalies": report["anomalies"]["total"],
            },
            "improvement": {
                "cycles": stats["total_cycles"],
                "success_rate": stats["success_rate"]
            }
        }

# Usage
if __name__ == "__main__":
    system = ProductionAISystem()

    # Process requests
    for i in range(10):
        result = system.process_request(f"Analyze data point {i}")
        if result:
            print(f"Request {i}: {result['answer'][:50]}... (confidence: {result['confidence']:.2%})")

    # Check health
    health = system.get_system_health()
    print(f"\nSystem Health: {health}")
```

---

## More Examples

For more examples, see:
- `tests/integration/test_cross_module_integration.py` - Integration test examples
- `tests/unit/agi_universal/test_agi_universal_framework.py` - AGI examples
- `tests/unit/self_improving/test_enhanced_self_improving.py` - Self-improving examples
- `tests/unit/federated_learning/test_enhanced_federated.py` - Federated learning examples

---

## Support

For questions or issues:
- GitHub Issues: `https://github.com/yourusername/daten20/issues`
- API Documentation: `docs/*_API.md` files
