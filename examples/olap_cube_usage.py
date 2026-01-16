#!/usr/bin/env python3
"""
OLAP Cube Usage Examples

Demonstrates how to use the OLAP Cube Engine for:
- Multidimensional data analysis
- Slice & dice operations
- Drill-down & drill-up (roll-up)
- Pivot tables
- MDX-like queries

Requirements:
- Basic: Works without pandas (cube structure only)
- Full features: Install pandas for data operations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analytics.olap_cube import (
    AggregationType,
    Dimension,
    Measure,
    OLAPCube,
    MDXQueryEngine,
    CubeManager,
    get_cube_manager,
    PANDAS_AVAILABLE,
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subsection(title: str):
    """Print subsection header"""
    print(f"\n--- {title} ---\n")


def example_1_cube_structure():
    """Example 1: Creating OLAP Cube Structure"""
    print_section("Example 1: OLAP Cube Structure")

    # Create cube
    cube = OLAPCube("SalesAnalysis")
    print(f"Created cube: {cube.name}")

    # Add dimensions with hierarchies
    print_subsection("Adding Dimensions")

    time_dim = Dimension(
        name="Time",
        hierarchy=["Year", "Quarter", "Month", "Day"]
    )
    cube.add_dimension(time_dim)
    print(f"✓ Time dimension: {' > '.join(time_dim.hierarchy)}")

    geo_dim = Dimension(
        name="Geography",
        hierarchy=["Region", "Country", "State", "City"]
    )
    cube.add_dimension(geo_dim)
    print(f"✓ Geography dimension: {' > '.join(geo_dim.hierarchy)}")

    product_dim = Dimension(
        name="Product",
        hierarchy=["Category", "Subcategory", "Product"]
    )
    cube.add_dimension(product_dim)
    print(f"✓ Product dimension: {' > '.join(product_dim.hierarchy)}")

    # Add measures
    print_subsection("Adding Measures")

    revenue = Measure(
        name="Revenue",
        aggregation=AggregationType.SUM,
        format="currency"
    )
    cube.add_measure(revenue)
    print(f"✓ Revenue (SUM, currency)")

    units = Measure(
        name="Units",
        aggregation=AggregationType.SUM,
        format="numeric"
    )
    cube.add_measure(units)
    print(f"✓ Units (SUM, numeric)")

    profit = Measure(
        name="Profit",
        aggregation=AggregationType.SUM,
        format="currency"
    )
    cube.add_measure(profit)
    print(f"✓ Profit (SUM, currency)")

    print(f"\nCube Summary:")
    print(f"  Dimensions: {len(cube.dimensions)}")
    print(f"  Measures: {len(cube.measures)}")
    print(f"  Status: Ready for data loading")


def example_2_slice_and_dice():
    """Example 2: Slice & Dice Operations"""
    print_section("Example 2: Slice & Dice Operations")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available. Skipping data operations.")
        print("   Install with: pip install pandas numpy")
        return

    import pandas as pd

    # Create and setup cube
    cube = OLAPCube("Sales")
    cube.add_dimension(Dimension("Year", ["Year"]))
    cube.add_dimension(Dimension("Product", ["Product"]))
    cube.add_dimension(Dimension("Region", ["Region"]))
    cube.add_measure(Measure("Sales", AggregationType.SUM))

    # Sample data
    data = pd.DataFrame({
        "Year": ["2023", "2023", "2023", "2024", "2024", "2024"],
        "Product": ["A", "B", "C", "A", "B", "C"],
        "Region": ["North", "South", "North", "South", "North", "South"],
        "Sales": [100, 150, 200, 250, 300, 350]
    })

    cube.load_data(data)
    print("Loaded sample sales data:")
    print(data.to_string(index=False))

    # Slice operation
    print_subsection("Slice: Filter by Year = 2024")

    sliced = cube.slice("Year", "2024")
    print(sliced.to_string(index=False))
    print(f"\nTotal records: {len(sliced)}")

    # Dice operation
    print_subsection("Dice: Year = 2024 AND Product in [A, B]")

    diced = cube.dice({
        "Year": ["2024"],
        "Product": ["A", "B"]
    })
    print(diced.to_string(index=False))
    print(f"\nTotal records: {len(diced)}")

    # Multiple dice
    print_subsection("Dice: Year = 2024 AND Region = North")

    diced2 = cube.dice({
        "Year": ["2024"],
        "Region": ["North"]
    })
    print(diced2.to_string(index=False))


def example_3_drill_operations():
    """Example 3: Drill-Down & Roll-Up Operations"""
    print_section("Example 3: Drill-Down & Roll-Up")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available. Skipping drill operations.")
        return

    import pandas as pd

    # Create hierarchical cube
    cube = OLAPCube("HierarchicalSales")

    time_dim = Dimension(
        name="Time",
        hierarchy=["Year", "Quarter", "Month"]
    )
    cube.add_dimension(time_dim)
    cube.add_measure(Measure("Sales", AggregationType.SUM))

    # Data with hierarchy
    data = pd.DataFrame({
        "Year": ["2024", "2024", "2024", "2024"],
        "Quarter": ["Q1", "Q1", "Q2", "Q2"],
        "Month": ["Jan", "Feb", "Apr", "May"],
        "Sales": [100, 110, 200, 210]
    })

    cube.load_data(data)

    print("Hierarchical data:")
    print(data.to_string(index=False))

    print_subsection("Aggregation by Quarter")

    # Aggregate by quarter
    quarterly = data.groupby("Quarter")["Sales"].sum().reset_index()
    print("Aggregated view (quarterly):")
    print(quarterly.to_string(index=False))
    print(f"\nTotal Q1 Sales: ${quarterly[quarterly['Quarter']=='Q1']['Sales'].values[0]}")
    print(f"Total Q2 Sales: ${quarterly[quarterly['Quarter']=='Q2']['Sales'].values[0]}")

    print_subsection("Roll-Up to Year Level")

    # Roll up to year
    yearly = data.groupby("Year")["Sales"].sum().reset_index()
    print("Rolled up view (yearly):")
    print(yearly.to_string(index=False))
    print(f"\nTotal 2024 Sales: ${yearly['Sales'].values[0]}")


def example_4_pivot_tables():
    """Example 4: Pivot Table Creation"""
    print_section("Example 4: Pivot Tables")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available. Skipping pivot tables.")
        return

    import pandas as pd

    # Create cube
    cube = OLAPCube("PivotSales")
    cube.add_dimension(Dimension("Year", ["Year"]))
    cube.add_dimension(Dimension("Product", ["Product"]))
    cube.add_dimension(Dimension("Region", ["Region"]))
    cube.add_measure(Measure("Sales", AggregationType.SUM))

    # Sample data
    data = pd.DataFrame({
        "Year": ["2023", "2023", "2023", "2024", "2024", "2024"],
        "Product": ["A", "B", "A", "B", "A", "B"],
        "Region": ["East", "West", "East", "West", "East", "West"],
        "Sales": [100, 150, 120, 180, 140, 200]
    })

    cube.load_data(data)

    print("Original data:")
    print(data.to_string(index=False))

    print_subsection("Pivot: Product (rows) x Year (columns)")

    pivot1 = cube.pivot(
        rows=["Product"],
        columns=["Year"],
        values="Sales",
        aggregation=AggregationType.SUM
    )

    print("Pivot table:")
    print(pivot1)

    print_subsection("Pivot: Region (rows) x Product (columns)")

    pivot2 = cube.pivot(
        rows=["Region"],
        columns=["Product"],
        values="Sales",
        aggregation=AggregationType.SUM
    )

    print("Pivot table:")
    print(pivot2)


def example_5_mdx_queries():
    """Example 5: MDX-like Queries"""
    print_section("Example 5: MDX-like Queries")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available. Skipping MDX queries.")
        return

    import pandas as pd

    # Create and setup cube
    cube = OLAPCube("QueryCube")
    cube.add_dimension(Dimension("Year", ["Year"]))
    cube.add_dimension(Dimension("Product", ["Product"]))
    cube.add_measure(Measure("Sales", AggregationType.SUM))

    # Load data
    data = pd.DataFrame({
        "Year": ["2023", "2023", "2024", "2024"],
        "Product": ["A", "B", "A", "B"],
        "Sales": [100, 150, 200, 250]
    })
    cube.load_data(data)

    # Create MDX engine
    engine = MDXQueryEngine(cube)

    print("Sample data:")
    print(data.to_string(index=False))

    print_subsection("MDX Query 1: Sales by Year")

    query1 = """
    SELECT [Sales] ON COLUMNS,
           [Year] ON ROWS
    FROM QueryCube
    """

    print("Query:")
    print(query1)

    try:
        result1 = engine.query(query1)
        print("\nResult:")
        print(result1)
    except Exception as e:
        print(f"Note: Query execution requires full implementation: {e}")

    print_subsection("MDX Query 2: Sales by Product for 2024")

    query2 = """
    SELECT [Sales] ON COLUMNS,
           [Product] ON ROWS
    FROM QueryCube
    WHERE [Year = '2024']
    """

    print("Query:")
    print(query2)

    try:
        result2 = engine.query(query2)
        print("\nResult:")
        print(result2)
    except Exception as e:
        print(f"Note: Filtered query may require additional implementation: {e}")


def example_6_cube_manager():
    """Example 6: Managing Multiple Cubes"""
    print_section("Example 6: Cube Manager")

    # Get singleton manager
    manager = get_cube_manager()

    print("Creating multiple cubes...")

    # Create sales cube
    sales_cube = manager.create_cube("SalesAnalysis")
    sales_cube.add_dimension(Dimension("Time", ["Year", "Quarter"]))
    sales_cube.add_measure(Measure("Revenue", AggregationType.SUM, "currency"))
    print(f"✓ Created: {sales_cube.name}")

    # Create usage cube
    usage_cube = manager.create_cube("UsageMetrics")
    usage_cube.add_dimension(Dimension("Date", ["Year", "Month"]))
    usage_cube.add_measure(Measure("API_Calls", AggregationType.SUM))
    print(f"✓ Created: {usage_cube.name}")

    # Create inventory cube
    inventory_cube = manager.create_cube("Inventory")
    inventory_cube.add_dimension(Dimension("Product", ["Category", "Product"]))
    inventory_cube.add_measure(Measure("Stock", AggregationType.SUM))
    print(f"✓ Created: {inventory_cube.name}")

    print_subsection("Cube Registry")

    print(f"Total cubes registered: {len(manager.cubes)}")
    for name in manager.cubes.keys():
        cube = manager.get_cube(name)
        print(f"\n  {name}:")
        print(f"    Dimensions: {len(cube.dimensions)}")
        print(f"    Measures: {len(cube.measures)}")

    print_subsection("Retrieving Specific Cube")

    sales = manager.get_cube("SalesAnalysis")
    if sales:
        print(f"Retrieved: {sales.name}")
        print(f"  Dimensions: {list(sales.dimensions.keys())}")
        print(f"  Measures: {list(sales.measures.keys())}")

    print_subsection("Standard Cubes")

    # Create standard sales cube
    standard_sales = manager.create_sales_cube()
    print(f"✓ Standard Sales Cube: {standard_sales.name}")
    print(f"  Dimensions: {list(standard_sales.dimensions.keys())}")
    print(f"  Measures: {list(standard_sales.measures.keys())}")

    # Create usage cube
    standard_usage = manager.create_usage_cube()
    print(f"\n✓ Standard Usage Cube: {standard_usage.name}")
    print(f"  Dimensions: {list(standard_usage.dimensions.keys())}")
    print(f"  Measures: {list(standard_usage.measures.keys())}")


def example_7_complete_workflow():
    """Example 7: Complete OLAP Workflow"""
    print_section("Example 7: Complete OLAP Workflow")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available for complete workflow.")
        return

    import pandas as pd

    print("Step 1: Create Cube Structure")
    print("-" * 50)

    cube = OLAPCube("CompleteSalesAnalysis")

    # Add dimensions
    cube.add_dimension(Dimension("Year", ["Year"]))
    cube.add_dimension(Dimension("Quarter", ["Quarter"]))
    cube.add_dimension(Dimension("Product", ["Product"]))
    cube.add_dimension(Dimension("Region", ["Region"]))

    # Add measures
    cube.add_measure(Measure("Revenue", AggregationType.SUM, "currency"))
    cube.add_measure(Measure("Quantity", AggregationType.SUM, "numeric"))
    cube.add_measure(Measure("Profit", AggregationType.SUM, "currency"))

    print(f"✓ Created cube with {len(cube.dimensions)} dimensions and {len(cube.measures)} measures")

    print("\nStep 2: Load Data")
    print("-" * 50)

    data = pd.DataFrame({
        "Year": ["2023", "2023", "2023", "2024", "2024", "2024"],
        "Quarter": ["Q1", "Q2", "Q1", "Q2", "Q1", "Q2"],
        "Product": ["Widget", "Gadget", "Widget", "Gadget", "Widget", "Gadget"],
        "Region": ["North", "South", "North", "South", "North", "South"],
        "Revenue": [10000, 15000, 12000, 18000, 14000, 20000],
        "Quantity": [100, 150, 120, 180, 140, 200],
        "Profit": [2000, 3000, 2400, 3600, 2800, 4000]
    })

    cube.load_data(data)
    print(f"✓ Loaded {len(data)} records")

    print("\nStep 3: Perform Analysis")
    print("-" * 50)

    # Slice by year
    data_2024 = cube.slice("Year", "2024")
    print(f"\n2024 Sales: {len(data_2024)} records")
    print(f"Total Revenue 2024: ${data_2024['Revenue'].sum():,.2f}")

    # Dice for specific product and region
    widget_north = cube.dice({
        "Product": ["Widget"],
        "Region": ["North"]
    })
    print(f"\nWidget sales in North: {len(widget_north)} records")
    print(f"Total Revenue: ${widget_north['Revenue'].sum():,.2f}")

    # Pivot table
    pivot = cube.pivot(
        rows=["Product"],
        columns=["Year"],
        values="Revenue",
        aggregation=AggregationType.SUM
    )
    print("\nRevenue by Product and Year:")
    print(pivot)

    print("\n" + "=" * 70)
    print("  COMPLETE WORKFLOW FINISHED!")
    print("=" * 70)


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  OLAP CUBE ENGINE - USAGE EXAMPLES")
    print("=" * 70)

    print("\nLibrary Availability:")
    print(f"  ✓ pandas: {'Yes' if PANDAS_AVAILABLE else 'No'}")

    if not PANDAS_AVAILABLE:
        print("\n⚠️  pandas not available. Some examples will be limited.")
        print("   For full functionality, install: pip install pandas numpy")

    try:
        # Run examples
        example_1_cube_structure()
        example_2_slice_and_dice()
        example_3_drill_operations()
        example_4_pivot_tables()
        example_5_mdx_queries()
        example_6_cube_manager()
        example_7_complete_workflow()

        print("\n" + "=" * 70)
        print("  ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
