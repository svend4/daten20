#!/usr/bin/env python3
"""
OpenAPI Specification Validator
================================

Validates the OpenAPI specification file for correctness.
"""

import sys
import yaml
from pathlib import Path

def validate_openapi_spec(spec_path):
    """Validate OpenAPI specification."""
    print(f"Validating OpenAPI spec: {spec_path}")
    print("=" * 60)

    try:
        # Load YAML
        with open(spec_path, 'r') as f:
            spec = yaml.safe_load(f)

        print("✅ YAML syntax is valid")

        # Check required fields
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                print(f"❌ Missing required field: {field}")
                return False
            print(f"✅ Found required field: {field}")

        # Check OpenAPI version
        if spec['openapi'].startswith('3.'):
            print(f"✅ OpenAPI version: {spec['openapi']}")
        else:
            print(f"⚠️  OpenAPI version: {spec['openapi']} (expected 3.x)")

        # Check info section
        info = spec.get('info', {})
        info_fields = ['title', 'version']
        for field in info_fields:
            if field in info:
                print(f"✅ Info.{field}: {info[field]}")
            else:
                print(f"❌ Missing info.{field}")
                return False

        # Count paths and operations
        paths = spec.get('paths', {})
        total_operations = 0
        for path, methods in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in methods:
                    total_operations += 1

        print(f"✅ Total paths: {len(paths)}")
        print(f"✅ Total operations: {total_operations}")

        # Check schemas
        schemas = spec.get('components', {}).get('schemas', {})
        print(f"✅ Total schemas: {len(schemas)}")

        # List all endpoints
        print("\n📋 Endpoints:")
        for path in sorted(paths.keys()):
            methods = []
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in paths[path]:
                    methods.append(method.upper())
            print(f"   {path:40} {', '.join(methods)}")

        # Check for schema references
        print("\n🔗 Checking schema references...")
        missing_refs = set()

        def check_refs(obj, path=""):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref = obj['$ref']
                    if ref.startswith('#/components/schemas/'):
                        schema_name = ref.split('/')[-1]
                        if schema_name not in schemas:
                            missing_refs.add(schema_name)
                for key, value in obj.items():
                    check_refs(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs(item, f"{path}[{i}]")

        check_refs(spec)

        if missing_refs:
            print(f"❌ Missing schema references: {', '.join(missing_refs)}")
            return False
        else:
            print("✅ All schema references are valid")

        print("\n" + "=" * 60)
        print("✅ OpenAPI specification is valid!")
        print("=" * 60)
        return True

    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


if __name__ == '__main__':
    spec_path = Path(__file__).parent.parent / 'docs' / 'api' / 'openapi.yaml'

    success = validate_openapi_spec(spec_path)
    sys.exit(0 if success else 1)
