"""
Comprehensive tests for OLAP Cube module

Tests cover:
- OLAP cube creation and configuration
- Multidimensional operations (slice, dice)
- Hierarchical operations (drill-down, drill-up)
- Pivot tables
- MDX query engine
- Aggregation caching
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch

from src.analytics.olap_cube import (
    AggregationType,
    Dimension,
    Measure,
    CubeCell,
    OLAPCube,
    MDXQueryEngine,
    CubeManager,
    get_cube_manager,
    PANDAS_AVAILABLE,
)


class TestEnums:
    """Test enums"""

    def test_aggregation_type_enum(self):
        """Test AggregationType enum values"""
        assert AggregationType.SUM == "sum"
        assert AggregationType.AVG == "avg"
        assert AggregationType.COUNT == "count"
        assert AggregationType.MIN == "min"
        assert AggregationType.MAX == "max"
        assert AggregationType.DISTINCT_COUNT == "distinct_count"


class TestDataClasses:
    """Test data classes"""

    def test_dimension_creation(self):
        """Test Dimension creation"""
        dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter", "Month", "Day"],
            members=["2024", "Q1", "January"]
        )

        assert dim.name == "Time"
        assert len(dim.hierarchy) == 4
        assert len(dim.members) == 3

    def test_dimension_defaults(self):
        """Test Dimension default values"""
        dim = Dimension(
            name="Product",
            hierarchy=["Category", "Subcategory", "Product"]
        )

        assert dim.members == []

    def test_measure_creation(self):
        """Test Measure creation"""
        measure = Measure(
            name="Sales",
            aggregation=AggregationType.SUM,
            format="currency"
        )

        assert measure.name == "Sales"
        assert measure.aggregation == AggregationType.SUM
        assert measure.format == "currency"

    def test_measure_defaults(self):
        """Test Measure default values"""
        measure = Measure(
            name="Count",
            aggregation=AggregationType.COUNT
        )

        assert measure.format == "numeric"

    def test_cube_cell_creation(self):
        """Test CubeCell creation"""
        cell = CubeCell(
            coordinates={"Year": "2024", "Product": "Widget"},
            value=1000.0,
            aggregation=AggregationType.SUM
        )

        assert cell.coordinates["Year"] == "2024"
        assert cell.value == 1000.0
        assert cell.aggregation == AggregationType.SUM


class TestOLAPCube:
    """Test OLAP Cube operations"""

    @pytest.fixture
    def cube(self):
        """Create OLAP cube instance"""
        return OLAPCube("SalesCube")

    @pytest.fixture
    def time_dimension(self):
        """Create time dimension"""
        return Dimension(
            name="Year",
            hierarchy=["Year", "Quarter", "Month"]
        )

    @pytest.fixture
    def product_dimension(self):
        """Create product dimension"""
        return Dimension(
            name="Product",
            hierarchy=["Category", "Product"]
        )

    @pytest.fixture
    def sales_measure(self):
        """Create sales measure"""
        return Measure(
            name="Sales",
            aggregation=AggregationType.SUM,
            format="currency"
        )

    @pytest.fixture
    def sample_data(self):
        """Create sample sales data"""
        if not PANDAS_AVAILABLE:
            return None

        import pandas as pd
        return pd.DataFrame({
            "Year": ["2023", "2023", "2024", "2024", "2024"],
            "Product": ["A", "B", "A", "B", "C"],
            "Category": ["Cat1", "Cat2", "Cat1", "Cat2", "Cat1"],
            "Sales": [100, 150, 200, 250, 300],
            "Quantity": [10, 15, 20, 25, 30]
        })

    def test_initialization(self, cube):
        """Test cube initialization"""
        assert cube.name == "SalesCube"
        assert len(cube.dimensions) == 0
        assert len(cube.measures) == 0
        assert cube.data is None

    def test_add_dimension(self, cube, time_dimension):
        """Test adding dimension"""
        cube.add_dimension(time_dimension)

        assert "Year" in cube.dimensions
        assert cube.dimensions["Year"] == time_dimension

    def test_add_measure(self, cube, sales_measure):
        """Test adding measure"""
        cube.add_measure(sales_measure)

        assert "Sales" in cube.measures
        assert cube.measures["Sales"] == sales_measure

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_load_data(self, cube, time_dimension, product_dimension, sample_data):
        """Test loading data into cube"""
        cube.add_dimension(time_dimension)
        cube.add_dimension(product_dimension)

        cube.load_data(sample_data)

        assert cube.data is not None
        assert len(cube.data) == 5
        # Members should be extracted from data
        assert len(cube.dimensions["Year"].members) > 0

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_slice_operation(self, cube, time_dimension, product_dimension,
                            sales_measure, sample_data):
        """Test slice operation"""
        cube.add_dimension(time_dimension)
        cube.add_dimension(product_dimension)
        cube.add_measure(sales_measure)
        cube.load_data(sample_data)

        # Slice by Year = 2024
        result = cube.slice("Year", "2024")

        assert len(result) == 3  # Only 2024 records
        assert all(result["Year"] == "2024")

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_dice_operation(self, cube, time_dimension, product_dimension,
                           sales_measure, sample_data):
        """Test dice operation"""
        cube.add_dimension(time_dimension)
        cube.add_dimension(product_dimension)
        cube.add_measure(sales_measure)
        cube.load_data(sample_data)

        # Dice by Year in [2024] and Product in [A, B]
        result = cube.dice({
            "Year": ["2024"],
            "Product": ["A", "B"]
        })

        assert len(result) == 2  # 2024-A and 2024-B
        assert all(result["Year"] == "2024")
        assert all(result["Product"].isin(["A", "B"]))

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_drill_down(self, cube, sample_data):
        """Test drill-down operation"""
        # Add hierarchical dimension
        time_dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter", "Month"]
        )
        cube.add_dimension(time_dim)
        cube.add_measure(Measure("Sales", AggregationType.SUM))

        cube.load_data(sample_data)

        # Drill down from Year to Product level
        result = cube.drill_down(
            cube.data,
            "Time",
            "Year",
            "Quarter"
        )

        assert isinstance(result, type(sample_data))

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_drill_up(self, cube, sample_data):
        """Test drill-up (roll-up) operation"""
        time_dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter"]
        )
        cube.add_dimension(time_dim)
        cube.add_measure(Measure("Sales", AggregationType.SUM))

        cube.load_data(sample_data)

        # Roll up from Product to Year
        result = cube.drill_up(
            cube.data,
            "Time",
            "Product",
            "Year"
        )

        assert isinstance(result, type(sample_data))

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_pivot_operation(self, cube, time_dimension, product_dimension,
                            sales_measure, sample_data):
        """Test pivot table creation"""
        cube.add_dimension(time_dimension)
        cube.add_dimension(product_dimension)
        cube.add_measure(sales_measure)
        cube.load_data(sample_data)

        # Create pivot: Year in rows, Product in columns, Sales as values
        result = cube.pivot(
            rows=["Year"],
            columns=["Product"],
            values="Sales",
            aggregation=AggregationType.SUM
        )

        assert isinstance(result, type(sample_data))

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_aggregate(self, cube, time_dimension, sales_measure, sample_data):
        """Test aggregation"""
        cube.add_dimension(time_dimension)
        cube.add_measure(sales_measure)
        cube.load_data(sample_data)

        # Aggregate by Year
        result = cube.aggregate(
            dimensions=["Year"],
            measure="Sales"
        )

        assert isinstance(result, type(sample_data))
        # Should group by Year
        assert len(result) <= len(sample_data)

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_slice_without_data_raises_error(self, cube, time_dimension):
        """Test that slice without data raises error"""
        cube.add_dimension(time_dimension)

        with pytest.raises(ValueError, match="no data"):
            cube.slice("Year", "2024")

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_dice_without_data_raises_error(self, cube):
        """Test that dice without data raises error"""
        with pytest.raises(ValueError, match="no data"):
            cube.dice({"Year": ["2024"]})

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_drill_down_invalid_dimension(self, cube, sample_data):
        """Test drill-down with invalid dimension"""
        cube.load_data(sample_data)

        with pytest.raises(ValueError, match="not found"):
            cube.drill_down(
                cube.data,
                "NonexistentDim",
                "Level1",
                "Level2"
            )

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_multiple_measures(self, cube, sample_data):
        """Test cube with multiple measures"""
        cube.add_measure(Measure("Sales", AggregationType.SUM))
        cube.add_measure(Measure("Quantity", AggregationType.SUM))

        cube.load_data(sample_data)

        assert len(cube.measures) == 2
        assert "Sales" in cube.measures
        assert "Quantity" in cube.measures


class TestMDXQueryEngine:
    """Test MDX Query Engine"""

    @pytest.fixture
    def cube_with_data(self):
        """Create cube with sample data"""
        if not PANDAS_AVAILABLE:
            return None

        import pandas as pd

        cube = OLAPCube("TestCube")

        # Add dimensions
        cube.add_dimension(Dimension("Year", ["Year"]))
        cube.add_dimension(Dimension("Product", ["Product"]))

        # Add measure
        cube.add_measure(Measure("Sales", AggregationType.SUM))

        # Load data
        data = pd.DataFrame({
            "Year": ["2023", "2024"],
            "Product": ["A", "B"],
            "Sales": [100, 200]
        })
        cube.load_data(data)

        return cube

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_initialization(self, cube_with_data):
        """Test engine initialization"""
        engine = MDXQueryEngine(cube_with_data)

        assert engine.cube == cube_with_data

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_query_execution(self, cube_with_data):
        """Test MDX query execution"""
        engine = MDXQueryEngine(cube_with_data)

        # Simple MDX-like query
        query = """
        SELECT [Sales] ON COLUMNS,
               [Year] ON ROWS
        FROM TestCube
        WHERE [Year = '2024']
        """

        result = engine.query(query)

        # Should return DataFrame
        assert result is not None


class TestCubeManager:
    """Test Cube Manager"""

    @pytest.fixture
    def manager(self):
        """Create cube manager"""
        return CubeManager()

    def test_initialization(self, manager):
        """Test manager initialization"""
        assert len(manager.cubes) == 0

    def test_create_cube(self, manager):
        """Test creating cube"""
        cube = manager.create_cube("MyCube")

        assert cube.name == "MyCube"
        assert "MyCube" in manager.cubes

    def test_get_cube(self, manager):
        """Test getting cube"""
        manager.create_cube("TestCube")

        cube = manager.get_cube("TestCube")

        assert cube is not None
        assert cube.name == "TestCube"

    def test_get_nonexistent_cube(self, manager):
        """Test getting nonexistent cube"""
        cube = manager.get_cube("NonexistentCube")

        assert cube is None

    def test_delete_cube(self, manager):
        """Test deleting cube"""
        manager.create_cube("ToDelete")

        assert "ToDelete" in manager.cubes

        manager.delete_cube("ToDelete")

        assert "ToDelete" not in manager.cubes

    def test_list_cubes(self, manager):
        """Test listing cubes"""
        manager.create_cube("Cube1")
        manager.create_cube("Cube2")
        manager.create_cube("Cube3")

        # Access cubes dictionary directly
        cubes = manager.cubes

        assert len(cubes) == 3
        assert "Cube1" in cubes
        assert "Cube2" in cubes
        assert "Cube3" in cubes

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_create_standard_sales_cube(self, manager):
        """Test creating standard sales cube"""
        cube = manager.create_sales_cube()

        assert cube.name == "Sales"
        assert len(cube.dimensions) > 0
        assert len(cube.measures) > 0
        # Check standard dimensions
        assert "Time" in cube.dimensions or "Geography" in cube.dimensions or "Product" in cube.dimensions
        # Check standard measures
        assert "Revenue" in cube.measures or "Units" in cube.measures or "Profit" in cube.measures


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_cube_manager(self):
        """Test getting singleton instance"""
        manager1 = get_cube_manager()
        manager2 = get_cube_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_manager_instance_type(self):
        """Test manager instance type"""
        manager = get_cube_manager()
        assert isinstance(manager, CubeManager)


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_olap_workflow(self):
        """Test complete OLAP workflow"""
        import pandas as pd

        # Create manager
        manager = CubeManager()

        # Create cube
        cube = manager.create_cube("SalesAnalysis")

        # Add dimensions
        time_dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter", "Month"]
        )
        cube.add_dimension(time_dim)

        product_dim = Dimension(
            name="Product",
            hierarchy=["Category", "Product"]
        )
        cube.add_dimension(product_dim)

        # Add measure
        sales_measure = Measure(
            name="Sales",
            aggregation=AggregationType.SUM,
            format="currency"
        )
        cube.add_measure(sales_measure)

        # Load data
        data = pd.DataFrame({
            "Year": ["2023", "2023", "2024", "2024"],
            "Product": ["A", "B", "A", "B"],
            "Category": ["Cat1", "Cat2", "Cat1", "Cat2"],
            "Sales": [100, 150, 200, 250]
        })
        cube.load_data(data)

        # Perform operations
        sliced = cube.slice("Year", "2024")
        assert len(sliced) == 2

        diced = cube.dice({"Year": ["2024"], "Product": ["A"]})
        assert len(diced) == 1

    def test_cube_with_aggregation_caching(self):
        """Test cube with aggregation caching"""
        import pandas as pd

        cube = OLAPCube("CachedCube")

        # Add components
        cube.add_dimension(Dimension("Year", ["Year"]))
        cube.add_measure(Measure("Sales", AggregationType.SUM))

        # Load data
        data = pd.DataFrame({
            "Year": ["2023", "2024", "2023", "2024"],
            "Sales": [100, 200, 150, 250]
        })
        cube.load_data(data)

        # First aggregation
        result1 = cube.aggregate(["Year"], "Sales")

        # Second aggregation (should use cache)
        result2 = cube.aggregate(["Year"], "Sales")

        # Results should be similar
        assert len(result1) == len(result2)

    def test_pivot_with_multiple_dimensions(self):
        """Test pivot with multiple row/column dimensions"""
        import pandas as pd

        cube = OLAPCube("MultiDimCube")

        # Setup
        cube.add_dimension(Dimension("Year", ["Year"]))
        cube.add_dimension(Dimension("Quarter", ["Quarter"]))
        cube.add_dimension(Dimension("Product", ["Product"]))
        cube.add_measure(Measure("Sales", AggregationType.SUM))

        # Data
        data = pd.DataFrame({
            "Year": ["2024", "2024", "2024", "2024"],
            "Quarter": ["Q1", "Q1", "Q2", "Q2"],
            "Product": ["A", "B", "A", "B"],
            "Sales": [100, 150, 200, 250]
        })
        cube.load_data(data)

        # Pivot
        result = cube.pivot(
            rows=["Year", "Quarter"],
            columns=["Product"],
            values="Sales"
        )

        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
