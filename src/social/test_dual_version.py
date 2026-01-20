"""Test Dual-Version Social Implementation"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from social import (
    HAS_NUMPY, SocialRole, VotingMethod, SwarmAlgorithm, SocialContext,
    get_social_cognition_engine, get_group_dynamics_system,
    get_collective_decision_system, get_swarm_intelligence_system,
    get_cultural_intelligence_system, get_social_network_analysis,
    get_collaboration_orchestrator,
)

async def main():
    print("=" * 60)
    print("Social Dual-Version Test Suite")
    print("=" * 60)
    print(f"\nHAS_NUMPY: {HAS_NUMPY}\n✅ Imports work!")
    
    print("\nTesting Social Cognition...")
    soc = get_social_cognition_engine()
    ctx = SocialContext(participants=["A", "B"], setting="meeting", formality="formal")
    roles = await soc.recognize_roles(ctx)
    print(f"  Roles: {len(roles)}")
    tom = await soc.theory_of_mind("A", depth=2)
    print(f"  ToM depth: {tom.depth}\n  ✅ Social Cognition works!")
    
    print("\nTesting Group Dynamics...")
    grp = get_group_dynamics_system()
    stage = await grp.assess_group_stage("group1")
    print(f"  Stage: {stage.value}\n  ✅ Group Dynamics works!")
    
    print("\nTesting Collective Decision...")
    col = get_collective_decision_system()
    vote = await col.vote(["A", "B", "C"], ["v1", "v2", "v3"], VotingMethod.PLURALITY)
    print(f"  Winner: {vote.winner}\n  ✅ Collective Decision works!")
    
    print("\nTesting Swarm Intelligence...")
    swarm = get_swarm_intelligence_system()
    result = await swarm.optimize("test", dimensions=5, swarm_size=20)
    print(f"  Fitness: {result['best_fitness']:.2f}\n  ✅ Swarm Intelligence works!")
    
    print("\nTesting Cultural Intelligence...")
    cult = get_cultural_intelligence_system()
    prof = await cult.get_profile("US")
    print(f"  Culture: {prof.culture}\n  ✅ Cultural Intelligence works!")
    
    print("\nTesting Social Network Analysis...")
    net = get_social_network_analysis()
    cent = await net.analyze_centrality("net1", "node1")
    print(f"  Centrality metrics: {len(cent)}\n  ✅ Social Network Analysis works!")
    
    print("\nTesting Collaboration Orchestrator...")
    collab = get_collaboration_orchestrator()
    coord = await collab.coordinate_collaboration("t1", ["h1"], ["ai1"])
    print(f"  Allocation: {len(coord['allocation'])}\n  ✅ Collaboration works!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
