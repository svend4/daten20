#!/usr/bin/env python3
"""
Data Warehouse Usage Examples

Demonstrates how to use the Data Warehouse module for:
- Star schema design
- ETL pipeline setup
- Data quality checks
- Incremental loading
- SQL DDL generation

Requirements:
- Basic: Works without pandas (schema design only)
- Full features: Install pandas for ETL operations
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analytics.data_warehouse import (
    SCDType,
    TableType,
    DimensionTable,
    FactTable,
    ETLJob,
    StarSchema,
    ETLPipeline,
    IncrementalLoader,
    DataQualityChecker,
    DataWarehouse,
    get_data_warehouse,
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


def example_1_star_schema_design():
    """Example 1: Designing Star Schema"""
    print_section("Example 1: Star Schema Design")

    schema = StarSchema()

    # Create dimension tables
    print("Creating dimension tables...")

    dim_customer = DimensionTable(
        name="dim_customer",
        columns=["customer_id", "name", "email", "segment", "country"],
        primary_key="customer_key",
        natural_key="customer_id",
        scd_type=SCDType.TYPE_2  # Track history
    )
    schema.add_dimension(dim_customer)
    print(f"  ✓ {dim_customer.name} (SCD Type 2 - History tracking)")

    dim_product = DimensionTable(
        name="dim_product",
        columns=["product_id", "name", "category", "brand", "price"],
        primary_key="product_key",
        natural_key="product_id",
        scd_type=SCDType.TYPE_1  # Overwrite changes
    )
    schema.add_dimension(dim_product)
    print(f"  ✓ {dim_product.name} (SCD Type 1 - Overwrite)")

    dim_date = DimensionTable(
        name="dim_date",
        columns=["date", "year", "month", "day", "quarter", "week", "is_weekend"],
        primary_key="date_key",
        natural_key="date",
        scd_type=SCDType.TYPE_0  # No changes allowed
    )
    schema.add_dimension(dim_date)
    print(f"  ✓ {dim_date.name} (SCD Type 0 - Static)")

    # Create fact table
    print("\nCreating fact table...")

    fact_sales = FactTable(
        name="fact_sales",
        measures=["quantity", "unit_price", "total_amount", "discount", "tax"],
        dimensions=["customer", "product", "date"],
        grain="One row per sale transaction",
        partition_column="date_key",
        partition_type="daily"
    )
    schema.add_fact(fact_sales)
    print(f"  ✓ {fact_sales.name}")
    print(f"    Measures: {', '.join(fact_sales.measures)}")
    print(f"    Dimensions: {', '.join(fact_sales.dimensions)}")
    print(f"    Grain: {fact_sales.grain}")

    # Generate DDL
    print_subsection("Generated SQL DDL")

    ddl_statements = schema.get_schema_ddl("postgresql")

    for i, ddl in enumerate(ddl_statements, 1):
        print(f"\n-- Statement {i}")
        print(ddl)

    print(f"\n✓ Generated {len(ddl_statements)} CREATE TABLE statements")


def example_2_data_warehouse_setup():
    """Example 2: Complete Data Warehouse Setup"""
    print_section("Example 2: Complete Data Warehouse Setup")

    warehouse = DataWarehouse()

    print("Creating standard schema for Document Management System...")

    warehouse.create_standard_schema()

    print(f"\n✓ Created {len(warehouse.schema.dimension_tables)} dimension tables:")
    for name, dim in warehouse.schema.dimension_tables.items():
        print(f"  - {name} (SCD {dim.scd_type.value})")

    print(f"\n✓ Created {len(warehouse.schema.fact_tables)} fact tables:")
    for name, fact in warehouse.schema.fact_tables.items():
        print(f"  - {name}")
        print(f"    Measures: {', '.join(fact.measures[:3])}...")
        print(f"    Partitioning: {fact.partition_type}")

    # Generate complete schema SQL
    print_subsection("Complete Schema SQL")

    sql = warehouse.generate_schema_sql("postgresql")
    lines = sql.split("\n")

    print(f"Generated {len(lines)} lines of SQL")
    print("\nFirst 20 lines:")
    print("\n".join(lines[:20]))
    print("...")


def example_3_etl_pipeline():
    """Example 3: ETL Pipeline Configuration"""
    print_section("Example 3: ETL Pipeline Configuration")

    pipeline = ETLPipeline()

    print("Registering ETL jobs...")

    # Daily usage aggregation job
    usage_job = ETLJob(
        id="daily_usage_agg",
        name="Daily Usage Aggregation",
        source_query="""
            SELECT
                tenant_id,
                DATE(timestamp) as date,
                COUNT(*) as api_calls,
                SUM(storage_bytes) / 1073741824 as storage_gb,
                COUNT(DISTINCT user_id) as active_users
            FROM operational_logs
            WHERE DATE(timestamp) = CURRENT_DATE
            GROUP BY tenant_id, DATE(timestamp)
        """,
        target_table="fact_usage",
        transformation_rules=[
            {"type": "aggregate", "group_by": ["tenant_id", "date"]},
            {"type": "calculate", "column": "bandwidth_gb", "expression": "api_calls * 0.001"}
        ],
        schedule="0 1 * * *"  # Daily at 1 AM
    )
    pipeline.register_job(usage_job)
    print(f"  ✓ {usage_job.name}")
    print(f"    Schedule: {usage_job.schedule} (Daily at 1 AM)")
    print(f"    Target: {usage_job.target_table}")

    # Weekly report job
    report_job = ETLJob(
        id="weekly_report",
        name="Weekly Analytics Report",
        source_query="""
            SELECT * FROM fact_usage
            WHERE date >= CURRENT_DATE - INTERVAL '7 days'
        """,
        target_table="report_weekly_usage",
        transformation_rules=[
            {"type": "aggregate", "group_by": ["tenant_id"], "function": "sum"}
        ],
        schedule="0 2 * * 1"  # Weekly on Monday at 2 AM
    )
    pipeline.register_job(report_job)
    print(f"  ✓ {report_job.name}")
    print(f"    Schedule: {report_job.schedule} (Weekly on Monday)")

    print(f"\n✓ Registered {len(pipeline.jobs)} ETL jobs")

    if not PANDAS_AVAILABLE:
        print("\n⚠️  pandas not available. ETL execution requires pandas.")
        print("   Install with: pip install pandas numpy")


def example_4_data_quality_checks():
    """Example 4: Data Quality Validation"""
    print_section("Example 4: Data Quality Validation")

    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available. Data quality checks require pandas.")
        print("   Install with: pip install pandas")
        return

    import pandas as pd

    checker = DataQualityChecker()

    print("Setting up data quality rules...")

    # Rule 1: Check for nulls in critical columns
    checker.add_rule({
        "type": "null_check",
        "column": "customer_id",
        "max_null_pct": 0.0  # No nulls allowed
    })
    print("  ✓ Null check: customer_id (0% nulls allowed)")

    # Rule 2: Check for duplicates
    checker.add_rule({
        "type": "duplicate_check",
        "columns": ["order_id"]
    })
    print("  ✓ Duplicate check: order_id")

    # Rule 3: Check value ranges
    checker.add_rule({
        "type": "range_check",
        "column": "amount",
        "min": 0,
        "max": 1000000
    })
    print("  ✓ Range check: amount (0 - 1,000,000)")

    # Sample data for validation
    print_subsection("Validating sample data")

    sample_data = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5],
        "customer_id": ["C001", "C002", "C003", "C004", "C005"],
        "amount": [150.00, 250.00, 350.00, 450.00, 550.00],
        "date": pd.date_range("2024-01-01", periods=5)
    })

    print(f"Sample data: {len(sample_data)} rows")

    result = checker.validate(sample_data)

    print(f"\n{'='*50}")
    print("VALIDATION RESULTS")
    print('='*50)
    print(f"Overall Status: {result['overall_status'].upper()}")
    print(f"Checks Passed: {result['passed_count']}/{len(result['checks'])}")
    print(f"Checks Failed: {result['failed_count']}/{len(result['checks'])}")

    print("\nDetailed Results:")
    for i, check in enumerate(result['checks'], 1):
        status = "✓ PASS" if check['passed'] else "✗ FAIL"
        print(f"\n  {i}. {check['rule']} - {status}")

        if check['rule'] == 'null_check':
            print(f"     Column: {check['column']}")
            print(f"     Null %: {check['null_percentage']:.1%}")
            print(f"     Threshold: {check['threshold']:.1%}")

        elif check['rule'] == 'duplicate_check':
            print(f"     Columns: {', '.join(check['columns'])}")
            print(f"     Duplicates found: {check['duplicates']}")

        elif check['rule'] == 'range_check':
            print(f"     Column: {check['column']}")
            print(f"     Range: {check['range'][0]} - {check['range'][1]}")
            print(f"     Out of range: {check['out_of_range']}")


def example_5_incremental_loading():
    """Example 5: Incremental Data Loading"""
    print_section("Example 5: Incremental Data Loading")

    loader = IncrementalLoader()

    print("Incremental loading tracks watermarks to load only new data.\n")

    # Initial load
    print_subsection("Initial Load")

    table_name = "customer_data"
    print(f"Loading data for: {table_name}")

    watermark = loader.get_watermark(table_name)
    print(f"Current watermark: {watermark}")

    if watermark is None:
        print("→ No watermark found. This is an initial load.")
        print("→ Will load ALL historical data")
    else:
        print(f"→ Watermark found: {watermark}")
        print(f"→ Will load data since {watermark}")

    # Simulate load
    load_time = datetime(2024, 1, 15, 10, 30, 0)
    print(f"\nSimulating data load at {load_time}...")

    loader.set_watermark(table_name, load_time)
    print(f"✓ Watermark updated to: {load_time}")

    # Second load
    print_subsection("Incremental Load (Next Day)")

    watermark = loader.get_watermark(table_name)
    print(f"Current watermark: {watermark}")
    print(f"→ Will load only data after {watermark}")

    # Simulate incremental load
    new_load_time = datetime(2024, 1, 16, 10, 30, 0)
    print(f"\nSimulating incremental load at {new_load_time}...")

    records_since_watermark = "WHERE timestamp > '2024-01-15 10:30:00'"
    print(f"Query condition: {records_since_watermark}")

    loader.set_watermark(table_name, new_load_time)
    print(f"✓ Watermark updated to: {new_load_time}")

    # Show all watermarks
    print_subsection("All Table Watermarks")

    # Add more tables
    loader.set_watermark("orders", datetime(2024, 1, 15, 12, 0, 0))
    loader.set_watermark("products", datetime(2024, 1, 14, 8, 0, 0))

    print("Table".ljust(20) + "Watermark")
    print("-" * 50)
    for table in ["customer_data", "orders", "products"]:
        wm = loader.get_watermark(table)
        if wm:
            print(f"{table.ljust(20)}{wm}")


def example_6_complete_workflow():
    """Example 6: Complete Data Warehouse Workflow"""
    print_section("Example 6: Complete Data Warehouse Workflow")

    # Get singleton instance
    warehouse = get_data_warehouse()

    print("Step 1: Create Schema")
    print("-" * 50)
    warehouse.create_standard_schema()
    print(f"✓ Created {len(warehouse.schema.dimension_tables)} dimensions")
    print(f"✓ Created {len(warehouse.schema.fact_tables)} facts")

    print("\nStep 2: Setup ETL Jobs")
    print("-" * 50)
    warehouse.setup_etl_jobs()
    print(f"✓ Registered {len(warehouse.etl.jobs)} ETL jobs")

    for job_id, job in warehouse.etl.jobs.items():
        print(f"  - {job.name} ({job.schedule})")

    print("\nStep 3: Configure Quality Checks")
    print("-" * 50)
    warehouse.quality_checker.add_rule({
        "type": "null_check",
        "column": "tenant_id",
        "max_null_pct": 0.0
    })
    print("✓ Added null check for tenant_id")

    print("\nStep 4: Setup Incremental Loading")
    print("-" * 50)
    for table in ["fact_usage", "fact_revenue", "fact_documents"]:
        warehouse.incremental_loader.set_watermark(
            table,
            datetime(2024, 1, 1, 0, 0, 0)
        )
    print("✓ Initialized watermarks for all fact tables")

    print("\nStep 5: Generate Deployment SQL")
    print("-" * 50)
    sql = warehouse.generate_schema_sql("postgresql")
    sql_lines = sql.count("\n") + 1
    print(f"✓ Generated {sql_lines} lines of SQL")
    print("  Ready for deployment to PostgreSQL database")

    print("\n" + "=" * 70)
    print("  WAREHOUSE SETUP COMPLETE!")
    print("=" * 70)
    print("\nThe data warehouse is ready for:")
    print("  ✓ Data ingestion via ETL pipelines")
    print("  ✓ Quality validation on incoming data")
    print("  ✓ Incremental loading of new records")
    print("  ✓ Analytics queries on star schema")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  DATA WAREHOUSE MODULE - USAGE EXAMPLES")
    print("=" * 70)

    print("\nLibrary Availability:")
    print(f"  ✓ pandas: {'Yes' if PANDAS_AVAILABLE else 'No'}")

    if not PANDAS_AVAILABLE:
        print("\n⚠️  pandas not available. Some examples will be limited.")
        print("   For full functionality, install: pip install pandas numpy")

    try:
        # Run examples
        example_1_star_schema_design()
        example_2_data_warehouse_setup()
        example_3_etl_pipeline()
        example_4_data_quality_checks()
        example_5_incremental_loading()
        example_6_complete_workflow()

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
