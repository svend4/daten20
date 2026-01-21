"""
Example 3: Communication Compression

Demonstrates quantization, top-k sparsification, and adaptive compression.
"""

import sys
sys.path.insert(0, '/home/user/daten20')

import random
from src.federated_learning import ModelWeights
from src.federated_learning.communication_efficiency import (
    CommunicationCompression,
    CompressionType,
    AdaptiveCompression,
)


def create_model(num_features: int = 1000):
    """Create a model with random weights"""
    weights = [random.gauss(0, 1.0) for _ in range(num_features)]
    return ModelWeights(weights=weights)


def calculate_size_mb(model: ModelWeights):
    """Calculate model size in MB (assuming float32 = 4 bytes)"""
    return len(model.weights) * 4 / (1024 * 1024)


def calculate_compression_ratio(original_model: ModelWeights, compressed_data):
    """Calculate compression ratio"""
    original_size = len(original_model.weights) * 4  # float32 = 4 bytes

    if 'indices' in compressed_data:
        # Sparse format: value (4 bytes) + index (4 bytes) per non-zero
        compressed_size = len(compressed_data['values']) * 8
    elif 'scale' in compressed_data and 'zero_point' in compressed_data:
        # Quantized format: 1 byte per weight + metadata
        compressed_size = len(compressed_data['quantized']) + 8
    else:
        compressed_size = original_size

    return original_size / compressed_size if compressed_size > 0 else 1.0


