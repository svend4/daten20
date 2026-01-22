"""
Integration tests for DATEN20 Basic AI Pipeline (v10-v20).

Tests the integrated pipeline that combines all basic AI modules.
"""

import unittest
import asyncio
from src.integration.basic_ai_pipeline import (
    BasicAIPipeline,
    BasicAIPipelineConfig,
    BasicAIMode
)


class TestBasicAIPipeline(unittest.TestCase):
    """Test cases for Basic AI integrated pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = BasicAIPipeline()
        self.basic_task = {
            "task_id": "test_basic_task",
            "description": "Test task for basic AI modules",
            "domain": "general"
        }

    def test_pipeline_singleton(self):
        """Test that Basic AI pipeline is a singleton."""
        pipeline1 = BasicAIPipeline()
        pipeline2 = BasicAIPipeline()
        self.assertIs(pipeline1, pipeline2)

    def test_deployment_mode(self):
        """Test deployment mode (v10 only)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.DEPLOYMENT)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIsNotNone(result.result)
            self.assertIn("deployment_id", result.result)

        asyncio.run(run())

    def test_federated_mode(self):
        """Test federated mode (v10-v11)."""
        async def run():
            config = BasicAIPipelineConfig(
                mode=BasicAIMode.FEDERATED,
                enable_privacy=True
            )
            task = {**self.basic_task, "num_clients": 5, "num_rounds": 10}
            result = await self.pipeline.solve_task(task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("federated_clients", result.result)
            self.assertTrue(result.result.get("privacy_preserved"))

        asyncio.run(run())

    def test_autonomous_mode(self):
        """Test autonomous mode (v10-v12)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.AUTONOMOUS)
            task = {
                **self.basic_task,
                "required_capabilities": ["reasoning", "planning"]
            }
            result = await self.pipeline.solve_task(task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11", "v12"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("agent_id", result.result)
            self.assertIn("agent_capabilities", result.result)

        asyncio.run(run())

    def test_explainable_mode(self):
        """Test explainable mode (v10-v13)."""
        async def run():
            config = BasicAIPipelineConfig(
                mode=BasicAIMode.EXPLAINABLE,
                enable_explainability=True
            )
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11", "v12", "v13"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("explainability_score", result.result)
            self.assertGreater(result.result["explainability_score"], 0.0)
            self.assertTrue(result.result.get("explanation_available"))

        asyncio.run(run())

    def test_neurosymbolic_mode(self):
        """Test neurosymbolic mode (v10-v14)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.NEUROSYMBOLIC)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11", "v12", "v13", "v14"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("neurosymbolic", result.result)
            self.assertIn("symbolic_rules_applied", result.result["neurosymbolic"])

        asyncio.run(run())

    def test_quantum_mode(self):
        """Test quantum mode (v10-v15)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.QUANTUM)
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11", "v12", "v13", "v14", "v15"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("quantum_speedup", result.result)
            self.assertGreater(result.result["quantum_speedup"], 1.0)

        asyncio.run(run())

    def test_edge_mode(self):
        """Test edge mode (v10-v16)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.EDGE)
            task = {**self.basic_task, "edge_nodes": 5}
            result = await self.pipeline.solve_task(task, config)

            self.assertTrue(result.success)
            self.assertEqual(result.modules_used, ["v10", "v11", "v12", "v13", "v14", "v15", "v16"])
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("edge_deployment", result.result)
            self.assertIn("edge_nodes", result.result["edge_deployment"])

        asyncio.run(run())

    def test_multimodal_mode(self):
        """Test multimodal mode (v10-v17)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.MULTIMODAL)
            task = {**self.basic_task, "modalities": ["text", "vision", "audio"]}
            result = await self.pipeline.solve_task(task, config)

            self.assertTrue(result.success)
            self.assertEqual(
                result.modules_used,
                ["v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17"]
            )
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("modalities_processed", result.result)
            self.assertEqual(len(result.result["modalities_processed"]), 3)

        asyncio.run(run())

    def test_safe_mode(self):
        """Test safe mode (v10-v18)."""
        async def run():
            config = BasicAIPipelineConfig(
                mode=BasicAIMode.SAFE,
                enable_safety_checks=True
            )
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(
                result.modules_used,
                ["v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18"]
            )
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("safety_score", result.result)
            self.assertGreater(result.result["safety_score"], 0.9)
            self.assertTrue(result.result.get("safety_verified"))

        asyncio.run(run())

    def test_agentic_mode(self):
        """Test agentic mode (v10-v19)."""
        async def run():
            config = BasicAIPipelineConfig(mode=BasicAIMode.AGENTIC)
            task = {**self.basic_task, "tools": ["calculator", "web_search", "python"]}
            result = await self.pipeline.solve_task(task, config)

            self.assertTrue(result.success)
            self.assertEqual(
                result.modules_used,
                ["v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19"]
            )
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("tools_used", result.result)
            self.assertEqual(len(result.result["tools_used"]), 3)

        asyncio.run(run())

    def test_collaborative_mode(self):
        """Test collaborative mode (v10-v20) - full pipeline."""
        async def run():
            config = BasicAIPipelineConfig(
                mode=BasicAIMode.COLLABORATIVE,
                enable_human_oversight=True
            )
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertTrue(result.success)
            self.assertEqual(
                result.modules_used,
                ["v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20"]
            )
            self.assertGreater(result.quality_score, 0.0)
            self.assertIn("human_approved", result.result)
            self.assertTrue(result.result.get("human_approved"))
            self.assertTrue(result.result.get("collaboration_enabled"))

        asyncio.run(run())

    def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        async def run():
            config = BasicAIPipelineConfig(
                mode=BasicAIMode.SAFE,
                enable_privacy=True,
                enable_explainability=True,
                enable_safety_checks=True
            )
            result = await self.pipeline.solve_task(self.basic_task, config)

            self.assertIsNotNone(result.metrics)
            self.assertGreater(result.metrics.total_time, 0.0)
            self.assertGreaterEqual(result.metrics.safety_score, 0.0)
            self.assertLessEqual(result.metrics.safety_score, 1.0)
            self.assertTrue(result.metrics.privacy_preserved)

        asyncio.run(run())

    def test_quality_progression(self):
        """Test that quality improves with more modules."""
        async def run():
            # Test increasing quality across modes
            modes = [
                BasicAIMode.DEPLOYMENT,
                BasicAIMode.FEDERATED,
                BasicAIMode.AUTONOMOUS,
                BasicAIMode.EXPLAINABLE,
                BasicAIMode.NEUROSYMBOLIC,
                BasicAIMode.QUANTUM,
                BasicAIMode.EDGE,
                BasicAIMode.MULTIMODAL,
                BasicAIMode.SAFE,
                BasicAIMode.AGENTIC,
                BasicAIMode.COLLABORATIVE
            ]

            prev_quality = 0.0
            for mode in modes:
                config = BasicAIPipelineConfig(mode=mode)
                result = await self.pipeline.solve_task(self.basic_task, config)

                self.assertTrue(result.success)
                self.assertGreaterEqual(result.quality_score, prev_quality)
                prev_quality = result.quality_score

        asyncio.run(run())

    def test_error_handling(self):
        """Test error handling for invalid task specs."""
        async def run():
            # Empty task spec should still work (with defaults)
            result = await self.pipeline.solve_task({}, BasicAIPipelineConfig())
            # Should not crash, might succeed or fail gracefully
            self.assertIsNotNone(result)
            self.assertIn("task_id", result.metadata or {})

        asyncio.run(run())


if __name__ == '__main__':
    unittest.main()
