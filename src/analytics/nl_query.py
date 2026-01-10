#!/usr/bin/env python3
"""
Natural Language Query Module

Converts natural language queries to structured database queries
with intent recognition and entity extraction.

Key Features:
- Intent classification (aggregate, filter, sort, compare, trend)
- Entity extraction (metrics, dimensions, time ranges, values)
- Query generation (SQL, aggregation pipelines)
- Conversation context management
- Query templates and patterns
- Multi-language support (basic)

Dependencies:
- re for pattern matching
- datetime for date parsing
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    """Query intent types"""
    AGGREGATE = "aggregate"  # Sum, average, count
    FILTER = "filter"  # Find records matching criteria
    SORT = "sort"  # Sort by field
    COMPARE = "compare"  # Compare values
    TREND = "trend"  # Show trends over time
    TOP_N = "top_n"  # Top/bottom N items
    FORECAST = "forecast"  # Predict future values
    ANOMALY = "anomaly"  # Find anomalies


class AggregateFunction(str, Enum):
    """Aggregate functions"""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class TimeGranularity(str, Enum):
    """Time granularity for grouping"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class Entity:
    """Extracted entity"""
    entity_type: str  # metric, dimension, value, time, etc.
    value: str
    normalized_value: Optional[Any] = None
    confidence: float = 1.0


@dataclass
class TimeRange:
    """Time range for query"""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    relative: Optional[str] = None  # "last 7 days", "this month", etc.

    def to_absolute(self) -> Tuple[datetime, datetime]:
        """Convert to absolute datetime range"""
        if self.start and self.end:
            return self.start, self.end

        if self.relative:
            return self._parse_relative()

        # Default to last 30 days
        end = datetime.now()
        start = end - timedelta(days=30)
        return start, end

    def _parse_relative(self) -> Tuple[datetime, datetime]:
        """Parse relative time expression"""
        end = datetime.now()

        if "today" in self.relative.lower():
            start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        elif "yesterday" in self.relative.lower():
            start = end - timedelta(days=1)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif "week" in self.relative.lower():
            # Extract number
            match = re.search(r'(\d+)', self.relative)
            days = int(match.group(1)) * 7 if match else 7
            start = end - timedelta(days=days)
        elif "month" in self.relative.lower():
            match = re.search(r'(\d+)', self.relative)
            months = int(match.group(1)) if match else 1
            start = end - timedelta(days=months * 30)
        elif "year" in self.relative.lower():
            match = re.search(r'(\d+)', self.relative)
            years = int(match.group(1)) if match else 1
            start = end - timedelta(days=years * 365)
        else:
            # Default to last 30 days
            start = end - timedelta(days=30)

        return start, end


@dataclass
class ParsedQuery:
    """Parsed natural language query"""
    original_query: str
    intent: QueryIntent
    entities: List[Entity] = field(default_factory=list)
    metric: Optional[str] = None
    aggregate_function: Optional[AggregateFunction] = None
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    time_range: Optional[TimeRange] = None
    time_granularity: Optional[TimeGranularity] = None
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    confidence: float = 1.0


