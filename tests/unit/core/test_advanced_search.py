"""
Tests for Advanced Search Module
"""

import re
from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from src.core.advanced_search import (
    AdvancedSearchEngine,
    DateRangeFilter,
    RangeFilter,
    SearchField,
    SearchFilter,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SortField,
    SortOrder,
    get_search_engine,
)


class TestEnums:
    """Test enum classes"""

    def test_search_field_enum(self):
        """Test SearchField enum values"""
        assert SearchField.ALL == "all"
        assert SearchField.SERVICE_NAME == "service_name"
        assert SearchField.REGION == "region"
        assert SearchField.CATEGORY == "category"
        assert SearchField.TAGS == "tags"
        assert SearchField.NOTES == "notes"

    def test_sort_field_enum(self):
        """Test SortField enum values"""
        assert SortField.RELEVANCE == "relevance"
        assert SortField.NAME == "name"
        assert SortField.DATE_CREATED == "date_created"
        assert SortField.DATE_MODIFIED == "date_modified"
        assert SortField.RATE == "rate"
        assert SortField.HOURS == "hours"

    def test_sort_order_enum(self):
        """Test SortOrder enum values"""
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"


class TestDataClasses:
    """Test data classes"""

    def test_search_filter_creation(self):
        """Test SearchFilter creation"""
        filter_obj = SearchFilter(field="region", operator="eq", value="EU")
        assert filter_obj.field == "region"
        assert filter_obj.operator == "eq"
        assert filter_obj.value == "EU"

    def test_date_range_filter_creation(self):
        """Test DateRangeFilter creation"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        filter_obj = DateRangeFilter(start=start, end=end)
        assert filter_obj.start == start
        assert filter_obj.end == end

    def test_date_range_filter_optional(self):
        """Test DateRangeFilter with None values"""
        filter_obj = DateRangeFilter()
        assert filter_obj.start is None
        assert filter_obj.end is None

    def test_range_filter_creation(self):
        """Test RangeFilter creation"""
        filter_obj = RangeFilter(min=30.0, max=50.0)
        assert filter_obj.min == 30.0
        assert filter_obj.max == 50.0

    def test_range_filter_optional(self):
        """Test RangeFilter with None values"""
        filter_obj = RangeFilter()
        assert filter_obj.min is None
        assert filter_obj.max is None

    def test_search_query_defaults(self):
        """Test SearchQuery default values"""
        query = SearchQuery()
        assert query.query == ""
        assert query.fields == [SearchField.ALL]
        assert query.filters == []
        assert query.sort_by == SortField.RELEVANCE
        assert query.sort_order == SortOrder.DESC
        assert query.limit == 50
        assert query.offset == 0
        assert query.include_inactive is False

    def test_search_query_custom(self):
        """Test SearchQuery with custom values"""
        query = SearchQuery(
            query="test",
            fields=[SearchField.SERVICE_NAME],
            limit=10,
            offset=20,
            sort_by=SortField.NAME,
            sort_order=SortOrder.ASC,
        )
        assert query.query == "test"
        assert query.fields == [SearchField.SERVICE_NAME]
        assert query.limit == 10
        assert query.offset == 20
        assert query.sort_by == SortField.NAME
        assert query.sort_order == SortOrder.ASC

    def test_search_result_creation(self):
        """Test SearchResult creation"""
        result = SearchResult(
            id=1,
            service_name="Test Service",
            region="EU",
            category="Care",
            brutto_rate=45.0,
            hours_per_month=160,
            date_created=datetime(2024, 1, 1),
            date_modified=datetime(2024, 1, 15),
            tags=["tag1", "tag2"],
            relevance_score=8.5,
            highlights={"service_name": ["<mark>Test</mark> Service"]},
        )
        assert result.id == 1
        assert result.service_name == "Test Service"
        assert result.region == "EU"
        assert result.relevance_score == 8.5
        assert "service_name" in result.highlights

    def test_search_response_creation(self):
        """Test SearchResponse creation"""
        response = SearchResponse(results=[], total=0, query="test", facets={}, suggestions=[], execution_time_ms=15.5)
        assert response.total == 0
        assert response.query == "test"
        assert response.execution_time_ms == 15.5


class TestAdvancedSearchEngine:
    """Test AdvancedSearchEngine class"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = Mock()
        db.conn = Mock()
        return db

    @pytest.fixture
    def search_engine(self, mock_db):
        """Create search engine instance"""
        return AdvancedSearchEngine(mock_db)

    @pytest.fixture
    def sample_services(self):
        """Sample services data"""
        return [
            {
                "id": 1,
                "service_name": "Shopping Service",
                "region": "EU",
                "brutto_rate": 35.0,
                "hours_per_month": 160,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-15T00:00:00",
                "relevance_score": 0.0,
            },
            {
                "id": 2,
                "service_name": "Cleaning Service",
                "region": "US",
                "brutto_rate": 45.0,
                "hours_per_month": 120,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-16T00:00:00",
                "relevance_score": 0.0,
            },
            {
                "id": 3,
                "service_name": "Cooking Service",
                "region": "EU",
                "brutto_rate": 55.0,
                "hours_per_month": 180,
                "created_at": "2024-01-03T00:00:00",
                "updated_at": "2024-01-17T00:00:00",
                "relevance_score": 0.0,
            },
            {
                "id": 4,
                "service_name": "Transport Service",
                "region": "APAC",
                "brutto_rate": 65.0,
                "hours_per_month": 200,
                "created_at": "2024-01-04T00:00:00",
                "updated_at": "2024-01-18T00:00:00",
                "relevance_score": 0.0,
            },
            {
                "id": 5,
                "service_name": "Care Service",
                "region": "EU",
                "brutto_rate": 25.0,
                "hours_per_month": 140,
                "created_at": "2024-01-05T00:00:00",
                "updated_at": "2024-01-19T00:00:00",
                "relevance_score": 0.0,
            },
        ]

    def test_init(self, mock_db):
        """Test initialization"""
        engine = AdvancedSearchEngine(mock_db)
        assert engine.db == mock_db

    def test_search_empty_query(self, search_engine, mock_db, sample_services):
        """Test search with empty query"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery()
        response = search_engine.search(query)

        assert isinstance(response, SearchResponse)
        assert response.total == 5
        assert len(response.results) == 5
        assert response.execution_time_ms >= 0

    def test_search_with_query(self, search_engine, mock_db):
        """Test search with text query"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [
            (1, "Shopping Service", "EU", 35.0, 160, "2024-01-01", "2024-01-15"),
            (2, "Shopping Cart", "US", 45.0, 120, "2024-01-02", "2024-01-16"),
        ]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(query="shopping")
        response = search_engine.search(query)

        assert response.total == 2
        assert all("shopping" in r.service_name.lower() for r in response.results)

    def test_search_with_region_filter(self, search_engine, mock_db, sample_services):
        """Test search with region filter"""
        eu_services = [s for s in sample_services if s["region"] == "EU"]
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in eu_services]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(region_filter=["EU"])
        response = search_engine.search(query)

        assert all(r.region == "EU" for r in response.results)

    def test_search_with_rate_range(self, search_engine, mock_db, sample_services):
        """Test search with rate range filter"""
        filtered = [s for s in sample_services if 30 <= s["brutto_rate"] <= 50]
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in filtered]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(rate_range=RangeFilter(min=30.0, max=50.0))
        response = search_engine.search(query)

        assert all(30 <= r.brutto_rate <= 50 for r in response.results)

    def test_search_with_hours_range(self, search_engine, mock_db, sample_services):
        """Test search with hours range filter"""
        filtered = [s for s in sample_services if 140 <= s["hours_per_month"] <= 180]
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in filtered]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(hours_range=RangeFilter(min=140, max=180))
        response = search_engine.search(query)

        assert all(140 <= r.hours_per_month <= 180 for r in response.results)

    def test_search_with_pagination(self, search_engine, mock_db, sample_services):
        """Test search with pagination"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(limit=2, offset=1)
        response = search_engine.search(query)

        assert len(response.results) == 2
        assert response.total == 5

    def test_search_with_sorting(self, search_engine, mock_db, sample_services):
        """Test search with sorting"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        # Sort by rate ascending
        query = SearchQuery(sort_by=SortField.RATE, sort_order=SortOrder.ASC, limit=10)
        response = search_engine.search(query)

        rates = [r.brutto_rate for r in response.results]
        assert rates == sorted(rates)

    def test_build_query_empty(self, search_engine):
        """Test _build_query with empty query"""
        query = SearchQuery()
        sql, params = search_engine._build_query(query)

        assert "SELECT" in sql
        assert "FROM services" in sql
        assert len(params) == 0

    def test_build_query_with_text(self, search_engine):
        """Test _build_query with text query"""
        query = SearchQuery(query="shopping")
        sql, params = search_engine._build_query(query)

        assert "WHERE" in sql
        assert "LIKE" in sql
        assert len(params) > 0
        assert any("shopping" in str(p) for p in params)

    def test_build_query_with_specific_field(self, search_engine):
        """Test _build_query with specific field"""
        query = SearchQuery(query="service", fields=[SearchField.SERVICE_NAME])
        sql, params = search_engine._build_query(query)

        assert "service_name" in sql.lower()
        assert "LIKE" in sql

    def test_build_query_with_region_filter(self, search_engine):
        """Test _build_query with region filter"""
        query = SearchQuery(region_filter=["EU", "US"])
        sql, params = search_engine._build_query(query)

        assert "region IN" in sql
        assert len(params) == 2
        assert "EU" in params
        assert "US" in params

    def test_build_query_with_rate_range(self, search_engine):
        """Test _build_query with rate range"""
        query = SearchQuery(rate_range=RangeFilter(min=30.0, max=50.0))
        sql, params = search_engine._build_query(query)

        assert "brutto_rate" in sql
        assert ">=" in sql
        assert "<=" in sql
        assert 30.0 in params
        assert 50.0 in params

    def test_build_query_with_hours_range(self, search_engine):
        """Test _build_query with hours range"""
        query = SearchQuery(hours_range=RangeFilter(min=120, max=180))
        sql, params = search_engine._build_query(query)

        assert "hours_per_month" in sql
        assert 120 in params
        assert 180 in params

    def test_execute_query(self, search_engine, mock_db):
        """Test _execute_query"""
        cursor = MagicMock()
        cursor.description = [("id",), ("name",)]
        cursor.fetchall.return_value = [(1, "Test"), (2, "Test2")]
        mock_db.conn.cursor.return_value = cursor

        results = search_engine._execute_query("SELECT * FROM services", [])

        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["name"] == "Test"

    def test_calculate_relevance_no_query(self, search_engine):
        """Test _calculate_relevance with no query"""
        results = [{"service_name": "Test", "region": "EU"}, {"service_name": "Test2", "region": "US"}]
        query = SearchQuery()

        scored = search_engine._calculate_relevance(results, query)

        assert all(r["relevance_score"] == 1.0 for r in scored)

    def test_calculate_relevance_with_query(self, search_engine):
        """Test _calculate_relevance with query"""
        results = [
            {"service_name": "Shopping Service", "region": "EU"},
            {"service_name": "Cleaning Service", "region": "US"},
            {"service_name": "Shopping", "region": "APAC"},
        ]
        query = SearchQuery(query="shopping")

        scored = search_engine._calculate_relevance(results, query)

        # "Shopping" exact match should have highest score
        shopping_scores = [r["relevance_score"] for r in scored if "shopping" in r["service_name"].lower()]
        assert max(shopping_scores) > 0

    def test_calculate_relevance_exact_match(self, search_engine):
        """Test relevance scoring for exact match"""
        results = [{"service_name": "shopping", "region": "EU"}, {"service_name": "shopping service", "region": "US"}]
        query = SearchQuery(query="shopping")

        scored = search_engine._calculate_relevance(results, query)

        # Exact match should have higher score
        assert scored[0]["relevance_score"] > scored[1]["relevance_score"]

    def test_calculate_relevance_start_match(self, search_engine):
        """Test relevance scoring for start match"""
        results = [
            {"service_name": "shopping service", "region": "EU"},
            {"service_name": "online shopping", "region": "US"},
        ]
        query = SearchQuery(query="shopping")

        scored = search_engine._calculate_relevance(results, query)

        # Start match should have higher score
        assert scored[0]["relevance_score"] > scored[1]["relevance_score"]

    def test_sort_results_by_relevance(self, search_engine):
        """Test _sort_results by relevance"""
        results = [
            {"service_name": "A", "relevance_score": 5.0},
            {"service_name": "B", "relevance_score": 8.0},
            {"service_name": "C", "relevance_score": 3.0},
        ]
        query = SearchQuery(sort_by=SortField.RELEVANCE, sort_order=SortOrder.DESC)

        sorted_results = search_engine._sort_results(results, query)

        scores = [r["relevance_score"] for r in sorted_results]
        assert scores == [8.0, 5.0, 3.0]

    def test_sort_results_by_name(self, search_engine):
        """Test _sort_results by name"""
        results = [
            {"service_name": "Zebra", "relevance_score": 1.0},
            {"service_name": "Apple", "relevance_score": 1.0},
            {"service_name": "Mango", "relevance_score": 1.0},
        ]
        query = SearchQuery(sort_by=SortField.NAME, sort_order=SortOrder.ASC)

        sorted_results = search_engine._sort_results(results, query)

        names = [r["service_name"] for r in sorted_results]
        assert names == ["Apple", "Mango", "Zebra"]

    def test_sort_results_by_rate(self, search_engine):
        """Test _sort_results by rate"""
        results = [
            {"service_name": "A", "brutto_rate": 50.0, "relevance_score": 1.0},
            {"service_name": "B", "brutto_rate": 30.0, "relevance_score": 1.0},
            {"service_name": "C", "brutto_rate": 70.0, "relevance_score": 1.0},
        ]
        query = SearchQuery(sort_by=SortField.RATE, sort_order=SortOrder.ASC)

        sorted_results = search_engine._sort_results(results, query)

        rates = [r["brutto_rate"] for r in sorted_results]
        assert rates == [30.0, 50.0, 70.0]

    def test_generate_highlights_no_query(self, search_engine):
        """Test _generate_highlights without query"""
        results = [
            {
                "id": 1,
                "service_name": "Test",
                "region": "EU",
                "brutto_rate": 50.0,
                "hours_per_month": 160,
                "created_at": "2024-01-01",
                "updated_at": "2024-01-01",
                "relevance_score": 1.0,
            }
        ]
        query = SearchQuery()

        highlighted = search_engine._generate_highlights(results, query)

        assert len(highlighted) == 1
        assert highlighted[0].highlights == {}

    def test_generate_highlights_with_query(self, search_engine):
        """Test _generate_highlights with query"""
        results = [
            {
                "id": 1,
                "service_name": "Shopping Service",
                "region": "EU",
                "brutto_rate": 50.0,
                "hours_per_month": 160,
                "created_at": "2024-01-01",
                "updated_at": "2024-01-01",
                "relevance_score": 5.0,
            }
        ]
        query = SearchQuery(query="shopping")

        highlighted = search_engine._generate_highlights(results, query)

        assert len(highlighted) == 1
        assert "service_name" in highlighted[0].highlights
        assert "<mark>" in highlighted[0].highlights["service_name"][0]

    def test_highlight_text_empty(self, search_engine):
        """Test _highlight_text with empty inputs"""
        assert search_engine._highlight_text("", "query") == ""
        assert search_engine._highlight_text("text", "") == "text"
        assert search_engine._highlight_text(None, "query") is None

    def test_highlight_text_single_term(self, search_engine):
        """Test _highlight_text with single term"""
        text = "Shopping Service"
        result = search_engine._highlight_text(text, "shopping")

        assert "<mark>" in result
        assert "</mark>" in result
        assert "Shopping" in result or "shopping" in result

    def test_highlight_text_multiple_terms(self, search_engine):
        """Test _highlight_text with multiple terms"""
        text = "Shopping and Cleaning Service"
        result = search_engine._highlight_text(text, "shopping cleaning")

        assert result.count("<mark>") == 2
        assert result.count("</mark>") == 2

    def test_highlight_text_case_insensitive(self, search_engine):
        """Test _highlight_text is case insensitive"""
        text = "Shopping Service"
        result = search_engine._highlight_text(text, "SHOPPING")

        assert "<mark>Shopping</mark>" in result

    def test_calculate_facets_empty(self, search_engine):
        """Test _calculate_facets with empty results"""
        facets = search_engine._calculate_facets([])

        assert "region" in facets
        assert "rate_ranges" in facets
        assert "hours_ranges" in facets
        assert len(facets["region"]) == 0

    def test_calculate_facets_with_data(self, search_engine, sample_services):
        """Test _calculate_facets with data"""
        facets = search_engine._calculate_facets(sample_services)

        assert facets["region"]["EU"] == 3
        assert facets["region"]["US"] == 1
        assert facets["region"]["APAC"] == 1

        # Check rate ranges
        assert facets["rate_ranges"]["0-30"] == 1  # 25.0
        assert facets["rate_ranges"]["30-40"] == 1  # 35.0
        assert facets["rate_ranges"]["40-50"] == 1  # 45.0
        assert facets["rate_ranges"]["50-60"] == 1  # 55.0
        assert facets["rate_ranges"]["60+"] == 1  # 65.0

    def test_calculate_facets_hours_ranges(self, search_engine):
        """Test _calculate_facets hours ranges"""
        services = [
            {"hours_per_month": 70, "region": "EU", "brutto_rate": 30},
            {"hours_per_month": 100, "region": "EU", "brutto_rate": 40},
            {"hours_per_month": 150, "region": "EU", "brutto_rate": 50},
            {"hours_per_month": 180, "region": "EU", "brutto_rate": 60},
            {"hours_per_month": 220, "region": "EU", "brutto_rate": 70},
        ]

        facets = search_engine._calculate_facets(services)

        assert facets["hours_ranges"]["0-80"] == 1
        assert facets["hours_ranges"]["80-120"] == 1
        assert facets["hours_ranges"]["120-160"] == 1
        assert facets["hours_ranges"]["160-200"] == 1
        assert facets["hours_ranges"]["200+"] == 1

    def test_generate_suggestions_empty_query(self, search_engine):
        """Test _generate_suggestions with empty query"""
        query = SearchQuery()
        suggestions = search_engine._generate_suggestions(query)

        assert len(suggestions) == 0

    def test_generate_suggestions_with_query(self, search_engine):
        """Test _generate_suggestions with query"""
        query = SearchQuery(query="shop")
        suggestions = search_engine._generate_suggestions(query)

        assert len(suggestions) > 0
        assert "shopping" in suggestions

    def test_generate_suggestions_exact_match(self, search_engine):
        """Test _generate_suggestions with exact match"""
        query = SearchQuery(query="shopping")
        suggestions = search_engine._generate_suggestions(query)

        # Exact match should not be in suggestions
        assert "shopping" not in suggestions

    def test_generate_suggestions_limit(self, search_engine):
        """Test _generate_suggestions respects limit"""
        query = SearchQuery(query="c")
        suggestions = search_engine._generate_suggestions(query)

        assert len(suggestions) <= 5

    def test_search_facets_in_response(self, search_engine, mock_db, sample_services):
        """Test facets are included in search response"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [tuple(s.values()) for s in sample_services]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery()
        response = search_engine.search(query)

        assert "region" in response.facets
        assert "rate_ranges" in response.facets
        assert "hours_ranges" in response.facets

    def test_search_suggestions_in_response(self, search_engine, mock_db):
        """Test suggestions are included in search response"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = [(1, "Shopping Service", "EU", 35.0, 160, "2024-01-01", "2024-01-15")]
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery(query="shop")
        response = search_engine.search(query)

        assert len(response.suggestions) > 0

    def test_search_execution_time(self, search_engine, mock_db):
        """Test execution time is measured"""
        cursor = MagicMock()
        cursor.description = [
            ("id",),
            ("service_name",),
            ("region",),
            ("brutto_rate",),
            ("hours_per_month",),
            ("created_at",),
            ("updated_at",),
        ]
        cursor.fetchall.return_value = []
        mock_db.conn.cursor.return_value = cursor

        query = SearchQuery()
        response = search_engine.search(query)

        assert response.execution_time_ms >= 0
        assert isinstance(response.execution_time_ms, float)


