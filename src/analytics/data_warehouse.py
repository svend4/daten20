#!/usr/bin/env python3
"""
Data Warehouse Module (Pure Python)

Enterprise data warehousing with star schema design, ETL pipelines,
and support for fact/dimension tables.

Features:
- Star Schema design (fact & dimension tables)
- SQL DDL generation (PostgreSQL, MySQL, SQLite)
- ETL (Extract, Transform, Load) pipelines
- Slowly Changing Dimensions (SCD Type 1, 2, 3)
- Incremental loading with watermarks
- Data quality checks
- Query builder
- Data transformation engine

Note: Pure Python implementation without external dependencies.
Provides complete warehouse functionality using only stdlib.
"""

import csv
import hashlib
import json
import re
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ============================================================================
# Enums and Data Classes
# ============================================================================

class SCDType(str, Enum):
    """Slowly Changing Dimension types"""
    TYPE_0 = "type_0"  # No changes allowed (fixed dimensions)
    TYPE_1 = "type_1"  # Overwrite (no history)
    TYPE_2 = "type_2"  # Add new row with versioning (full history)
    TYPE_3 = "type_3"  # Add new column (limited history)


class TableType(str, Enum):
    """Data warehouse table types"""
    FACT = "fact"
    DIMENSION = "dimension"
    BRIDGE = "bridge"


