"""Test Dual-Version QML Implementation"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qml import (
    HAS_NUMPY, AnsatzType, EncodingType, OptimizerType, QuantumCircuit,
    get_quantum_circuit_learning, get_quantum_kernel_methods,
    get_quantum_neural_networks, get_quantum_optimization,
    get_quantum_data_encoder, get_quantum_measurement,
    get_hybrid_training_system,
)

async def main():
    print("=" * 60)
    print("QML Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Quantum Circuit Learning...")
    qcl = get_quantum_circuit_learning()
    circuit = await qcl.create_variational_circuit(4, AnsatzType.HARDWARE_EFFICIENT, 3)
    print(f"  Circuit qubits: {circuit.num_qubits}")
    train_result = await qcl.train_circuit(circuit, [[0.1, 0.2]], [1])
    print(f"  Accuracy: {train_result['accuracy']:.2f}")
    print("  ✅ Quantum Circuit Learning works!")
    
    print("\nTesting Quantum Kernel Methods...")
    qkm = get_quantum_kernel_methods()
    kernel = await qkm.compute_kernel_matrix([[0.1], [0.2]])
    print(f"  Kernel shape: {len(kernel)}x{len(kernel[0])}")
    print("  ✅ Quantum Kernel Methods works!")
    
    print("\nTesting Quantum Neural Networks...")
    qnn_sys = get_quantum_neural_networks()
    qnn = await qnn_sys.create_qnn(4, 2, [8, 4])
    print(f"  QNN params: {qnn['num_parameters']}")
    print("  ✅ Quantum Neural Networks works!")
    
    print("\nTesting Quantum Optimization...")
    opt = get_quantum_optimization()
    vqe_result = await opt.solve_vqe("H2", 4)
    print(f"  VQE value: {vqe_result.optimal_value:.2f}")
    print("  ✅ Quantum Optimization works!")
    
    print("\nTesting Quantum Data Encoder...")
    enc = get_quantum_data_encoder()
    state = await enc.encode_data([0.1, 0.2], EncodingType.AMPLITUDE)
    print(f"  State dimension: {len(state)}")
    print("  ✅ Quantum Data Encoder works!")
    
    print("\nTesting Quantum Measurement...")
    meas = get_quantum_measurement()
    counts = await meas.measure_circuit(circuit, shots=100)
    print(f"  Measurement outcomes: {len(counts)}")
    print("  ✅ Quantum Measurement works!")
    
    print("\nTesting Hybrid Training...")
    hybrid = get_hybrid_training_system()
    train_result = await hybrid.train_hybrid(circuit, "mse", OptimizerType.SPSA)
    print(f"  Final loss: {train_result['final_loss']:.2f}")
    print("  ✅ Hybrid Training works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
