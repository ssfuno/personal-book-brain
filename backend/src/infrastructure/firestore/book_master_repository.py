"""Firestore implementation of BookMasterRepository."""

from google.cloud import firestore

from src.domain.interfaces.book_repository import BookMasterRepository
from src.domain.models.book_master import BookMaster, TableOfContentsItem


class FirestoreBookMasterRepository(BookMasterRepository):
    """Book master repository implementation using Firestore.

    Stores canonical book data in the 'books' collection.
    Uses ISBN as the document ID to prevent duplicates.
    """

    def __init__(self, client: firestore.Client) -> None:
        """Initialize Firestore book master repository."""
        self.client = client
        self.collection = self.client.collection("books")

    def save(self, book: BookMaster) -> BookMaster:
        """Save a book master record using ISBN as document ID.

        This uses set() which will create or update the document.
        Since ISBN is the document ID, duplicates are automatically prevented.
        """
        # Normalize ISBN for consistency
        normalized_isbn = BookMaster.normalize_isbn(book.isbn)
        book_dict = book.model_dump()

        # Use ISBN as document ID
        ref = self.collection.document(normalized_isbn)
        ref.set(book_dict)

        return book

    def find_by_isbn(self, isbn: str) -> BookMaster | None:
        """Find a book by ISBN."""
        normalized_isbn = BookMaster.normalize_isbn(isbn)
        doc = self.collection.document(normalized_isbn).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        # Explicitly convert TOC dicts to TableOfContentsItem objects
        if data.get("toc"):
            data["toc"] = [TableOfContentsItem(**item) for item in data["toc"]]
        return BookMaster(**data)

    def exists(self, isbn: str) -> bool:
        """Check if a book exists in the master collection."""
        normalized_isbn = BookMaster.normalize_isbn(isbn)
        doc = self.collection.document(normalized_isbn).get()
        return doc.exists

    def save_if_not_exists(
        self,
        transaction: firestore.Transaction,
        book: BookMaster,
    ) -> tuple[BookMaster, bool]:
        """Save a book only if it doesn't exist (transactional).

        This is used to prevent race conditions when multiple users
        try to register the same book simultaneously.

        Args:
            transaction: Firestore transaction
            book: The book to save

        Returns:
            Tuple of (book_data, was_created)
            - book_data: The book master (either newly created or existing)
            - was_created: True if the book was created, False if it already existed

        """
        normalized_isbn = BookMaster.normalize_isbn(book.isbn)
        ref = self.collection.document(normalized_isbn)

        # Check if book exists within transaction
        snapshot = ref.get(transaction=transaction)

        if snapshot.exists:
            # Book already exists, return existing data
            existing_data = snapshot.to_dict()
            # Explicitly convert TOC dicts to TableOfContentsItem objects
            if existing_data.get("toc"):
                existing_data["toc"] = [
                    TableOfContentsItem(**item) for item in existing_data["toc"]
                ]
            return BookMaster(**existing_data), False

        # Book doesn't exist, create it
        book_dict = book.model_dump()
        transaction.set(ref, book_dict)
        return book, True
