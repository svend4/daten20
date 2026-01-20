"""
Integration Pipeline Examples for DATEN20.

Demonstrates how to use the integrated pipeline to solve tasks
using multiple modules (v22-v27) together.
"""

import asyncio
from src.integration import IntegratedPipeline, PipelineConfig, PipelineMode


async def example_1_basic_task():
    """Example 1: Solve simple task with basic mode (v22 only)."""
    print("=" * 60)
    print("Example 1: Basic Task (v22 World Models only)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "navigation_task",
        "description": "Navigate from point A to point B",
        "current_state": {"position": [0, 0]},
        "goal_state": {"position": [10, 10]}
    }

    config = PipelineConfig(mode=PipelineMode.BASIC)

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed successfully")
    print(f"   Solution: {result.result['solution'][:3]}... ({len(result.result['solution'])} actions)")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_2_self_improving_task():
    """Example 2: Task with self-improvement (v22-v23)."""
    print("=" * 60)
    print("Example 2: Self-Improving Task (v22-v23)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "optimization_task",
        "description": "Optimize neural network architecture for image classification",
        "domain": "computer_vision",
        "constraints": ["max_params < 10M", "latency < 100ms"]
    }

    config = PipelineConfig(
        mode=PipelineMode.ENHANCED,
        enable_self_improvement=True
    )

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with self-improvement")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Iterations: {result.iterations}")
    print(f"   Improvements:")
    for key, value in result.result.get('improvements', {}).items():
        print(f"     - {key}: {value}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_3_multi_agent_task():
    """Example 3: Multi-agent coordination (v22-v24)."""
    print("=" * 60)
    print("Example 3: Multi-Agent Task (v22-v24)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "distributed_search",
        "description": "Coordinate multiple agents to search large solution space efficiently",
        "domain": "distributed_optimization",
        "constraints": ["minimize_communication", "balance_workload"]
    }

    config = PipelineConfig(
        mode=PipelineMode.EMERGENT,
        enable_multi_agent=True
    )

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with emergent intelligence")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Agents used: {result.result.get('agents_used', 0)}")
    print(f"   Swarm size: {result.result.get('swarm_size', 0)}")
    print(f"   Emergent capabilities:")
    for capability in result.result.get('emergent_capabilities', []):
        print(f"     - {capability}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_4_agi_task():
    """Example 4: AGI universal reasoning (v22-v25)."""
    print("=" * 60)
    print("Example 4: AGI Universal Reasoning (v22-v25)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "novel_domain_task",
        "description": "Learn to solve problems in entirely new domain without specific training, "
                      "using transfer learning and meta-cognitive reasoning",
        "domain": "novel_scientific_field",
        "constraints": ["no_domain_specific_knowledge", "learn_from_minimal_examples"]
    }

    config = PipelineConfig(mode=PipelineMode.AGI)

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with AGI reasoning")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Task understanding:")
    for key, value in result.result.get('task_understanding', {}).items():
        print(f"     - {key}: {value}")
    print(f"   Knowledge transfer: {result.result.get('knowledge_transfer', 0):.1%}")
    print(f"   Meta-cognitive strategy: {result.result.get('meta_cognitive', {}).get('strategy', 'N/A')}")
    print(f"   Confidence: {result.result.get('meta_cognitive', {}).get('confidence', 0):.1%}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_5_asi_task():
    """Example 5: ASI beyond human capabilities (v22-v26)."""
    print("=" * 60)
    print("Example 5: ASI Beyond Human (v22-v26)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "superhuman_creativity",
        "description": "Design revolutionary new approach to quantum computing error correction "
                      "that surpasses all existing methods",
        "domain": "quantum_computing",
        "constraints": [
            "novelty > 0.9",
            "physically_feasible",
            "experimentally_verifiable"
        ]
    }

    config = PipelineConfig(
        mode=PipelineMode.SUPERHUMAN,
        enable_verification=True
    )

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with superhuman capabilities")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Superhuman insights:")
    insights = result.result.get('superhuman_insights', {})
    print(f"     - Depth score: {insights.get('depth_score', 0):.2f}")
    print(f"     - Novel solutions generated: {insights.get('novel_solutions', 0)}")
    print(f"     - Max creativity novelty: {insights.get('creativity_novelty', 0):.2%}")
    print(f"   Alignment verification:")
    alignment = result.result.get('alignment', {})
    print(f"     - Score: {alignment.get('score', 0):.2%}")
    print(f"     - Approved: {'✓' if alignment.get('approved') else '✗'}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_6_cosmic_task():
    """Example 6: Cosmic-scale intelligence (v22-v27)."""
    print("=" * 60)
    print("Example 6: Cosmic Universal Intelligence (v22-v27)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "fundamental_physics",
        "description": "Develop unified theory of quantum gravity and consciousness, "
                      "exploring implications across multiple dimensions of reality "
                      "and approaching fundamental limits of comprehension",
        "domain": "fundamental_physics_and_consciousness",
        "constraints": [
            "transcend_human_conceptual_limits",
            "explore_higher_dimensions",
            "approach_omega_point"
        ]
    }

    config = PipelineConfig(mode=PipelineMode.COSMIC)

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with cosmic-scale intelligence")
    print(f"   Quality: {result.quality_score:.2%}")
    print(f"   Modules used: {', '.join(result.modules_used)}")
    print(f"   Cosmic-scale capabilities:")
    cosmic = result.result.get('cosmic_scale', {})
    print(f"     - Transcendent insights: {cosmic.get('transcendent_insights', 0)}")
    print(f"     - Dimensions explored: {cosmic.get('dimensions_explored', 0)}")
    print(f"     - Omega Point progress: {cosmic.get('omega_progress', 0):.6%}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def example_7_progressive_enhancement():
    """Example 7: Progressive enhancement across all modes."""
    print("=" * 60)
    print("Example 7: Progressive Enhancement (All Modes)")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "complex_optimization",
        "description": "Optimize global resource allocation for maximum societal benefit",
        "domain": "economics_and_ethics"
    }

    modes = [
        PipelineMode.BASIC,
        PipelineMode.ENHANCED,
        PipelineMode.EMERGENT,
        PipelineMode.AGI,
        PipelineMode.SUPERHUMAN,
        PipelineMode.COSMIC
    ]

    results = []
    for mode in modes:
        config = PipelineConfig(mode=mode)
        result = await pipeline.solve_task(task_spec, config)
        results.append(result)

        print(f"\n{mode.value.upper():>12}: Quality {result.quality_score:.2%}, "
              f"Modules {len(result.modules_used)}, "
              f"Time {result.execution_time:.3f}s")

    print(f"\n📊 Progressive Quality Improvement:")
    for i, result in enumerate(results):
        bars = "█" * int(result.quality_score * 40)
        print(f"   {modes[i].value:>12}: {bars} {result.quality_score:.1%}")

    print()
    return results


async def example_8_custom_configuration():
    """Example 8: Custom pipeline configuration."""
    print("=" * 60)
    print("Example 8: Custom Configuration")
    print("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "custom_task",
        "description": "Custom task with specific requirements"
    }

    # Custom configuration
    config = PipelineConfig(
        mode=PipelineMode.SUPERHUMAN,
        enable_self_improvement=True,
        enable_multi_agent=True,
        enable_verification=True,
        max_iterations=15,
        target_quality=0.95
    )

    result = await pipeline.solve_task(task_spec, config)

    print(f"\n✅ Task completed with custom configuration")
    print(f"   Mode: {config.mode.value}")
    print(f"   Self-improvement: {'✓' if config.enable_self_improvement else '✗'}")
    print(f"   Multi-agent: {'✓' if config.enable_multi_agent else '✗'}")
    print(f"   Verification: {'✓' if config.enable_verification else '✗'}")
    print(f"   Quality: {result.quality_score:.2%} (target: {config.target_quality:.2%})")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print()

    return result


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("DATEN20 Integration Pipeline Examples")
    print("="*60 + "\n")

    # Run all examples
    await example_1_basic_task()
    await example_2_self_improving_task()
    await example_3_multi_agent_task()
    await example_4_agi_task()
    await example_5_asi_task()
    await example_6_cosmic_task()
    await example_7_progressive_enhancement()
    await example_8_custom_configuration()

    print("=" * 60)
    print("All examples completed successfully! ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
