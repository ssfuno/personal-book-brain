"""Firebase initialization module."""

import firebase_admin


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK.

    Checks if the default app is already initialized. If not, initializes it.
    In Cloud Run, default credentials are used automatically.
    Locally, GOOGLE_APPLICATION_CREDENTIALS is required.
    """
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app()