class IntentClassifier:
    """
    Classifies query intent from natural language

    Uses pattern matching and keyword analysis.
    """

    def __init__(self):
        self._intent_patterns = {
            QueryIntent.AGGREGATE: [
                r'\b(total|sum|average|mean|count|number)\b',
                r'\bhow (many|much)\b',
                r'\bwhat (is|are) the (total|average|sum)\b',
            ],
            QueryIntent.FILTER: [
                r'\b(show|list|find|get|display)\b.*\bwhere\b',
                r'\bwith\b.*\b(greater|less|equal|above|below)\b',
                r'\b(customers|users|transactions) (with|that|who)\b',
            ],
            QueryIntent.SORT: [
                r'\b(sort|order|rank)\b',
                r'\b(highest|lowest|best|worst)\b',
                r'\b(top|bottom)\b',
            ],
            QueryIntent.COMPARE: [
                r'\bcompare\b',
                r'\b(versus|vs|compared to)\b',
                r'\bdifference between\b',
            ],
            QueryIntent.TREND: [
                r'\btrend\b',
                r'\bover time\b',
                r'\b(growth|decline)\b',
                r'\bhow .* (changed|evolved)\b',
            ],
            QueryIntent.TOP_N: [
                r'\btop \d+\b',
                r'\bbottom \d+\b',
                r'\b(best|worst) \d+\b',
            ],
            QueryIntent.FORECAST: [
                r'\bforecast\b',
                r'\bpredict\b',
                r'\bexpected\b',
                r'\bnext (week|month|quarter|year)\b',
            ],
            QueryIntent.ANOMALY: [
                r'\banomaly\b',
                r'\bunusual\b',
                r'\boutlier\b',
                r'\bspike\b',
            ],
        }

    def classify(self, query: str) -> Tuple[QueryIntent, float]:
        """
        Classify query intent

        Args:
            query: Natural language query

        Returns:
            Tuple of (intent, confidence)
        """
        query_lower = query.lower()
        scores = defaultdict(float)

        for intent, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    scores[intent] += 1.0

        if not scores:
            return QueryIntent.FILTER, 0.5  # Default intent

        best_intent = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_intent[1] / 2.0, 1.0)  # Normalize confidence

        return best_intent[0], confidence


