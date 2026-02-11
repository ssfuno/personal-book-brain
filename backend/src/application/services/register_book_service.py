"""Service for registering books."""

from datetime import UTC, datetime

from google.cloud import firestore

from src.domain.interfaces.book_indexer import BookIndexer
from src.domain.interfaces.book_repository import (
    BookMasterRepository,
    UserLibraryRepository,
)
from src.domain.models.book_master import BookMaster, TableOfContentsItem
from src.domain.models.user import User
from src.domain.models.user_library import UserLibraryEntry


class RegisterBookUseCase:
    """Use case for registering a new book.

    This handles:
    1. Creating/retrieving the book master record (shared across users)
    2. Adding the book to the user's library
    3. Indexing the book for search
    """

    def __init__(
        self,
        book_master_repo: BookMasterRepository,
        user_library_repo: UserLibraryRepository,
        book_indexer: BookIndexer,
        firestore_client: firestore.Client,
    ) -> None:
        """Initialize the use case."""
        self.book_master_repo = book_master_repo
        self.user_library_repo = user_library_repo
        self.book_indexer = book_indexer
        self.firestore_client = firestore_client

    async def execute(
        self,
        user: User,
        isbn: str,
        toc: list[dict],
        title: str | None = None,
    ) -> tuple[BookMaster, UserLibraryEntry]:
        """Execute the book registration process.

        Args:
            user: The authenticated user
            isbn: The ISBN of the book to register
            toc: Mandatory TOC from preview
            title: Optional title

        Returns:
            Tuple of (book_master, library_entry)

        """
        # Normalize ISBN using domain logic
        normalized_isbn = BookMaster.normalize_isbn(isbn)

        # Check if book master exists
        book_master = self.book_master_repo.find_by_isbn(normalized_isbn)

        if not book_master:
            # Create new BookMaster using provided TOC
            book_master = BookMaster(
                isbn=normalized_isbn,
                title=title or "Unknown Title",
                toc=[TableOfContentsItem(**item) for item in toc],
                last_updated_by=user.uid,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            self.book_master_repo.save(book_master)

        else:
            # Book exists. Update TOC (Vandalism/Correction support)
            # Convert dicts to domain objects to avoid Pydantic serialization warnings
            # and ensure valid structure
            book_master.toc = [TableOfContentsItem(**item) for item in toc]
            book_master.last_updated_by = user.uid
            book_master.updated_at = datetime.now(UTC)
            self.book_master_repo.save(book_master)

        # Add to user's library (Idempotent)
        library_entry = UserLibraryEntry(
            user_id=user.uid,
            isbn=normalized_isbn,
            added_at=datetime.now(UTC),
        )
        saved_entry = self.user_library_repo.add_book(library_entry)

        return book_master, saved_entry
