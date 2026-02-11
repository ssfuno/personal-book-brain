"""Search Report domain models."""

from pydantic import BaseModel, Field


class ChapterRef(BaseModel):
    """Reference to a specific chapter in a book."""

    chapter_title: str = Field(..., description="Title of the chapter")


class RecommendedBook(BaseModel):
    """A book recommended in the search report."""

    isbn: str = Field(..., description="ISBN of the book")
    title: str = Field(..., description="Title of the book")
    summary: str = Field(
        ..., description="Overview of the book and its relevance to the query"
    )
    relevant_chapters: list[ChapterRef] = Field(
        ..., description="List of relevant chapters"
    )


class SearchReport(BaseModel):
    """The structured search report."""

    recommendations: list[RecommendedBook] = Field(
        ..., description="List of recommended books"
    )
