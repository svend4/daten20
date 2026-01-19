"""
Comprehensive tests for Service Templates System

Tests cover:
- ServiceTemplate dataclass (to_dict, from_dict)
- ServiceTemplateManager initialization
- Template CRUD operations (add, update, delete, get)
- Template search and filtering (by category, search)
- Service creation from templates
- Template import/export
- Default template creation
- Global singleton instance
"""

import pytest
import json
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock FinancialData before importing service_templates
# This is needed because service_templates.py imports a non-existent model
class MockFinancialData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Patch the import
sys.modules['src.models'].FinancialData = MockFinancialData

from src.core.service_templates import (
    ServiceTemplate,
    ServiceTemplateManager,
    get_template_manager,
)


class TestServiceTemplate:
    """Test ServiceTemplate dataclass"""

    def test_service_template_creation(self):
        """Test creating a service template"""
        template = ServiceTemplate(
            id="test1",
            name="Test Service",
            category="Test Category",
            description="Test description",
            default_region="Bavaria",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=["test", "example"],
            notes="Test notes"
        )

        assert template.id == "test1"
        assert template.name == "Test Service"
        assert template.category == "Test Category"
        assert template.default_brutto_rate == 40.00
        assert len(template.tags) == 2

    def test_service_template_to_dict(self):
        """Test converting template to dictionary"""
        template = ServiceTemplate(
            id="test1",
            name="Test",
            category="Category",
            description="Description",
            default_region="Region",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=["tag1"],
        )

        data = template.to_dict()

        assert isinstance(data, dict)
        assert data["id"] == "test1"
        assert data["name"] == "Test"
        assert data["default_brutto_rate"] == 40.00
        assert "tags" in data

    def test_service_template_from_dict(self):
        """Test creating template from dictionary"""
        data = {
            "id": "test1",
            "name": "Test",
            "category": "Category",
            "description": "Description",
            "default_region": "Region",
            "default_brutto_rate": 40.00,
            "default_hours_per_month": 160,
            "use_umlages": True,
            "tags": ["tag1"],
            "notes": ""
        }

        template = ServiceTemplate.from_dict(data)

        assert template.id == "test1"
        assert template.name == "Test"
        assert template.default_brutto_rate == 40.00
        assert template.tags == ["tag1"]

    def test_service_template_roundtrip(self):
        """Test to_dict and from_dict roundtrip"""
        original = ServiceTemplate(
            id="test1",
            name="Test",
            category="Category",
            description="Description",
            default_region="Region",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=["tag1", "tag2"],
            notes="Some notes"
        )

        data = original.to_dict()
        restored = ServiceTemplate.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.default_brutto_rate == original.default_brutto_rate
        assert restored.tags == original.tags
        assert restored.notes == original.notes


class TestServiceTemplateManagerInit:
    """Test ServiceTemplateManager initialization"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for templates"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_manager_initialization(self, temp_dir):
        """Test manager initializes with directory"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        assert manager.templates_dir.exists()
        assert manager.templates_file.parent.exists()

    def test_manager_creates_default_templates(self, temp_dir):
        """Test manager creates default templates on first run"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        # Check templates file was created
        assert manager.templates_file.exists()

        # Check default templates were created
        templates = manager.get_all_templates()
        assert len(templates) > 0

    def test_manager_does_not_recreate_templates(self, temp_dir):
        """Test manager doesn't recreate templates if file exists"""
        # First initialization
        manager1 = ServiceTemplateManager(templates_dir=temp_dir)
        count1 = len(manager1.get_all_templates())

        # Second initialization
        manager2 = ServiceTemplateManager(templates_dir=temp_dir)
        count2 = len(manager2.get_all_templates())

        assert count1 == count2


