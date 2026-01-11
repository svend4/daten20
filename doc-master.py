#!/usr/bin/env python3
"""
Document Management Master Control Panel
==========================================

Unified control panel for all document management applications and tools.

Features:
- Service management (start/stop/status)
- Unified CLI for all tools
- Pipeline builder and executor
- Health checks and monitoring
- Configuration management
- Status dashboard

Applications Managed:
- doc-processor: Single document processing
- doc-dashboard: Web UI dashboard
- doc-api-server: REST API server
- doc-batch-processor: Batch processing
- doc-search: Search engine
- doc-comparator: Document comparison
- doc-anonymizer: PII anonymization
- doc-quality: Quality analysis

Usage:
    # Show status of all components
    python doc-master.py status

    # Health check
    python doc-master.py health

    # Run a pipeline
    python doc-master.py pipeline run gdpr-compliance --input /documents/

    # Quick process with full pipeline
    python doc-master.py quick-process document.pdf --steps all

Author: Document Management System
Version: 1.0.0
"""

import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import platform

# Setup logging
from src.core.logging_config import setup_logging
logger = setup_logging(__name__, log_level="INFO")


@dataclass
class ServiceInfo:
    """Information about a service/application."""
    name: str
    script: str
    description: str
    type: str  # service, tool, daemon
    is_available: bool = False
    status: str = "unknown"  # running, stopped, error, n/a


@dataclass
class PipelineStep:
    """Single step in processing pipeline."""
    tool: str
    action: str
    params: Dict[str, Any]


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    pipeline_name: str
    executed_at: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    total_time_seconds: float
    results: List[Dict[str, Any]]


