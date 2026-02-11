"""Authentication service interface."""

from abc import ABC, abstractmethod

from src.domain.models.user import User


class AuthService(ABC):
    """Interface for authentication services.

    This interface defines the contract for authentication operations,
    allowing different authentication providers (Firebase, Auth0, etc.)
    to be used interchangeably.
    """

    @abstractmethod
    def verify_token(self, token: str) -> User:
        """Verify an authentication token and return the authenticated user.

        Args:
            token: The authentication token to verify (e.g., JWT, ID token).

        Returns:
            User: The authenticated user.

        Raises:
            AuthenticationError: If the token is invalid or expired.

        """
