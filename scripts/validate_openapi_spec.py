#!/usr/bin/env python3
"""
OpenAPI Specification Validator
================================

Validates OpenAPI 3.0 specifications and checks for common issues.

Usage:
    python scripts/validate_openapi_spec.py [FILE]

Features:
    - OpenAPI 3.0 syntax validation
    - Schema validation
    - Reference validation
    - Security definition checks
    - Best practices checks
    - Detailed error reporting
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml

try:
    from jsonschema import Draft7Validator, ValidationError
    from jsonschema.validators import RefResolver

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Schema validation disabled.", file=sys.stderr)


class OpenAPIValidator:
    """Validator for OpenAPI 3.0 specifications"""

    def __init__(self, spec: Dict[str, Any], filename: str = "openapi.yaml"):
        self.spec = spec
        self.filename = filename
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str], List[str]]:
        """
        Validate the OpenAPI specification

        Returns:
            Tuple of (is_valid, errors, warnings, info)
        """
        # Basic structure validation
        self._validate_structure()

        # Validate OpenAPI version
        self._validate_version()

        # Validate info section
        self._validate_info()

        # Validate servers
        self._validate_servers()

        # Validate paths
        self._validate_paths()

        # Validate components
        self._validate_components()

        # Validate security
        self._validate_security()

        # Check best practices
        self._check_best_practices()

        # Validate references
        self._validate_references()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings, self.info

    def _validate_structure(self):
        """Validate basic structure"""
        required_fields = ["openapi", "info", "paths"]

        for field in required_fields:
            if field not in self.spec:
                self.errors.append(f"Missing required field: '{field}'")

    def _validate_version(self):
        """Validate OpenAPI version"""
        if "openapi" not in self.spec:
            return

        version = self.spec["openapi"]
        if not isinstance(version, str):
            self.errors.append("'openapi' field must be a string")
            return

        if not version.startswith("3.0"):
            self.errors.append(f"Unsupported OpenAPI version: {version}. Expected 3.0.x")

        self.info.append(f"OpenAPI version: {version}")

    def _validate_info(self):
        """Validate info section"""
        if "info" not in self.spec:
            return

        info = self.spec["info"]
        if not isinstance(info, dict):
            self.errors.append("'info' must be an object")
            return

        # Required fields in info
        required_info_fields = ["title", "version"]
        for field in required_info_fields:
            if field not in info:
                self.errors.append(f"Missing required field in info: '{field}'")

        # Optional but recommended fields
        recommended_fields = ["description", "contact", "license"]
        for field in recommended_fields:
            if field not in info:
                self.warnings.append(f"Missing recommended field in info: '{field}'")

        if "title" in info:
            self.info.append(f"API Title: {info['title']}")
        if "version" in info:
            self.info.append(f"API Version: {info['version']}")

    def _validate_servers(self):
        """Validate servers section"""
        if "servers" not in self.spec:
            self.warnings.append("No 'servers' defined. Using default: /")
            return

        servers = self.spec["servers"]
        if not isinstance(servers, list):
            self.errors.append("'servers' must be an array")
            return

        if len(servers) == 0:
            self.warnings.append("'servers' array is empty")

        for i, server in enumerate(servers):
            if not isinstance(server, dict):
                self.errors.append(f"Server {i} must be an object")
                continue

            if "url" not in server:
                self.errors.append(f"Server {i} missing required field: 'url'")

        self.info.append(f"Servers defined: {len(servers)}")

    def _validate_paths(self):
        """Validate paths section"""
        if "paths" not in self.spec:
            return

        paths = self.spec["paths"]
        if not isinstance(paths, dict):
            self.errors.append("'paths' must be an object")
            return

        if len(paths) == 0:
            self.warnings.append("No paths defined")
            return

        # Valid HTTP methods
        valid_methods = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]

        path_count = 0
        operation_count = 0

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                self.errors.append(f"Path '{path}' must be an object")
                continue

            path_count += 1

            # Check path starts with /
            if not path.startswith("/"):
                self.errors.append(f"Path must start with '/': {path}")

            # Validate operations
            for method, operation in path_item.items():
                if method.lower() not in valid_methods:
                    continue  # Might be $ref or other field

                operation_count += 1

                # Validate operation
                if not isinstance(operation, dict):
                    self.errors.append(f"{method.upper()} {path}: operation must be an object")
                    continue

                # Check for required fields
                if "responses" not in operation:
                    self.errors.append(f"{method.upper()} {path}: missing required 'responses'")

                # Check for recommended fields
                if "summary" not in operation and "description" not in operation:
                    self.warnings.append(f"{method.upper()} {path}: missing 'summary' or 'description'")

                if "tags" not in operation:
                    self.warnings.append(f"{method.upper()} {path}: missing 'tags'")

                if "operationId" not in operation:
                    self.warnings.append(f"{method.upper()} {path}: missing 'operationId'")

        self.info.append(f"Total paths: {path_count}")
        self.info.append(f"Total operations: {operation_count}")

    def _validate_components(self):
        """Validate components section"""
        if "components" not in self.spec:
            self.info.append("No 'components' defined")
            return

        components = self.spec["components"]
        if not isinstance(components, dict):
            self.errors.append("'components' must be an object")
            return

        # Count components
        component_types = ["schemas", "responses", "parameters", "examples", "requestBodies", "headers", "securitySchemes"]

        for comp_type in component_types:
            if comp_type in components:
                count = len(components[comp_type])
                self.info.append(f"{comp_type.capitalize()}: {count}")

    def _validate_security(self):
        """Validate security definitions"""
        if "security" not in self.spec and "components" not in self.spec:
            self.warnings.append("No security defined")
            return

        # Check securitySchemes
        if "components" in self.spec and "securitySchemes" in self.spec["components"]:
            schemes = self.spec["components"]["securitySchemes"]
            self.info.append(f"Security schemes defined: {len(schemes)}")

            for name, scheme in schemes.items():
                if "type" not in scheme:
                    self.errors.append(f"Security scheme '{name}' missing 'type'")
                    continue

                scheme_type = scheme["type"]
                valid_types = ["apiKey", "http", "oauth2", "openIdConnect"]

                if scheme_type not in valid_types:
                    self.errors.append(f"Security scheme '{name}' has invalid type: {scheme_type}")

        # Check global security
        if "security" in self.spec:
            security = self.spec["security"]
            if not isinstance(security, list):
                self.errors.append("'security' must be an array")

    def _check_best_practices(self):
        """Check best practices"""
        # Check for tags
        if "tags" in self.spec:
            tags = self.spec["tags"]
            if isinstance(tags, list):
                self.info.append(f"Tags defined: {len(tags)}")
            else:
                self.warnings.append("'tags' should be an array")
        else:
            self.warnings.append("No global 'tags' defined (recommended)")

        # Check for contact info
        if "info" in self.spec and "contact" in self.spec["info"]:
            contact = self.spec["info"]["contact"]
            if "email" not in contact and "url" not in contact:
                self.warnings.append("Contact info missing 'email' or 'url'")

        # Check for license
        if "info" in self.spec and "license" in self.spec["info"]:
            license_info = self.spec["info"]["license"]
            if "name" not in license_info:
                self.warnings.append("License missing 'name'")

    def _validate_references(self):
        """Validate $ref references"""
        refs = self._find_all_refs(self.spec)
        self.info.append(f"Total $ref references: {len(refs)}")

        for ref in refs:
            if ref.startswith("#/"):
                # Internal reference
                if not self._resolve_internal_ref(ref):
                    self.errors.append(f"Invalid $ref: {ref}")
            elif ref.startswith("http://") or ref.startswith("https://"):
                # External reference (can't validate easily)
                self.info.append(f"External $ref: {ref}")
            else:
                self.warnings.append(f"Unusual $ref format: {ref}")

    def _find_all_refs(self, obj: Any, refs: Set[str] = None) -> Set[str]:
        """Find all $ref references in the spec"""
        if refs is None:
            refs = set()

        if isinstance(obj, dict):
            if "$ref" in obj:
                refs.add(obj["$ref"])
            for value in obj.values():
                self._find_all_refs(value, refs)
        elif isinstance(obj, list):
            for item in obj:
                self._find_all_refs(item, refs)

        return refs

    def _resolve_internal_ref(self, ref: str) -> bool:
        """Check if internal reference exists"""
        if not ref.startswith("#/"):
            return False

        parts = ref[2:].split("/")
        current = self.spec

        try:
            for part in parts:
                # Handle URL encoding in keys
                part = part.replace("~1", "/").replace("~0", "~")
                current = current[part]
            return True
        except (KeyError, TypeError):
            return False

    def format_report(self) -> str:
        """Format validation report"""
        lines = []

        lines.append("=" * 70)
        lines.append(f"OpenAPI Specification Validation Report")
        lines.append(f"File: {self.filename}")
        lines.append("=" * 70)
        lines.append("")

        # Summary
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        info_count = len(self.info)

        if error_count == 0:
            lines.append("✓ Status: VALID")
        else:
            lines.append("✗ Status: INVALID")

        lines.append("")
        lines.append(f"Errors:   {error_count}")
        lines.append(f"Warnings: {warning_count}")
        lines.append(f"Info:     {info_count}")
        lines.append("")

        # Info
        if self.info:
            lines.append("📋 Information:")
            lines.append("-" * 70)
            for msg in self.info:
                lines.append(f"  ℹ️  {msg}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("⚠️  Warnings:")
            lines.append("-" * 70)
            for msg in self.warnings:
                lines.append(f"  ⚠️  {msg}")
            lines.append("")

        # Errors
        if self.errors:
            lines.append("❌ Errors:")
            lines.append("-" * 70)
            for msg in self.errors:
                lines.append(f"  ❌ {msg}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate OpenAPI 3.0 specification", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("file", nargs="?", default="docs/api/openapi.yaml", help="OpenAPI spec file (default: docs/api/openapi.yaml)")

    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    parser.add_argument("--quiet", action="store_true", help="Only show errors and warnings")

    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Load specification
    spec_file = Path(args.file)
    if not spec_file.exists():
        print(f"Error: File not found: {spec_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {spec_file}...", file=sys.stderr)

    try:
        with open(spec_file, "r") as f:
            if spec_file.suffix == ".json":
                spec = json.load(f)
            else:
                spec = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validator = OpenAPIValidator(spec, filename=spec_file.name)
    is_valid, errors, warnings, info = validator.validate()

    # Output results
    if args.json:
        results = {"valid": is_valid, "errors": errors, "warnings": warnings, "info": info}
        print(json.dumps(results, indent=2))
    else:
        report = validator.format_report()
        print(report)

    # Exit code
    if not is_valid:
        sys.exit(1)
    elif args.strict and len(warnings) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
