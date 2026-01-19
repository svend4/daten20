"""
Unit tests for pagination module
"""

import base64
import json
from datetime import datetime

import pytest

from src.core.pagination import (
    CursorPaginator,
    PaginatedResult,
    PaginationInfo,
    Paginator,
    get_paginator,
    paginate_query_result,
    paginate_with_cursor,
)


# ============================================================================
# PaginationInfo Tests
# ============================================================================


class TestPaginationInfo:
    """Test PaginationInfo dataclass"""

    def test_to_dict(self):
        """Test PaginationInfo conversion to dict"""
        info = PaginationInfo(
            page=2,
            per_page=20,
            total_items=100,
            total_pages=5,
            has_next=True,
            has_prev=True,
            next_page=3,
            prev_page=1,
            offset=20,
            limit=20,
        )

        result = info.to_dict()

        assert result["page"] == 2
        assert result["per_page"] == 20
        assert result["total_items"] == 100
        assert result["total_pages"] == 5
        assert result["has_next"] is True
        assert result["has_prev"] is True
        assert result["next_page"] == 3
        assert result["prev_page"] == 1
        assert result["offset"] == 20
        assert result["limit"] == 20

    def test_to_dict_without_next_prev(self):
        """Test to_dict without next/prev pages"""
        info = PaginationInfo(
            page=1, per_page=20, total_items=10, total_pages=1, has_next=False, has_prev=False, offset=0, limit=20
        )

        result = info.to_dict()

        assert "next_page" not in result
        assert "prev_page" not in result


# ============================================================================
# PaginatedResult Tests
# ============================================================================


class TestPaginatedResult:
    """Test PaginatedResult container"""

    def test_to_dict_with_dict_items(self):
        """Test to_dict with dictionary items"""
        pagination = PaginationInfo(
            page=1, per_page=10, total_items=3, total_pages=1, has_next=False, has_prev=False
        )
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}, {"id": 3, "name": "Item 3"}]

        result = PaginatedResult(items=items, pagination=pagination)
        result_dict = result.to_dict()

        assert len(result_dict["items"]) == 3
        assert result_dict["items"][0]["id"] == 1
        assert result_dict["meta"]["total_items"] == 3

    def test_to_dict_with_objects_having_to_dict(self):
        """Test to_dict with objects that have to_dict method"""

        class Item:
            def __init__(self, id, name):
                self.id = id
                self.name = name

            def to_dict(self):
                return {"id": self.id, "name": self.name}

        pagination = PaginationInfo(
            page=1, per_page=10, total_items=2, total_pages=1, has_next=False, has_prev=False
        )
        items = [Item(1, "Item 1"), Item(2, "Item 2")]

        result = PaginatedResult(items=items, pagination=pagination)
        result_dict = result.to_dict()

        assert len(result_dict["items"]) == 2
        assert result_dict["items"][0]["id"] == 1

    def test_to_dict_with_links(self):
        """Test to_dict with pagination links"""
        pagination = PaginationInfo(
            page=2, per_page=10, total_items=50, total_pages=5, has_next=True, has_prev=True
        )
        pagination.links = {
            "self": "/api/items?page=2",
            "first": "/api/items?page=1",
            "last": "/api/items?page=5",
            "next": "/api/items?page=3",
            "prev": "/api/items?page=1",
        }

        items = [{"id": 11}, {"id": 12}]
        result = PaginatedResult(items=items, pagination=pagination)
        result_dict = result.to_dict(include_links=True)

        assert "links" in result_dict
        assert result_dict["links"]["self"] == "/api/items?page=2"

    def test_to_dict_without_links(self):
        """Test to_dict without links"""
        pagination = PaginationInfo(
            page=1, per_page=10, total_items=5, total_pages=1, has_next=False, has_prev=False
        )

        items = [{"id": 1}]
        result = PaginatedResult(items=items, pagination=pagination)
        result_dict = result.to_dict(include_links=False)

        assert "links" not in result_dict


# ============================================================================
# Paginator Tests
# ============================================================================


