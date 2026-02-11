"""Service for fetching book metadata (preview)."""

from datetime import UTC, datetime

from google.cloud import firestore

from src.domain.interfaces.book_repository import (
    BookMasterRepository,
    TOCGenerator,
)
from src.domain.models.book_master import BookMaster


class FetchBookMetadataUseCase:
    """Use case for fetching book metadata (preview).

    This handles:
    1. Checking if the book exists in the master record
    2. If not, generating the metadata using Gemini
    3. Returning the metadata for preview
    """

    def __init__(
        self,
        book_master_repo: BookMasterRepository,
        toc_generator: TOCGenerator,
        firestore_client: firestore.Client,
    ) -> None:
        """Initialize the use case."""
        self.book_master_repo = book_master_repo
        self.toc_generator = toc_generator
        self.firestore_client = firestore_client

    async def execute(
        self,
        isbn: str,
        title: str | None = None,
    ) -> BookMaster:
        """Execute the fetch metadata process.

        Args:
            isbn: The ISBN of the book
            title: Optional title hint

        Returns:
            BookMaster: The book metadata

        """
        # Normalize ISBN
        normalized_isbn = BookMaster.normalize_isbn(isbn)

        # Check if book master exists
        book_master = self.book_master_repo.find_by_isbn(normalized_isbn)

        if book_master:
            return book_master

        # Book doesn't exist, generate it
        query = f"ISBN: {normalized_isbn}"
        if title:
            query += f" (Title: {title})"

        result = await self.toc_generator.generate_from_query(query)

        final_title = title or result.get("title", "Unknown Title")
        toc = result.get("toc", [])

        # Create tentative BookMaster
        return BookMaster(
            isbn=normalized_isbn,
            title=final_title,
            toc=toc,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
