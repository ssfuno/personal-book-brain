"""User library domain model - represents a user's ownership of a book."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class UserLibraryEntry(BaseModel):
    """Represents a user's ownership of a book.

    This is stored in users/{user_id}/library/{isbn} in Firestore.
    It links a user to a book in the master collection.
    """

    user_id: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=10)  # Reference to BookMaster
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id is not empty or whitespace only."""
        if not v.strip():
            msg = "User ID cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        """Validate ISBN format."""
        # Use simple normalization here to avoid circular imports at runtime
        # logic duplicated from BookMaster.normalize_isbn
        normalized = v.replace("-", "").replace(" ", "")

        if len(normalized) not in [10, 13]:
            msg = "ISBN must be 10 or 13 digits"
            raise ValueError(msg)
        if not normalized.isdigit():
            msg = "ISBN must contain only digits"
            raise ValueError(msg)
        return normalized