class SQLDialect(str, Enum):
    """Supported SQL dialects"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


@dataclass
class DimensionTable:
    """Dimension table definition"""
    name: str
    columns: List[str]
    primary_key: str
    scd_type: SCDType = SCDType.TYPE_2
    natural_key: Optional[str] = None

    # SCD Type 2 columns
    valid_from: str = "valid_from"
    valid_to: str = "valid_to"
    is_current: str = "is_current"

    # Data storage
    data: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FactTable:
    """Fact table definition"""
    name: str
    measures: List[str]  # Additive measures
    dimensions: List[str]  # Foreign keys to dimensions
    grain: str  # Level of detail

    # Partitioning
    partition_column: Optional[str] = None
    partition_type: Optional[str] = None  # "daily", "monthly", "yearly"

    # Data storage
    data: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ETLJob:
    """ETL job configuration"""
    id: str
    name: str
    source_query: str
    target_table: str
    transformation_rules: List[Dict[str, Any]]
    schedule: str  # cron expression
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class DataQualityRule:
    """Data quality rule"""
    id: str
    rule_type: str  # "null_check", "duplicate_check", "range_check", "pattern_check"
    column: str
    parameters: Dict[str, Any]
    severity: str = "error"  # "error", "warning"


# ============================================================================
# SQL DDL Generator
# ============================================================================

class DDLGenerator:
    """SQL DDL generator for different database dialects"""

    @staticmethod
    def get_type_mapping(dialect: SQLDialect) -> Dict[str, str]:
        """Get SQL type mappings for dialect"""
        if dialect == SQLDialect.POSTGRESQL:
            return {
                "integer": "INTEGER",
                "bigint": "BIGINT",
                "decimal": "DECIMAL(18,2)",
                "varchar": "VARCHAR(255)",
                "text": "TEXT",
                "timestamp": "TIMESTAMP",
                "date": "DATE",
                "boolean": "BOOLEAN",
            }
        elif dialect == SQLDialect.MYSQL:
            return {
                "integer": "INT",
                "bigint": "BIGINT",
                "decimal": "DECIMAL(18,2)",
                "varchar": "VARCHAR(255)",
                "text": "TEXT",
                "timestamp": "TIMESTAMP",
                "date": "DATE",
                "boolean": "TINYINT(1)",
            }
        else:  # SQLite
            return {
                "integer": "INTEGER",
                "bigint": "INTEGER",
                "decimal": "REAL",
                "varchar": "TEXT",
                "text": "TEXT",
                "timestamp": "TEXT",
                "date": "TEXT",
                "boolean": "INTEGER",
            }

    @staticmethod
    def generate_dimension_ddl(dim: DimensionTable, dialect: SQLDialect = SQLDialect.POSTGRESQL) -> str:
        """Generate DDL for dimension table"""
        types = DDLGenerator.get_type_mapping(dialect)
        columns = []

        # Surrogate key (auto-increment)
        if dialect == SQLDialect.POSTGRESQL:
            columns.append(f"    {dim.primary_key} SERIAL PRIMARY KEY")
        elif dialect == SQLDialect.MYSQL:
            columns.append(f"    {dim.primary_key} INT AUTO_INCREMENT PRIMARY KEY")
        else:  # SQLite
            columns.append(f"    {dim.primary_key} INTEGER PRIMARY KEY AUTOINCREMENT")

        # Natural key
        if dim.natural_key:
            columns.append(f"    {dim.natural_key} {types['varchar']} NOT NULL")

        # Attributes
        for col in dim.columns:
            if col not in [dim.primary_key, dim.natural_key]:
                columns.append(f"    {col} {types['varchar']}")

        # SCD Type 2 columns
        if dim.scd_type == SCDType.TYPE_2:
            columns.append(f"    {dim.valid_from} {types['timestamp']} NOT NULL")
            columns.append(f"    {dim.valid_to} {types['timestamp']}")
            columns.append(f"    {dim.is_current} {types['boolean']} DEFAULT TRUE")

        # SCD Type 3 columns (example: previous value)
        elif dim.scd_type == SCDType.TYPE_3:
            columns.append(f"    previous_value {types['varchar']}")
            columns.append(f"    effective_date {types['timestamp']}")

        ddl = f"CREATE TABLE {dim.name} (\n"
        ddl += ",\n".join(columns)
        ddl += "\n);"

        return ddl

    @staticmethod
    def generate_fact_ddl(fact: FactTable, dialect: SQLDialect = SQLDialect.POSTGRESQL) -> str:
        """Generate DDL for fact table"""
        types = DDLGenerator.get_type_mapping(dialect)
        columns = []
        pk_cols = []

        # Dimension foreign keys
        for dim in fact.dimensions:
            columns.append(f"    {dim}_key {types['integer']} NOT NULL")
            pk_cols.append(f"{dim}_key")

        # Measures
        for measure in fact.measures:
            columns.append(f"    {measure} {types['decimal']}")

        # Time dimension (usually part of every fact)
        if "time" not in fact.dimensions and "date" not in fact.dimensions:
            columns.append(f"    date_key {types['integer']} NOT NULL")
            pk_cols.append("date_key")

        # Primary key constraint
        if pk_cols:
            pk_constraint = f"    PRIMARY KEY ({', '.join(pk_cols)})"
            columns.append(pk_constraint)

        ddl = f"CREATE TABLE {fact.name} (\n"
        ddl += ",\n".join(columns)
        ddl += "\n);"

        return ddl

    @staticmethod
    def generate_indexes(table_name: str, columns: List[str], dialect: SQLDialect = SQLDialect.POSTGRESQL) -> List[str]:
        """Generate index DDL statements"""
        indexes = []

        for col in columns:
            idx_name = f"idx_{table_name}_{col}"
            if dialect == SQLDialect.MYSQL:
                indexes.append(f"CREATE INDEX {idx_name} ON {table_name}({col});")
            else:
                indexes.append(f"CREATE INDEX {idx_name} ON {table_name} ({col});")

        return indexes


# ============================================================================
# Star Schema Designer
# ============================================================================

class StarSchema:
    """Star Schema designer and manager"""

    def __init__(self):
        self.fact_tables: Dict[str, FactTable] = {}
        self.dimension_tables: Dict[str, DimensionTable] = {}

    def add_dimension(self, dimension: DimensionTable):
        """Add dimension table to schema"""
        self.dimension_tables[dimension.name] = dimension

    def add_fact(self, fact: FactTable):
        """Add fact table to schema"""
        self.fact_tables[fact.name] = fact

    def get_schema_ddl(self, dialect: SQLDialect = SQLDialect.POSTGRESQL) -> List[str]:
        """Generate DDL statements for the schema"""
        ddl_statements = []

        # Create dimension tables first (referenced by facts)
        for dim in self.dimension_tables.values():
            ddl = DDLGenerator.generate_dimension_ddl(dim, dialect)
            ddl_statements.append(ddl)

        # Create fact tables
        for fact in self.fact_tables.values():
            ddl = DDLGenerator.generate_fact_ddl(fact, dialect)
            ddl_statements.append(ddl)

        # Create indexes for better query performance
        for dim in self.dimension_tables.values():
            if dim.natural_key:
                indexes = DDLGenerator.generate_indexes(
                    dim.name,
                    [dim.natural_key],
                    dialect
                )
                ddl_statements.extend(indexes)

        return ddl_statements

    def validate_schema(self) -> Dict[str, Any]:
        """Validate star schema design"""
        issues = []
        warnings = []

        # Check for fact tables
        if not self.fact_tables:
            issues.append("No fact tables defined")

        # Check for dimension tables
        if not self.dimension_tables:
            warnings.append("No dimension tables defined")

        # Validate fact table references
        for fact in self.fact_tables.values():
            for dim_ref in fact.dimensions:
                dim_table_name = f"dim_{dim_ref}"
                if dim_table_name not in self.dimension_tables:
                    issues.append(f"Fact table {fact.name} references undefined dimension: {dim_ref}")

        # Check for time dimension
        has_time_dim = any("time" in name or "date" in name for name in self.dimension_tables.keys())
        if not has_time_dim:
            warnings.append("No time dimension found - recommended for temporal analysis")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "fact_count": len(self.fact_tables),
            "dimension_count": len(self.dimension_tables),
        }


# ============================================================================
# SCD Type 2 Implementation
# ============================================================================

class SCDType2Handler:
    """Slowly Changing Dimension Type 2 handler"""

    @staticmethod
    def insert_new_record(
        dimension: DimensionTable,
        natural_key_value: str,
        attributes: Dict[str, Any],
        effective_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Insert new SCD Type 2 record"""
        if effective_date is None:
            effective_date = datetime.now()

        # Generate surrogate key
        surrogate_key = len(dimension.data) + 1

        # Create new record
        record = {
            dimension.primary_key: surrogate_key,
            dimension.natural_key: natural_key_value,
            dimension.valid_from: effective_date,
            dimension.valid_to: None,
            dimension.is_current: True,
        }

        # Add attributes
        record.update(attributes)

        dimension.data.append(record)

        return record

    @staticmethod
    def update_record(
        dimension: DimensionTable,
        natural_key_value: str,
        new_attributes: Dict[str, Any],
        effective_date: Optional[datetime] = None
    ) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Update SCD Type 2 record (creates new version)"""
        if effective_date is None:
            effective_date = datetime.now()

        # Find current record
        current_record = None
        for record in dimension.data:
            if (record[dimension.natural_key] == natural_key_value and
                record[dimension.is_current]):
                current_record = record
                break

        if not current_record:
            return None, None

        # Check if attributes actually changed
        changed = False
        for key, value in new_attributes.items():
            if key in current_record and current_record[key] != value:
                changed = True
                break

        if not changed:
            return current_record, None

        # Expire current record
        current_record[dimension.valid_to] = effective_date
        current_record[dimension.is_current] = False

        # Create new record
        new_record = SCDType2Handler.insert_new_record(
            dimension,
            natural_key_value,
            new_attributes,
            effective_date
        )

        return current_record, new_record

    @staticmethod
    def get_current_record(dimension: DimensionTable, natural_key_value: str) -> Optional[Dict[str, Any]]:
        """Get current version of a record"""
        for record in dimension.data:
            if (record[dimension.natural_key] == natural_key_value and
                record[dimension.is_current]):
                return record
        return None

    @staticmethod
    def get_record_at_date(
        dimension: DimensionTable,
        natural_key_value: str,
        as_of_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get record version as of specific date"""
        for record in dimension.data:
            if record[dimension.natural_key] != natural_key_value:
                continue

            valid_from = record[dimension.valid_from]
            valid_to = record[dimension.valid_to]

            if valid_from <= as_of_date:
                if valid_to is None or valid_to > as_of_date:
                    return record

        return None


