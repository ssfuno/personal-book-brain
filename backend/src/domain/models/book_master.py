"""Book master domain model - represents the canonical book data."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class TableOfContentsItem(BaseModel):
    """Represents a single item in the table of contents."""

    title: str = Field(..., min_length=1)
    level: int = Field(default=1, ge=1)  # 1: Chapter, 2: Section, etc.

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        if not v.strip():
            msg = "TOC item title cannot be empty"
            raise ValueError(msg)
        return v.strip()


class BookMaster(BaseModel):
    """Represents the canonical book data shared across all users.

    This is the master record for a book, identified by ISBN.
    Each book exists only once in the system, regardless of how many users own it.
    """

    isbn: str = Field(..., min_length=10)  # This is the document ID in Firestore
    title: str = Field(..., min_length=1)
    toc: list[TableOfContentsItem] = Field(default_factory=list)
    last_updated_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def normalize_isbn(isbn: str) -> str:
        """Normalize ISBN by removing hyphens and spaces.

        This is a business rule that belongs in the domain layer.
        """
        return isbn.replace("-", "").replace(" ", "")

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        """Validate ISBN format.

        Business rule: ISBN must be 10 or 13 digits after normalization.
        """
        normalized = cls.normalize_isbn(v)
        if len(normalized) not in [10, 13]:
            msg = "ISBN must be 10 or 13 digits"
            raise ValueError(msg)
        if not normalized.isdigit():
            msg = "ISBN must contain only digits (after removing hyphens and spaces)"
            raise ValueError(msg)
        return normalized  # Store normalized version

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        if not v.strip():
            msg = "Title cannot be empty"
            raise ValueError(msg)
        return v.strip()

    def update_title(self, new_title: str) -> None:
        """Update book title with validation.

        Business rule: Title cannot be empty.
        This will trigger Pydantic validation automatically.
        """
        self.title = new_title  # Pydantic will validate
        self.updated_at = datetime.now(UTC)

    def add_toc_item(self, item: TableOfContentsItem) -> None:
        """Add a table of contents item.

        Business rule: TOC items must have unique titles at the same level.
        """
        # Check for duplicates at the same level
        existing_titles = {toc.title for toc in self.toc if toc.level == item.level}
        if item.title in existing_titles:
            msg = f"TOC item '{item.title}' already exists at level {item.level}"
            raise ValueError(msg)

        self.toc.append(item)
        self.updated_at = datetime.now(UTC)

    def has_toc(self) -> bool:
        """Check if book has table of contents."""
        return len(self.toc) > 0

    def get_chapter_count(self) -> int:
        """Get the number of chapters (level 1 items)."""
        return len([item for item in self.toc if item.level == 1])