class TestPaginator:
    """Test Paginator class"""

    def test_init(self):
        """Test paginator initialization"""
        paginator = Paginator(per_page=25, max_per_page=500)

        assert paginator.per_page == 25
        assert paginator.max_per_page == 500

    def test_paginate_first_page(self):
        """Test paginating first page"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 51))  # 50 items

        result = paginator.paginate(items, page=1)

        assert len(result.items) == 10
        assert result.items == list(range(1, 11))
        assert result.pagination.page == 1
        assert result.pagination.total_items == 50
        assert result.pagination.total_pages == 5
        assert result.pagination.has_next is True
        assert result.pagination.has_prev is False

    def test_paginate_middle_page(self):
        """Test paginating middle page"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 51))

        result = paginator.paginate(items, page=3)

        assert len(result.items) == 10
        assert result.items == list(range(21, 31))
        assert result.pagination.page == 3
        assert result.pagination.has_next is True
        assert result.pagination.has_prev is True
        assert result.pagination.next_page == 4
        assert result.pagination.prev_page == 2

    def test_paginate_last_page(self):
        """Test paginating last page"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 51))

        result = paginator.paginate(items, page=5)

        assert len(result.items) == 10
        assert result.items == list(range(41, 51))
        assert result.pagination.has_next is False
        assert result.pagination.has_prev is True
        assert result.pagination.next_page is None

    def test_paginate_partial_last_page(self):
        """Test paginating partial last page"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 46))  # 45 items

        result = paginator.paginate(items, page=5)

        assert len(result.items) == 5
        assert result.items == list(range(41, 46))

    def test_paginate_with_custom_per_page(self):
        """Test pagination with custom per_page"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 51))

        result = paginator.paginate(items, page=1, per_page=20)

        assert len(result.items) == 20
        assert result.pagination.per_page == 20
        assert result.pagination.total_pages == 3

    def test_paginate_enforces_max_per_page(self):
        """Test that max_per_page is enforced"""
        paginator = Paginator(per_page=50, max_per_page=100)
        items = list(range(1, 201))

        result = paginator.paginate(items, page=1, per_page=150)

        assert result.pagination.per_page == 100

    def test_paginate_with_total_count(self):
        """Test pagination with total_count (database query scenario)"""
        paginator = Paginator(per_page=10)
        # Only 10 items from database, but total is 50
        items = list(range(21, 31))

        result = paginator.paginate(items, page=3, per_page=10, total_count=50)

        assert len(result.items) == 10
        assert result.pagination.total_items == 50
        assert result.pagination.total_pages == 5

    def test_paginate_empty_list(self):
        """Test paginating empty list"""
        paginator = Paginator(per_page=10)
        items = []

        result = paginator.paginate(items, page=1)

        assert len(result.items) == 0
        assert result.pagination.total_items == 0
        assert result.pagination.total_pages == 1
        assert result.pagination.has_next is False

    def test_paginate_page_out_of_range(self):
        """Test pagination with page number out of range"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 21))  # 20 items, 2 pages

        # Request page 10 - should clamp to page 2
        result = paginator.paginate(items, page=10)

        assert result.pagination.page == 2
        assert len(result.items) == 10

    def test_paginate_page_zero(self):
        """Test pagination with page 0 (should normalize to 1)"""
        paginator = Paginator(per_page=10)
        items = list(range(1, 21))

        result = paginator.paginate(items, page=0)

        assert result.pagination.page == 1

    def test_get_offset_limit(self):
        """Test get_offset_limit helper"""
        paginator = Paginator(per_page=20)

        offset, limit = paginator.get_offset_limit(page=1)
        assert offset == 0
        assert limit == 20

        offset, limit = paginator.get_offset_limit(page=3)
        assert offset == 40
        assert limit == 20

        offset, limit = paginator.get_offset_limit(page=5, per_page=50)
        assert offset == 200
        assert limit == 50

    def test_create_pagination_info(self):
        """Test create_pagination_info method"""
        paginator = Paginator(per_page=10)

        info = paginator.create_pagination_info(page=3, per_page=20, total_items=100)

        assert info.page == 3
        assert info.per_page == 20
        assert info.total_items == 100
        assert info.total_pages == 5
        assert info.has_next is True
        assert info.has_prev is True
        assert info.offset == 40
        assert info.limit == 20

    def test_create_links(self):
        """Test create_links method"""
        paginator = Paginator()

        links = paginator.create_links(
            base_url="/api/items", page=3, per_page=20, total_pages=5, category="books", sort="title"
        )

        assert "self" in links
        assert "first" in links
        assert "last" in links
        assert "next" in links
        assert "prev" in links
        assert "page=3" in links["self"]
        assert "per_page=20" in links["self"]
        assert "category=books" in links["self"]

    def test_create_links_first_page(self):
        """Test create_links for first page (no prev)"""
        paginator = Paginator()

        links = paginator.create_links(base_url="/api/items", page=1, per_page=10, total_pages=5)

        assert "prev" not in links
        assert "next" in links

    def test_create_links_last_page(self):
        """Test create_links for last page (no next)"""
        paginator = Paginator()

        links = paginator.create_links(base_url="/api/items", page=5, per_page=10, total_pages=5)

        assert "next" not in links
        assert "prev" in links

    def test_create_link_header(self):
        """Test create_link_header (RFC 5988)"""
        paginator = Paginator()

        links = {
            "first": "/api/items?page=1",
            "prev": "/api/items?page=2",
            "next": "/api/items?page=4",
            "last": "/api/items?page=10",
        }

        header = paginator.create_link_header(links)

        assert '</api/items?page=1>; rel="first"' in header
        assert '</api/items?page=2>; rel="prev"' in header
        assert '</api/items?page=4>; rel="next"' in header
        assert '</api/items?page=10>; rel="last"' in header


