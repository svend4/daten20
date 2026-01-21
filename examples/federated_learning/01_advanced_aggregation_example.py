"""
Example 1: Advanced Federated Aggregation Algorithms

Demonstrates FedAvg, FedProx, FedAdam, SCAFFOLD, and Byzantine-robust methods.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import random
from src.federated_learning import (
    FederatedAveraging,
    FederatedClient,
    ModelWeights,
)
from src.federated_learning.advanced_aggregation import (
    FedProx,
    FedProxConfig,
    FedAdam,
    FedAdamConfig,
    SCAFFOLD,
    SCAFFOLDConfig,
    ByzantineRobustAggregation,
)


def create_clients(num_clients: int = 10, num_features: int = 10):
    """Create federated clients with heterogeneous data"""
    clients = []
    for i in range(num_clients):
        # Heterogeneous data sizes
        data_size = random.randint(50, 500)
        client = FederatedClient(f"client_{i}", data_size, num_features)
        clients.append(client)
    return clients


def main():
    print("=" * 60)
    print("Federated Learning v12.0 - Advanced Aggregation")
    print("=" * 60)

    num_clients = 10
    num_features = 10
    num_rounds = 20

    # Create clients
    print(f"\n[1] Creating {num_clients} Federated Clients...")
    clients = create_clients(num_clients, num_features)

    total_data = sum(c.data_size for c in clients)
    print(f"Total data samples: {total_data}")
    print(f"Data per client: min={min(c.data_size for c in clients)}, "
          f"max={max(c.data_size for c in clients)}")

    # ========================================================================
    # FedAvg Baseline
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.1] FedAvg (Baseline)")
    print("=" * 60)

    fedavg = FederatedAveraging(num_features=num_features)

    print(f"\nTraining with FedAvg for {num_rounds} rounds...")

    for round_num in range(num_rounds):
        result = fedavg.run_round(clients, client_fraction=0.3, local_epochs=1)

        if round_num % 5 == 0 or round_num == num_rounds - 1:
            print(f"Round {result['round']:2d}: "
                  f"Loss={result['average_loss']:.4f}, "
                  f"Clients={result['participating_clients']}, "
                  f"Convergence={result['convergence_indicator']:.2f}")

    fedavg_final_loss = fedavg.loss_history[-1] if fedavg.loss_history else 1.0
    print(f"\nFedAvg Final Loss: {fedavg_final_loss:.4f}")

    # ========================================================================
    # FedProx - Handles heterogeneity
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.2] FedProx (Proximal Term for Heterogeneity)")
    print("=" * 60)

    fedprox_config = FedProxConfig(
        mu=0.01,  # Proximal term coefficient
        learning_rate=0.01
    )

    fedprox = FedProx(fedprox_config, num_features=num_features)

    print(f"\nFedProx Configuration:")
    print(f"  Proximal coefficient (μ): {fedprox_config.mu}")
    print(f"  Learning rate: {fedprox_config.learning_rate}")

    print(f"\nTraining with FedProx for {num_rounds} rounds...")

    loss_history = []

    for round_num in range(num_rounds):
        # Select clients
        selected_clients = random.sample(clients, k=3)

        # Train locally
        client_updates = []
        for client in selected_clients:
            updated_model, loss = client.train_local(fedprox.global_model, num_epochs=1)
            client_updates.append((client.client_id, updated_model, client.data_size))

        # Aggregate with FedProx
        fedprox.global_model = fedprox.aggregate(client_updates, fedprox.global_model)

        # Track loss
        avg_loss = sum(client.local_loss for client in selected_clients) / len(selected_clients)
        loss_history.append(avg_loss)

        if round_num % 5 == 0 or round_num == num_rounds - 1:
            print(f"Round {round_num:2d}: Loss={avg_loss:.4f}")

    fedprox_final_loss = loss_history[-1]
    print(f"\nFedProx Final Loss: {fedprox_final_loss:.4f}")

    # ========================================================================
    # FedAdam - Server-side Adam optimizer
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.3] FedAdam (Server-Side Adaptive Optimizer)")
    print("=" * 60)

    fedadam_config = FedAdamConfig(
        learning_rate=0.001,
        beta1=0.9,
        beta2=0.999,
        epsilon=1e-8
    )

    fedadam = FedAdam(fedadam_config, num_features=num_features)

    print(f"\nFedAdam Configuration:")
    print(f"  Server learning rate: {fedadam_config.learning_rate}")
    print(f"  Beta1 (momentum): {fedadam_config.beta1}")
    print(f"  Beta2 (variance): {fedadam_config.beta2}")

    print(f"\nTraining with FedAdam for {num_rounds} rounds...")

    loss_history = []

    for round_num in range(num_rounds):
        # Select clients
        selected_clients = random.sample(clients, k=3)

        # Train locally
        client_updates = []
        for client in selected_clients:
            updated_model, loss = client.train_local(fedadam.global_model, num_epochs=1)
            client_updates.append((client.client_id, updated_model, client.data_size))

        # Aggregate with FedAdam (uses Adam optimizer on server)
        fedadam.global_model = fedadam.aggregate(client_updates, fedadam.global_model)

        # Track loss
        avg_loss = sum(client.local_loss for client in selected_clients) / len(selected_clients)
        loss_history.append(avg_loss)

        if round_num % 5 == 0 or round_num == num_rounds - 1:
            print(f"Round {round_num:2d}: Loss={avg_loss:.4f}, "
                  f"Momentum step: {fedadam.t}")

    fedadam_final_loss = loss_history[-1]
    print(f"\nFedAdam Final Loss: {fedadam_final_loss:.4f}")

    # ========================================================================
    # SCAFFOLD - Control variates for variance reduction
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.4] SCAFFOLD (Stochastic Controlled Averaging)")
    print("=" * 60)

    scaffold_config = SCAFFOLDConfig(
        learning_rate=0.01,
        global_momentum=0.9
    )

    scaffold = SCAFFOLD(scaffold_config, num_features=num_features)

    print(f"\nSCAFFOLD Configuration:")
    print(f"  Learning rate: {scaffold_config.learning_rate}")
    print(f"  Global momentum: {scaffold_config.global_momentum}")

    print(f"\nTraining with SCAFFOLD for {num_rounds} rounds...")

    loss_history = []

    for round_num in range(num_rounds):
        # Select clients
        selected_clients = random.sample(clients, k=3)

        # Train locally with control variates
        client_updates = []
        for client in selected_clients:
            updated_model, loss = client.train_local(scaffold.global_model, num_epochs=1)

            # Initialize client control variate if needed
            if client.client_id not in scaffold.c_clients:
                scaffold.c_clients[client.client_id] = [0.0] * num_features

            # Get client control variate
            c_client = scaffold.c_clients[client.client_id]

            client_updates.append((client.client_id, updated_model, client.data_size, c_client))

        # Aggregate with SCAFFOLD
        scaffold.global_model = scaffold.aggregate(client_updates, scaffold.global_model)

        # Track loss
        avg_loss = sum(client.local_loss for client in selected_clients) / len(selected_clients)
        loss_history.append(avg_loss)

        if round_num % 5 == 0 or round_num == num_rounds - 1:
            print(f"Round {round_num:2d}: Loss={avg_loss:.4f}, "
                  f"Control variates: {len(scaffold.c_clients)}")

    scaffold_final_loss = loss_history[-1]
    print(f"\nSCAFFOLD Final Loss: {scaffold_final_loss:.4f}")

    # ========================================================================
    # Byzantine-Robust: Krum
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.5] Krum (Byzantine-Robust Aggregation)")
    print("=" * 60)

    print("\nSimulating Byzantine attack scenario...")
    print("10 honest clients + 2 Byzantine (malicious) clients")

    # Create honest clients
    honest_clients = create_clients(num_clients=10, num_features=num_features)

    # Train honest clients
    global_model = ModelWeights(weights=[random.uniform(-0.1, 0.1) for _ in range(num_features)])

    client_models = []
    for client in honest_clients:
        updated_model, _ = client.train_local(global_model, num_epochs=1)
        client_models.append((client.client_id, updated_model, client.data_size))

    # Add 2 Byzantine clients with malicious updates
    for i in range(2):
        # Byzantine client sends extreme values
        malicious_weights = [random.uniform(-10.0, 10.0) for _ in range(num_features)]
        byzantine_model = ModelWeights(weights=malicious_weights)
        client_models.append((f"byzantine_{i}", byzantine_model, 100))

    print(f"\nTotal clients: {len(client_models)} (10 honest + 2 Byzantine)")

    # Krum aggregation (tolerates f=2 Byzantine clients)
    krum_result = ByzantineRobustAggregation.krum(client_models, f=2)

    print(f"\nKrum selected model (Byzantine-robust):")
    print(f"  Selected from honest clients")
    print(f"  Model norm: {sum(w**2 for w in krum_result.weights)**0.5:.4f}")

    # Compare with naive average (vulnerable to Byzantine)
    print("\n  For comparison, naive averaging (vulnerable):")
    naive_avg_weights = [0.0] * num_features
    for _, model, _ in client_models:
        for i in range(num_features):
            naive_avg_weights[i] += model.weights[i] / len(client_models)

    naive_norm = sum(w**2 for w in naive_avg_weights)**0.5
    print(f"  Naive average norm: {naive_norm:.4f} (corrupted by Byzantine clients)")

    # ========================================================================
    # Byzantine-Robust: Coordinate-wise Median
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2.6] Coordinate-Wise Median (Byzantine-Robust)")
    print("=" * 60)

    median_result = ByzantineRobustAggregation.coordinate_wise_median(client_models)

    print(f"\nMedian aggregation (Byzantine-robust):")
    print(f"  Takes median of each weight coordinate")
    print(f"  Model norm: {sum(w**2 for w in median_result.weights)**0.5:.4f}")
    print(f"  Robust to up to 50% Byzantine clients")

    # Comparison summary
    print("\n" + "=" * 60)
    print("[3] Algorithm Comparison Summary")
    print("=" * 60)

    print(f"""
Algorithm Performance Comparison:

1. FedAvg (Baseline):       {fedavg_final_loss:.4f}
2. FedProx:                 {fedprox_final_loss:.4f}
3. FedAdam:                 {fedadam_final_loss:.4f}
4. SCAFFOLD:                {scaffold_final_loss:.4f}

**When to Use Each:**

• FedAvg: Standard baseline, homogeneous data
• FedProx: Heterogeneous data, system heterogeneity
• FedAdam: Fast convergence, adaptive learning
• SCAFFOLD: Variance reduction, client drift
• Krum: Byzantine fault tolerance (up to f clients)
• Median: Simple Byzantine robustness (up to 50%)

**Trade-offs:**

FedAvg:     Fast, simple, but sensitive to heterogeneity
FedProx:    Handles heterogeneity, slight overhead
FedAdam:    Best convergence, momentum storage overhead
SCAFFOLD:   Variance reduction, requires control variates
Krum:       Byzantine-robust, O(n²) complexity
Median:     Byzantine-robust, simple, coordinate-wise
    """)

    print("\n✓ Advanced aggregation example complete!")


if __name__ == "__main__":
    main()
