"""Firebase implementation of authentication service."""

from firebase_admin import auth

from src.domain.exceptions import AuthenticationError
from src.domain.interfaces.auth_service import AuthService
from src.domain.models.user import User


class FirebaseAuthService(AuthService):
    """Firebase implementation of the AuthService interface.

    This service uses Firebase Admin SDK to verify ID tokens
    and authenticate users.
    """

    def verify_token(self, token: str) -> User:
        """Verify a Firebase ID token and return the authenticated user.

        Args:
            token: The Firebase ID token to verify.

        Returns:
            User: The authenticated user with uid and email.

        Raises:
            AuthenticationError: If the token is invalid, expired,
                or verification fails.

        """
        try:
            decoded_token = auth.verify_id_token(token)
        except auth.InvalidIdTokenError as e:
            msg = f"Invalid ID token: {e!s}"
            raise AuthenticationError(msg) from e
        except auth.ExpiredIdTokenError as e:
            msg = f"Expired ID token: {e!s}"
            raise AuthenticationError(msg) from e
        except auth.RevokedIdTokenError as e:
            msg = f"Revoked ID token: {e!s}"
            raise AuthenticationError(msg) from e
        except auth.CertificateFetchError as e:
            msg = f"Certificate fetch error: {e!s}"
            raise AuthenticationError(msg) from e
        except Exception as e:
            # Catch any other unexpected errors
            msg = f"Authentication failed: {e!s}"
            raise AuthenticationError(msg) from e

        uid = decoded_token.get("uid")
        if not uid:
            msg = "Token does not contain user ID"
            raise AuthenticationError(msg)

        email = decoded_token.get("email")
        return User(uid=uid, email=email)
