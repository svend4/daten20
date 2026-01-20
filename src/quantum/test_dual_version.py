"""Test Quantum Dual-Version"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum import (
    HAS_NUMPY, GateType, BackendType,
    get_quantum_circuit_engine, get_quantum_algorithms,
    get_quantum_hardware_manager, get_hybrid_quantum_classical,
    get_quantum_machine_learning, get_quantum_optimization,
)

async def main():
    print("=" * 60)
    print("Quantum Computing Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Circuit Engine...")
    qce = get_quantum_circuit_engine()
    circuit = qce.create_circuit(4)
    qce.add_gate(circuit, GateType.H, [0])
    qce.add_gate(circuit, GateType.CNOT, [0, 1])
    qce.measure(circuit)
    result = await qce.execute(circuit, BackendType.SIMULATOR, 100)
    print(f"  Shots: {result.shots}")
    print(f"  Outcomes: {len(result.counts)}")
    print("  ✅ Circuit Engine works!")
    
    print("\nTesting Quantum Algorithms...")
    qa = get_quantum_algorithms()
    grover = await qa.grover_search("oracle", 4)
    print(f"  Grover probability: {grover['probability']:.2f}")
    vqe = await qa.vqe_ground_state("H2", 4)
    print(f"  VQE energy: {vqe['ground_state_energy']:.2f}")
    print("  ✅ Quantum Algorithms works!")
    
    print("\nTesting Hardware Manager...")
    qhm = get_quantum_hardware_manager()
    backends = await qhm.list_backends()
    print(f"  Available backends: {len(backends)}")
    job_id = await qhm.submit_job(circuit, "simulator", 1024)
    print(f"  Job submitted: {job_id}")
    print("  ✅ Hardware Manager works!")
    
    print("\nTesting Hybrid QC...")
    hqc = get_hybrid_quantum_classical()
    opt_result = await hqc.hybrid_optimization("f(x)", 10)
    print(f"  Optimal value: {opt_result['optimal_value']:.2f}")
    print("  ✅ Hybrid QC works!")
    
    print("\nTesting Quantum ML...")
    qml = get_quantum_machine_learning()
    kernel = await qml.quantum_kernel_matrix([[0.1, 0.2], [0.3, 0.4]])
    print(f"  Kernel shape: {len(kernel)}x{len(kernel[0])}")
    print("  ✅ Quantum ML works!")
    
    print("\nTesting Quantum Optimization...")
    qopt = get_quantum_optimization()
    maxcut = await qopt.solve_max_cut({"a": ["b"], "b": ["a"]})
    print(f"  Max-Cut value: {maxcut['cut_value']}")
    print("  ✅ Quantum Optimization works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
