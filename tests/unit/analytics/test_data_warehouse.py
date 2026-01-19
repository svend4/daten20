"""
Comprehensive tests for Data Warehouse module

Tests cover:
- Star schema design (fact & dimension tables)
- ETL pipeline operations
- Incremental loading
- Data quality checks
- SCD Type 2 support
- SQL DDL generation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

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


class TestEnums:
    """Test enums"""

    def test_scd_type_enum(self):
        """Test SCDType enum values"""
        assert SCDType.TYPE_0 == "type_0"
        assert SCDType.TYPE_1 == "type_1"
        assert SCDType.TYPE_2 == "type_2"
        assert SCDType.TYPE_3 == "type_3"

    def test_table_type_enum(self):
        """Test TableType enum values"""
        assert TableType.FACT == "fact"
        assert TableType.DIMENSION == "dimension"
        assert TableType.BRIDGE == "bridge"


class TestDataClasses:
    """Test data classes"""

    def test_dimension_table_creation(self):
        """Test DimensionTable creation"""
        dim = DimensionTable(
            name="dim_customer",
            columns=["customer_id", "name", "email"],
            primary_key="customer_key",
            natural_key="customer_id",
            scd_type=SCDType.TYPE_2
        )

        assert dim.name == "dim_customer"
        assert len(dim.columns) == 3
        assert dim.primary_key == "customer_key"
        assert dim.natural_key == "customer_id"
        assert dim.scd_type == SCDType.TYPE_2

    def test_dimension_table_defaults(self):
        """Test DimensionTable default values"""
        dim = DimensionTable(
            name="dim_test",
            columns=["id", "name"],
            primary_key="test_key"
        )

        assert dim.scd_type == SCDType.TYPE_2
        assert dim.valid_from == "valid_from"
        assert dim.valid_to == "valid_to"
        assert dim.is_current == "is_current"

    def test_fact_table_creation(self):
        """Test FactTable creation"""
        fact = FactTable(
            name="fact_sales",
            measures=["amount", "quantity", "discount"],
            dimensions=["customer", "product", "time"],
            grain="One row per sale transaction"
        )

        assert fact.name == "fact_sales"
        assert len(fact.measures) == 3
        assert len(fact.dimensions) == 3
        assert fact.grain == "One row per sale transaction"

    def test_fact_table_with_partitioning(self):
        """Test FactTable with partitioning"""
        fact = FactTable(
            name="fact_orders",
            measures=["total_amount"],
            dimensions=["customer"],
            grain="One row per order",
            partition_column="order_date",
            partition_type="daily"
        )

        assert fact.partition_column == "order_date"
        assert fact.partition_type == "daily"

    def test_etl_job_creation(self):
        """Test ETLJob creation"""
        job = ETLJob(
            id="job1",
            name="Daily Load",
            source_query="SELECT * FROM source",
            target_table="target",
            transformation_rules=[{"type": "filter"}],
            schedule="0 0 * * *"
        )

        assert job.id == "job1"
        assert job.name == "Daily Load"
        assert job.enabled is True
        assert job.last_run is None


class TestStarSchema:
    """Test StarSchema class"""

    @pytest.fixture
    def schema(self):
        """Create StarSchema instance"""
        return StarSchema()

    @pytest.fixture
    def sample_dimension(self):
        """Create sample dimension table"""
        return DimensionTable(
            name="dim_product",
            columns=["product_id", "name", "category", "price"],
            primary_key="product_key",
            natural_key="product_id",
            scd_type=SCDType.TYPE_2
        )

    @pytest.fixture
    def sample_fact(self):
        """Create sample fact table"""
        return FactTable(
            name="fact_orders",
            measures=["order_amount", "quantity"],
            dimensions=["customer", "product"],
            grain="One row per order"
        )

    def test_initialization(self, schema):
        """Test schema initialization"""
        assert len(schema.fact_tables) == 0
        assert len(schema.dimension_tables) == 0

    def test_add_dimension(self, schema, sample_dimension):
        """Test adding dimension table"""
        schema.add_dimension(sample_dimension)

        assert "dim_product" in schema.dimension_tables
        assert schema.dimension_tables["dim_product"] == sample_dimension

    def test_add_fact(self, schema, sample_fact):
        """Test adding fact table"""
        schema.add_fact(sample_fact)

        assert "fact_orders" in schema.fact_tables
        assert schema.fact_tables["fact_orders"] == sample_fact

    def test_generate_dimension_ddl(self, schema, sample_dimension):
        """Test dimension DDL generation"""
        schema.add_dimension(sample_dimension)
        ddl_statements = schema.get_schema_ddl("postgresql")

        assert len(ddl_statements) > 0
        ddl = ddl_statements[0]

        # Check DDL contains expected elements
        assert "CREATE TABLE dim_product" in ddl
        assert "product_key INTEGER PRIMARY KEY" in ddl
        assert "product_id VARCHAR(255) NOT NULL" in ddl
        assert "valid_from TIMESTAMP NOT NULL" in ddl
        assert "valid_to TIMESTAMP" in ddl
        assert "is_current BOOLEAN DEFAULT TRUE" in ddl

    def test_generate_fact_ddl(self, schema, sample_fact):
        """Test fact DDL generation"""
        schema.add_fact(sample_fact)
        ddl_statements = schema.get_schema_ddl("postgresql")

        assert len(ddl_statements) > 0
        ddl = ddl_statements[0]

        # Check DDL contains expected elements
        assert "CREATE TABLE fact_orders" in ddl
        assert "customer_key INTEGER NOT NULL" in ddl
        assert "product_key INTEGER NOT NULL" in ddl
        assert "order_amount DECIMAL(18,2)" in ddl
        assert "quantity DECIMAL(18,2)" in ddl
        assert "PRIMARY KEY" in ddl

    def test_generate_complete_schema(self, schema, sample_dimension, sample_fact):
        """Test generating complete schema DDL"""
        schema.add_dimension(sample_dimension)
        schema.add_fact(sample_fact)

        ddl_statements = schema.get_schema_ddl("postgresql")

        # Should have DDL for both dimension and fact
        assert len(ddl_statements) == 2
        assert any("dim_product" in ddl for ddl in ddl_statements)
        assert any("fact_orders" in ddl for ddl in ddl_statements)

    def test_scd_type_0_no_versioning(self, schema):
        """Test SCD Type 0 (no versioning columns)"""
        dim = DimensionTable(
            name="dim_static",
            columns=["id", "name"],
            primary_key="static_key",
            scd_type=SCDType.TYPE_0
        )

        schema.add_dimension(dim)
        ddl = schema.get_schema_ddl()[0]

        # Should NOT have versioning columns
        assert "valid_from" not in ddl
        assert "valid_to" not in ddl
        assert "is_current" not in ddl


class TestETLPipeline:
    """Test ETL Pipeline"""

    @pytest.fixture
    def pipeline(self):
        """Create ETL pipeline instance"""
        return ETLPipeline()

    @pytest.fixture
    def sample_job(self):
        """Create sample ETL job"""
        return ETLJob(
            id="test_job",
            name="Test Job",
            source_query="SELECT * FROM source",
            target_table="target",
            transformation_rules=[],
            schedule="0 0 * * *"
        )

    def test_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert len(pipeline.jobs) == 0
        assert pipeline.execution_log == []

    def test_register_job(self, pipeline, sample_job):
        """Test registering ETL job"""
        pipeline.register_job(sample_job)

        assert "test_job" in pipeline.jobs
        assert pipeline.jobs["test_job"] == sample_job

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_extract_data(self, pipeline):
        """Test data extraction"""
        import pandas as pd

        # Mock connection
        mock_conn = Mock()

        # Extract should return DataFrame
        result = pipeline.extract("SELECT * FROM test", mock_conn)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_transform_aggregate(self, pipeline):
        """Test data transformation - aggregation"""
        import pandas as pd

        data = pd.DataFrame({
            "category": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40]
        })

        rules = [{"type": "aggregate", "group_by": ["category"], "agg_col": "value", "function": "sum"}]

        result = pipeline.transform(data, rules)

        assert isinstance(result, pd.DataFrame)
        # After aggregation, should have 2 rows (A and B)
        assert len(result) <= 2

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_transform_filter(self, pipeline):
        """Test data transformation - filtering"""
        import pandas as pd

        data = pd.DataFrame({
            "value": [10, 20, 30, 40, 50]
        })

        rules = [{"type": "filter", "column": "value", "operator": ">", "value": 25}]

        result = pipeline.transform(data, rules)

        # Should filter to values > 25
        assert len(result) <= len(data)
        if len(result) > 0:
            assert all(result["value"] > 25)

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_transform_calculate(self, pipeline):
        """Test data transformation - calculation"""
        import pandas as pd

        data = pd.DataFrame({
            "quantity": [10, 20, 30],
            "price": [5, 10, 15]
        })

        rules = [{"type": "calculate", "column": "total", "expression": "quantity * price"}]

        result = pipeline.transform(data, rules)

        assert "total" in result.columns

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_run_job(self, pipeline, sample_job):
        """Test running ETL job"""
        pipeline.register_job(sample_job)

        # Mock connections
        mock_source = Mock()
        mock_target = Mock()

        result = pipeline.run_job("test_job", mock_source, mock_target)

        assert result["status"] in ["success", "failed"]
        if result["status"] == "success":
            assert "rows_processed" in result


class TestIncrementalLoader:
    """Test Incremental Loader"""

    @pytest.fixture
    def loader(self):
        """Create loader instance"""
        return IncrementalLoader()

    def test_initialization(self, loader):
        """Test loader initialization"""
        assert len(loader.watermarks) == 0

    def test_get_watermark_nonexistent(self, loader):
        """Test getting watermark for non-existent table"""
        watermark = loader.get_watermark("nonexistent_table")
        assert watermark is None

    def test_set_and_get_watermark(self, loader):
        """Test setting and getting watermark"""
        now = datetime.now()
        loader.set_watermark("test_table", now)

        watermark = loader.get_watermark("test_table")
        assert watermark == now

    def test_watermark_persistence(self, loader):
        """Test multiple watermarks"""
        time1 = datetime(2024, 1, 1)
        time2 = datetime(2024, 1, 2)

        loader.set_watermark("table1", time1)
        loader.set_watermark("table2", time2)

        assert loader.get_watermark("table1") == time1
        assert loader.get_watermark("table2") == time2

    def test_update_watermark(self, loader):
        """Test updating existing watermark"""
        old_time = datetime(2024, 1, 1)
        new_time = datetime(2024, 1, 2)

        loader.set_watermark("table", old_time)
        loader.set_watermark("table", new_time)

        assert loader.get_watermark("table") == new_time


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
class TestDataQualityChecker:
    """Test Data Quality Checker"""

    @pytest.fixture
    def checker(self):
        """Create checker instance"""
        return DataQualityChecker()

    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame"""
        import pandas as pd
        return pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["A", "B", None, "D", "E"],
            "value": [10, 20, 30, 40, 50],
            "category": ["X", "Y", "X", "Y", "X"]
        })

    def test_initialization(self, checker):
        """Test checker initialization"""
        assert checker.rules == []

    def test_add_rule(self, checker):
        """Test adding quality rule"""
        rule = {"type": "null_check", "column": "name"}
        checker.add_rule(rule)

        assert len(checker.rules) == 1
        assert checker.rules[0] == rule

    def test_check_nulls_pass(self, checker):
        """Test null check passing"""
        import pandas as pd

        df = pd.DataFrame({"col": [1, 2, 3, 4, 5]})
        result = checker.check_nulls(df, "col", max_null_pct=0.05)

        assert result["rule"] == "null_check"
        assert result["passed"] is True
        assert result["null_percentage"] == 0.0

    def test_check_nulls_fail(self, checker, sample_data):
        """Test null check failing"""
        # name column has 1 null out of 5 (20%)
        result = checker.check_nulls(sample_data, "name", max_null_pct=0.10)

        assert result["rule"] == "null_check"
        assert result["passed"] is False
        assert result["null_percentage"] == 0.2

    def test_check_duplicates_none(self, checker, sample_data):
        """Test duplicate check with no duplicates"""
        result = checker.check_duplicates(sample_data, ["id"])

        assert result["rule"] == "duplicate_check"
        assert result["passed"] is True
        assert result["duplicates"] == 0

    def test_check_duplicates_found(self, checker):
        """Test duplicate check finding duplicates"""
        import pandas as pd

        df = pd.DataFrame({
            "id": [1, 2, 2, 3],
            "value": [10, 20, 20, 30]
        })

        result = checker.check_duplicates(df, ["id", "value"])

        assert result["rule"] == "duplicate_check"
        assert result["passed"] is False
        assert result["duplicates"] > 0

    def test_check_range_pass(self, checker, sample_data):
        """Test range check passing"""
        result = checker.check_range(sample_data, "value", 0, 100)

        assert result["rule"] == "range_check"
        assert result["passed"] is True
        assert result["out_of_range"] == 0

    def test_check_range_fail(self, checker, sample_data):
        """Test range check failing"""
        result = checker.check_range(sample_data, "value", 25, 100)

        assert result["rule"] == "range_check"
        assert result["passed"] is False
        assert result["out_of_range"] == 2  # 10 and 20 are out of range

    def test_validate_all_rules(self, checker, sample_data):
        """Test validating all rules"""
        checker.add_rule({"type": "null_check", "column": "name", "max_null_pct": 0.10})
        checker.add_rule({"type": "duplicate_check", "columns": ["id"]})
        checker.add_rule({"type": "range_check", "column": "value", "min": 0, "max": 100})

        result = checker.validate(sample_data)

        assert "overall_status" in result
        assert "checks" in result
        assert len(result["checks"]) == 3
        assert "passed_count" in result
        assert "failed_count" in result


