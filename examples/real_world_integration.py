"""
Real-world integration examples with logging and error handling.

Demonstrates practical usage of the IntegratedPipeline with real API integration.
"""

import asyncio
import logging
from src.integration import IntegratedPipeline, PipelineConfig, PipelineMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_1_with_logging():
    """Example 1: Basic usage with logging enabled."""
    logger.info("=" * 60)
    logger.info("Example 1: Basic pipeline with logging")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "example_1",
        "description": "Optimize resource allocation for a small project",
        "domain": "optimization"
    }

    config = PipelineConfig(mode=PipelineMode.BASIC)

    result = await pipeline.solve_task(task_spec, config)

    logger.info(f"Task completed:")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Quality: {result.quality_score:.4f}")
    logger.info(f"  Time: {result.execution_time:.2f}s")
    logger.info(f"  Modules: {result.modules_used}")

    if result.metrics:
        logger.info(f"  API calls: {result.metrics.api_calls}")


async def example_2_error_handling():
    """Example 2: Handling errors gracefully."""
    logger.info("=" * 60)
    logger.info("Example 2: Error handling")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    # Task with invalid specification
    task_spec = {
        "task_id": "example_2",
        "description": "",  # Empty description might cause issues
        "domain": "unknown"
    }

    config = PipelineConfig(mode=PipelineMode.EMERGENT)

    try:
        result = await pipeline.solve_task(task_spec, config)

        if result.success:
            logger.info("Task completed successfully")
            logger.info(f"  Quality: {result.quality_score:.4f}")
        else:
            logger.warning("Task failed")
            logger.warning(f"  Error: {result.metadata.get('error', 'Unknown')}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def example_3_mode_comparison():
    """Example 3: Compare performance across different modes."""
    logger.info("=" * 60)
    logger.info("Example 3: Mode comparison")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "example_3",
        "description": "Solve complex multi-objective optimization problem",
        "domain": "optimization",
        "constraints": ["minimize_cost", "maximize_efficiency"]
    }

    modes = [
        PipelineMode.BASIC,
        PipelineMode.ENHANCED,
        PipelineMode.EMERGENT,
        PipelineMode.AGI
    ]

    results = []

    for mode in modes:
        config = PipelineConfig(mode=mode)
        result = await pipeline.solve_task(task_spec, config)
        results.append((mode, result))

        logger.info(f"{mode.value:12} | Quality: {result.quality_score:.4f} | Time: {result.execution_time:.2f}s")

    # Show quality progression
    logger.info("\nQuality Progression:")
    for mode, result in results:
        logger.info(f"  {mode.value}: {result.quality_score:.4f}")


async def example_4_advanced_config():
    """Example 4: Advanced configuration options."""
    logger.info("=" * 60)
    logger.info("Example 4: Advanced configuration")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "example_4",
        "description": "Design advanced AI system architecture",
        "domain": "design"
    }

    config = PipelineConfig(
        mode=PipelineMode.SUPERHUMAN,
        enable_self_improvement=True,
        enable_multi_agent=True,
        enable_verification=True,
        max_iterations=15,
        target_quality=0.95
    )

    result = await pipeline.solve_task(task_spec, config)

    logger.info(f"Advanced task completed:")
    logger.info(f"  Quality: {result.quality_score:.4f}")
    logger.info(f"  Target: {config.target_quality:.2f}")
    logger.info(f"  Achieved target: {result.quality_score >= config.target_quality}")
    logger.info(f"  Iterations: {result.iterations}")
    logger.info(f"  Execution time: {result.execution_time:.2f}s")


async def example_5_metrics_analysis():
    """Example 5: Analyzing performance metrics."""
    logger.info("=" * 60)
    logger.info("Example 5: Metrics analysis")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    task_spec = {
        "task_id": "example_5",
        "description": "Analyze large-scale data processing pipeline",
        "domain": "analytics"
    }

    config = PipelineConfig(mode=PipelineMode.COSMIC)

    result = await pipeline.solve_task(task_spec, config)

    logger.info(f"Task metrics:")
    logger.info(f"  Total time: {result.execution_time:.2f}s")
    logger.info(f"  Modules used: {len(result.modules_used)}")
    logger.info(f"  Quality score: {result.quality_score:.4f}")

    if result.metrics:
        logger.info(f"  API calls: {result.metrics.api_calls}")
        logger.info(f"  Total time: {result.metrics.total_time:.2f}s")


async def example_6_production_workflow():
    """Example 6: Production-ready workflow with full features."""
    logger.info("=" * 60)
    logger.info("Example 6: Production workflow")
    logger.info("=" * 60)

    pipeline = IntegratedPipeline()

    # Simulate production task
    task_spec = {
        "task_id": "prod_task_001",
        "description": "Optimize global supply chain logistics",
        "domain": "optimization",
        "constraints": [
            "minimize_transportation_cost",
            "maximize_delivery_speed",
            "minimize_environmental_impact",
            "ensure_product_quality"
        ]
    }

    config = PipelineConfig(
        mode=PipelineMode.SUPERHUMAN,
        enable_self_improvement=True,
        enable_multi_agent=True,
        enable_verification=True,
        max_iterations=20,
        target_quality=0.98
    )

    logger.info("Starting production task...")

    result = await pipeline.solve_task(task_spec, config)

    logger.info(f"\nProduction task results:")
    logger.info(f"  Status: {'SUCCESS' if result.success else 'FAILED'}")
    logger.info(f"  Task ID: {result.task_id}")
    logger.info(f"  Quality: {result.quality_score:.4f}")
    logger.info(f"  Execution time: {result.execution_time:.2f}s")
    logger.info(f"  Modules: {', '.join(result.modules_used)}")
    logger.info(f"  Iterations: {result.iterations}")

    # Additional result analysis
    if "superhuman_insights" in result.result:
        insights = result.result["superhuman_insights"]
        logger.info(f"\nSuperhuman insights:")
        logger.info(f"  Depth score: {insights.get('depth_score', 0):.2f}")
        logger.info(f"  Novel solutions: {insights.get('novel_solutions', 0)}")
        logger.info(f"  Creativity: {insights.get('creativity_novelty', 0):.2f}")

    if "alignment" in result.result:
        alignment = result.result["alignment"]
        logger.info(f"\nAlignment verification:")
        logger.info(f"  Score: {alignment.get('score', 0):.2f}")
        logger.info(f"  Approved: {alignment.get('approved', False)}")


async def main():
    """Run all examples."""
    examples = [
        ("Basic with logging", example_1_with_logging),
        ("Error handling", example_2_error_handling),
        ("Mode comparison", example_3_mode_comparison),
        ("Advanced config", example_4_advanced_config),
        ("Metrics analysis", example_5_metrics_analysis),
        ("Production workflow", example_6_production_workflow)
    ]

    for name, example_func in examples:
        try:
            await example_func()
            print()  # Empty line for readability
        except Exception as e:
            logger.error(f"Example '{name}' failed: {e}")


if __name__ == "__main__":
    print("Real-world Integration Examples")
    print("=" * 60)
    print()

    asyncio.run(main())

    print()
    print("All examples completed!")
