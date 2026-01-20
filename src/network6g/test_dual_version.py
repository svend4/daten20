"""Test Network6G Dual-Version"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network6g import (
    HAS_NUMPY, SliceType,
    get_network6g_manager, get_terahertz_communication,
    get_intelligent_reflecting_surface, get_edge_intelligence,
    get_holographic_communication, get_quantum_secured_6g,
)

async def main():
    print("=" * 60)
    print("Network6G Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Network Manager...")
    nm = get_network6g_manager()
    slice_obj = await nm.create_slice(SliceType.URLLC, 10.0)
    print(f"  Slice latency: {slice_obj.latency_ms}ms")
    print("  ✅ Network Manager works!")
    
    print("\nTesting THz Communication...")
    thz = get_terahertz_communication()
    link = await thz.establish_thz_link(1.0, 100.0)
    print(f"  Data rate: {link['data_rate_gbps']:.1f} Gbps")
    print("  ✅ THz Communication works!")
    
    print("\nTesting IRS...")
    irs = get_intelligent_reflecting_surface()
    config = await irs.configure_irs(64, 1.0)
    print(f"  IRS elements: {config.num_elements}")
    print("  ✅ IRS works!")
    
    print("\nTesting Edge Intelligence...")
    edge = get_edge_intelligence()
    deploy = await edge.deploy_model("node1", 100.0)
    print(f"  Inference latency: {deploy['inference_latency_ms']:.1f}ms")
    print("  ✅ Edge Intelligence works!")
    
    print("\nTesting Holographic Communication...")
    holo = get_holographic_communication()
    stream = await holo.stream_hologram("8K", 60)
    print(f"  Required BW: {stream['required_bandwidth_gbps']} Gbps")
    print("  ✅ Holographic Communication works!")
    
    print("\nTesting Quantum Secured 6G...")
    qsec = get_quantum_secured_6g()
    qkd = await qsec.establish_qkd_link("A", "B")
    print(f"  Key rate: {qkd['key_rate_kbps']:.1f} kbps")
    print("  ✅ Quantum Secured 6G works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
