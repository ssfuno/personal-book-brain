"""Interfaces for Book Repository and TOC Generator."""

from abc import ABC, abstractmethod

from src.domain.models.book_master import BookMaster
from src.domain.models.user_library import UserLibraryEntry


class BookMasterRepository(ABC):
    """Abstract interface for book master storage operations.

    Manages the canonical book data shared across all users.
    """

    @abstractmethod
    def save(self, book: BookMaster) -> BookMaster:
        """Save a book master record.

        Args:
            book: The book master to save (ISBN is used as document ID)

        Returns:
            The saved book master

        """

    @abstractmethod
    def find_by_isbn(self, isbn: str) -> BookMaster | None:
        """Find a book by ISBN.

        Args:
            isbn: The ISBN to search for (will be normalized)

        Returns:
            The book master if found, None otherwise

        """

    @abstractmethod
    def exists(self, isbn: str) -> bool:
        """Check if a book exists in the master collection.

        Args:
            isbn: The ISBN to check (will be normalized)

        Returns:
            True if the book exists, False otherwise

        """


class UserLibraryRepository(ABC):
    """Abstract interface for user library storage operations.

    Manages user-specific book ownership and reading status.
    """

    @abstractmethod
    def add_book(self, entry: UserLibraryEntry) -> UserLibraryEntry:
        """Add a book to user's library.

        Args:
            entry: The library entry to add

        Returns:
            The saved library entry

        """

    @abstractmethod
    def remove_book(self, user_id: str, isbn: str) -> None:
        """Remove a book from user's library.

        Args:
            user_id: The user ID
            isbn: The ISBN of the book to remove

        """

    @abstractmethod
    def find_by_user(self, user_id: str) -> list[UserLibraryEntry]:
        """Find all library entries for a user.

        Args:
            user_id: The user ID

        Returns:
            List of library entries for the user

        """

    @abstractmethod
    def find_entry(self, user_id: str, isbn: str) -> UserLibraryEntry | None:
        """Find a specific library entry.

        Args:
            user_id: The user ID
            isbn: The ISBN of the book

        Returns:
            The library entry if found, None otherwise

        """

    @abstractmethod
    def update_entry(self, entry: UserLibraryEntry) -> UserLibraryEntry:
        """Update a library entry.

        Args:
            entry: The library entry to update
        Returns:
            The updated library entry

        """


class TOCGenerator(ABC):
    """Abstract interface for TOC generation."""

    @abstractmethod
    async def generate_from_query(self, query: str) -> dict:
        """Generate title and TOC from a search query (ISBN/Title)."""

    @abstractmethod
    def generate_from_image(self, image_data: bytes) -> list[dict]:
        """Generate TOC from an image."""
