"""Domain interfaces."""

from src.domain.interfaces.auth_service import AuthService
from src.domain.interfaces.book_indexer import BookIndexer
from src.domain.interfaces.book_repository import (
    BookMasterRepository,
    TOCGenerator,
    UserLibraryRepository,
)
from src.domain.interfaces.report_generator import ReportGenerator
from src.domain.interfaces.search_engine import SearchEngine, SearchResult

__all__ = [
    "AuthService",
    "BookIndexer",
    "BookMasterRepository",
    "ReportGenerator",
    "SearchEngine",
    "SearchResult",
    "TOCGenerator",
    "UserLibraryRepository",
]
