"""
Advanced Search System

Provides full-text search with filters, sorting, and faceted search capabilities.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class SearchField(str, Enum):
    """Searchable fields"""

    ALL = "all"
    SERVICE_NAME = "service_name"
    REGION = "region"
    CATEGORY = "category"
    TAGS = "tags"
    NOTES = "notes"


class SortField(str, Enum):
    """Sort fields"""

    RELEVANCE = "relevance"
    NAME = "name"
    DATE_CREATED = "date_created"
    DATE_MODIFIED = "date_modified"
    RATE = "rate"
    HOURS = "hours"


class SortOrder(str, Enum):
    """Sort order"""

    ASC = "asc"
    DESC = "desc"


@dataclass
class SearchFilter:
    """Search filter definition"""

    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, contains, starts_with, ends_with
    value: Any


@dataclass
class DateRangeFilter:
    """Date range filter"""

    start: Optional[datetime] = None
    end: Optional[datetime] = None


@dataclass
class RangeFilter:
    """Numeric range filter"""

    min: Optional[float] = None
    max: Optional[float] = None


@dataclass
class SearchQuery:
    """Search query definition"""

    query: str = ""
    fields: List[SearchField] = None
    filters: List[SearchFilter] = None
    region_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    rate_range: Optional[RangeFilter] = None
    hours_range: Optional[RangeFilter] = None
    date_range: Optional[DateRangeFilter] = None
    tags: Optional[List[str]] = None
    sort_by: SortField = SortField.RELEVANCE
    sort_order: SortOrder = SortOrder.DESC
    limit: int = 50
    offset: int = 0
    include_inactive: bool = False

    def __post_init__(self):
        if self.fields is None:
            self.fields = [SearchField.ALL]
        if self.filters is None:
            self.filters = []


@dataclass
class SearchResult:
    """Search result item"""

    id: int
    service_name: str
    region: str
    category: Optional[str]
    brutto_rate: float
    hours_per_month: int
    date_created: datetime
    date_modified: Optional[datetime]
    tags: List[str]
    relevance_score: float
    highlights: Dict[str, List[str]]  # field -> highlighted snippets


@dataclass
class SearchResponse:
    """Search response with results and metadata"""

    results: List[SearchResult]
    total: int
    query: str
    facets: Dict[str, Dict[str, int]]  # field -> {value: count}
    suggestions: List[str]
    execution_time_ms: float


class AdvancedSearchEngine:
    """Advanced search engine with full-text search and filtering"""

    def __init__(self, database):
        self.db = database

    def search(self, search_query: SearchQuery) -> SearchResponse:
        """Execute search query"""
        import time

        start_time = time.time()

        # Build SQL query
        sql, params = self._build_query(search_query)

        # Execute query
        results = self._execute_query(sql, params)

        # Calculate relevance scores
        scored_results = self._calculate_relevance(results, search_query)

        # Sort results
        sorted_results = self._sort_results(scored_results, search_query)

        # Paginate
        paginated = sorted_results[search_query.offset : search_query.offset + search_query.limit]

        # Generate highlights
        highlighted = self._generate_highlights(paginated, search_query)

        # Calculate facets
        facets = self._calculate_facets(results)

        # Generate suggestions
        suggestions = self._generate_suggestions(search_query)

        execution_time = (time.time() - start_time) * 1000

        return SearchResponse(
            results=highlighted,
            total=len(scored_results),
            query=search_query.query,
            facets=facets,
            suggestions=suggestions,
            execution_time_ms=execution_time,
        )

    def _build_query(self, search_query: SearchQuery) -> Tuple[str, List]:
        """Build SQL query from search query"""
        conditions = []
        params = []

        # Full-text search
        if search_query.query:
            search_conditions = []
            query_lower = search_query.query.lower()

            if SearchField.ALL in search_query.fields:
                search_conditions.append("LOWER(service_name) LIKE ?")
                params.append(f"%{query_lower}%")
                search_conditions.append("LOWER(region) LIKE ?")
                params.append(f"%{query_lower}%")
            else:
                for field in search_query.fields:
                    if field == SearchField.SERVICE_NAME:
                        search_conditions.append("LOWER(service_name) LIKE ?")
                        params.append(f"%{query_lower}%")
                    elif field == SearchField.REGION:
                        search_conditions.append("LOWER(region) LIKE ?")
                        params.append(f"%{query_lower}%")

            if search_conditions:
                conditions.append(f"({' OR '.join(search_conditions)})")

        # Region filter
        if search_query.region_filter:
            placeholders = ",".join(["?" for _ in search_query.region_filter])
            conditions.append(f"region IN ({placeholders})")
            params.extend(search_query.region_filter)

        # Rate range filter
        if search_query.rate_range:
            if search_query.rate_range.min is not None:
                conditions.append("brutto_rate >= ?")
                params.append(search_query.rate_range.min)
            if search_query.rate_range.max is not None:
                conditions.append("brutto_rate <= ?")
                params.append(search_query.rate_range.max)

        # Hours range filter
        if search_query.hours_range:
            if search_query.hours_range.min is not None:
                conditions.append("hours_per_month >= ?")
                params.append(search_query.hours_range.min)
            if search_query.hours_range.max is not None:
                conditions.append("hours_per_month <= ?")
                params.append(search_query.hours_range.max)

        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
            SELECT id, service_name, region, brutto_rate, hours_per_month,
                   created_at, updated_at
            FROM services
            {where_clause}
        """

        return sql, params

    def _execute_query(self, sql: str, params: List) -> List[Dict]:
        """Execute SQL query and return results"""
        cursor = self.db.conn.cursor()
        cursor.execute(sql, params)

        columns = [col[0] for col in cursor.description]
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def _calculate_relevance(self, results: List[Dict], query: SearchQuery) -> List[Dict]:
        """Calculate relevance scores for results"""
        if not query.query:
            # No search query, all results have same relevance
            for result in results:
                result["relevance_score"] = 1.0
            return results

        query_terms = query.query.lower().split()

        for result in results:
            score = 0.0

            # Score based on field matches
            service_name = result.get("service_name", "").lower()
            region = result.get("region", "").lower()

            for term in query_terms:
                # Exact match in service name (highest weight)
                if term == service_name:
                    score += 10.0
                elif term in service_name:
                    score += 5.0

                # Match at start of service name
                if service_name.startswith(term):
                    score += 3.0

                # Match in region
                if term in region:
                    score += 2.0

            # Normalize score
            result["relevance_score"] = min(score / 10.0, 10.0)

        return results

    def _sort_results(self, results: List[Dict], query: SearchQuery) -> List[Dict]:
        """Sort results based on sort field and order"""
        sort_map = {
            SortField.RELEVANCE: "relevance_score",
            SortField.NAME: "service_name",
            SortField.DATE_CREATED: "created_at",
            SortField.DATE_MODIFIED: "updated_at",
            SortField.RATE: "brutto_rate",
            SortField.HOURS: "hours_per_month",
        }

        sort_key = sort_map.get(query.sort_by, "relevance_score")
        reverse = query.sort_order == SortOrder.DESC

        return sorted(results, key=lambda x: x.get(sort_key, 0) or 0, reverse=reverse)

    def _generate_highlights(self, results: List[Dict], query: SearchQuery) -> List[SearchResult]:
        """Generate highlighted snippets for search results"""
        highlighted_results = []

        for result in results:
            highlights = {}

            if query.query:
                # Highlight matches in service name
                service_name = result.get("service_name", "")
                highlighted_name = self._highlight_text(service_name, query.query)
                if highlighted_name != service_name:
                    highlights["service_name"] = [highlighted_name]

                # Highlight matches in region
                region = result.get("region", "")
                highlighted_region = self._highlight_text(region, query.query)
                if highlighted_region != region:
                    highlights["region"] = [highlighted_region]

            search_result = SearchResult(
                id=result["id"],
                service_name=result.get("service_name", ""),
                region=result.get("region", ""),
                category=None,
                brutto_rate=result.get("brutto_rate", 0.0),
                hours_per_month=result.get("hours_per_month", 0),
                date_created=result.get("created_at"),
                date_modified=result.get("updated_at"),
                tags=[],
                relevance_score=result.get("relevance_score", 0.0),
                highlights=highlights,
            )

            highlighted_results.append(search_result)

        return highlighted_results

    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text"""
        if not text or not query:
            return text

        terms = query.split()
        highlighted = text

        for term in terms:
            # Case-insensitive replacement with highlighting
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", highlighted)

        return highlighted

    def _calculate_facets(self, results: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Calculate facets (aggregations) for search results"""
        facets = {
            "region": {},
            "rate_ranges": {"0-30": 0, "30-40": 0, "40-50": 0, "50-60": 0, "60+": 0},
            "hours_ranges": {"0-80": 0, "80-120": 0, "120-160": 0, "160-200": 0, "200+": 0},
        }

        for result in results:
            # Region facet
            region = result.get("region", "Unknown")
            facets["region"][region] = facets["region"].get(region, 0) + 1

            # Rate range facet
            rate = result.get("brutto_rate", 0)
            if rate < 30:
                facets["rate_ranges"]["0-30"] += 1
            elif rate < 40:
                facets["rate_ranges"]["30-40"] += 1
            elif rate < 50:
                facets["rate_ranges"]["40-50"] += 1
            elif rate < 60:
                facets["rate_ranges"]["50-60"] += 1
            else:
                facets["rate_ranges"]["60+"] += 1

            # Hours range facet
            hours = result.get("hours_per_month", 0)
            if hours < 80:
                facets["hours_ranges"]["0-80"] += 1
            elif hours < 120:
                facets["hours_ranges"]["80-120"] += 1
            elif hours < 160:
                facets["hours_ranges"]["120-160"] += 1
            elif hours < 200:
                facets["hours_ranges"]["160-200"] += 1
            else:
                facets["hours_ranges"]["200+"] += 1

        return facets

    def _generate_suggestions(self, query: SearchQuery) -> List[str]:
        """Generate search suggestions based on query"""
        suggestions = []

        if not query.query:
            return suggestions

        # Simple suggestions based on common terms
        common_terms = [
            "shopping",
            "cleaning",
            "cooking",
            "transport",
            "care",
            "nursing",
            "therapy",
            "medication",
            "mobility",
            "companionship",
        ]

        query_lower = query.query.lower()

        for term in common_terms:
            if term.startswith(query_lower) and term != query_lower:
                suggestions.append(term)

        return suggestions[:5]


def get_search_engine(database) -> AdvancedSearchEngine:
    """Get search engine instance"""
    return AdvancedSearchEngine(database)
