#!/usr/bin/env python3
"""
OpenAPI Specification Export Utility

Export OpenAPI 3.0 specification from FastAPI application to YAML/JSON format.

Usage:
    python export_openapi.py --format yaml --output openapi.yaml
    python export_openapi.py --format json --output openapi.json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("WARNING: PyYAML not installed. YAML export unavailable.")


def export_openapi_spec(app, output_path: str, format: str = "yaml"):
    """
    Export OpenAPI specification from FastAPI app.

    Args:
        app: FastAPI application instance
        output_path: Output file path
        format: Output format (yaml or json)
    """
    # Get OpenAPI schema from FastAPI
    openapi_schema = app.openapi()

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if format == "yaml":
        if not YAML_AVAILABLE:
            print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
            sys.exit(1)

        with open(output_file, "w") as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)
        print(f"✅ OpenAPI spec exported to {output_file} (YAML)")

    elif format == "json":
        with open(output_file, "w") as f:
            json.dump(openapi_schema, f, indent=2)
        print(f"✅ OpenAPI spec exported to {output_file} (JSON)")

    else:
        print(f"ERROR: Unknown format '{format}'. Use 'yaml' or 'json'.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Export OpenAPI specification")
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)"
    )
    parser.add_argument(
        "--output",
        default="openapi.yaml",
        help="Output file path (default: openapi.yaml)"
    )
    parser.add_argument(
        "--server",
        default="doc-api-server",
        help="Server module to import (default: doc-api-server)"
    )

    args = parser.parse_args()

    # Import FastAPI app
    try:
        if args.server == "doc-api-server":
            from doc_api_server import app
        else:
            # Dynamic import
            module = __import__(args.server)
            app = module.app

        if app is None:
            print("ERROR: FastAPI app not initialized. Install FastAPI first.")
            sys.exit(1)

        # Export specification
        export_openapi_spec(app, args.output, args.format)

        # Print statistics
        schema = app.openapi()
        endpoints = sum(len(methods) for methods in schema.get("paths", {}).values())
        print(f"\n📊 Statistics:")
        print(f"   - Endpoints: {endpoints}")
        print(f"   - Tags: {len(schema.get('tags', []))}")
        print(f"   - Schemas: {len(schema.get('components', {}).get('schemas', {}))}")
        print(f"   - API Version: {schema.get('info', {}).get('version')}")

    except ImportError as e:
        print(f"ERROR: Could not import server module: {e}")
        print("Make sure FastAPI is installed and the server module exists.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