def main():
    print("=" * 60)
    print("Federated Learning v12.0 - Communication Compression")
    print("=" * 60)

    num_features = 1000

    # Create a model
    print(f"\n[1] Creating Model with {num_features} Parameters...")
    model = create_model(num_features)

    original_size = calculate_size_mb(model)
    print(f"Original model size: {original_size:.4f} MB")
    print(f"Sample weights: {[f'{w:.4f}' for w in model.weights[:5]]}...")

    # Initialize compressor
    compressor = CommunicationCompression()

    # ========================================================================
    # Quantization Compression
    # ========================================================================
    print("\n" + "=" * 60)
    print("[2] Quantization Compression")
    print("=" * 60)

    print("\nQuantization reduces precision (e.g., float32 → int8)")

    # 8-bit quantization
    print("\n[2.1] 8-bit Quantization")
    print("-" * 60)

    compressed_8bit = compressor.compress(
        model,
        compression_type=CompressionType.QUANTIZATION,
        num_bits=8
    )

    print(f"\nCompression Results:")
    print(f"  Original bits: 32 (float32)")
    print(f"  Compressed bits: 8 (int8)")
    print(f"  Compression ratio: {compressed_8bit['compression_ratio']:.2f}x")
    print(f"  Size reduction: {(1 - 1/compressed_8bit['compression_ratio'])*100:.1f}%")

    # Decompress and check accuracy
    decompressed_8bit = compressor.decompress(compressed_8bit)

    # Calculate reconstruction error
    mse = sum((o - d) ** 2 for o, d in zip(model.weights, decompressed_8bit.weights)) / len(model.weights)
    print(f"  Reconstruction MSE: {mse:.6f}")

    print(f"\nOriginal:      {[f'{w:.4f}' for w in model.weights[:5]]}...")
    print(f"Decompressed:  {[f'{w:.4f}' for w in decompressed_8bit.weights[:5]]}...")

    # 4-bit quantization
    print("\n[2.2] 4-bit Quantization (More Aggressive)")
    print("-" * 60)

    compressed_4bit = compressor.compress(
        model,
        compression_type=CompressionType.QUANTIZATION,
        num_bits=4
    )

    print(f"\nCompression Results:")
    print(f"  Original bits: 32 (float32)")
    print(f"  Compressed bits: 4 (int4)")
    print(f"  Compression ratio: {compressed_4bit['compression_ratio']:.2f}x")
    print(f"  Size reduction: {(1 - 1/compressed_4bit['compression_ratio'])*100:.1f}%")

    decompressed_4bit = compressor.decompress(compressed_4bit)

    mse_4bit = sum((o - d) ** 2 for o, d in zip(model.weights, decompressed_4bit.weights)) / len(model.weights)
    print(f"  Reconstruction MSE: {mse_4bit:.6f}")

    print(f"\nNote: 4-bit has higher error ({mse_4bit:.6f}) than 8-bit ({mse:.6f})")

    # ========================================================================
    # Top-K Sparsification
    # ========================================================================
    print("\n" + "=" * 60)
    print("[3] Top-K Sparsification")
    print("=" * 60)

    print("\nTop-K sends only the K largest (by magnitude) weights")

    # Top-10%
    print("\n[3.1] Top-10% Sparsification")
    print("-" * 60)

    compressed_top10 = compressor.compress(
        model,
        compression_type=CompressionType.TOPK,
        sparsity_ratio=0.1  # Keep top 10%
    )

    print(f"\nCompression Results:")
    print(f"  Original params: {num_features}")
    print(f"  Transmitted params: {len(compressed_top10['values'])} (top 10%)")
    print(f"  Compression ratio: {compressed_top10['compression_ratio']:.2f}x")
    print(f"  Size reduction: {(1 - 1/compressed_top10['compression_ratio'])*100:.1f}%")

    decompressed_top10 = compressor.decompress(compressed_top10)

    # Calculate sparsity
    num_zeros = sum(1 for w in decompressed_top10.weights if abs(w) < 1e-9)
    actual_sparsity = num_zeros / len(decompressed_top10.weights)

    print(f"  Actual sparsity: {actual_sparsity*100:.1f}% (90% zeros)")

    mse_top10 = sum((o - d) ** 2 for o, d in zip(model.weights, decompressed_top10.weights)) / len(model.weights)
    print(f"  Reconstruction MSE: {mse_top10:.6f}")

    # Top-1%
    print("\n[3.2] Top-1% Sparsification (Ultra Sparse)")
    print("-" * 60)

    compressed_top1 = compressor.compress(
        model,
        compression_type=CompressionType.TOPK,
        sparsity_ratio=0.01  # Keep only top 1%
    )

    print(f"\nCompression Results:")
    print(f"  Original params: {num_features}")
    print(f"  Transmitted params: {len(compressed_top1['values'])} (top 1%)")
    print(f"  Compression ratio: {compressed_top1['compression_ratio']:.2f}x")
    print(f"  Size reduction: {(1 - 1/compressed_top1['compression_ratio'])*100:.1f}%")

    decompressed_top1 = compressor.decompress(compressed_top1)

    mse_top1 = sum((o - d) ** 2 for o, d in zip(model.weights, decompressed_top1.weights)) / len(model.weights)
    print(f"  Reconstruction MSE: {mse_top1:.6f}")

    print(f"\nNote: Top-1% has much higher error ({mse_top1:.6f}) than top-10% ({mse_top10:.6f})")

    # ========================================================================
    # Random Sparsification
    # ========================================================================
    print("\n" + "=" * 60)
    print("[4] Random Sparsification")
    print("=" * 60)

    print("\nRandom sparsification: send random subset of weights")

    compressed_random = compressor.compress(
        model,
        compression_type=CompressionType.RANDOM_SPARSIFICATION,
        sparsity_ratio=0.1
    )

    print(f"\nCompression Results:")
    print(f"  Transmitted params: {len(compressed_random['values'])} (random 10%)")
    print(f"  Compression ratio: {compressed_random['compression_ratio']:.2f}x")

    decompressed_random = compressor.decompress(compressed_random)

    mse_random = sum((o - d) ** 2 for o, d in zip(model.weights, decompressed_random.weights)) / len(model.weights)
    print(f"  Reconstruction MSE: {mse_random:.6f}")

    print(f"\nNote: Random ({mse_random:.6f}) typically worse than top-k ({mse_top10:.6f})")

    # ========================================================================
    # Adaptive Compression
    # ========================================================================
    print("\n" + "=" * 60)
    print("[5] Adaptive Compression (Network-Aware)")
    print("=" * 60)

    print("\nAdaptive compression adjusts based on network conditions")

    adaptive = AdaptiveCompression(
        initial_ratio=0.5,  # Start at 50% compression
        target_bandwidth_mbps=10.0,  # Target 10 Mbps
        adaptation_rate=0.1
    )

    print(f"\nConfiguration:")
    print(f"  Initial compression ratio: {adaptive.current_ratio:.1%}")
    print(f"  Target bandwidth: {adaptive.target_bandwidth} Mbps")
    print(f"  Adaptation rate: {adaptive.adaptation_rate}")

    # Simulate multiple rounds with varying network conditions
    print(f"\nSimulating 10 communication rounds with varying bandwidth...")
    print("-" * 60)

    network_conditions = [
        (5.0, "Poor"),    # Round 1-2: Low bandwidth
        (5.0, "Poor"),
        (15.0, "Good"),   # Round 3-4: High bandwidth
        (15.0, "Good"),
        (8.0, "Medium"),  # Round 5-6: Medium bandwidth
        (8.0, "Medium"),
        (3.0, "Very Poor"), # Round 7-8: Very low bandwidth
        (3.0, "Very Poor"),
        (20.0, "Excellent"), # Round 9-10: Excellent bandwidth
        (20.0, "Excellent"),
    ]

    for round_num, (bandwidth_mbps, condition) in enumerate(network_conditions, 1):
        # Compress model
        compressed = adaptive.compress_adaptive(model)

        # Simulate transmission
        model_size_mb = calculate_size_mb(model)
        compressed_size_mb = model_size_mb / compressed['compression_ratio']
        transmission_time = compressed_size_mb / bandwidth_mbps

        # Update based on bandwidth
        adaptive.update_based_on_bandwidth(bandwidth_mbps, transmission_time)

        print(f"\nRound {round_num:2d} ({condition:12s} | {bandwidth_mbps:5.1f} Mbps):")
        print(f"  Compression ratio: {compressed['compression_ratio']:.2f}x")
        print(f"  Compressed size: {compressed_size_mb:.4f} MB")
        print(f"  Transmission time: {transmission_time*1000:.2f}ms")
        print(f"  Next round ratio: {adaptive.current_ratio:.1%}")

    # ========================================================================
    # Compression Comparison
    # ========================================================================
    print("\n" + "=" * 60)
    print("[6] Compression Method Comparison")
    print("=" * 60)

    print(f"""
Summary of Compression Methods:

METHOD                  | RATIO  | MSE      | USE CASE
------------------------|--------|----------|---------------------------
8-bit Quantization      | 4.00x  | {mse:.6f} | Balanced compression/accuracy
4-bit Quantization      | 8.00x  | {mse_4bit:.6f} | Aggressive compression
Top-10% Sparsification  | {compressed_top10['compression_ratio']:.2f}x  | {mse_top10:.6f} | Moderate sparsity
Top-1% Sparsification   | {compressed_top1['compression_ratio']:.2f}x | {mse_top1:.6f} | Ultra-sparse models
Random Sparsification   | {compressed_random['compression_ratio']:.2f}x  | {mse_random:.6f} | Unbiased sampling
Adaptive Compression    | Dynamic | Varies   | Network-aware FL

**Recommendations:**

1. **Stable Networks (>10 Mbps)**
   → Use 8-bit quantization (4x, low error)

2. **Constrained Networks (1-10 Mbps)**
   → Use top-10% sparsification (10x, acceptable error)

3. **Very Limited (<1 Mbps, mobile)**
   → Use top-1% or adaptive compression

4. **Varying Network Conditions**
   → Use adaptive compression (dynamic adjustment)

5. **Accuracy-Critical Applications**
   → Use 8-bit quantization or no compression

6. **Large Models (>100M params)**
   → Combine quantization + sparsification

**Trade-off Analysis:**

Compression ↑ → Communication ↓, Accuracy ↓
Sparsity ↑ → Bandwidth ↓, Convergence slower
Quantization ↑ → Size ↓, Precision ↓
Adaptation ↑ → Efficiency ↑, Complexity ↑
    """)

    # Performance impact
    print("\n" + "=" * 60)
    print("[7] Performance Impact Analysis")
    print("=" * 60)

    print(f"""
**Bandwidth Savings (for {num_features}-parameter model):**

Original size: {original_size:.4f} MB per client per round

With compression:
• 8-bit quantization:  {original_size/4:.4f} MB (75% reduction)
• Top-10%:             {original_size/10:.4f} MB (90% reduction)
• Top-1%:              {original_size/100:.4f} MB (99% reduction)

For 100 clients over 100 rounds:
• Uncompressed:        {original_size * 100 * 100:.2f} MB total
• With 8-bit:          {original_size * 100 * 100 / 4:.2f} MB total
• With top-10%:        {original_size * 100 * 100 / 10:.2f} MB total

**Savings: Up to 90%+ bandwidth reduction!**

**Convergence Impact:**

Light compression (4x):   ~0-5% slower convergence
Medium compression (10x):  ~5-15% slower convergence
Heavy compression (100x):  ~20-50% slower convergence

**Best Practice:**
Start with 8-bit quantization, increase compression only if needed.
    """)

    print("\n✓ Communication compression example complete!")
    print("\nKey Takeaways:")
    print("  • Compression dramatically reduces communication costs")
    print("  • 4-10x reduction with minimal accuracy loss")
    print("  • Essential for mobile and cross-silo FL")
    print("  • Adaptive methods handle varying network conditions")


if __name__ == "__main__":
    main()
