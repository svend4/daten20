"""
Pagination Module

Provides comprehensive pagination utilities for API endpoints and database queries.
Supports:
- Offset-based pagination (page/per_page)
- Cursor-based pagination (for large datasets)
- RFC 5988 Link headers
- Flask integration
"""

import base64
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar
from urllib.parse import urlencode

logger = logging.getLogger("dms.pagination")


T = TypeVar('T')


@dataclass
class PaginationInfo:
    """Pagination metadata"""
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    # Additional fields for enhanced API responses
    offset: int = 0
    limit: int = 0
    links: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            'page': self.page,
            'per_page': self.per_page,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_prev': self.has_prev,
            'offset': self.offset,
            'limit': self.limit,
        }

        if self.next_page:
            result['next_page'] = self.next_page
        if self.prev_page:
            result['prev_page'] = self.prev_page

        return result


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result container"""
    items: List[T]
    pagination: PaginationInfo

    def to_dict(self, include_links: bool = True) -> Dict[str, Any]:
        """
        Convert to dictionary for API responses.

        Args:
            include_links: Include pagination links in response

        Returns:
            Dictionary with items, meta (pagination), and optional links
        """
        result = {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            'meta': self.pagination.to_dict(),
        }

        # Add links if available and requested
        if include_links and self.pagination.links:
            result['links'] = self.pagination.links

        return result


class Paginator:
    """Paginator for database queries and list results"""

    def __init__(self, per_page: int = 50, max_per_page: int = 1000):
        """
        Initialize paginator

        Args:
            per_page: Default items per page
            max_per_page: Maximum items per page
        """
        self.per_page = per_page
        self.max_per_page = max_per_page

    def paginate(
        self,
        items: List[T],
        page: int = 1,
        per_page: Optional[int] = None,
        total_count: Optional[int] = None
    ) -> PaginatedResult[T]:
        """
        Paginate a list of items

        Args:
            items: List of items to paginate
            page: Page number (1-indexed)
            per_page: Items per page (uses default if None)
            total_count: Total count of items (if known, for database queries)

        Returns:
            PaginatedResult with items and pagination info

        Raises:
            ValueError: If page or per_page are invalid
        """
        # Validate and normalize parameters
        page = max(1, page)
        per_page = per_page or self.per_page
        per_page = min(per_page, self.max_per_page)

        # Calculate total items and pages
        if total_count is not None:
            total_items = total_count
        else:
            total_items = len(items)

        total_pages = max(1, (total_items + per_page - 1) // per_page)

        # Clamp page to valid range
        page = min(page, total_pages)

        # Calculate pagination info
        has_prev = page > 1
        has_next = page < total_pages
        next_page = page + 1 if has_next else None
        prev_page = page - 1 if has_prev else None

        # Create pagination info
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=next_page,
            prev_page=prev_page
        )

        # If items already sliced (from database with offset), use as-is
        # Otherwise, slice the items list
        if total_count is not None:
            # Items already sliced from database
            result_items = items
        else:
            # Slice items from full list
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            result_items = items[start_idx:end_idx]

        return PaginatedResult(items=result_items, pagination=pagination)

    def get_offset_limit(self, page: int, per_page: Optional[int] = None) -> tuple:
        """
        Get offset and limit for database queries

        Args:
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (offset, limit)
        """
        page = max(1, page)
        per_page = per_page or self.per_page
        per_page = min(per_page, self.max_per_page)

        offset = (page - 1) * per_page
        limit = per_page

        return offset, limit

    def create_pagination_info(
        self,
        page: int,
        per_page: int,
        total_items: int
    ) -> PaginationInfo:
        """
        Create pagination info without items

        Args:
            page: Current page number
            per_page: Items per page
            total_items: Total number of items

        Returns:
            PaginationInfo object
        """
        total_pages = max(1, (total_items + per_page - 1) // per_page)
        page = min(page, total_pages)

        has_prev = page > 1
        has_next = page < total_pages
        next_page = page + 1 if has_next else None
        prev_page = page - 1 if has_prev else None

        offset, limit = self.get_offset_limit(page, per_page)

        return PaginationInfo(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=next_page,
            prev_page=prev_page,
            offset=offset,
            limit=limit
        )

    def create_links(
        self,
        base_url: str,
        page: int,
        per_page: int,
        total_pages: int,
        **query_params
    ) -> Dict[str, str]:
        """
        Create pagination links (RFC 5988 compliant).

        Args:
            base_url: Base URL for pagination links
            page: Current page number
            per_page: Items per page
            total_pages: Total number of pages
            **query_params: Additional query parameters

        Returns:
            Dictionary with pagination links (self, first, last, next, prev)
        """
        links = {}

        def build_url(page_num: int) -> str:
            """Build URL with page parameter."""
            params = {**query_params, 'page': page_num, 'per_page': per_page}
            query_string = urlencode(params)
            return f"{base_url}?{query_string}"

        # Self link
        links['self'] = build_url(page)

        # First page
        links['first'] = build_url(1)

        # Last page
        links['last'] = build_url(total_pages)

        # Next page
        if page < total_pages:
            links['next'] = build_url(page + 1)

        # Previous page
        if page > 1:
            links['prev'] = build_url(page - 1)

        return links

    def create_link_header(self, links: Dict[str, str]) -> str:
        """
        Create Link header (RFC 5988).

        Format: <url>; rel="relation", <url>; rel="relation"

        Args:
            links: Dictionary of pagination links

        Returns:
            Link header string
        """
        link_parts = []

        # Order: first, prev, next, last
        for rel in ['first', 'prev', 'next', 'last']:
            if rel in links:
                link_parts.append(f'<{links[rel]}>; rel="{rel}"')

        return ', '.join(link_parts)


# Global paginator instance
_default_paginator: Optional[Paginator] = None


def get_paginator(per_page: int = 50) -> Paginator:
    """Get or create default paginator instance"""
    global _default_paginator
    if _default_paginator is None:
        _default_paginator = Paginator(per_page=per_page)
    return _default_paginator


def paginate_query_result(
    items: List[T],
    page: int = 1,
    per_page: int = 50,
    total_count: Optional[int] = None
) -> PaginatedResult[T]:
    """
    Helper function to paginate query results

    Args:
        items: List of items from query
        page: Page number
        per_page: Items per page
        total_count: Total count from query (if available)

    Returns:
        PaginatedResult
    """
    paginator = get_paginator(per_page=per_page)
    return paginator.paginate(items, page=page, per_page=per_page, total_count=total_count)


class CursorPaginator:
    """
    Cursor-based pagination for large datasets.

    Cursor pagination is more efficient than offset pagination for:
    - Large datasets (millions of records)
    - Frequently changing data
    - Infinite scroll UIs
    - Real-time feeds

    Benefits:
    - Consistent results even when data changes
    - Better performance (no COUNT queries needed)
    - No page drift issues
    """

    def __init__(self, page_size: int = 50, max_page_size: int = 1000):
        """
        Initialize cursor paginator.

        Args:
            page_size: Default page size
            max_page_size: Maximum page size
        """
        self.page_size = page_size
        self.max_page_size = max_page_size

    def encode_cursor(self, value: Any) -> str:
        """
        Encode cursor value to base64.

        Args:
            value: Cursor value (usually ID or timestamp)

        Returns:
            Base64 encoded cursor string
        """
        cursor_data = {'value': value}
        json_str = json.dumps(cursor_data, default=str)
        encoded = base64.b64encode(json_str.encode('utf-8'))
        return encoded.decode('utf-8')

    def decode_cursor(self, cursor: str) -> Optional[Any]:
        """
        Decode cursor from base64.

        Args:
            cursor: Base64 encoded cursor

        Returns:
            Decoded cursor value or None if invalid
        """
        try:
            decoded = base64.b64decode(cursor.encode('utf-8'))
            json_str = decoded.decode('utf-8')
            cursor_data = json.loads(json_str)
            return cursor_data.get('value')
        except Exception as e:
            logger.warning(f"Failed to decode cursor: {e}")
            return None

    def create_response(
        self,
        items: List[T],
        limit: int,
        cursor_field: str = 'id',
        has_more: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Create cursor-based pagination response.

        Args:
            items: List of items
            limit: Items limit
            cursor_field: Field to use for cursor
            has_more: Whether there are more items (auto-detect if None)

        Returns:
            Response dictionary with items, meta, and cursors
        """
        # Auto-detect has_more if not provided
        if has_more is None:
            has_more = len(items) > limit
            # Trim items to limit if has_more
            if has_more:
                items = items[:limit]

        response = {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in items],
            'meta': {
                'count': len(items),
                'limit': limit,
                'has_more': has_more,
            }
        }

        # Add cursors
        if items:
            first_item = items[0]
            last_item = items[-1]

            # Extract cursor values
            if isinstance(first_item, dict):
                first_cursor_value = first_item.get(cursor_field)
                last_cursor_value = last_item.get(cursor_field)
            else:
                first_cursor_value = getattr(first_item, cursor_field, None)
                last_cursor_value = getattr(last_item, cursor_field, None)

            # Add cursors if available
            if first_cursor_value is not None:
                response['meta']['first_cursor'] = self.encode_cursor(first_cursor_value)

            if last_cursor_value is not None and has_more:
                response['meta']['next_cursor'] = self.encode_cursor(last_cursor_value)

        return response


# Helper function for cursor pagination
def paginate_with_cursor(
    items: List[T],
    limit: int = 50,
    cursor_field: str = 'id',
    has_more: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Helper function for cursor-based pagination.

    Args:
        items: List of items
        limit: Page size limit
        cursor_field: Field to use for cursor
        has_more: Whether there are more items

    Returns:
        Cursor-paginated response
    """
    paginator = CursorPaginator(page_size=limit)
    return paginator.create_response(items, limit, cursor_field, has_more)
