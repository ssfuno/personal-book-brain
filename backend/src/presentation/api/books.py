"""API endpoints for managing books."""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel, ValidationError

from src.application.services.fetch_book_metadata_service import (
    FetchBookMetadataUseCase,
)
from src.application.services.list_books_service import (
    ListBooksUseCase,
)
from src.application.services.register_book_service import RegisterBookUseCase
from src.config import get_settings
from src.domain.models.book_master import TableOfContentsItem
from src.domain.models.user import User
from src.infrastructure.firestore.book_master_repository import (
    FirestoreBookMasterRepository,
)
from src.infrastructure.firestore.user_library_repository import (
    FirestoreUserLibraryRepository,
)
from src.infrastructure.gemini.toc_generator import GeminiTOCGenerator
from src.infrastructure.vertex.book_indexer import VertexAIBookIndexer
from src.presentation.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/books", tags=["books"])


def get_register_use_case() -> RegisterBookUseCase:
    """Dependency injection for RegisterBookUseCase."""
    settings = get_settings()
    db = firestore.client()

    book_master_repo = FirestoreBookMasterRepository(db)
    user_library_repo = FirestoreUserLibraryRepository(db)
    book_indexer = VertexAIBookIndexer(
        settings.google_cloud_project,
        settings.vertex_ai_data_store_id,
        settings.vertex_ai_location,
    )

    return RegisterBookUseCase(
        book_master_repo,
        user_library_repo,
        book_indexer,
        db,
    )


def get_fetch_metadata_use_case() -> FetchBookMetadataUseCase:
    """Dependency injection for FetchBookMetadataUseCase."""
    settings = get_settings()
    db = firestore.client()
    book_master_repo = FirestoreBookMasterRepository(db)
    toc_gen = GeminiTOCGenerator(
        project_id=settings.google_cloud_project,
        location=settings.gemini_location,
        model=settings.gemini_toc_model,
    )
    return FetchBookMetadataUseCase(book_master_repo, toc_gen, db)


def get_list_books_use_case() -> ListBooksUseCase:
    """Dependency injection for ListBooksUseCase."""
    db = firestore.client()
    book_master_repo = FirestoreBookMasterRepository(db)
    user_library_repo = FirestoreUserLibraryRepository(db)
    return ListBooksUseCase(book_master_repo, user_library_repo)


class BookPreviewRequest(BaseModel):
    """Request model for previewing a book."""

    isbn: str
    title: str | None = None


class BookRegisterRequest(BaseModel):
    """Request model for registering a book."""

    isbn: str
    title: str | None = None
    toc: list[TableOfContentsItem]


class BookResponse(BaseModel):
    """Response model for a book with user library info."""

    isbn: str
    title: str
    toc: list[TableOfContentsItem]
    added_at: datetime


class BookPreviewResponse(BaseModel):
    """Response model for book preview."""

    isbn: str
    title: str
    toc: list[TableOfContentsItem]


@router.post("/preview")
async def preview_book(
    request: BookPreviewRequest,
    _user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[FetchBookMetadataUseCase, Depends(get_fetch_metadata_use_case)],
) -> BookPreviewResponse:
    """Preview book metadata (TOC) before registration."""
    try:
        book_master = await use_case.execute(
            isbn=request.isbn,
            title=request.title,
        )
        return BookPreviewResponse(
            isbn=book_master.isbn,
            title=book_master.title,
            toc=book_master.toc,
        )
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="ISBNの形式が正しくありません。10桁または13桁の数字を入力してください。",
        ) from None
    except Exception as e:
        logger.exception("Failed to preview book")
        raise HTTPException(
            status_code=500,
            detail="書籍情報の取得中にエラーが発生しました。しばらく時間を置いてから再度お試しください。",
        ) from e


@router.post("")
async def create_book(
    request: BookRegisterRequest,
    background_tasks: BackgroundTasks,
    _user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[RegisterBookUseCase, Depends(get_register_use_case)],
) -> BookResponse:
    """Create a new book entry from ISBN."""
    try:
        # Pydantic model to dict list for use case
        toc_dict = [item.model_dump() for item in request.toc]

        book_master, library_entry = await use_case.execute(
            user=_user,
            isbn=request.isbn,
            title=request.title,
            toc=toc_dict,
        )

        # Background Indexing
        background_tasks.add_task(
            use_case.book_indexer.index_book,
            book=book_master,
            user_id=_user.uid,
        )
        return BookResponse(
            isbn=book_master.isbn,
            title=book_master.title,
            toc=book_master.toc,
            added_at=library_entry.added_at,
        )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=400,
            detail="入力内容に不備があります。ISBNやタイトルを確認してください。",
        ) from None
    except Exception as e:
        logger.exception("Failed to create book")
        raise HTTPException(
            status_code=500, detail="書籍の登録中にエラーが発生しました。"
        ) from e


@router.get("")
def list_books(
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListBooksUseCase, Depends(get_list_books_use_case)],
) -> list[BookResponse]:
    """List all books belonging to the authenticated user."""
    books_with_info = use_case.execute(user)
    return [
        BookResponse(
            isbn=item.book.isbn,
            title=item.book.title,
            toc=item.book.toc,
            added_at=item.library_entry.added_at,
        )
        for item in books_with_info
    ]