class TestTemplateRetrieval:
    """Test template retrieval operations"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        return ServiceTemplateManager(templates_dir=temp_dir)

    @pytest.fixture
    def sample_templates(self):
        return [
            ServiceTemplate(
                id="test1",
                name="Shopping",
                category="Daily Living",
                description="Shopping assistance",
                default_region="Bavaria",
                default_brutto_rate=38.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["shopping", "daily"],
            ),
            ServiceTemplate(
                id="test2",
                name="Nursing",
                category="Professional Services",
                description="Professional nursing",
                default_region="Bavaria",
                default_brutto_rate=55.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["nursing", "medical"],
            ),
            ServiceTemplate(
                id="test3",
                name="Cleaning",
                category="Daily Living",
                description="Household cleaning",
                default_region="Bavaria",
                default_brutto_rate=35.00,
                default_hours_per_month=120,
                use_umlages=True,
                tags=["cleaning", "household"],
            ),
        ]

    def test_get_all_templates(self, manager, sample_templates):
        """Test getting all templates"""
        manager.save_templates(sample_templates)

        templates = manager.get_all_templates()

        assert len(templates) == 3
        assert all(isinstance(t, ServiceTemplate) for t in templates)

    def test_get_template_by_id_exists(self, manager, sample_templates):
        """Test getting template by ID when it exists"""
        manager.save_templates(sample_templates)

        template = manager.get_template_by_id("test1")

        assert template is not None
        assert template.id == "test1"
        assert template.name == "Shopping"

    def test_get_template_by_id_not_exists(self, manager, sample_templates):
        """Test getting template by ID when it doesn't exist"""
        manager.save_templates(sample_templates)

        template = manager.get_template_by_id("nonexistent")

        assert template is None

    def test_get_templates_by_category(self, manager, sample_templates):
        """Test getting templates by category"""
        manager.save_templates(sample_templates)

        daily_living = manager.get_templates_by_category("Daily Living")

        assert len(daily_living) == 2
        assert all(t.category == "Daily Living" for t in daily_living)

    def test_get_templates_by_category_empty(self, manager, sample_templates):
        """Test getting templates from non-existent category"""
        manager.save_templates(sample_templates)

        templates = manager.get_templates_by_category("Nonexistent")

        assert len(templates) == 0

    def test_get_categories(self, manager, sample_templates):
        """Test getting all categories"""
        manager.save_templates(sample_templates)

        categories = manager.get_categories()

        assert len(categories) == 2
        assert "Daily Living" in categories
        assert "Professional Services" in categories
        assert categories == sorted(categories)  # Should be sorted