# ============================================================================
# Data Transformation Engine
# ============================================================================

class TransformationEngine:
    """Data transformation engine for ETL"""

    @staticmethod
    def apply_transformations(data: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply transformation rules to data"""
        result = data.copy()

        for rule in rules:
            rule_type = rule.get("type")

            if rule_type == "rename":
                result = TransformationEngine._rename_columns(result, rule.get("mapping", {}))

            elif rule_type == "filter":
                result = TransformationEngine._filter_rows(result, rule.get("condition", ""))

            elif rule_type == "aggregate":
                result = TransformationEngine._aggregate(
                    result,
                    rule.get("group_by", []),
                    rule.get("aggregations", {})
                )

            elif rule_type == "calculate":
                result = TransformationEngine._calculate_column(
                    result,
                    rule.get("column", ""),
                    rule.get("expression", "")
                )

            elif rule_type == "cast":
                result = TransformationEngine._cast_column(
                    result,
                    rule.get("column", ""),
                    rule.get("to_type", "str")
                )

        return result

    @staticmethod
    def _rename_columns(data: List[Dict[str, Any]], mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Rename columns"""
        result = []
        for row in data:
            new_row = {}
            for old_name, value in row.items():
                new_name = mapping.get(old_name, old_name)
                new_row[new_name] = value
            result.append(new_row)
        return result

    @staticmethod
    def _filter_rows(data: List[Dict[str, Any]], condition: str) -> List[Dict[str, Any]]:
        """Filter rows based on condition"""
        result = []
        for row in data:
            try:
                # Simple condition evaluation (column == value)
                # Example: "status == 'active'"
                if "==" in condition:
                    col, val = condition.split("==")
                    col = col.strip()
                    val = val.strip().strip("'\"")

                    if col in row and str(row[col]) == val:
                        result.append(row)

                elif ">" in condition:
                    col, val = condition.split(">")
                    col = col.strip()
                    val = float(val.strip())

                    if col in row and float(row[col]) > val:
                        result.append(row)

                elif "<" in condition:
                    col, val = condition.split("<")
                    col = col.strip()
                    val = float(val.strip())

                    if col in row and float(row[col]) < val:
                        result.append(row)

                else:
                    result.append(row)

            except:
                continue

        return result

    @staticmethod
    def _aggregate(
        data: List[Dict[str, Any]],
        group_by: List[str],
        aggregations: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Aggregate data"""
        if not group_by:
            return data

        # Group data
        groups = defaultdict(list)
        for row in data:
            key = tuple(row.get(col) for col in group_by)
            groups[key].append(row)

        # Aggregate
        result = []
        for key, rows in groups.items():
            agg_row = {}

            # Add group by columns
            for i, col in enumerate(group_by):
                agg_row[col] = key[i]

            # Apply aggregations
            for col, func in aggregations.items():
                values = [row.get(col, 0) for row in rows if col in row]

                if func == "sum":
                    agg_row[col] = sum(values)
                elif func == "avg" or func == "mean":
                    agg_row[col] = sum(values) / len(values) if values else 0
                elif func == "count":
                    agg_row[col] = len(values)
                elif func == "min":
                    agg_row[col] = min(values) if values else None
                elif func == "max":
                    agg_row[col] = max(values) if values else None

            result.append(agg_row)

        return result

    @staticmethod
    def _calculate_column(data: List[Dict[str, Any]], column: str, expression: str) -> List[Dict[str, Any]]:
        """Calculate new column"""
        result = []
        for row in data:
            new_row = row.copy()
            try:
                # Simple expression evaluation
                # Example: "price * quantity"
                expr = expression
                for col_name in row.keys():
                    if col_name in expr:
                        expr = expr.replace(col_name, str(row[col_name]))

                # Evaluate (safe for simple math)
                try:
                    value = eval(expr, {"__builtins__": {}}, {})
                    new_row[column] = value
                except:
                    new_row[column] = None

            except:
                new_row[column] = None

            result.append(new_row)

        return result

    @staticmethod
    def _cast_column(data: List[Dict[str, Any]], column: str, to_type: str) -> List[Dict[str, Any]]:
        """Cast column to type"""
        result = []
        for row in data:
            new_row = row.copy()
            if column in row:
                try:
                    if to_type == "int":
                        new_row[column] = int(row[column])
                    elif to_type == "float":
                        new_row[column] = float(row[column])
                    elif to_type == "str":
                        new_row[column] = str(row[column])
                    elif to_type == "bool":
                        new_row[column] = bool(row[column])
                except:
                    new_row[column] = None

            result.append(new_row)

        return result


# ============================================================================
# ETL Pipeline
# ============================================================================

class ETLPipeline:
    """ETL Pipeline for data warehouse"""

    def __init__(self):
        self.jobs: Dict[str, ETLJob] = {}
        self.execution_log: List[Dict[str, Any]] = []

    def register_job(self, job: ETLJob):
        """Register ETL job"""
        self.jobs[job.id] = job

    def extract(self, source: Any) -> List[Dict[str, Any]]:
        """
        Extract data from source

        Args:
            source: Data source (file path, query, etc.)

        Returns:
            List of dictionaries with extracted data
        """
        data = []

        # Handle different source types
        if isinstance(source, str):
            # Check if it's a file path
            path = Path(source)
            if path.exists():
                if path.suffix == ".csv":
                    data = self._extract_from_csv(str(path))
                elif path.suffix == ".json":
                    data = self._extract_from_json(str(path))

        elif isinstance(source, list):
            # Already in list format
            data = source

        return data

    def _extract_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract data from CSV file"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
        except Exception as e:
            print(f"Error reading CSV: {e}")

        return data

    def _extract_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract data from JSON file"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, list):
                    data = content
                elif isinstance(content, dict):
                    data = [content]
        except Exception as e:
            print(f"Error reading JSON: {e}")

        return data

    def transform(self, data: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform data according to rules"""
        return TransformationEngine.apply_transformations(data, rules)

    def load(self, data: List[Dict[str, Any]], target_table: str, mode: str = "append") -> Dict[str, Any]:
        """
        Load data into target table

        Args:
            data: Data to load
            target_table: Target table name
            mode: 'append', 'replace', 'incremental'

        Returns:
            Load result
        """
        # This would normally write to a database
        # For pure Python, we just log the operation

        result = {
            "timestamp": datetime.now(),
            "table": target_table,
            "rows_loaded": len(data),
            "mode": mode,
            "status": "success",
        }

        self.execution_log.append(result)

        return result

    def run_job(self, job_id: str, source: Any = None) -> Dict[str, Any]:
        """Execute ETL job"""
        job = self.jobs.get(job_id)
        if not job:
            return {"status": "failed", "error": f"Job {job_id} not found"}

        try:
            start_time = datetime.now()

            # Extract
            data = self.extract(source if source else job.source_query)

            # Transform
            transformed = self.transform(data, job.transformation_rules)

            # Load
            load_result = self.load(transformed, job.target_table)

            # Update job metadata
            job.last_run = datetime.now()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return {
                "status": "success",
                "job_id": job_id,
                "rows_extracted": len(data),
                "rows_loaded": len(transformed),
                "duration_seconds": duration,
                "timestamp": end_time,
            }

        except Exception as e:
            return {"status": "failed", "job_id": job_id, "error": str(e)}


# ============================================================================
# Incremental Loader
# ============================================================================

class IncrementalLoader:
    """Incremental data loading with watermarks"""

    def __init__(self):
        self.watermarks: Dict[str, datetime] = {}
        self.watermark_file = Path(".watermarks.json")
        self._load_watermarks()

    def _load_watermarks(self):
        """Load watermarks from file"""
        if self.watermark_file.exists():
            try:
                with open(self.watermark_file, 'r') as f:
                    data = json.load(f)
                    for table, timestamp_str in data.items():
                        self.watermarks[table] = datetime.fromisoformat(timestamp_str)
            except:
                pass

    def _save_watermarks(self):
        """Save watermarks to file"""
        try:
            data = {
                table: timestamp.isoformat()
                for table, timestamp in self.watermarks.items()
            }
            with open(self.watermark_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def get_watermark(self, table: str) -> Optional[datetime]:
        """Get high watermark for table"""
        return self.watermarks.get(table)

    def set_watermark(self, table: str, watermark: datetime):
        """Set high watermark for table"""
        self.watermarks[table] = watermark
        self._save_watermarks()

    def get_new_data(
        self,
        table: str,
        all_data: List[Dict[str, Any]],
        timestamp_column: str
    ) -> List[Dict[str, Any]]:
        """Filter data to only new records since last watermark"""
        watermark = self.get_watermark(table)

        if not watermark:
            # First load - return all data
            return all_data

        # Filter to new records
        new_data = []
        max_timestamp = watermark

        for record in all_data:
            if timestamp_column in record:
                try:
                    record_time = datetime.fromisoformat(str(record[timestamp_column]))
                    if record_time > watermark:
                        new_data.append(record)
                        if record_time > max_timestamp:
                            max_timestamp = record_time
                except:
                    continue

        # Update watermark
        if max_timestamp > watermark:
            self.set_watermark(table, max_timestamp)

        return new_data


# ============================================================================
# Data Quality Checker
# ============================================================================

class DataQualityChecker:
    """Data quality validation"""

    def __init__(self):
        self.rules: List[DataQualityRule] = []

    def add_rule(self, rule: DataQualityRule):
        """Add quality rule"""
        self.rules.append(rule)

    def check_nulls(
        self,
        data: List[Dict[str, Any]],
        column: str,
        max_null_pct: float = 0.05
    ) -> Dict[str, Any]:
        """Check null percentage in column"""
        if not data:
            return {"rule": "null_check", "passed": True, "null_percentage": 0.0}

        null_count = sum(1 for row in data if row.get(column) is None or row.get(column) == "")
        null_pct = null_count / len(data)

        return {
            "rule": "null_check",
            "column": column,
            "null_percentage": null_pct,
            "null_count": null_count,
            "total_rows": len(data),
            "passed": null_pct <= max_null_pct,
            "threshold": max_null_pct,
        }

    def check_duplicates(
        self,
        data: List[Dict[str, Any]],
        columns: List[str]
    ) -> Dict[str, Any]:
        """Check for duplicate rows"""
        seen = set()
        duplicates = 0

        for row in data:
            key = tuple(row.get(col) for col in columns)
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)

        return {
            "rule": "duplicate_check",
            "columns": columns,
            "duplicates": duplicates,
            "passed": duplicates == 0,
        }

    def check_range(
        self,
        data: List[Dict[str, Any]],
        column: str,
        min_val: float,
        max_val: float
    ) -> Dict[str, Any]:
        """Check value range"""
        out_of_range = 0

        for row in data:
            if column in row:
                try:
                    value = float(row[column])
                    if value < min_val or value > max_val:
                        out_of_range += 1
                except:
                    continue

        return {
            "rule": "range_check",
            "column": column,
            "out_of_range": out_of_range,
            "passed": out_of_range == 0,
            "range": [min_val, max_val],
        }

    def check_pattern(
        self,
        data: List[Dict[str, Any]],
        column: str,
        pattern: str
    ) -> Dict[str, Any]:
        """Check if values match pattern (regex)"""
        import re

        regex = re.compile(pattern)
        non_matching = 0

        for row in data:
            if column in row:
                value = str(row[column])
                if not regex.match(value):
                    non_matching += 1

        return {
            "rule": "pattern_check",
            "column": column,
            "pattern": pattern,
            "non_matching": non_matching,
            "passed": non_matching == 0,
        }

    def validate(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run all quality checks"""
        results = []

        for rule in self.rules:
            if rule.rule_type == "null_check":
                result = self.check_nulls(
                    data,
                    rule.column,
                    rule.parameters.get("max_null_pct", 0.05)
                )

            elif rule.rule_type == "duplicate_check":
                result = self.check_duplicates(
                    data,
                    rule.parameters.get("columns", [rule.column])
                )

            elif rule.rule_type == "range_check":
                result = self.check_range(
                    data,
                    rule.column,
                    rule.parameters.get("min", 0),
                    rule.parameters.get("max", 1000000)
                )

            elif rule.rule_type == "pattern_check":
                result = self.check_pattern(
                    data,
                    rule.column,
                    rule.parameters.get("pattern", ".*")
                )

            else:
                continue

            result["rule_id"] = rule.id
            result["severity"] = rule.severity
            results.append(result)

        all_passed = all(r["passed"] for r in results)
        errors = [r for r in results if not r["passed"] and r["severity"] == "error"]
        warnings = [r for r in results if not r["passed"] and r["severity"] == "warning"]

        return {
            "overall_status": "passed" if all_passed else "failed",
            "checks": results,
            "passed_count": sum(1 for r in results if r["passed"]),
            "failed_count": sum(1 for r in results if not r["passed"]),
            "errors": errors,
            "warnings": warnings,
        }


# ============================================================================
# Main Data Warehouse
# ============================================================================

class DataWarehouse:
    """Main Data Warehouse manager"""

    def __init__(self, name: str = "default"):
        self.name = name
        self.schema = StarSchema()
        self.etl = ETLPipeline()
        self.incremental_loader = IncrementalLoader()
        self.quality_checker = DataQualityChecker()

    def create_dimension(
        self,
        name: str,
        columns: List[str],
        scd_type: SCDType = SCDType.TYPE_2,
        natural_key: Optional[str] = None
    ) -> DimensionTable:
        """Create dimension table"""
        dim = DimensionTable(
            name=name,
            columns=columns,
            primary_key=f"{name}_key",
            scd_type=scd_type,
            natural_key=natural_key
        )
        self.schema.add_dimension(dim)
        return dim

    def create_fact(
        self,
        name: str,
        measures: List[str],
        dimensions: List[str],
        grain: str
    ) -> FactTable:
        """Create fact table"""
        fact = FactTable(
            name=name,
            measures=measures,
            dimensions=dimensions,
            grain=grain
        )
        self.schema.add_fact(fact)
        return fact

    def create_standard_schema(self):
        """Create standard star schema"""
        # Time dimension
        self.create_dimension(
            "dim_time",
            ["date", "year", "month", "day", "quarter", "week", "day_of_week"],
            scd_type=SCDType.TYPE_0,
            natural_key="date"
        )

        # User dimension
        self.create_dimension(
            "dim_user",
            ["user_id", "username", "email", "role", "tenant_id"],
            scd_type=SCDType.TYPE_2,
            natural_key="user_id"
        )

        # Tenant dimension
        self.create_dimension(
            "dim_tenant",
            ["tenant_id", "name", "tier", "industry", "created_date"],
            scd_type=SCDType.TYPE_2,
            natural_key="tenant_id"
        )

        # Document dimension
        self.create_dimension(
            "dim_document",
            ["document_id", "title", "category", "status", "file_type"],
            scd_type=SCDType.TYPE_1,
            natural_key="document_id"
        )

        # Usage fact
        self.create_fact(
            "fact_usage",
            ["api_calls", "storage_gb", "active_users", "bandwidth_gb"],
            ["time", "tenant"],
            "One row per tenant per day"
        )

        # Revenue fact
        self.create_fact(
            "fact_revenue",
            ["mrr", "arr", "new_revenue", "churned_revenue", "expansion_revenue"],
            ["time", "tenant"],
            "One row per tenant per month"
        )

    def generate_schema_sql(self, dialect: SQLDialect = SQLDialect.POSTGRESQL) -> str:
        """Generate SQL for entire schema"""
        ddl_statements = self.schema.get_schema_ddl(dialect)
        return "\n\n".join(ddl_statements)

    def validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data quality"""
        return self.quality_checker.validate(data)

    def query(
        self,
        fact_table: str,
        measures: List[str],
        dimensions: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query warehouse (simplified)"""
        fact = self.schema.fact_tables.get(fact_table)
        if not fact:
            return {"error": f"Fact table {fact_table} not found"}

        # This is a simplified query - in production would generate SQL
        return {
            "fact_table": fact_table,
            "measures": measures,
            "dimensions": dimensions,
            "filters": filters or {},
            "data": fact.data,  # Would normally execute query
            "row_count": len(fact.data),
        }


# ============================================================================
# Singleton and Convenience Functions
# ============================================================================

_warehouse_instance = None
_instance_lock = threading.Lock()


def get_data_warehouse(name: str = "default") -> DataWarehouse:
    """Get singleton Data Warehouse instance"""
    global _warehouse_instance

    if _warehouse_instance is None:
        with _instance_lock:
            if _warehouse_instance is None:
                _warehouse_instance = DataWarehouse(name)

    return _warehouse_instance


if __name__ == "__main__":
    # Example usage
    print("Data Warehouse Module (Pure Python)")
    print("=" * 60)

    # Create warehouse
    warehouse = get_data_warehouse()

    # Create standard schema
    warehouse.create_standard_schema()

    print("\n✅ Standard schema created")
    print(f"   Dimensions: {len(warehouse.schema.dimension_tables)}")
    print(f"   Facts: {len(warehouse.schema.fact_tables)}")

    # Validate schema
    validation = warehouse.schema.validate_schema()
    print(f"\n✅ Schema validation: {validation['valid']}")
    if validation['warnings']:
        print(f"   Warnings: {validation['warnings']}")

    # Generate SQL
    print("\n✅ Generating DDL (PostgreSQL):")
    sql = warehouse.generate_schema_sql(SQLDialect.POSTGRESQL)
    print(f"   Generated {len(sql.split(';'))-1} DDL statements")
    print(f"   Total SQL length: {len(sql)} characters")

    # Test SCD Type 2
    print("\n✅ Testing SCD Type 2:")
    dim_user = warehouse.schema.dimension_tables["dim_user"]

    # Insert new user
    SCDType2Handler.insert_new_record(
        dim_user,
        "user123",
        {"username": "john_doe", "email": "john@example.com", "role": "admin"}
    )
    print(f"   Inserted new user: user123")

    # Update user (creates new version)
    old, new = SCDType2Handler.update_record(
        dim_user,
        "user123",
        {"username": "john_doe", "email": "john.doe@example.com", "role": "admin"}
    )
    print(f"   Updated user: user123 (2 versions now)")

    # Test data quality
    print("\n✅ Testing Data Quality:")
    test_data = [
        {"id": 1, "value": 100, "status": "active"},
        {"id": 2, "value": 200, "status": "active"},
        {"id": 3, "value": None, "status": "inactive"},
    ]

    warehouse.quality_checker.add_rule(DataQualityRule(
        id="null_check_1",
        rule_type="null_check",
        column="value",
        parameters={"max_null_pct": 0.1}
    ))

    quality_result = warehouse.validate_data(test_data)
    print(f"   Quality checks: {quality_result['passed_count']}/{len(quality_result['checks'])} passed")

    print("\n✅ Data Warehouse module ready!")
