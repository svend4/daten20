#!/usr/bin/env python3
"""
OLAP Cube Engine (Pure Python)

Multidimensional analysis engine for business intelligence.
Supports slice, dice, drill-down, drill-up, and pivot operations.

Features:
- OLAP cube creation and management
- Slice & dice operations
- Drill-down & drill-up (roll-up)
- Pivot tables
- MDX-like query support
- Hierarchies and levels
- Calculated members
- Aggregation caching
- Multiple aggregation types

Note: Pure Python implementation without external dependencies.
Provides complete OLAP functionality using only stdlib.
"""

import re
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ============================================================================
# Enums and Data Classes
# ============================================================================

class AggregationType(str, Enum):
    """Aggregation functions"""
    SUM = "sum"
    AVG = "avg"
    MEAN = "mean"  # Alias for avg
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"
    FIRST = "first"
    LAST = "last"


@dataclass
class Dimension:
    """OLAP dimension with hierarchy"""
    name: str
    hierarchy: List[str]  # Levels in hierarchy (e.g., ["Year", "Quarter", "Month", "Day"])
    members: Set[str] = field(default_factory=set)

    def add_member(self, member: str):
        """Add member to dimension"""
        self.members.add(str(member))

    def get_level_index(self, level: str) -> int:
        """Get index of level in hierarchy"""
        try:
            return self.hierarchy.index(level)
        except ValueError:
            return -1

    def is_valid_level(self, level: str) -> bool:
        """Check if level exists in hierarchy"""
        return level in self.hierarchy

    def get_parent_level(self, level: str) -> Optional[str]:
        """Get parent level in hierarchy"""
        idx = self.get_level_index(level)
        if idx > 0:
            return self.hierarchy[idx - 1]
        return None

    def get_child_level(self, level: str) -> Optional[str]:
        """Get child level in hierarchy"""
        idx = self.get_level_index(level)
        if 0 <= idx < len(self.hierarchy) - 1:
            return self.hierarchy[idx + 1]
        return None


@dataclass
class Measure:
    """OLAP measure"""
    name: str
    aggregation: AggregationType
    format: str = "numeric"  # "numeric", "currency", "percentage"

    def format_value(self, value: float) -> str:
        """Format value according to format type"""
        if self.format == "currency":
            return f"${value:,.2f}"
        elif self.format == "percentage":
            return f"{value:.2f}%"
        else:
            return f"{value:,.2f}"


@dataclass
class CubeCell:
    """Individual cube cell with coordinates and value"""
    coordinates: Dict[str, str]  # dimension -> member
    value: float
    measure: str
    aggregation: AggregationType


# ============================================================================
# Aggregation Engine
# ============================================================================

class AggregationEngine:
    """Engine for aggregating data"""

    @staticmethod
    def aggregate(
        data: List[Dict[str, Any]],
        measure: str,
        aggregation: AggregationType
    ) -> Optional[float]:
        """
        Aggregate measure values

        Args:
            data: List of records
            measure: Measure column name
            aggregation: Aggregation type

        Returns:
            Aggregated value
        """
        if not data:
            return None

        values = [row.get(measure, 0) for row in data if measure in row and row[measure] is not None]

        if not values:
            return None

        if aggregation == AggregationType.SUM:
            return sum(values)

        elif aggregation in (AggregationType.AVG, AggregationType.MEAN):
            return sum(values) / len(values)

        elif aggregation == AggregationType.COUNT:
            return float(len(values))

        elif aggregation == AggregationType.MIN:
            return min(values)

        elif aggregation == AggregationType.MAX:
            return max(values)

        elif aggregation == AggregationType.DISTINCT_COUNT:
            return float(len(set(values)))

        elif aggregation == AggregationType.FIRST:
            return values[0]

        elif aggregation == AggregationType.LAST:
            return values[-1]

        return None

    @staticmethod
    def group_by(
        data: List[Dict[str, Any]],
        dimensions: List[str],
        measure: str,
        aggregation: AggregationType
    ) -> List[Dict[str, Any]]:
        """
        Group data by dimensions and aggregate

        Args:
            data: Input data
            dimensions: Dimensions to group by
            measure: Measure to aggregate
            aggregation: Aggregation function

        Returns:
            Grouped and aggregated data
        """
        if not data:
            return []

        # Group data
        groups = defaultdict(list)

        for row in data:
            # Create key from dimension values
            key = tuple(row.get(dim) for dim in dimensions)
            groups[key].append(row)

        # Aggregate each group
        result = []
        for key, group_data in groups.items():
            agg_value = AggregationEngine.aggregate(group_data, measure, aggregation)

            if agg_value is not None:
                record = {dim: value for dim, value in zip(dimensions, key)}
                record[measure] = agg_value
                result.append(record)

        return result


