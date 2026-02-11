"""Firestore implementation of UserLibraryRepository."""

from google.cloud import firestore

from src.domain.interfaces.book_repository import UserLibraryRepository
from src.domain.models.book_master import BookMaster
from src.domain.models.user_library import UserLibraryEntry


class FirestoreUserLibraryRepository(UserLibraryRepository):
    """User library repository implementation using Firestore.

    Stores user-specific book ownership in subcollections:
    users/{user_id}/library/{isbn}
    """

    def __init__(self, client: firestore.Client) -> None:
        """Initialize Firestore user library repository."""
        self.client = client

    def _get_library_ref(self, user_id: str) -> firestore.CollectionReference:
        """Get the library collection reference for a user."""
        return self.client.collection("users").document(user_id).collection("library")

    def add_book(self, entry: UserLibraryEntry) -> UserLibraryEntry:
        """Add a book to user's library."""
        normalized_isbn = BookMaster.normalize_isbn(entry.isbn)
        entry_dict = entry.model_dump()

        # Use ISBN as document ID in the user's library subcollection
        ref = self._get_library_ref(entry.user_id).document(normalized_isbn)
        ref.set(entry_dict)

        return entry

    def remove_book(self, user_id: str, isbn: str) -> None:
        """Remove a book from user's library."""
        normalized_isbn = BookMaster.normalize_isbn(isbn)
        ref = self._get_library_ref(user_id).document(normalized_isbn)
        ref.delete()

    def find_by_user(self, user_id: str) -> list[UserLibraryEntry]:
        """Find all library entries for a user."""
        library_ref = self._get_library_ref(user_id)
        docs = library_ref.stream()

        entries = []
        for doc in docs:
            data = doc.to_dict()
            entries.append(UserLibraryEntry(**data))

        return entries

    def find_entry(self, user_id: str, isbn: str) -> UserLibraryEntry | None:
        """Find a specific library entry."""
        normalized_isbn = BookMaster.normalize_isbn(isbn)
        doc = self._get_library_ref(user_id).document(normalized_isbn).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        return UserLibraryEntry(**data)

    def update_entry(self, entry: UserLibraryEntry) -> UserLibraryEntry:
        """Update a library entry."""
        normalized_isbn = BookMaster.normalize_isbn(entry.isbn)
        entry_dict = entry.model_dump()

        ref = self._get_library_ref(entry.user_id).document(normalized_isbn)
        ref.update(entry_dict)

        return entry
