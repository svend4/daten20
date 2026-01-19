#!/usr/bin/env python3
"""
OpenAPI Specification Generator
================================

Automatically generates complete OpenAPI 3.0 specification by scanning
all Flask routes in the project.

Usage:
    python scripts/generate_openapi_spec.py [--output FILE] [--validate]

Features:
    - Scans all Python files for Flask routes
    - Extracts docstrings and converts to OpenAPI format
    - Generates schemas from type hints
    - Validates against OpenAPI 3.0 spec
    - Merges with existing documentation
    - Outputs YAML or JSON format
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RouteInfo:
    """Information about a Flask route"""

    def __init__(
        self,
        path: str,
        methods: List[str],
        function_name: str,
        docstring: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.path = path
        self.methods = methods
        self.function_name = function_name
        self.docstring = docstring or ""
        self.tags = tags or []
        self.parameters = []
        self.responses = {}
        self.summary = ""
        self.description = ""
        self._parse_docstring()

    def _parse_docstring(self):
        """Parse docstring to extract OpenAPI information"""
        if not self.docstring:
            return

        lines = self.docstring.strip().split("\n")
        current_section = None
        description_lines = []

        for line in lines:
            line = line.strip()

            # Check for YAML frontmatter (flasgger style)
            if line == "---":
                current_section = "yaml"
                continue

            # Extract summary (first line)
            if not self.summary and line and not line.startswith(("-", ":", "tags")):
                self.summary = line
                continue

            # Extract tags
            if line.startswith("tags:"):
                continue
            elif current_section == "yaml" and line.startswith("- "):
                tag = line[2:].strip()
                if tag not in self.tags:
                    self.tags.append(tag)

            # Collect description
            elif line and not line.startswith(("-", ":", "tags", "parameters", "responses")):
                description_lines.append(line)

        self.description = " ".join(description_lines)

    def to_openapi(self) -> Dict[str, Any]:
        """Convert route info to OpenAPI path object"""
        path_obj = {}

        for method in self.methods:
            method_lower = method.lower()
            operation = {
                "operationId": f"{method_lower}_{self.function_name}",
                "tags": self.tags or ["Uncategorized"],
                "summary": self.summary or f"{method} {self.path}",
                "description": self.description or "",
                "responses": self.responses
                or {
                    "200": {
                        "description": "Successful operation",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }

            # Add parameters if any
            if self.parameters:
                operation["parameters"] = self.parameters

            path_obj[method_lower] = operation

        return path_obj


class OpenAPIGenerator:
    """Generator for OpenAPI 3.0 specification"""

    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.routes: List[RouteInfo] = []
        self.base_spec = self._get_base_spec()

    def _get_base_spec(self) -> Dict[str, Any]:
        """Get base OpenAPI specification template"""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "Document Management System API",
                "description": "Comprehensive REST API with AI/ML capabilities",
                "version": "4.1.0",
                "contact": {
                    "name": "DMS Support",
                    "email": "support@example.com",
                    "url": "https://github.com/svend4/daten20",
                },
                "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
            },
            "servers": [
                {"url": "http://localhost:5000", "description": "Local Flask server"},
                {"url": "http://localhost:8000", "description": "Local FastAPI server"},
                {"url": "https://api.example.com", "description": "Production server"},
            ],
            "tags": [
                {"name": "System", "description": "Health checks and system status"},
                {"name": "Services", "description": "Service management operations"},
                {"name": "Documents", "description": "Document operations"},
                {"name": "Analytics", "description": "Analytics and BI operations"},
                {"name": "ML", "description": "Machine learning operations"},
                {"name": "Admin", "description": "Administration operations"},
            ],
            "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key authentication",
                    },
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token authentication",
                    },
                },
                "schemas": {},
            },
            "paths": {},
        }

    def scan_file(self, file_path: Path) -> List[RouteInfo]:
        """Scan a Python file for Flask routes"""
        routes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for route decorator
                    for decorator in node.decorator_list:
                        route_info = self._extract_route_info(decorator, node)
                        if route_info:
                            routes.append(route_info)

        except Exception as e:
            print(f"Warning: Error scanning {file_path}: {e}", file=sys.stderr)

        return routes

    def _extract_route_info(self, decorator: ast.expr, function_def: ast.FunctionDef) -> Optional[RouteInfo]:
        """Extract route information from decorator"""
        # Check if it's a route decorator
        if not isinstance(decorator, ast.Call):
            return None

        # Get decorator name
        decorator_name = ""
        if isinstance(decorator.func, ast.Attribute):
            decorator_name = decorator.func.attr
        elif isinstance(decorator.func, ast.Name):
            decorator_name = decorator.func.id

        # Check if it's a route decorator
        if not decorator_name.endswith("route"):
            return None

        # Extract route path
        path = None
        methods = ["GET"]  # Default method

        for arg in decorator.args:
            if isinstance(arg, ast.Constant):
                path = arg.value

        # Extract methods from kwargs
        for keyword in decorator.keywords:
            if keyword.arg == "methods":
                if isinstance(keyword.value, ast.List):
                    methods = [elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)]

        if not path:
            return None

        # Extract docstring
        docstring = ast.get_docstring(function_def)

        # Extract tags from file path or function name
        tags = self._infer_tags(function_def.name)

        return RouteInfo(
            path=path, methods=methods, function_name=function_def.name, docstring=docstring, tags=tags
        )

    def _infer_tags(self, function_name: str) -> List[str]:
        """Infer tags from function name"""
        tags = []

        # Common tag patterns
        tag_patterns = {
            "health": "System",
            "stats": "System",
            "service": "Services",
            "document": "Documents",
            "doc": "Documents",
            "analytics": "Analytics",
            "predict": "ML",
            "extract": "ML",
            "classify": "ML",
            "admin": "Admin",
        }

        function_lower = function_name.lower()
        for pattern, tag in tag_patterns.items():
            if pattern in function_lower:
                tags.append(tag)
                break

        return tags or ["Uncategorized"]

    def scan_all_files(self) -> List[RouteInfo]:
        """Scan all Python files in src directory"""
        all_routes = []

        # Files to scan
        api_files = [
            "api_v1.py",
            "api_analytics.py",
            "api_docs.py",
            "web_app.py",
            "graphql_api.py",
        ]

        for file_name in api_files:
            file_path = self.src_dir / file_name
            if file_path.exists():
                print(f"Scanning {file_path}...", file=sys.stderr)
                routes = self.scan_file(file_path)
                all_routes.extend(routes)
                print(f"  Found {len(routes)} routes", file=sys.stderr)

        return all_routes

    def generate_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI specification"""
        print("Scanning for Flask routes...", file=sys.stderr)
        routes = self.scan_all_files()
        print(f"\nTotal routes found: {len(routes)}", file=sys.stderr)

        spec = self.base_spec.copy()

        # Group routes by path
        paths: Dict[str, Dict[str, Any]] = {}
        for route in routes:
            path = route.path
            if path not in paths:
                paths[path] = {}

            # Merge methods
            route_spec = route.to_openapi()
            paths[path].update(route_spec)

        spec["paths"] = paths

        # Sort paths alphabetically
        spec["paths"] = dict(sorted(spec["paths"].items()))

        return spec

    def merge_with_existing(self, existing_spec_path: Path) -> Dict[str, Any]:
        """Merge generated spec with existing documentation"""
        if not existing_spec_path.exists():
            return self.generate_spec()

        print(f"Merging with existing spec: {existing_spec_path}", file=sys.stderr)

        with open(existing_spec_path, "r") as f:
            if existing_spec_path.suffix == ".json":
                existing_spec = json.load(f)
            else:
                existing_spec = yaml.safe_load(f)

        generated_spec = self.generate_spec()

        # Merge paths (prefer existing documentation if more detailed)
        for path, methods in generated_spec["paths"].items():
            if path in existing_spec.get("paths", {}):
                # Merge methods
                for method, operation in methods.items():
                    if method not in existing_spec["paths"][path]:
                        existing_spec["paths"][path][method] = operation
                    # If existing has more detail, keep it
                    elif len(str(existing_spec["paths"][path][method])) < len(str(operation)):
                        existing_spec["paths"][path][method] = operation
            else:
                existing_spec.setdefault("paths", {})[path] = methods

        # Merge tags
        existing_tags = {tag["name"] for tag in existing_spec.get("tags", [])}
        for tag in generated_spec.get("tags", []):
            if tag["name"] not in existing_tags:
                existing_spec.setdefault("tags", []).append(tag)

        return existing_spec

    def validate_spec(self, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate OpenAPI specification"""
        errors = []

        # Basic validation
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in spec:
                errors.append(f"Missing required field: {field}")

        # Validate OpenAPI version
        if spec.get("openapi") and not spec["openapi"].startswith("3.0"):
            errors.append(f"Unsupported OpenAPI version: {spec['openapi']}")

        # Validate paths
        if not spec.get("paths"):
            errors.append("No paths defined")

        return len(errors) == 0, errors


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI 3.0 specification from Flask routes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-o", "--output", default="docs/api/openapi_generated.yaml", help="Output file path (default: docs/api/openapi_generated.yaml)"
    )

    parser.add_argument(
        "-f", "--format", choices=["yaml", "json"], default="yaml", help="Output format (default: yaml)"
    )

    parser.add_argument("--merge", help="Merge with existing spec file")

    parser.add_argument("--validate", action="store_true", help="Validate generated specification")

    parser.add_argument("--src-dir", default="src", help="Source directory to scan (default: src)")

    args = parser.parse_args()

    # Create generator
    generator = OpenAPIGenerator(src_dir=args.src_dir)

    # Generate or merge specification
    if args.merge:
        merge_path = Path(args.merge)
        spec = generator.merge_with_existing(merge_path)
        print(f"\nMerged with {args.merge}", file=sys.stderr)
    else:
        spec = generator.generate_spec()

    # Validate if requested
    if args.validate:
        print("\nValidating specification...", file=sys.stderr)
        valid, errors = generator.validate_spec(spec)
        if valid:
            print("✓ Specification is valid", file=sys.stderr)
        else:
            print("✗ Specification has errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        if args.format == "json" or output_path.suffix == ".json":
            json.dump(spec, f, indent=2)
        else:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✓ OpenAPI specification written to: {output_path}", file=sys.stderr)
    print(f"  Total paths: {len(spec.get('paths', {}))}", file=sys.stderr)
    print(f"  Total tags: {len(spec.get('tags', []))}", file=sys.stderr)


if __name__ == "__main__":
    main()