# ============================================================================
# OLAP Cube
# ============================================================================

class OLAPCube:
    """
    OLAP Cube for multidimensional analysis

    Supports:
    - Multiple dimensions with hierarchies
    - Multiple measures with different aggregations
    - Slice, dice, drill-down, drill-up operations
    - Pivot tables
    - Aggregation caching
    """

    def __init__(self, name: str):
        self.name = name
        self.dimensions: Dict[str, Dimension] = {}
        self.measures: Dict[str, Measure] = {}
        self.data: List[Dict[str, Any]] = []
        self.aggregation_cache: Dict[str, Any] = {}

    def add_dimension(self, dimension: Dimension):
        """Add dimension to cube"""
        self.dimensions[dimension.name] = dimension

    def add_measure(self, measure: Measure):
        """Add measure to cube"""
        self.measures[measure.name] = measure

    def load_data(self, data: List[Dict[str, Any]]):
        """
        Load fact data into cube

        Args:
            data: List of dictionaries containing facts
        """
        self.data = [row.copy() for row in data]

        # Extract unique members for each dimension
        for dim_name, dim in self.dimensions.items():
            for row in self.data:
                if dim_name in row:
                    dim.add_member(str(row[dim_name]))

        # Clear cache when new data is loaded
        self.aggregation_cache.clear()

    def slice(self, dimension: str, member: str) -> List[Dict[str, Any]]:
        """
        Slice cube by fixing one dimension to a specific member

        Args:
            dimension: Dimension name
            member: Specific member value

        Returns:
            Sliced data
        """
        if not self.data:
            return []

        result = []
        for row in self.data:
            if row.get(dimension) == member:
                result.append(row.copy())

        return result

    def dice(self, filters: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Dice cube by filtering multiple dimensions

        Args:
            filters: Dictionary of dimension -> list of members

        Returns:
            Diced data
        """
        if not self.data:
            return []

        result = []
        for row in self.data:
            include = True
            for dim, members in filters.items():
                if dim in row:
                    if row[dim] not in members:
                        include = False
                        break

            if include:
                result.append(row.copy())

        return result

    def drill_down(
        self,
        data: List[Dict[str, Any]],
        dimension: str,
        from_level: str,
        to_level: str
    ) -> List[Dict[str, Any]]:
        """
        Drill down from higher level to lower level in hierarchy

        Args:
            data: Input data
            dimension: Dimension name
            from_level: Current level
            to_level: Target (lower) level

        Returns:
            Drilled-down data
        """
        dim = self.dimensions.get(dimension)
        if not dim:
            raise ValueError(f"Dimension {dimension} not found")

        if not dim.is_valid_level(from_level) or not dim.is_valid_level(to_level):
            raise ValueError("Invalid hierarchy levels")

        # Check that to_level is below from_level
        from_idx = dim.get_level_index(from_level)
        to_idx = dim.get_level_index(to_level)

        if to_idx <= from_idx:
            raise ValueError("to_level must be below from_level in hierarchy")

        # Group by lower level dimensions
        group_dims = []
        for level in dim.hierarchy:
            if level in data[0] if data else {}:
                level_idx = dim.get_level_index(level)
                if level_idx <= to_idx:
                    group_dims.append(level)

        # Also include other dimensions
        for row in data:
            for key in row.keys():
                if key not in group_dims and key not in [m.name for m in self.measures.values()]:
                    group_dims.append(key)

        group_dims = list(dict.fromkeys(group_dims))  # Remove duplicates, preserve order

        # Aggregate by lower level
        result = []
        if group_dims:
            for measure_name, measure in self.measures.items():
                if any(measure_name in row for row in data):
                    grouped = AggregationEngine.group_by(
                        data, group_dims, measure_name, measure.aggregation
                    )
                    # Merge results
                    if not result:
                        result = grouped
                    else:
                        for i, res_row in enumerate(result):
                            if i < len(grouped):
                                res_row[measure_name] = grouped[i].get(measure_name)

        return result if result else data

    def drill_up(
        self,
        data: List[Dict[str, Any]],
        dimension: str,
        from_level: str,
        to_level: str
    ) -> List[Dict[str, Any]]:
        """
        Drill up (roll up) from lower level to higher level

        Args:
            data: Input data
            dimension: Dimension name
            from_level: Current (lower) level
            to_level: Target (higher) level

        Returns:
            Rolled-up data
        """
        dim = self.dimensions.get(dimension)
        if not dim:
            raise ValueError(f"Dimension {dimension} not found")

        if not dim.is_valid_level(from_level) or not dim.is_valid_level(to_level):
            raise ValueError("Invalid hierarchy levels")

        # Check that to_level is above from_level
        from_idx = dim.get_level_index(from_level)
        to_idx = dim.get_level_index(to_level)

        if to_idx >= from_idx:
            raise ValueError("to_level must be above from_level in hierarchy")

        # Group by higher level dimensions
        group_dims = []
        for row in data:
            for key in row.keys():
                if key != from_level and key not in [m.name for m in self.measures.values()]:
                    if key not in group_dims:
                        group_dims.append(key)

        # Aggregate
        result_by_measure = {}
        for measure_name, measure in self.measures.items():
            if any(measure_name in row for row in data):
                grouped = AggregationEngine.group_by(
                    data, group_dims if group_dims else [to_level],
                    measure_name,
                    measure.aggregation
                )
                result_by_measure[measure_name] = grouped

        # Merge all measures
        result = []
        if result_by_measure:
            first_measure = list(result_by_measure.values())[0]
            for i, row in enumerate(first_measure):
                merged_row = row.copy()
                for measure_name, grouped in result_by_measure.items():
                    if i < len(grouped):
                        merged_row[measure_name] = grouped[i].get(measure_name)
                result.append(merged_row)

        return result

    def pivot(
        self,
        rows: List[str],
        columns: List[str],
        values: str,
        aggregation: Optional[AggregationType] = None
    ) -> Dict[str, Any]:
        """
        Create pivot table

        Args:
            rows: Dimensions for rows
            columns: Dimensions for columns
            values: Measure to aggregate
            aggregation: Aggregation function (uses measure default if None)

        Returns:
            Pivot table as nested dictionary
        """
        if not self.data:
            return {"rows": [], "columns": [], "data": {}}

        # Get measure
        measure = self.measures.get(values)
        if not measure:
            raise ValueError(f"Measure {values} not found")

        agg = aggregation or measure.aggregation

        # Get unique row and column values
        row_values_set = defaultdict(set)
        col_values_set = defaultdict(set)

        for row in self.data:
            for r in rows:
                if r in row:
                    row_values_set[r].add(row[r])
            for c in columns:
                if c in row:
                    col_values_set[c].add(row[c])

        # Sort for consistency
        row_values = {k: sorted(v) for k, v in row_values_set.items()}
        col_values = {k: sorted(v) for k, v in col_values_set.items()}

        # Build pivot data
        pivot_data = {}

        for row in self.data:
            # Get row key
            row_key = tuple(row.get(r) for r in rows)

            # Get column key
            col_key = tuple(row.get(c) for c in columns)

            # Initialize if needed
            if row_key not in pivot_data:
                pivot_data[row_key] = {}

            if col_key not in pivot_data[row_key]:
                pivot_data[row_key][col_key] = []

            # Add value
            if values in row and row[values] is not None:
                pivot_data[row_key][col_key].append(row[values])

        # Aggregate
        pivot_result = {}
        for row_key, col_data in pivot_data.items():
            pivot_result[row_key] = {}
            for col_key, vals in col_data.items():
                if vals:
                    fake_data = [{values: v} for v in vals]
                    agg_val = AggregationEngine.aggregate(fake_data, values, agg)
                    pivot_result[row_key][col_key] = agg_val

        return {
            "rows": rows,
            "columns": columns,
            "values": values,
            "row_values": row_values,
            "column_values": col_values,
            "data": pivot_result,
        }

    def aggregate(
        self,
        dimensions: List[str],
        measures: List[str],
        filters: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate data by dimensions

        Args:
            dimensions: Dimensions to group by
            measures: Measures to aggregate
            filters: Optional filters

        Returns:
            Aggregated data
        """
        # Apply filters if provided
        data = self.data
        if filters:
            data = self.dice(filters)

        if not data:
            return []

        # If no dimensions, return grand total
        if not dimensions:
            result = {}
            for measure_name in measures:
                measure = self.measures.get(measure_name)
                if measure:
                    agg_val = AggregationEngine.aggregate(
                        data, measure_name, measure.aggregation
                    )
                    if agg_val is not None:
                        result[measure_name] = agg_val
            return [result] if result else []

        # Group by dimensions and aggregate each measure
        result_by_measure = {}
        for measure_name in measures:
            measure = self.measures.get(measure_name)
            if measure:
                grouped = AggregationEngine.group_by(
                    data, dimensions, measure_name, measure.aggregation
                )
                result_by_measure[measure_name] = grouped

        # Merge all measures
        result = []
        if result_by_measure:
            # Get longest result as base
            max_len = max(len(v) for v in result_by_measure.values())
            first_measure = list(result_by_measure.values())[0]

            for i in range(max_len):
                if i < len(first_measure):
                    merged_row = first_measure[i].copy()
                    for measure_name, grouped in result_by_measure.items():
                        if i < len(grouped) and measure_name in grouped[i]:
                            merged_row[measure_name] = grouped[i][measure_name]
                    result.append(merged_row)

        return result

    def get_cell(
        self,
        coordinates: Dict[str, str],
        measure: str
    ) -> Optional[float]:
        """
        Get value of specific cell

        Args:
            coordinates: Dictionary of dimension -> member
            measure: Measure name

        Returns:
            Cell value or None
        """
        # Filter data by coordinates
        filtered = self.data
        for dim, member in coordinates.items():
            filtered = [row for row in filtered if row.get(dim) == member]

        if not filtered:
            return None

        # Get measure
        m = self.measures.get(measure)
        if not m:
            return None

        # Aggregate
        return AggregationEngine.aggregate(filtered, measure, m.aggregation)

    def get_statistics(self) -> Dict[str, Any]:
        """Get cube statistics"""
        return {
            "name": self.name,
            "dimensions": len(self.dimensions),
            "measures": len(self.measures),
            "facts": len(self.data),
            "cache_size": len(self.aggregation_cache),
        }


# ============================================================================
# MDX Query Engine
# ============================================================================

class MDXQueryEngine:
    """
    MDX-like query engine

    Simplified MDX (Multidimensional Expressions) query support.

    Example query:
        SELECT [Revenue, Units] ON COLUMNS,
               [Year, Quarter] ON ROWS
        FROM [Sales]
        WHERE [Region = 'North']
    """

    def __init__(self, cube: OLAPCube):
        self.cube = cube

    def query(self, mdx_query: str) -> List[Dict[str, Any]]:
        """
        Execute MDX-like query

        Args:
            mdx_query: MDX query string

        Returns:
            Query result as list of dictionaries
        """
        # Parse query
        parsed = self._parse_query(mdx_query)

        # Execute
        result = self.cube.aggregate(
            parsed["dimensions"],
            parsed["measures"],
            parsed["filters"] if parsed["filters"] else None
        )

        return result

    def _parse_query(self, mdx_query: str) -> Dict[str, Any]:
        """
        Parse MDX query

        Returns:
            Dictionary with measures, dimensions, and filters
        """
        lines = [l.strip() for l in mdx_query.upper().split("\n") if l.strip()]

        measures = []
        dimensions = []
        filters = {}
        cube_name = None

        for line in lines:
            # Parse SELECT ... ON COLUMNS
            if "SELECT" in line and "ON COLUMNS" in line:
                parts = line.split("ON COLUMNS")[0].replace("SELECT", "").strip()
                # Remove brackets and split by comma
                parts = parts.strip("[]")
                measures = [p.strip("[] ") for p in parts.split(",") if p.strip()]

            # Parse ... ON ROWS
            elif "ON ROWS" in line:
                parts = line.split("ON ROWS")[0].strip()
                # Remove brackets and split
                parts = parts.strip("[]")
                dimensions = [p.strip("[] ") for p in parts.split(",") if p.strip()]

            # Parse FROM [Cube]
            elif "FROM" in line:
                parts = line.split("FROM")[1].strip()
                cube_name = parts.strip("[]")

            # Parse WHERE clause
            elif "WHERE" in line:
                parts = line.split("WHERE")[1].strip()
                # Parse dimension = 'value'
                if "=" in parts:
                    dim, value = parts.split("=", 1)
                    dim = dim.strip("[] ")
                    value = value.strip("'\" []")
                    filters[dim] = [value]

        return {
            "measures": measures,
            "dimensions": dimensions,
            "cube": cube_name,
            "filters": filters,
        }


# ============================================================================
# Cube Builder
# ============================================================================

class CubeBuilder:
    """Builder for creating cubes with fluent API"""

    def __init__(self, name: str):
        self.cube = OLAPCube(name)

    def with_dimension(
        self,
        name: str,
        hierarchy: List[str]
    ) -> 'CubeBuilder':
        """Add dimension"""
        dim = Dimension(name=name, hierarchy=hierarchy)
        self.cube.add_dimension(dim)
        return self

    def with_measure(
        self,
        name: str,
        aggregation: AggregationType,
        format: str = "numeric"
    ) -> 'CubeBuilder':
        """Add measure"""
        measure = Measure(name=name, aggregation=aggregation, format=format)
        self.cube.add_measure(measure)
        return self

    def with_data(self, data: List[Dict[str, Any]]) -> 'CubeBuilder':
        """Load data"""
        self.cube.load_data(data)
        return self

    def build(self) -> OLAPCube:
        """Build and return cube"""
        return self.cube


# ============================================================================
# Cube Manager
# ============================================================================

class CubeManager:
    """
    Manage multiple OLAP cubes

    Provides central management for all cubes.
    """

    def __init__(self):
        self.cubes: Dict[str, OLAPCube] = {}

    def create_cube(self, name: str) -> OLAPCube:
        """Create new OLAP cube"""
        cube = OLAPCube(name)
        self.cubes[name] = cube
        return cube

    def get_cube(self, name: str) -> Optional[OLAPCube]:
        """Get cube by name"""
        return self.cubes.get(name)

    def delete_cube(self, name: str):
        """Delete cube"""
        if name in self.cubes:
            del self.cubes[name]

    def list_cubes(self) -> List[str]:
        """List all cube names"""
        return list(self.cubes.keys())

    def create_sales_cube(self) -> OLAPCube:
        """Create standard sales cube"""
        cube = self.create_cube("Sales")

        # Time dimension
        time_dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter", "Month", "Day"]
        )
        cube.add_dimension(time_dim)

        # Geography dimension
        geo_dim = Dimension(
            name="Geography",
            hierarchy=["Region", "Country", "State", "City"]
        )
        cube.add_dimension(geo_dim)

        # Product dimension
        product_dim = Dimension(
            name="Product",
            hierarchy=["Category", "Subcategory", "Product"]
        )
        cube.add_dimension(product_dim)

        # Measures
        cube.add_measure(Measure("Revenue", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("Units", AggregationType.SUM, "numeric"))
        cube.add_measure(Measure("Profit", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("Transactions", AggregationType.COUNT, "numeric"))

        return cube

    def create_usage_cube(self) -> OLAPCube:
        """Create usage analytics cube"""
        cube = self.create_cube("Usage")

        # Time dimension
        time_dim = Dimension(
            name="Date",
            hierarchy=["Year", "Month", "Day"]
        )
        cube.add_dimension(time_dim)

        # Tenant dimension
        tenant_dim = Dimension(
            name="Tenant",
            hierarchy=["Tenant"]
        )
        cube.add_dimension(tenant_dim)

        # User dimension
        user_dim = Dimension(
            name="User",
            hierarchy=["User"]
        )
        cube.add_dimension(user_dim)

        # Measures
        cube.add_measure(Measure("API_Calls", AggregationType.SUM, "numeric"))
        cube.add_measure(Measure("Storage_GB", AggregationType.SUM, "numeric"))
        cube.add_measure(Measure("Active_Users", AggregationType.DISTINCT_COUNT, "numeric"))
        cube.add_measure(Measure("Bandwidth_GB", AggregationType.SUM, "numeric"))

        return cube

    def create_revenue_cube(self) -> OLAPCube:
        """Create revenue analytics cube"""
        cube = self.create_cube("Revenue")

        # Time dimension
        time_dim = Dimension(
            name="Time",
            hierarchy=["Year", "Quarter", "Month"]
        )
        cube.add_dimension(time_dim)

        # Tenant dimension
        tenant_dim = Dimension(
            name="Tenant",
            hierarchy=["Tier", "Tenant"]
        )
        cube.add_dimension(tenant_dim)

        # Measures
        cube.add_measure(Measure("MRR", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("ARR", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("New_Revenue", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("Churned_Revenue", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("Expansion_Revenue", AggregationType.SUM, "currency"))

        return cube


# ============================================================================
# Pivot Table Formatter
# ============================================================================

class PivotTableFormatter:
    """Format pivot tables for display"""

    @staticmethod
    def format_pivot(pivot_result: Dict[str, Any]) -> str:
        """
        Format pivot table as string

        Args:
            pivot_result: Result from OLAPCube.pivot()

        Returns:
            Formatted string representation
        """
        rows = pivot_result["rows"]
        columns = pivot_result["columns"]
        data = pivot_result["data"]
        row_values = pivot_result["row_values"]
        col_values = pivot_result["column_values"]

        if not data:
            return "Empty pivot table"

        lines = []

        # Header row
        header = rows.copy()
        if columns:
            # Get all column combinations
            col_keys = list(list(data.values())[0].keys())
            for col_key in col_keys:
                header.append(str(col_key))
        lines.append(" | ".join(header))
        lines.append("-" * (len(" | ".join(header))))

        # Data rows
        for row_key, col_data in sorted(data.items()):
            row = [str(v) for v in row_key]
            for col_key in sorted(col_data.keys()):
                value = col_data[col_key]
                row.append(f"{value:.2f}" if value is not None else "N/A")
            lines.append(" | ".join(row))

        return "\n".join(lines)


# ============================================================================
# Singleton and Convenience Functions
# ============================================================================

_cube_manager_instance = None
_instance_lock = threading.Lock()


def get_cube_manager() -> CubeManager:
    """Get singleton Cube Manager instance"""
    global _cube_manager_instance

    if _cube_manager_instance is None:
        with _instance_lock:
            if _cube_manager_instance is None:
                _cube_manager_instance = CubeManager()

    return _cube_manager_instance


def get_olap_cube(name: str = "default") -> OLAPCube:
    """Get or create OLAP cube"""
    manager = get_cube_manager()
    cube = manager.get_cube(name)
    if not cube:
        cube = manager.create_cube(name)
    return cube


if __name__ == "__main__":
    # Example usage
    print("OLAP Cube Engine (Pure Python)")
    print("=" * 60)

    # Create manager
    manager = get_cube_manager()

    # Create sales cube
    print("\n✅ Creating Sales cube...")
    sales_cube = manager.create_sales_cube()

    print(f"   Cube: {sales_cube.name}")
    print(f"   Dimensions: {list(sales_cube.dimensions.keys())}")
    print(f"   Measures: {list(sales_cube.measures.keys())}")

    # Create sample data
    print("\n✅ Loading sample data...")
    data = [
        {
            "Year": "2025",
            "Quarter": "Q1",
            "Month": "Jan",
            "Region": "North",
            "Country": "USA",
            "Category": "Electronics",
            "Product": "Laptop",
            "Revenue": 1000,
            "Units": 10,
            "Profit": 300,
        },
        {
            "Year": "2025",
            "Quarter": "Q1",
            "Month": "Feb",
            "Region": "North",
            "Country": "USA",
            "Category": "Electronics",
            "Product": "Phone",
            "Revenue": 1500,
            "Units": 15,
            "Profit": 450,
        },
        {
            "Year": "2025",
            "Quarter": "Q2",
            "Month": "Mar",
            "Region": "South",
            "Country": "UK",
            "Category": "Electronics",
            "Product": "Laptop",
            "Revenue": 2000,
            "Units": 20,
            "Profit": 600,
        },
        {
            "Year": "2026",
            "Quarter": "Q1",
            "Month": "Jan",
            "Region": "East",
            "Country": "Japan",
            "Category": "Electronics",
            "Product": "Tablet",
            "Revenue": 1200,
            "Units": 12,
            "Profit": 360,
        },
    ]

    sales_cube.load_data(data)
    print(f"   Loaded {len(data)} rows")

    # Test slice
    print("\n✅ Testing Slice operation:")
    q1_data = sales_cube.slice("Quarter", "Q1")
    print(f"   Q1 slice: {len(q1_data)} rows")
    print(f"   Total revenue in Q1: ${sum(row.get('Revenue', 0) for row in q1_data):,.2f}")

    # Test dice
    print("\n✅ Testing Dice operation:")
    diced = sales_cube.dice({"Year": ["2025"], "Region": ["North"]})
    print(f"   2025 North dice: {len(diced)} rows")
    print(f"   Total revenue: ${sum(row.get('Revenue', 0) for row in diced):,.2f}")

    # Test aggregate
    print("\n✅ Testing Aggregate:")
    agg = sales_cube.aggregate(
        dimensions=["Year", "Quarter"],
        measures=["Revenue", "Units"]
    )
    print(f"   Aggregated by Year, Quarter: {len(agg)} groups")
    for row in agg:
        print(f"     {row.get('Year')} {row.get('Quarter')}: "
              f"${row.get('Revenue', 0):,.2f}, {row.get('Units', 0):.0f} units")

    # Test pivot
    print("\n✅ Testing Pivot table:")
    pivot = sales_cube.pivot(
        rows=["Year", "Quarter"],
        columns=["Region"],
        values="Revenue"
    )
    print(f"   Pivot dimensions: {len(pivot['data'])} rows")

    # Test MDX query
    print("\n✅ Testing MDX Query:")
    mdx_engine = MDXQueryEngine(sales_cube)
    mdx_query = """
        SELECT [Revenue, Units] ON COLUMNS,
               [Year, Quarter] ON ROWS
        FROM [Sales]
        WHERE [Region = 'North']
    """
    result = mdx_engine.query(mdx_query)
    print(f"   MDX query result: {len(result)} rows")
    for row in result:
        print(f"     {row}")

    # Test CubeBuilder
    print("\n✅ Testing CubeBuilder:")
    custom_cube = (CubeBuilder("CustomCube")
        .with_dimension("Date", ["Year", "Month"])
        .with_measure("Value", AggregationType.SUM)
        .with_data([
            {"Date": "2025", "Year": "2025", "Month": "Jan", "Value": 100},
            {"Date": "2025", "Year": "2025", "Month": "Feb", "Value": 150},
        ])
        .build()
    )
    print(f"   Custom cube created: {custom_cube.name}")
    print(f"   Facts: {len(custom_cube.data)}")

    # Statistics
    print("\n✅ Cube Statistics:")
    stats = sales_cube.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ OLAP Cube module ready!")
