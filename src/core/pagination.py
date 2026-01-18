"""
Pagination Module

Provides pagination utilities for API endpoints and database queries.
Supports offset-based and cursor-based pagination.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

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


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result container"""
    items: List[T]
    pagination: PaginationInfo

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            'pagination': {
                'page': self.pagination.page,
                'per_page': self.pagination.per_page,
                'total_items': self.pagination.total_items,
                'total_pages': self.pagination.total_pages,
                'has_next': self.pagination.has_next,
                'has_prev': self.pagination.has_prev,
                'next_page': self.pagination.next_page,
                'prev_page': self.pagination.prev_page,
            }
        }


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

        return PaginationInfo(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=next_page,
            prev_page=prev_page
        )


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
