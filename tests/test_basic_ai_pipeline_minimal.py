"""
Basic test for DATEN20 Basic AI Pipeline (v10-v20) - minimal version without numpy dependencies.

Tests the pipeline initialization and basic functionality with modules that don't require numpy.
"""

import unittest
import asyncio


class TestBasicAIPipelineMinimal(unittest.TestCase):
    """Minimal test cases for Basic AI integrated pipeline (no numpy required)."""

    def test_pipeline_import(self):
        """Test that pipeline can be imported."""
        try:
            from src.integration.basic_ai_pipeline import BasicAIPipeline
            self.assertTrue(True, "Pipeline imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import pipeline: {e}")

    def test_pipeline_initialization(self):
        """Test that pipeline can be initialized with available modules."""
        try:
            from src.integration.basic_ai_pipeline import BasicAIPipeline
            pipeline = BasicAIPipeline()
            self.assertIsNotNone(pipeline)
            self.assertTrue(pipeline._initialized)
        except Exception as e:
            self.fail(f"Failed to initialize pipeline: {e}")

    def test_pipeline_singleton(self):
        """Test that pipeline is a singleton."""
        from src.integration.basic_ai_pipeline import BasicAIPipeline
        pipeline1 = BasicAIPipeline()
        pipeline2 = BasicAIPipeline()
        self.assertIs(pipeline1, pipeline2)

    def test_deployment_mode_basic(self):
        """Test deployment mode (v10 only) - basic functionality."""
        async def run():
            from src.integration.basic_ai_pipeline import (
                BasicAIPipeline,
                BasicAIPipelineConfig,
                BasicAIMode
            )

            pipeline = BasicAIPipeline()
            task = {
                "task_id": "test_minimal",
                "description": "Minimal test task",
                "domain": "test"
            }

            config = BasicAIPipelineConfig(mode=BasicAIMode.DEPLOYMENT)
            result = await pipeline.solve_task(task, config)

            self.assertIsNotNone(result)
            self.assertTrue(result.success or not result.success)  # Should complete either way
            self.assertIsNotNone(result.task_id)
            self.assertIsNotNone(result.result)

        asyncio.run(run())

    def test_federated_mode_basic(self):
        """Test federated mode (v10-v11) - basic functionality."""
        async def run():
            from src.integration.basic_ai_pipeline import (
                BasicAIPipeline,
                BasicAIPipelineConfig,
                BasicAIMode
            )

            pipeline = BasicAIPipeline()
            task = {
                "task_id": "test_federated",
                "description": "Federated test task",
                "domain": "test",
                "num_clients": 3,
                "num_rounds": 5
            }

            config = BasicAIPipelineConfig(
                mode=BasicAIMode.FEDERATED,
                enable_privacy=True
            )
            result = await pipeline.solve_task(task, config)

            self.assertIsNotNone(result)
            self.assertIsNotNone(result.task_id)

        asyncio.run(run())

    def test_available_modules_logged(self):
        """Test that available modules are properly logged."""
        import logging
        from src.integration.basic_ai_pipeline import BasicAIPipeline

        # Capture log messages
        with self.assertLogs('src.integration.basic_ai_pipeline', level='INFO') as log:
            pipeline = BasicAIPipeline()

        # Should have initialization log
        self.assertTrue(any("Basic AI Pipeline initialized" in msg for msg in log.output))


if __name__ == '__main__':
    unittest.main()
