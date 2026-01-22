"""
Integration tests for DATEN20 cross-module pipeline.

Tests the integrated pipeline that combines all modules (v22-v27).
"""

import unittest
import asyncio
from src.integration import IntegratedPipeline, PipelineConfig, PipelineMode


class TestIntegratedPipeline(unittest.TestCase):
    """Test cases for integrated pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = IntegratedPipeline()
        self.basic_task = {
            "task_id": "test_task",
            "description": "Test task",
            "domain": "test"
        }

    def test_pipeline_singleton(self):
        """Test that pipeline is a singleton."""
        pipeline1 = IntegratedPipeline()
        pipeline2 = IntegratedPipeline()
        self.assertIs(pipeline1, pipeline2)

    def test_basic_mode(self):
        """Test basic mode (v22 only)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.BASIC)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIsNotNone(result.result)

        asyncio.run(run())

    def test_enhanced_mode(self):
        """Test enhanced mode (v22-v23)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.ENHANCED)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22", "v23"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("improvements", result.result)

        asyncio.run(run())

    def test_emergent_mode(self):
        """Test emergent mode (v22-v24)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.EMERGENT)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22", "v23", "v24"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("emergent_capabilities", result.result)

        asyncio.run(run())

    def test_agi_mode(self):
        """Test AGI mode (v22-v25)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.AGI)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22", "v23", "v24", "v25"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("task_understanding", result.result)

        asyncio.run(run())

    def test_superhuman_mode(self):
        """Test superhuman mode (v22-v26)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.SUPERHUMAN)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22", "v23", "v24", "v25", "v26"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("superhuman_insights", result.result)
            self.assertIn("alignment", result.result)

        asyncio.run(run())

    def test_cosmic_mode(self):
        """Test cosmic mode (v22-v27)."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.COSMIC)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v22", "v23", "v24", "v25", "v26", "v27"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("cosmic_scale", result.result)

        asyncio.run(run())

    def test_quality_progression(self):
        """Test that quality improves with higher modes."""
        async def run():
            modes = [
                PipelineMode.BASIC,
                PipelineMode.ENHANCED,
                PipelineMode.EMERGENT,
                PipelineMode.AGI,
                PipelineMode.SUPERHUMAN,
                PipelineMode.COSMIC
            ]

            qualities = []
            for mode in modes:
                config = PipelineConfig(mode=mode)
                result = await self.pipeline.solve_task(self.basic_task, config)
                qualities.append(result.quality_score)

            # Quality should generally increase with more modules
            for i in range(len(qualities) - 1):
                self.assertGreaterEqual(qualities[i+1], qualities[i],
                    f"Quality should increase: {modes[i].value} -> {modes[i+1].value}")

        asyncio.run(run())

    def test_custom_configuration(self):
        """Test custom pipeline configuration."""
        async def run():
            config = PipelineConfig(
                mode=PipelineMode.AGI,
                enable_self_improvement=True,
                enable_multi_agent=True,
                enable_verification=False,
                max_iterations=5,
                target_quality=0.85
            )

            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertLessEqual(result.iterations, config.max_iterations)

        asyncio.run(run())

    def test_complex_task(self):
        """Test with complex task specification."""
        async def run():
            complex_task = {
                "task_id": "complex_optimization",
                "description": "Solve multi-objective optimization problem with "
                              "conflicting constraints and uncertain parameters",
                "domain": "optimization",
                "constraints": [
                    "minimize_cost",
                    "maximize_quality",
                    "satisfy_time_constraints"
                ]
            }

            config = PipelineConfig(mode=PipelineMode.SUPERHUMAN)
            result = await self.pipeline.solve_task(complex_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.metadata.get("complexity"), "complex")

        asyncio.run(run())

    def test_result_structure(self):
        """Test that result has expected structure."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.BASIC)
            result = await self.pipeline.solve_task(self.basic_task, config)

            # Check required fields
            self.assertIsNotNone(result.task_id)
            self.assertIsInstance(result.success, bool)
            self.assertIsNotNone(result.result)
            self.assertIsInstance(result.modules_used, list)
            self.assertIsInstance(result.execution_time, float)
            self.assertIsInstance(result.quality_score, float)
            self.assertIsInstance(result.iterations, int)
            self.assertIsInstance(result.metadata, dict)

            # Check value ranges
            self.assertGreaterEqual(result.quality_score, 0.0)
            self.assertLessEqual(result.quality_score, 1.0)
            self.assertGreater(result.execution_time, 0.0)
            self.assertGreater(result.iterations, 0)

        asyncio.run(run())

    def test_execution_time_tracking(self):
        """Test that execution time is tracked correctly."""
        async def run():
            config = PipelineConfig(mode=PipelineMode.ENHANCED)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertGreater(result.execution_time, 0.0)
            self.assertLess(result.execution_time, 10.0)  # Should complete in < 10s

        asyncio.run(run())


if __name__ == '__main__':
    unittest.main()
