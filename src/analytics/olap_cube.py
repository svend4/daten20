#!/usr/bin/env python3
"""
OLAP Cube Engine

Multidimensional analysis engine for business intelligence.
Supports slice, dice, drill-down, drill-up, and pivot operations.

Key Features:
- OLAP cube creation and management
- Slice & dice operations
- Drill-down & drill-up (roll-up)
- Pivot tables
- MDX-like query support
- Hierarchies and levels
- Calculated members
- Aggregation caching

Dependencies:
- pandas, numpy (for data processing)
"""

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. OLAP features limited.")


class AggregationType(str, Enum):
    """Aggregation functions"""

    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"


@dataclass
class Dimension:
    """OLAP dimension"""

    name: str
    hierarchy: List[str]  # Levels in hierarchy (e.g., ["Year", "Quarter", "Month", "Day"])
    members: List[str] = field(default_factory=list)


@dataclass
class Measure:
    """OLAP measure"""

    name: str
    aggregation: AggregationType
    format: str = "numeric"  # "numeric", "currency", "percentage"


@dataclass
class CubeCell:
    """Individual cube cell with coordinates and value"""

    coordinates: Dict[str, str]  # dimension -> member
    value: float
    aggregation: AggregationType


class OLAPCube:
    """
    OLAP Cube for multidimensional analysis

    Supports:
    - Multiple dimensions
    - Multiple measures
    - Hierarchical dimensions
    - Aggregations
    - Slicing, dicing, drilling
    """

    def __init__(self, name: str):
        self.name = name
        self.dimensions: Dict[str, Dimension] = {}
        self.measures: Dict[str, Measure] = {}
        self.data: Optional[pd.DataFrame] = None
        self.aggregation_cache: Dict[str, Any] = {}

    def add_dimension(self, dimension: Dimension):
        """Add dimension to cube"""
        self.dimensions[dimension.name] = dimension

    def add_measure(self, measure: Measure):
        """Add measure to cube"""
        self.measures[measure.name] = measure

    def load_data(self, data: pd.DataFrame):
        """Load fact data into cube"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required for OLAP operations")

        self.data = data.copy()

        # Extract unique members for each dimension
        for dim_name, dim in self.dimensions.items():
            if dim_name in data.columns:
                unique_members = data[dim_name].unique().tolist()
                dim.members = [str(m) for m in unique_members]

    def slice(self, dimension: str, member: str) -> pd.DataFrame:
        """
        Slice cube by fixing one dimension to a specific member

        Args:
            dimension: Dimension name
            member: Specific member value

        Returns:
            Sliced DataFrame
        """
        if self.data is None:
            raise ValueError("Cube has no data loaded")

        return self.data[self.data[dimension] == member].copy()

    def dice(self, filters: Dict[str, List[str]]) -> pd.DataFrame:
        """
        Dice cube by filtering multiple dimensions

        Args:
            filters: Dictionary of dimension -> list of members

        Returns:
            Diced DataFrame
        """
        if self.data is None:
            raise ValueError("Cube has no data loaded")

        result = self.data.copy()

        for dim, members in filters.items():
            if dim in result.columns:
                result = result[result[dim].isin(members)]

        return result

    def drill_down(self, data: pd.DataFrame, dimension: str, from_level: str, to_level: str) -> pd.DataFrame:
        """
        Drill down from higher level to lower level in hierarchy

        Args:
            data: Input DataFrame
            dimension: Dimension name
            from_level: Current level
            to_level: Target (lower) level

        Returns:
            Drilled-down DataFrame
        """
        dim = self.dimensions.get(dimension)
        if not dim:
            raise ValueError(f"Dimension {dimension} not found")

        # Verify levels exist in hierarchy
        if from_level not in dim.hierarchy or to_level not in dim.hierarchy:
            raise ValueError("Invalid hierarchy levels")

        # Group by lower level
        measure_cols = [m.name for m in self.measures.values()]
        group_cols = [c for c in data.columns if c in dim.hierarchy and c != from_level]

        if to_level in data.columns:
            group_cols.append(to_level)

        agg_dict = {m: "sum" for m in measure_cols if m in data.columns}

        if group_cols:
            result = data.groupby(group_cols).agg(agg_dict).reset_index()
        else:
            result = data

        return result

    def drill_up(self, data: pd.DataFrame, dimension: str, from_level: str, to_level: str) -> pd.DataFrame:
        """
        Drill up (roll up) from lower level to higher level

        Args:
            data: Input DataFrame
            dimension: Dimension name
            from_level: Current (lower) level
            to_level: Target (higher) level

        Returns:
            Rolled-up DataFrame
        """
        dim = self.dimensions.get(dimension)
        if not dim:
            raise ValueError(f"Dimension {dimension} not found")

        # Group by higher level
        measure_cols = [m.name for m in self.measures.values()]
        group_cols = [c for c in data.columns if c != from_level]

        if to_level in data.columns and to_level not in group_cols:
            group_cols.append(to_level)

        agg_dict = {}
        for m_name, m in self.measures.items():
            if m_name in data.columns:
                agg_dict[m_name] = m.aggregation.value

        if group_cols:
            result = data.groupby(group_cols).agg(agg_dict).reset_index()
        else:
            result = data

        return result

    def pivot(
        self, rows: List[str], columns: List[str], values: str, aggregation: AggregationType = AggregationType.SUM
    ) -> pd.DataFrame:
        """
        Create pivot table

        Args:
            rows: Dimensions for rows
            columns: Dimensions for columns
            values: Measure to aggregate
            aggregation: Aggregation function

        Returns:
            Pivot table as DataFrame
        """
        if self.data is None:
            raise ValueError("Cube has no data loaded")

        pivot = pd.pivot_table(
            self.data, index=rows, columns=columns, values=values, aggfunc=aggregation.value, fill_value=0
        )

        return pivot

    def aggregate(
        self, dimensions: List[str], measures: List[str], filters: Optional[Dict[str, List[str]]] = None
    ) -> pd.DataFrame:
        """
        Aggregate data by dimensions

        Args:
            dimensions: Dimensions to group by
            measures: Measures to aggregate
            filters: Optional filters

        Returns:
            Aggregated DataFrame
        """
        if self.data is None:
            raise ValueError("Cube has no data loaded")

        # Apply filters if provided
        data = self.data.copy()
        if filters:
            for dim, members in filters.items():
                if dim in data.columns:
                    data = data[data[dim].isin(members)]

        # Create aggregation dict
        agg_dict = {}
        for measure in measures:
            m = self.measures.get(measure)
            if m and measure in data.columns:
                agg_dict[measure] = m.aggregation.value

        # Group and aggregate
        if dimensions:
            result = data.groupby(dimensions).agg(agg_dict).reset_index()
        else:
            # Grand total
            result = pd.DataFrame([{m: data[m].agg(agg_dict[m]) for m in agg_dict}])

        return result

    def get_cell(self, coordinates: Dict[str, str], measure: str) -> Optional[float]:
        """
        Get value of specific cell

        Args:
            coordinates: Dictionary of dimension -> member
            measure: Measure name

        Returns:
            Cell value or None
        """
        if self.data is None:
            return None

        # Filter data by coordinates
        data = self.data.copy()
        for dim, member in coordinates.items():
            if dim in data.columns:
                data = data[data[dim] == member]

        if len(data) == 0:
            return None

        # Get measure value
        m = self.measures.get(measure)
        if not m or measure not in data.columns:
            return None

        # Aggregate
        if m.aggregation == AggregationType.SUM:
            return float(data[measure].sum())
        elif m.aggregation == AggregationType.AVG:
            return float(data[measure].mean())
        elif m.aggregation == AggregationType.COUNT:
            return float(len(data))
        elif m.aggregation == AggregationType.MIN:
            return float(data[measure].min())
        elif m.aggregation == AggregationType.MAX:
            return float(data[measure].max())
        elif m.aggregation == AggregationType.DISTINCT_COUNT:
            return float(data[measure].nunique())

        return None


class MDXQueryEngine:
    """
    MDX-like query engine

    Simplified MDX (Multidimensional Expressions) query support.
    """

    def __init__(self, cube: OLAPCube):
        self.cube = cube

    def query(self, mdx_query: str) -> pd.DataFrame:
        """
        Execute MDX-like query

        Simplified syntax:
        SELECT [Measure] ON COLUMNS, [Dimension1, Dimension2] ON ROWS
        FROM [Cube]
        WHERE [Dimension3 = 'Value']

        Args:
            mdx_query: MDX query string

        Returns:
            Query result as DataFrame
        """
        # This is a very simplified MDX parser
        # Full MDX support would require a proper parser

        # Extract components
        lines = [l.strip() for l in mdx_query.upper().split("\n")]

        measures = []
        dimensions = []
        filters = {}

        for line in lines:
            if "SELECT" in line and "ON COLUMNS" in line:
                # Extract measures
                parts = line.split("ON COLUMNS")[0].replace("SELECT", "").strip()
                measures = [p.strip("[] ") for p in parts.split(",")]

            elif "ON ROWS" in line:
                # Extract dimensions
                parts = line.split("ON ROWS")[0].split(",")
                dimensions = [p.strip("[] ") for p in parts if p.strip()]

            elif "WHERE" in line:
                # Extract filters
                parts = line.split("WHERE")[1].strip()
                # Simple parsing: Dimension = 'Value'
                if "=" in parts:
                    dim, value = parts.split("=")
                    dim = dim.strip("[] ")
                    value = value.strip("'\" ")
                    filters[dim] = [value]

        # Execute query
        result = self.cube.aggregate(dimensions, measures, filters if filters else None)

        return result


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

    def create_sales_cube(self) -> OLAPCube:
        """Create standard sales cube"""
        cube = self.create_cube("Sales")

        # Time dimension
        time_dim = Dimension(name="Time", hierarchy=["Year", "Quarter", "Month", "Day"])
        cube.add_dimension(time_dim)

        # Geography dimension
        geo_dim = Dimension(name="Geography", hierarchy=["Region", "Country", "State", "City"])
        cube.add_dimension(geo_dim)

        # Product dimension
        product_dim = Dimension(name="Product", hierarchy=["Category", "Subcategory", "Product"])
        cube.add_dimension(product_dim)

        # Measures
        cube.add_measure(Measure("Revenue", AggregationType.SUM, "currency"))
        cube.add_measure(Measure("Units", AggregationType.SUM, "numeric"))
        cube.add_measure(Measure("Profit", AggregationType.SUM, "currency"))

        return cube

    def create_usage_cube(self) -> OLAPCube:
        """Create usage analytics cube"""
        cube = self.create_cube("Usage")

        # Time dimension
        time_dim = Dimension(name="Date", hierarchy=["Year", "Month", "Day"])
        cube.add_dimension(time_dim)

        # Tenant dimension
        tenant_dim = Dimension(name="Tenant", hierarchy=["Tenant"])
        cube.add_dimension(tenant_dim)

        # Measures
        cube.add_measure(Measure("API_Calls", AggregationType.SUM))
        cube.add_measure(Measure("Storage_GB", AggregationType.SUM))
        cube.add_measure(Measure("Active_Users", AggregationType.DISTINCT_COUNT))

        return cube


# Singleton instance
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


if __name__ == "__main__":
    # Example usage
    manager = get_cube_manager()

    # Create sales cube
    sales_cube = manager.create_sales_cube()
    print(f"Created cube: {sales_cube.name}")
    print(f"Dimensions: {list(sales_cube.dimensions.keys())}")
    print(f"Measures: {list(sales_cube.measures.keys())}")

    # Create sample data
    if PANDAS_AVAILABLE:
        data = pd.DataFrame(
            {
                "Year": ["2025", "2025", "2025", "2026"],
                "Quarter": ["Q1", "Q1", "Q2", "Q1"],
                "Month": ["Jan", "Feb", "Mar", "Jan"],
                "Region": ["North", "North", "South", "East"],
                "Country": ["USA", "USA", "UK", "Japan"],
                "Product": ["A", "B", "A", "C"],
                "Revenue": [1000, 1500, 2000, 1200],
                "Units": [10, 15, 20, 12],
                "Profit": [300, 450, 600, 360],
            }
        )

        sales_cube.load_data(data)
        print(f"\nLoaded {len(data)} rows into cube")

        # Slice
        q1_data = sales_cube.slice("Quarter", "Q1")
        print(f"\nQ1 slice: {len(q1_data)} rows")

        # Pivot
        pivot = sales_cube.pivot(
            rows=["Year", "Quarter"], columns=["Region"], values="Revenue", aggregation=AggregationType.SUM
        )
        print("\nPivot table:")
        print(pivot)

    print("\nOLAP Cube module loaded successfully!")