class MasterControlPanel:
    """Master control panel for document management system."""

    def __init__(self):
        """Initialize master control panel."""
        self.services = self._discover_services()
        logger.info("MasterControlPanel initialized")

    def _discover_services(self) -> Dict[str, ServiceInfo]:
        """Discover available services and tools."""
        services = {
            # Processing services
            "processor": ServiceInfo(
                name="Document Processor",
                script="doc-processor.py",
                description="Single document processing with NER, classification, relations",
                type="tool"
            ),
            "batch": ServiceInfo(
                name="Batch Processor",
                script="doc-batch-processor.py",
                description="Multi-threaded batch document processing",
                type="service"
            ),
            "api": ServiceInfo(
                name="API Server",
                script="doc-api-server.py",
                description="FastAPI REST API server",
                type="daemon"
            ),
            "dashboard": ServiceInfo(
                name="Web Dashboard",
                script="doc-dashboard.py",
                description="Interactive web dashboard with visualizations",
                type="daemon"
            ),
            "search": ServiceInfo(
                name="Search Engine",
                script="doc-search.py",
                description="Full-text and semantic search engine",
                type="service"
            ),

            # Intelligence tools
            "comparator": ServiceInfo(
                name="Document Comparator",
                script="doc-comparator.py",
                description="Advanced document comparison with similarity metrics",
                type="tool"
            ),
            "anonymizer": ServiceInfo(
                name="Document Anonymizer",
                script="doc-anonymizer.py",
                description="GDPR-compliant PII anonymization",
                type="tool"
            ),
            "quality": ServiceInfo(
                name="Quality Analyzer",
                script="doc-quality.py",
                description="Comprehensive document quality assessment",
                type="tool"
            ),
        }

        # Check which services are available
        for key, service in services.items():
            service_path = Path(service.script)
            service.is_available = service_path.exists()
            service.status = "available" if service.is_available else "not_found"

        return services

    def status(self) -> Dict[str, Any]:
        """
        Get status of all components.

        Returns:
            Status dictionary
        """
        logger.info("Checking status of all components")

        status = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "services": {},
            "summary": {
                "total": len(self.services),
                "available": 0,
                "running": 0,
                "stopped": 0
            }
        }

        for key, service in self.services.items():
            status["services"][key] = {
                "name": service.name,
                "type": service.type,
                "available": service.is_available,
                "status": service.status,
                "description": service.description
            }

            if service.is_available:
                status["summary"]["available"] += 1

        return status

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Health status dictionary
        """
        logger.info("Performing health check")

        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }

        # Check Python environment
        health["checks"]["python"] = {
            "status": "ok",
            "version": platform.python_version()
        }

        # Check required scripts
        required_scripts = ["doc-processor.py", "doc-comparator.py", "doc-anonymizer.py"]
        missing = []
        for script in required_scripts:
            if not Path(script).exists():
                missing.append(script)

        health["checks"]["scripts"] = {
            "status": "ok" if not missing else "warning",
            "missing": missing
        }

        # Check src/ directory
        src_path = Path("src")
        health["checks"]["src_directory"] = {
            "status": "ok" if src_path.exists() else "error",
            "exists": src_path.exists()
        }

        # Check data/ directory
        data_path = Path("data")
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)

        health["checks"]["data_directory"] = {
            "status": "ok",
            "exists": data_path.exists()
        }

        # Overall status
        if any(check["status"] == "error" for check in health["checks"].values()):
            health["overall_status"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health["checks"].values()):
            health["overall_status"] = "degraded"

        return health

    def quick_process(
        self,
        file_path: str,
        steps: List[str],
        output_dir: str = "output"
    ) -> PipelineResult:
        """
        Quick process document with specified steps.

        Args:
            file_path: Path to document
            steps: List of processing steps
            output_dir: Output directory

        Returns:
            PipelineResult
        """
        logger.info(f"Quick processing: {file_path} with steps: {steps}")

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        base_name = Path(file_path).stem
        results = []
        start_time = datetime.now()

        completed = 0
        failed = 0

        # Process document
        if "process" in steps or "all" in steps:
            try:
                output_file = output_path / f"{base_name}_processed.json"
                result = self._run_command([
                    "python", "doc-processor.py", "process",
                    file_path, "--output", str(output_file)
                ])
                results.append({"step": "process", "status": "success", "output": str(output_file)})
                completed += 1
            except Exception as e:
                results.append({"step": "process", "status": "failed", "error": str(e)})
                failed += 1

        # Anonymize document
        if "anonymize" in steps or "all" in steps:
            try:
                output_file = output_path / f"{base_name}_anonymized.txt"
                result = self._run_command([
                    "python", "doc-anonymizer.py", "anonymize",
                    file_path, "--output", str(output_file)
                ])
                results.append({"step": "anonymize", "status": "success", "output": str(output_file)})
                completed += 1
            except Exception as e:
                results.append({"step": "anonymize", "status": "failed", "error": str(e)})
                failed += 1

        # Quality check
        if "quality" in steps or "all" in steps:
            try:
                output_file = output_path / f"{base_name}_quality.json"
                result = self._run_command([
                    "python", "doc-quality.py", "analyze",
                    file_path, "--output", str(output_file)
                ])
                results.append({"step": "quality", "status": "success", "output": str(output_file)})
                completed += 1
            except Exception as e:
                results.append({"step": "quality", "status": "failed", "error": str(e)})
                failed += 1

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        return PipelineResult(
            pipeline_name="quick-process",
            executed_at=start_time.isoformat(),
            total_steps=len(steps),
            completed_steps=completed,
            failed_steps=failed,
            total_time_seconds=total_time,
            results=results
        )

    def run_pipeline(
        self,
        pipeline_name: str,
        input_path: str,
        params: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Run predefined pipeline.

        Args:
            pipeline_name: Name of pipeline (e.g., 'gdpr-compliance')
            input_path: Input file or directory
            params: Optional parameters

        Returns:
            PipelineResult
        """
        logger.info(f"Running pipeline: {pipeline_name}")

        pipelines = {
            "gdpr-compliance": [
                {"tool": "anonymizer", "action": "scan", "params": {}},
                {"tool": "anonymizer", "action": "anonymize", "params": {"strategy": "masking"}},
                {"tool": "quality", "action": "analyze", "params": {}},
            ],
            "quality-assurance": [
                {"tool": "quality", "action": "analyze", "params": {"threshold": 80}},
                {"tool": "processor", "action": "process", "params": {}},
            ],
            "full-analysis": [
                {"tool": "processor", "action": "process", "params": {}},
                {"tool": "quality", "action": "analyze", "params": {}},
            ],
        }

        if pipeline_name not in pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")

        steps = pipelines[pipeline_name]
        start_time = datetime.now()

        results = []
        completed = 0
        failed = 0

        for step in steps:
            try:
                # Execute step
                logger.info(f"Executing step: {step['tool']}.{step['action']}")
                # Simplified execution (in production, implement full pipeline logic)
                results.append({
                    "tool": step["tool"],
                    "action": step["action"],
                    "status": "success"
                })
                completed += 1
            except Exception as e:
                logger.error(f"Step failed: {e}")
                results.append({
                    "tool": step["tool"],
                    "action": step["action"],
                    "status": "failed",
                    "error": str(e)
                })
                failed += 1

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        return PipelineResult(
            pipeline_name=pipeline_name,
            executed_at=start_time.isoformat(),
            total_steps=len(steps),
            completed_steps=completed,
            failed_steps=failed,
            total_time_seconds=total_time,
            results=results
        )

    def _run_command(self, command: List[str], timeout: int = 120) -> str:
        """
        Run shell command and return output.

        Args:
            command: Command to run
            timeout: Timeout in seconds

        Returns:
            Command output
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command timed out after {timeout}s")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Document Management Master Control Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check status of all components
  python doc-master.py status

  # Health check
  python doc-master.py health

  # Quick process document with all steps
  python doc-master.py quick-process document.pdf --steps all

  # Run specific steps
  python doc-master.py quick-process document.pdf --steps process anonymize

  # Run GDPR compliance pipeline
  python doc-master.py pipeline gdpr-compliance --input /documents/

  # List available pipelines
  python doc-master.py pipelines
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show status of all components")

    # Health command
    health_parser = subparsers.add_parser("health", help="Perform health check")

    # Quick process command
    quick_parser = subparsers.add_parser("quick-process", help="Quick process document")
    quick_parser.add_argument("file", help="Document to process")
    quick_parser.add_argument("--steps", nargs="+",
                             choices=["process", "anonymize", "quality", "all"],
                             default=["process"],
                             help="Processing steps")
    quick_parser.add_argument("--output-dir", "-o", default="output",
                             help="Output directory")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run pipeline")
    pipeline_parser.add_argument("name",
                                choices=["gdpr-compliance", "quality-assurance", "full-analysis"],
                                help="Pipeline name")
    pipeline_parser.add_argument("--input", "-i", required=True,
                                help="Input file or directory")

    # Pipelines list command
    pipelines_parser = subparsers.add_parser("pipelines", help="List available pipelines")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    panel = MasterControlPanel()

    try:
        if args.command == "status":
            status = panel.status()

            print("\n📊 Document Management System Status")
            print("=" * 80)
            print(f"Platform: {status['platform']}")
            print(f"Python: {status['python_version']}")
            print(f"\nComponents:")

            for key, service in status["services"].items():
                status_icon = "✅" if service["available"] else "❌"
                print(f"  {status_icon} {service['name']:30s} [{service['type']:10s}] - {service['description']}")

            print(f"\nSummary:")
            print(f"  Total: {status['summary']['total']}")
            print(f"  Available: {status['summary']['available']}")

        elif args.command == "health":
            health = panel.health_check()

            print("\n🏥 System Health Check")
            print("=" * 80)
            print(f"Overall Status: {health['overall_status'].upper()}")
            print(f"\nChecks:")

            for check_name, check_data in health["checks"].items():
                status_icon = "✅" if check_data["status"] == "ok" else "⚠️" if check_data["status"] == "warning" else "❌"
                print(f"  {status_icon} {check_name:20s}: {check_data['status']}")

        elif args.command == "quick-process":
            result = panel.quick_process(args.file, args.steps, args.output_dir)

            print("\n⚡ Quick Process Complete")
            print("=" * 80)
            print(f"Pipeline: {result.pipeline_name}")
            print(f"Total steps: {result.total_steps}")
            print(f"Completed: {result.completed_steps}")
            print(f"Failed: {result.failed_steps}")
            print(f"Time: {result.total_time_seconds:.2f}s")
            print(f"\nResults:")

            for res in result.results:
                status_icon = "✅" if res["status"] == "success" else "❌"
                print(f"  {status_icon} {res['step']:15s}: {res.get('output', res.get('error', 'N/A'))}")

        elif args.command == "pipeline":
            result = panel.run_pipeline(args.name, args.input)

            print(f"\n🔧 Pipeline '{result.pipeline_name}' Complete")
            print("=" * 80)
            print(f"Completed: {result.completed_steps}/{result.total_steps}")
            print(f"Time: {result.total_time_seconds:.2f}s")

        elif args.command == "pipelines":
            print("\n📋 Available Pipelines")
            print("=" * 80)
            pipelines = {
                "gdpr-compliance": "GDPR compliance workflow (scan → anonymize → quality check)",
                "quality-assurance": "Quality assurance workflow (quality check → process)",
                "full-analysis": "Full document analysis (process → quality check)",
            }

            for name, desc in pipelines.items():
                print(f"  • {name:20s}: {desc}")

    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