class EntityExtractor:
    """
    Extracts entities from natural language queries

    Identifies metrics, dimensions, values, time ranges, etc.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        self.schema = schema or self._default_schema()

        # Build metric patterns from schema
        self._metric_keywords = self.schema.get("metrics", [])
        self._dimension_keywords = self.schema.get("dimensions", [])

        # Common time expressions
        self._time_patterns = [
            (r'\b(last|past) (\d+) (day|week|month|year)s?\b', 'relative'),
            (r'\btoday\b', 'relative'),
            (r'\byesterday\b', 'relative'),
            (r'\bthis (week|month|quarter|year)\b', 'relative'),
            (r'\b(\d{4})-(\d{2})-(\d{2})\b', 'absolute'),
        ]

    def _default_schema(self) -> Dict[str, Any]:
        """Default data schema"""
        return {
            "metrics": [
                "revenue", "sales", "profit", "cost", "price",
                "users", "customers", "transactions", "orders",
                "churn", "retention", "conversion", "engagement"
            ],
            "dimensions": [
                "product", "category", "region", "country", "city",
                "customer", "user", "segment", "channel", "source",
                "date", "time", "day", "month", "year"
            ]
        }

    def extract(self, query: str) -> List[Entity]:
        """
        Extract entities from query

        Args:
            query: Natural language query

        Returns:
            List of extracted entities
        """
        entities = []
        query_lower = query.lower()

        # Extract metrics
        for metric in self._metric_keywords:
            if metric.lower() in query_lower:
                entities.append(Entity(
                    entity_type="metric",
                    value=metric,
                    normalized_value=metric.lower().replace(" ", "_"),
                    confidence=0.9
                ))

        # Extract dimensions
        for dimension in self._dimension_keywords:
            if dimension.lower() in query_lower:
                entities.append(Entity(
                    entity_type="dimension",
                    value=dimension,
                    normalized_value=dimension.lower().replace(" ", "_"),
                    confidence=0.9
                ))

        # Extract time expressions
        for pattern, time_type in self._time_patterns:
            match = re.search(pattern, query_lower)
            if match:
                entities.append(Entity(
                    entity_type="time",
                    value=match.group(0),
                    normalized_value=time_type,
                    confidence=0.95
                ))

        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query)
        for num in numbers:
            entities.append(Entity(
                entity_type="number",
                value=num,
                normalized_value=float(num),
                confidence=1.0
            ))

        # Extract aggregate functions
        agg_patterns = {
            AggregateFunction.SUM: r'\b(total|sum)\b',
            AggregateFunction.AVG: r'\b(average|mean|avg)\b',
            AggregateFunction.COUNT: r'\b(count|number)\b',
            AggregateFunction.MIN: r'\b(minimum|min|lowest)\b',
            AggregateFunction.MAX: r'\b(maximum|max|highest)\b',
        }

        for agg_func, pattern in agg_patterns.items():
            if re.search(pattern, query_lower):
                entities.append(Entity(
                    entity_type="aggregate_function",
                    value=agg_func.value,
                    normalized_value=agg_func,
                    confidence=0.95
                ))

        return entities


class QueryGenerator:
    """
    Generates structured queries from parsed NL queries

    Supports SQL and aggregation pipeline generation.
    """

    def generate_sql(self, parsed_query: ParsedQuery) -> str:
        """
        Generate SQL query

        Args:
            parsed_query: Parsed query

        Returns:
            SQL query string
        """
        # SELECT clause
        if parsed_query.aggregate_function and parsed_query.metric:
            agg = parsed_query.aggregate_function.value.upper()
            select = f"SELECT {agg}({parsed_query.metric})"

            if parsed_query.dimensions:
                select += ", " + ", ".join(parsed_query.dimensions)
        else:
            select = "SELECT *"

        # FROM clause (simplified - would need table name from schema)
        from_clause = "FROM data"

        # WHERE clause
        where_parts = []
        if parsed_query.time_range:
            start, end = parsed_query.time_range.to_absolute()
            where_parts.append(f"timestamp >= '{start.isoformat()}'")
            where_parts.append(f"timestamp < '{end.isoformat()}'")

        for key, value in parsed_query.filters.items():
            if isinstance(value, str):
                where_parts.append(f"{key} = '{value}'")
            else:
                where_parts.append(f"{key} = {value}")

        where_clause = ""
        if where_parts:
            where_clause = "WHERE " + " AND ".join(where_parts)

        # GROUP BY clause
        group_by = ""
        if parsed_query.dimensions:
            group_by = "GROUP BY " + ", ".join(parsed_query.dimensions)

        # ORDER BY clause
        order_by = ""
        if parsed_query.sort_by:
            order_by = f"ORDER BY {parsed_query.sort_by} {parsed_query.sort_order.upper()}"

        # LIMIT clause
        limit = ""
        if parsed_query.limit:
            limit = f"LIMIT {parsed_query.limit}"

        # Combine clauses
        parts = [select, from_clause, where_clause, group_by, order_by, limit]
        sql = " ".join(p for p in parts if p)

        return sql

    def generate_aggregation_pipeline(self, parsed_query: ParsedQuery) -> List[Dict[str, Any]]:
        """
        Generate aggregation pipeline (MongoDB-style)

        Args:
            parsed_query: Parsed query

        Returns:
            List of pipeline stages
        """
        pipeline = []

        # $match stage (filters)
        match_stage = {}

        if parsed_query.time_range:
            start, end = parsed_query.time_range.to_absolute()
            match_stage["timestamp"] = {
                "$gte": start,
                "$lt": end
            }

        if parsed_query.filters:
            match_stage.update(parsed_query.filters)

        if match_stage:
            pipeline.append({"$match": match_stage})

        # $group stage (aggregation)
        if parsed_query.aggregate_function and parsed_query.metric:
            group_stage = {"_id": {}}

            # Group by dimensions
            for dim in parsed_query.dimensions:
                group_stage["_id"][dim] = f"${dim}"

            # Aggregation
            agg_op = f"${parsed_query.aggregate_function.value}"
            group_stage[parsed_query.metric] = {
                agg_op: f"${parsed_query.metric}"
            }

            pipeline.append({"$group": group_stage})

        # $sort stage
        if parsed_query.sort_by:
            sort_order = -1 if parsed_query.sort_order == "desc" else 1
            pipeline.append({"$sort": {parsed_query.sort_by: sort_order}})

        # $limit stage
        if parsed_query.limit:
            pipeline.append({"$limit": parsed_query.limit})

        return pipeline


class NLQueryProcessor:
    """
    Natural Language Query Processor

    Main interface for NL query processing.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor(schema)
        self.query_generator = QueryGenerator()
        self._conversation_context: List[ParsedQuery] = []

    def process(self, query: str) -> ParsedQuery:
        """
        Process natural language query

        Args:
            query: Natural language query string

        Returns:
            ParsedQuery object
        """
        # Classify intent
        intent, confidence = self.intent_classifier.classify(query)

        # Extract entities
        entities = self.entity_extractor.extract(query)

        # Build parsed query
        parsed = ParsedQuery(
            original_query=query,
            intent=intent,
            entities=entities,
            confidence=confidence
        )

        # Extract specific fields from entities
        for entity in entities:
            if entity.entity_type == "metric":
                parsed.metric = entity.normalized_value
            elif entity.entity_type == "dimension":
                parsed.dimensions.append(entity.normalized_value)
            elif entity.entity_type == "aggregate_function":
                parsed.aggregate_function = entity.normalized_value
            elif entity.entity_type == "time":
                if not parsed.time_range:
                    parsed.time_range = TimeRange(relative=entity.value)

        # Extract limit (for top N queries)
        if intent == QueryIntent.TOP_N:
            top_match = re.search(r'(top|bottom|best|worst) (\d+)', query.lower())
            if top_match:
                parsed.limit = int(top_match.group(2))
                parsed.sort_order = "desc" if top_match.group(1) in ["top", "best"] else "asc"

        # Store in conversation context
        self._conversation_context.append(parsed)

        logger.info(f"Processed query: {query} -> Intent: {intent}, Confidence: {confidence:.2f}")

        return parsed

    def to_sql(self, query: str) -> str:
        """
        Convert NL query to SQL

        Args:
            query: Natural language query

        Returns:
            SQL query string
        """
        parsed = self.process(query)
        return self.query_generator.generate_sql(parsed)

    def to_aggregation_pipeline(self, query: str) -> List[Dict[str, Any]]:
        """
        Convert NL query to aggregation pipeline

        Args:
            query: Natural language query

        Returns:
            Aggregation pipeline
        """
        parsed = self.process(query)
        return self.query_generator.generate_aggregation_pipeline(parsed)

    def get_conversation_context(self) -> List[ParsedQuery]:
        """Get conversation history"""
        return self._conversation_context.copy()


