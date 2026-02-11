"""Interfaces for Search Engine."""

from abc import ABC, abstractmethod
from typing import Any


class SearchResult(dict[str, Any]):
    """Represents a search result item.

    Expected keys: 'id', 'title', 'content', 'score', etc.
    """


class SearchEngine(ABC):
    """Abstract interface for search operations."""

    @abstractmethod
    def search(
        self, query: str, limit: int = 5, user_id: str | None = None
    ) -> list[SearchResult]:
        """Search for documents matching the query, optionally filtered by user."""