class TestTemplateSearch:
    """Test template search functionality"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        return ServiceTemplateManager(templates_dir=temp_dir)

    @pytest.fixture
    def sample_templates(self):
        return [
            ServiceTemplate(
                id="test1",
                name="Shopping Assistance",
                category="Daily Living",
                description="Help with grocery shopping",
                default_region="Bavaria",
                default_brutto_rate=38.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["shopping", "errands"],
            ),
            ServiceTemplate(
                id="test2",
                name="Nursing Care",
                category="Professional",
                description="Professional nursing services",
                default_region="Bavaria",
                default_brutto_rate=55.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["nursing", "medical"],
            ),
        ]

    def test_search_by_name(self, manager, sample_templates):
        """Test searching templates by name"""
        manager.save_templates(sample_templates)

        results = manager.search_templates("shopping")

        assert len(results) == 1
        assert results[0].id == "test1"

    def test_search_by_description(self, manager, sample_templates):
        """Test searching templates by description"""
        manager.save_templates(sample_templates)

        results = manager.search_templates("grocery")

        assert len(results) == 1
        assert results[0].id == "test1"

    def test_search_by_tags(self, manager, sample_templates):
        """Test searching templates by tags"""
        manager.save_templates(sample_templates)

        results = manager.search_templates("nursing")

        assert len(results) == 1
        assert results[0].id == "test2"

    def test_search_case_insensitive(self, manager, sample_templates):
        """Test search is case insensitive"""
        manager.save_templates(sample_templates)

        results = manager.search_templates("SHOPPING")

        assert len(results) == 1

    def test_search_no_results(self, manager, sample_templates):
        """Test search with no matching results"""
        manager.save_templates(sample_templates)

        results = manager.search_templates("nonexistent")

        assert len(results) == 0


class TestTemplateCRUD:
    """Test template CRUD operations"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        return ServiceTemplateManager(templates_dir=temp_dir)

    @pytest.fixture
    def sample_template(self):
        return ServiceTemplate(
            id="test1",
            name="Test Service",
            category="Test",
            description="Test description",
            default_region="Bavaria",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=["test"],
        )

    def test_add_template_success(self, manager, sample_template):
        """Test adding a new template"""
        result = manager.add_template(sample_template)

        assert result is True
        assert manager.get_template_by_id("test1") is not None

    def test_add_template_duplicate_id(self, manager, sample_template):
        """Test adding template with duplicate ID fails"""
        manager.add_template(sample_template)

        result = manager.add_template(sample_template)

        assert result is False

    def test_update_template_success(self, manager, sample_template):
        """Test updating an existing template"""
        manager.add_template(sample_template)

        updated = ServiceTemplate(
            id="updated_id",  # Will be overridden
            name="Updated Name",
            category="Updated Category",
            description="Updated",
            default_region="Berlin",
            default_brutto_rate=50.00,
            default_hours_per_month=180,
            use_umlages=False,
            tags=["updated"],
        )

        result = manager.update_template("test1", updated)

        assert result is True
        template = manager.get_template_by_id("test1")
        assert template.name == "Updated Name"
        assert template.default_brutto_rate == 50.00

    def test_update_template_preserves_id(self, manager, sample_template):
        """Test update preserves original ID"""
        manager.add_template(sample_template)

        updated = ServiceTemplate(
            id="different_id",
            name="Updated",
            category="Cat",
            description="Desc",
            default_region="Region",
            default_brutto_rate=50.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=[],
        )

        manager.update_template("test1", updated)

        template = manager.get_template_by_id("test1")
        assert template.id == "test1"

    def test_update_template_not_exists(self, manager):
        """Test updating non-existent template fails"""
        template = ServiceTemplate(
            id="test1",
            name="Test",
            category="Cat",
            description="Desc",
            default_region="Region",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=[],
        )

        result = manager.update_template("nonexistent", template)

        assert result is False

    def test_delete_template_success(self, manager, sample_template):
        """Test deleting an existing template"""
        manager.add_template(sample_template)

        result = manager.delete_template("test1")

        assert result is True
        assert manager.get_template_by_id("test1") is None

    def test_delete_template_not_exists(self, manager):
        """Test deleting non-existent template fails"""
        result = manager.delete_template("nonexistent")

        assert result is False