def test_get_search_engine():
    """Test factory function"""
    mock_db = Mock()
    engine = get_search_engine(mock_db)

    assert isinstance(engine, AdvancedSearchEngine)
    assert engine.db == mock_db


def test_integration_full_search():
    """Integration test for full search workflow"""
    # Setup mock database
    mock_db = Mock()
    mock_db.conn = Mock()
    cursor = MagicMock()
    cursor.description = [
        ("id",),
        ("service_name",),
        ("region",),
        ("brutto_rate",),
        ("hours_per_month",),
        ("created_at",),
        ("updated_at",),
    ]
    cursor.fetchall.return_value = [
        (1, "Shopping Service", "EU", 35.0, 160, "2024-01-01", "2024-01-15"),
        (2, "Shopping Cart", "EU", 45.0, 140, "2024-01-02", "2024-01-16"),
        (3, "Cleaning Service", "US", 55.0, 180, "2024-01-03", "2024-01-17"),
        (4, "Care Service", "APAC", 65.0, 200, "2024-01-04", "2024-01-18"),
    ]
    mock_db.conn.cursor.return_value = cursor

    # Execute search
    engine = AdvancedSearchEngine(mock_db)
    query = SearchQuery(query="shopping", sort_by=SortField.RELEVANCE, sort_order=SortOrder.DESC, limit=10)
    response = engine.search(query)

    # Verify response
    assert isinstance(response, SearchResponse)
    assert response.total == 4
    assert len(response.results) == 4
    assert response.execution_time_ms >= 0
    assert len(response.facets) > 0
    assert "region" in response.facets

    # Verify results are sorted by relevance
    # Services with "Shopping" should have higher relevance
    shopping_results = [r for r in response.results if "shopping" in r.service_name.lower()]
    assert len(shopping_results) >= 2
    assert all(r.relevance_score > 0 for r in shopping_results)