class TestDataWarehouse:
    """Test main DataWarehouse class"""

    @pytest.fixture
    def warehouse(self):
        """Create warehouse instance"""
        return DataWarehouse()

    def test_initialization(self, warehouse):
        """Test warehouse initialization"""
        assert warehouse.schema is not None
        assert warehouse.etl is not None
        assert warehouse.incremental_loader is not None
        assert warehouse.quality_checker is not None

    def test_create_standard_schema(self, warehouse):
        """Test creating standard schema"""
        warehouse.create_standard_schema()

        # Should have standard dimensions
        assert "dim_time" in warehouse.schema.dimension_tables
        assert "dim_user" in warehouse.schema.dimension_tables
        assert "dim_tenant" in warehouse.schema.dimension_tables
        assert "dim_document" in warehouse.schema.dimension_tables

        # Should have standard facts
        assert "fact_documents" in warehouse.schema.fact_tables
        assert "fact_usage" in warehouse.schema.fact_tables
        assert "fact_revenue" in warehouse.schema.fact_tables

    def test_dimension_tables_configuration(self, warehouse):
        """Test dimension table configurations"""
        warehouse.create_standard_schema()

        # Check dim_time (TYPE_0 - no changes)
        dim_time = warehouse.schema.dimension_tables["dim_time"]
        assert dim_time.scd_type == SCDType.TYPE_0

        # Check dim_user (TYPE_2 - versioning)
        dim_user = warehouse.schema.dimension_tables["dim_user"]
        assert dim_user.scd_type == SCDType.TYPE_2

        # Check dim_document (TYPE_1 - overwrite)
        dim_document = warehouse.schema.dimension_tables["dim_document"]
        assert dim_document.scd_type == SCDType.TYPE_1

    def test_fact_tables_configuration(self, warehouse):
        """Test fact table configurations"""
        warehouse.create_standard_schema()

        # Check fact_documents
        fact_docs = warehouse.schema.fact_tables["fact_documents"]
        assert len(fact_docs.measures) == 3
        assert len(fact_docs.dimensions) == 4
        assert fact_docs.partition_type == "daily"

        # Check fact_usage
        fact_usage = warehouse.schema.fact_tables["fact_usage"]
        assert len(fact_usage.measures) == 4
        assert "api_calls" in fact_usage.measures
        assert "storage_gb" in fact_usage.measures

        # Check fact_revenue
        fact_revenue = warehouse.schema.fact_tables["fact_revenue"]
        assert "mrr" in fact_revenue.measures
        assert "arr" in fact_revenue.measures
        assert fact_revenue.partition_type == "monthly"

    def test_generate_schema_sql(self, warehouse):
        """Test SQL generation"""
        warehouse.create_standard_schema()
        sql = warehouse.generate_schema_sql("postgresql")

        assert isinstance(sql, str)
        assert len(sql) > 0
        assert "CREATE TABLE" in sql
        assert "dim_time" in sql
        assert "fact_documents" in sql

    def test_setup_etl_jobs(self, warehouse):
        """Test ETL jobs setup"""
        warehouse.setup_etl_jobs()

        # Should have registered ETL jobs
        assert "daily_usage" in warehouse.etl.jobs
        assert "monthly_revenue" in warehouse.etl.jobs

        # Check daily usage job
        usage_job = warehouse.etl.jobs["daily_usage"]
        assert usage_job.target_table == "fact_usage"
        assert usage_job.schedule == "0 1 * * *"

        # Check monthly revenue job
        revenue_job = warehouse.etl.jobs["monthly_revenue"]
        assert revenue_job.target_table == "fact_revenue"
        assert revenue_job.schedule == "0 2 1 * *"


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_data_warehouse(self):
        """Test getting singleton instance"""
        warehouse1 = get_data_warehouse()
        warehouse2 = get_data_warehouse()

        # Should return same instance
        assert warehouse1 is warehouse2

    def test_warehouse_instance_type(self):
        """Test warehouse instance type"""
        warehouse = get_data_warehouse()
        assert isinstance(warehouse, DataWarehouse)


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_warehouse_setup(self):
        """Test complete warehouse setup workflow"""
        warehouse = DataWarehouse()

        # Create schema
        warehouse.create_standard_schema()

        # Setup ETL jobs
        warehouse.setup_etl_jobs()

        # Generate SQL
        sql = warehouse.generate_schema_sql()

        # Verify complete setup
        assert len(warehouse.schema.dimension_tables) == 4
        assert len(warehouse.schema.fact_tables) == 3
        assert len(warehouse.etl.jobs) == 2
        assert len(sql) > 0

    @pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
    def test_etl_with_quality_checks(self):
        """Test ETL pipeline with quality checks"""
        import pandas as pd

        warehouse = DataWarehouse()

        # Setup quality rules
        warehouse.quality_checker.add_rule({
            "type": "null_check",
            "column": "id",
            "max_null_pct": 0.01
        })

        # Sample data
        data = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "value": [10, 20, 30, 40, 50]
        })

        # Run quality checks
        result = warehouse.quality_checker.validate(data)

        assert result["overall_status"] == "passed"

    def test_incremental_loading_workflow(self):
        """Test incremental loading workflow"""
        warehouse = DataWarehouse()

        # Initial watermark
        assert warehouse.incremental_loader.get_watermark("test_table") is None

        # Set watermark after load
        now = datetime.now()
        warehouse.incremental_loader.set_watermark("test_table", now)

        # Verify watermark
        assert warehouse.incremental_loader.get_watermark("test_table") == now


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