# ============================================================================
# Helper Functions Tests
# ============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    def test_get_paginator(self):
        """Test get_paginator returns singleton"""
        paginator1 = get_paginator(per_page=50)
        paginator2 = get_paginator(per_page=50)

        assert paginator1 is paginator2

    def test_paginate_query_result(self):
        """Test paginate_query_result helper"""
        items = list(range(1, 101))

        result = paginate_query_result(items, page=2, per_page=20)

        assert len(result.items) == 20
        assert result.items == list(range(21, 41))
        assert result.pagination.page == 2


# ============================================================================
# CursorPaginator Tests
# ============================================================================


class TestCursorPaginator:
    """Test cursor-based pagination"""

    def test_init(self):
        """Test cursor paginator initialization"""
        paginator = CursorPaginator(page_size=25, max_page_size=500)

        assert paginator.page_size == 25
        assert paginator.max_page_size == 500

    def test_encode_cursor(self):
        """Test cursor encoding"""
        paginator = CursorPaginator()

        cursor = paginator.encode_cursor(12345)

        assert isinstance(cursor, str)
        assert len(cursor) > 0

    def test_decode_cursor(self):
        """Test cursor decoding"""
        paginator = CursorPaginator()

        cursor = paginator.encode_cursor(12345)
        value = paginator.decode_cursor(cursor)

        assert value == 12345

    def test_encode_decode_string_cursor(self):
        """Test encoding/decoding string cursor"""
        paginator = CursorPaginator()

        cursor = paginator.encode_cursor("abc-def-123")
        value = paginator.decode_cursor(cursor)

        assert value == "abc-def-123"

    def test_encode_decode_datetime_cursor(self):
        """Test encoding/decoding datetime cursor"""
        paginator = CursorPaginator()
        dt = datetime(2024, 1, 15, 10, 30, 0)

        cursor = paginator.encode_cursor(dt)
        value = paginator.decode_cursor(cursor)

        # Datetime is serialized as string (default str() format)
        assert value == str(dt)

    def test_decode_invalid_cursor(self):
        """Test decoding invalid cursor returns None"""
        paginator = CursorPaginator()

        value = paginator.decode_cursor("invalid-base64!!!")

        assert value is None

    def test_create_response_with_dict_items(self):
        """Test create_response with dictionary items"""
        paginator = CursorPaginator(page_size=3)
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}, {"id": 3, "name": "Item 3"}]

        response = paginator.create_response(items, limit=3, cursor_field="id")

        assert len(response["items"]) == 3
        assert response["meta"]["count"] == 3
        assert response["meta"]["limit"] == 3
        assert response["meta"]["has_more"] is False
        assert "first_cursor" in response["meta"]

    def test_create_response_has_more_auto_detect(self):
        """Test auto-detection of has_more"""
        paginator = CursorPaginator(page_size=3)
        # 4 items, limit is 3 - should detect has_more
        items = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
            {"id": 4, "name": "Item 4"},
        ]

        response = paginator.create_response(items, limit=3, cursor_field="id")

        # Should trim to 3 items
        assert len(response["items"]) == 3
        assert response["meta"]["has_more"] is True
        assert "next_cursor" in response["meta"]

    def test_create_response_with_objects(self):
        """Test create_response with objects"""

        class Item:
            def __init__(self, id, name):
                self.id = id
                self.name = name

            def to_dict(self):
                return {"id": self.id, "name": self.name}

        paginator = CursorPaginator()
        items = [Item(1, "Item 1"), Item(2, "Item 2")]

        response = paginator.create_response(items, limit=10, cursor_field="id")

        assert len(response["items"]) == 2
        assert response["items"][0]["id"] == 1

    def test_create_response_explicit_has_more(self):
        """Test create_response with explicit has_more"""
        paginator = CursorPaginator()
        items = [{"id": 1}, {"id": 2}]

        response = paginator.create_response(items, limit=10, cursor_field="id", has_more=True)

        assert response["meta"]["has_more"] is True

    def test_create_response_empty_items(self):
        """Test create_response with empty items"""
        paginator = CursorPaginator()
        items = []

        response = paginator.create_response(items, limit=10, cursor_field="id")

        assert len(response["items"]) == 0
        assert response["meta"]["has_more"] is False
        assert "first_cursor" not in response["meta"]
        assert "next_cursor" not in response["meta"]

    def test_create_response_no_next_cursor_when_no_more(self):
        """Test that next_cursor is not included when has_more is False"""
        paginator = CursorPaginator()
        items = [{"id": 1}, {"id": 2}]

        response = paginator.create_response(items, limit=10, cursor_field="id", has_more=False)

        assert "next_cursor" not in response["meta"]


# ============================================================================
# Cursor Pagination Helper Tests
# ============================================================================


class TestCursorPaginationHelper:
    """Test cursor pagination helper function"""

    def test_paginate_with_cursor(self):
        """Test paginate_with_cursor helper"""
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}, {"id": 3, "name": "Item 3"}]

        response = paginate_with_cursor(items, limit=3, cursor_field="id")

        assert len(response["items"]) == 3
        assert response["meta"]["limit"] == 3
