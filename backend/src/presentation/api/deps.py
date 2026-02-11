"""Dependency injection components for the API."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.exceptions import AuthenticationError
from src.domain.interfaces.auth_service import AuthService
from src.domain.models.user import User
from src.infrastructure.firebase.auth_service import FirebaseAuthService
from src.infrastructure.firebase.setup import initialize_firebase

# Ensure firebase is initialized
initialize_firebase()

security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Provide the authentication service implementation.

    Returns:
        AuthService: The authentication service instance (Firebase implementation).

    """
    return FirebaseAuthService()


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """Validate authentication token and return the current user.

    Args:
        creds: HTTP authorization credentials containing the bearer token.
        auth_service: The authentication service to use for token verification.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If authentication fails (401 Unauthorized).

    """
    token = creds.credentials
    try:
        return auth_service.verify_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
