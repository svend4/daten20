"""
ETL (Extract, Transform, Load) Pipeline Engine

Provides data pipeline capabilities:
- Data extraction from multiple sources
- Data transformation and cleansing
- Data loading to targets
- Pipeline orchestration
- Error handling and logging
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class DataSource(str, Enum):
    """Data source types"""

    DATABASE = "database"
    CSV_FILE = "csv_file"
    JSON_FILE = "json_file"
    API = "api"
    S3_BUCKET = "s3_bucket"
    FTP = "ftp"
    SFTP = "sftp"


class TransformationType(str, Enum):
    """Transformation types"""

    MAP_FIELDS = "map_fields"
    FILTER_ROWS = "filter_rows"
    AGGREGATE = "aggregate"
    JOIN = "join"
    PIVOT = "pivot"
    NORMALIZE = "normalize"
    CUSTOM_FUNCTION = "custom_function"


class PipelineStatus(str, Enum):
    """Pipeline execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ExtractConfig:
    """Extraction configuration"""

    source_type: DataSource
    connection_string: str
    query: Optional[str] = None
    file_path: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformStep:
    """Transformation step"""

    id: str
    type: TransformationType
    config: Dict[str, Any]
    enabled: bool = True


@dataclass
class LoadConfig:
    """Load configuration"""

    target_type: DataSource
    connection_string: str
    table_name: Optional[str] = None
    file_path: Optional[str] = None
    mode: str = "append"  # append, replace, upsert
    batch_size: int = 1000


@dataclass
class ETLPipeline:
    """ETL Pipeline definition"""

    id: str
    name: str
    description: str
    extract_config: ExtractConfig
    transform_steps: List[TransformStep]
    load_config: LoadConfig
    schedule: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineExecution:
    """Pipeline execution record"""

    id: str
    pipeline_id: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    rows_extracted: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    errors: List[str] = field(default_factory=list)


class ETLEngine:
    """Main ETL pipeline engine"""

    def __init__(self, database=None):
        self.database = database
        self.pipelines: Dict[str, ETLPipeline] = {}
        self.executions: List[PipelineExecution] = []

    def create_pipeline(
        self,
        name: str,
        description: str,
        extract_config: ExtractConfig,
        transform_steps: List[TransformStep],
        load_config: LoadConfig,
    ) -> str:
        """Create ETL pipeline"""
        pipeline_id = str(uuid.uuid4())

        pipeline = ETLPipeline(
            id=pipeline_id,
            name=name,
            description=description,
            extract_config=extract_config,
            transform_steps=transform_steps,
            load_config=load_config,
        )

        self.pipelines[pipeline_id] = pipeline
        return pipeline_id

    def execute_pipeline(self, pipeline_id: str) -> str:
        """Execute ETL pipeline"""
        if pipeline_id not in self.pipelines:
            return ""

        pipeline = self.pipelines[pipeline_id]

        execution_id = str(uuid.uuid4())
        execution = PipelineExecution(
            id=execution_id, pipeline_id=pipeline_id, status=PipelineStatus.RUNNING, started_at=datetime.now()
        )

        self.executions.append(execution)

        try:
            # Extract
            data = self._extract_data(pipeline.extract_config)
            execution.rows_extracted = len(data)

            # Transform
            for step in pipeline.transform_steps:
                if step.enabled:
                    data = self._transform_data(data, step)

            execution.rows_transformed = len(data)

            # Load
            loaded = self._load_data(data, pipeline.load_config)
            execution.rows_loaded = loaded

            execution.status = PipelineStatus.COMPLETED
            execution.completed_at = datetime.now()

        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.errors.append(str(e))
            execution.completed_at = datetime.now()

        return execution_id

    def _extract_data(self, config: ExtractConfig) -> List[Dict[str, Any]]:
        """Extract data from source"""
        print(f"[ETL] Extracting from {config.source_type}")

        # Simulated extraction
        return [{"id": i, "value": f"data_{i}"} for i in range(100)]

    def _transform_data(self, data: List[Dict[str, Any]], step: TransformStep) -> List[Dict[str, Any]]:
        """Transform data"""
        print(f"[ETL] Transforming with {step.type}")

        if step.type == TransformationType.FILTER_ROWS:
            # Filter rows based on condition
            condition = step.config.get("condition", lambda x: True)
            return [row for row in data if condition(row)]

        elif step.type == TransformationType.MAP_FIELDS:
            # Map fields
            mapping = step.config.get("mapping", {})
            return [{mapping.get(k, k): v for k, v in row.items()} for row in data]

        return data

    def _load_data(self, data: List[Dict[str, Any]], config: LoadConfig) -> int:
        """Load data to target"""
        print(f"[ETL] Loading to {config.target_type}")

        # Simulated load
        return len(data)

    def get_statistics(self) -> Dict[str, Any]:
        """Get ETL statistics"""
        total_executions = len(self.executions)
        successful = len([e for e in self.executions if e.status == PipelineStatus.COMPLETED])

        return {
            "total_pipelines": len(self.pipelines),
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": total_executions - successful,
        }


# Global instance
_etl_engine: Optional[ETLEngine] = None


def get_etl_engine(database=None) -> ETLEngine:
    """Get global ETL engine instance"""
    global _etl_engine

    if _etl_engine is None:
        _etl_engine = ETLEngine(database)

    return _etl_engine
