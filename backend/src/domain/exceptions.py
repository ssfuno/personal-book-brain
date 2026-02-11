"""Domain-level exceptions."""


class DomainError(Exception):
    """Base exception for domain-level errors."""


class BookNotFoundError(DomainError):
    """Raised when a requested book is not found."""

    def __init__(self, book_id: str) -> None:
        """Initialize book not found error.

        Args:
            book_id: The ID of the book that was not found.

        """
        self.book_id = book_id
        self.message = f"Book with ID '{book_id}' not found"
        super().__init__(self.message)


class AuthenticationError(DomainError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize authentication error.

        Args:
            message: Error message describing the authentication failure.

        """
        self.message = message
        super().__init__(self.message)