# Singleton instance
_nl_processor_instance = None
_instance_lock = threading.Lock()


def get_nl_processor(schema: Optional[Dict[str, Any]] = None) -> NLQueryProcessor:
    """Get singleton NL Query Processor instance"""
    global _nl_processor_instance

    if _nl_processor_instance is None:
        import threading
        with _instance_lock:
            if _nl_processor_instance is None:
                _nl_processor_instance = NLQueryProcessor(schema)

    return _nl_processor_instance


if __name__ == "__main__":
    import threading

    # Example usage
    processor = get_nl_processor()

    # Test queries
    queries = [
        "What is the total revenue for last month?",
        "Show me the top 10 customers by sales",
        "How has user engagement changed over time?",
        "Find all transactions greater than 1000",
        "Compare revenue between this year and last year",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        parsed = processor.process(query)
        print(f"Intent: {parsed.intent}")
        print(f"Confidence: {parsed.confidence:.2f}")
        print(f"Metric: {parsed.metric}")
        print(f"Aggregate: {parsed.aggregate_function}")
        print(f"Dimensions: {parsed.dimensions}")

        # Generate SQL
        sql = processor.to_sql(query)
        print(f"SQL: {sql}")

        # Generate aggregation pipeline
        pipeline = processor.to_aggregation_pipeline(query)
        print(f"Pipeline: {pipeline}")

    print("\nNatural Language Query module loaded successfully!")
