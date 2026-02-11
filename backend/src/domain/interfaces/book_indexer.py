"""Interface for Book Indexer."""

from abc import ABC, abstractmethod

from src.domain.models.book_master import BookMaster


class BookIndexer(ABC):
    """Abstract interface for book indexing operations."""

    @abstractmethod
    def index_book(self, book: BookMaster, user_id: str) -> None:
        """Index a book into the search engine for a specific user."""
