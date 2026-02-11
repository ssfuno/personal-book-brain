"""Service for listing books."""

from src.domain.interfaces.book_repository import (
    BookMasterRepository,
    UserLibraryRepository,
)
from src.domain.models.book_master import BookMaster
from src.domain.models.user import User
from src.domain.models.user_library import UserLibraryEntry


class BookWithLibraryInfo:
    """Combined view of book master and user library entry."""

    def __init__(self, book: BookMaster, library_entry: UserLibraryEntry) -> None:
        """Initialize combined book view."""
        self.book = book
        self.library_entry = library_entry


class ListBooksUseCase:
    """Use case for listing user's books."""

    def __init__(
        self,
        book_master_repo: BookMasterRepository,
        user_library_repo: UserLibraryRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            book_master_repo: Repository for book master operations.
            user_library_repo: Repository for user library operations.

        """
        self.book_master_repo = book_master_repo
        self.user_library_repo = user_library_repo

    def execute(self, user: User) -> list[BookWithLibraryInfo]:
        """Execute the list books process.

        Args:
            user: The authenticated user.

        Returns:
            List of books with library info belonging to the user.

        """
        # 1. Get user's library entries
        library_entries = self.user_library_repo.find_by_user(user.uid)

        # 2. Fetch book master data for each entry
        result = []
        for entry in library_entries:
            book_master = self.book_master_repo.find_by_isbn(entry.isbn)
            if book_master:
                result.append(BookWithLibraryInfo(book_master, entry))

        return result