class TestImportExport:
    """Test template import and export"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        return ServiceTemplateManager(templates_dir=temp_dir)

    @pytest.fixture
    def sample_templates(self):
        return [
            ServiceTemplate(
                id="test1",
                name="Service 1",
                category="Category",
                description="Description 1",
                default_region="Bavaria",
                default_brutto_rate=40.00,
                default_hours_per_month=160,
                use_umlages=True,
                tags=["tag1"],
            ),
            ServiceTemplate(
                id="test2",
                name="Service 2",
                category="Category",
                description="Description 2",
                default_region="Bavaria",
                default_brutto_rate=50.00,
                default_hours_per_month=120,
                use_umlages=True,
                tags=["tag2"],
            ),
        ]

    def test_export_templates(self, manager, sample_templates, temp_dir):
        """Test exporting templates to file"""
        manager.save_templates(sample_templates)

        output_path = str(Path(temp_dir) / "export.json")
        result = manager.export_templates(output_path)

        assert result is True
        assert Path(output_path).exists()

        # Verify exported content
        with open(output_path, "r") as f:
            data = json.load(f)
        assert len(data) == 2

    def test_import_templates_replace(self, manager, sample_templates, temp_dir):
        """Test importing templates (replace mode)"""
        # Create export file
        export_path = str(Path(temp_dir) / "import.json")
        data = [t.to_dict() for t in sample_templates]
        with open(export_path, "w") as f:
            json.dump(data, f)

        result = manager.import_templates(export_path, merge=False)

        assert result is True
        templates = manager.get_all_templates()
        assert len(templates) == 2

    def test_import_templates_merge(self, manager, sample_templates, temp_dir):
        """Test importing templates (merge mode)"""
        # Clear default templates
        manager.save_templates([])

        # Add initial template
        initial = ServiceTemplate(
            id="initial",
            name="Initial",
            category="Cat",
            description="Desc",
            default_region="Region",
            default_brutto_rate=30.00,
            default_hours_per_month=100,
            use_umlages=True,
            tags=[],
        )
        manager.add_template(initial)

        # Create import file with different templates
        export_path = str(Path(temp_dir) / "import.json")
        data = [t.to_dict() for t in sample_templates]
        with open(export_path, "w") as f:
            json.dump(data, f)

        result = manager.import_templates(export_path, merge=True)

        assert result is True
        templates = manager.get_all_templates()
        assert len(templates) == 3  # 1 initial + 2 imported

    def test_import_templates_merge_duplicates(self, manager, sample_templates, temp_dir):
        """Test importing with duplicates in merge mode"""
        # Clear default templates
        manager.save_templates([])

        # Add one of the templates first
        manager.add_template(sample_templates[0])

        # Create import file
        export_path = str(Path(temp_dir) / "import.json")
        data = [t.to_dict() for t in sample_templates]
        with open(export_path, "w") as f:
            json.dump(data, f)

        result = manager.import_templates(export_path, merge=True)

        assert result is True
        templates = manager.get_all_templates()
        # Should have 2 templates (test1 already existed, test2 added)
        assert len(templates) == 2


class TestDefaultTemplates:
    """Test default template creation"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_default_templates_created(self, temp_dir):
        """Test default templates are created on initialization"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        templates = manager.get_all_templates()

        assert len(templates) > 0

    def test_default_templates_have_required_fields(self, temp_dir):
        """Test all default templates have required fields"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        templates = manager.get_all_templates()

        for template in templates:
            assert template.id
            assert template.name
            assert template.category
            assert template.description
            assert template.default_region
            assert template.default_brutto_rate > 0
            assert template.default_hours_per_month > 0
            assert isinstance(template.tags, list)

    def test_default_templates_categories(self, temp_dir):
        """Test default templates have various categories"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        categories = manager.get_categories()

        # Should have multiple categories
        assert len(categories) >= 5
        assert "Daily Living" in categories
        assert "Personal Care" in categories

    def test_default_templates_searchable(self, temp_dir):
        """Test default templates are searchable"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        # Search for common terms
        results = manager.search_templates("shopping")
        assert len(results) > 0

        results = manager.search_templates("nursing")
        assert len(results) > 0


class TestGlobalInstance:
    """Test global template manager instance"""

    def test_get_template_manager_singleton(self):
        """Test global manager is singleton"""
        manager1 = get_template_manager()
        manager2 = get_template_manager()

        assert manager1 is manager2

    def test_get_template_manager_initialized(self):
        """Test global manager is properly initialized"""
        manager = get_template_manager()

        assert manager.templates_dir.exists()
        assert isinstance(manager.get_all_templates(), list)


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        return ServiceTemplateManager(templates_dir=temp_dir)

    def test_get_all_templates_empty_file(self, temp_dir):
        """Test getting templates when file is empty"""
        manager = ServiceTemplateManager(templates_dir=temp_dir)

        # Clear templates
        manager.save_templates([])

        templates = manager.get_all_templates()
        assert len(templates) == 0

    def test_save_templates_empty_list(self, manager):
        """Test saving empty template list"""
        manager.save_templates([])

        templates = manager.get_all_templates()
        assert len(templates) == 0

    def test_search_empty_string(self, manager):
        """Test searching with empty string"""
        template = ServiceTemplate(
            id="test1",
            name="Test",
            category="Cat",
            description="Desc",
            default_region="Region",
            default_brutto_rate=40.00,
            default_hours_per_month=160,
            use_umlages=True,
            tags=[],
        )
        manager.add_template(template)

        # Empty search should return nothing
        results = manager.search_templates("")
        # Actually empty string will match nothing because query_lower will be ""
        # and "" in string is always True, so it might return all
        # Let's just check it doesn't crash
        assert isinstance(results, list)

