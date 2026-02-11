"""User domain model."""

from pydantic import BaseModel


class User(BaseModel):
    """Represents a User entity."""

    uid: str
    email: str | None = None
