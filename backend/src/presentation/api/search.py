"""API endpoints for search and report generation."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.application.services.search_report_service import SearchReportUseCase
from src.config import get_settings
from src.domain.models.search_report import SearchReport
from src.domain.models.user import User
from src.infrastructure.gemini.report_generator import GeminiReportGenerator
from src.infrastructure.vertex.search_engine import VertexAISearchEngine
from src.presentation.api.deps import get_current_user

router = APIRouter(prefix="/api/search", tags=["search"])

logger = logging.getLogger(__name__)


def get_search_use_case() -> SearchReportUseCase:
    """Dependency injection for SearchReportUseCase."""
    settings = get_settings()

    search_engine = VertexAISearchEngine(
        settings.google_cloud_project,
        settings.vertex_ai_data_store_id,
        settings.vertex_ai_location,
    )
    report_generator = GeminiReportGenerator(
        settings.google_cloud_project,
        settings.gemini_location,
        settings.gemini_report_model,
    )

    return SearchReportUseCase(search_engine, report_generator)


class SearchResponse(BaseModel):
    """Response model for search results and report."""

    query: str
    results_count: int
    search_results: list[dict]
    report: SearchReport


@router.get("")
def search_and_report(
    q: Annotated[str, Query(..., description="Search query")],
    _user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SearchReportUseCase, Depends(get_search_use_case)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> dict:
    """Search for books and generate a summary report."""
    try:
        return use_case.execute(q, limit, user_id=_user.uid)
    except Exception as e:
        logger.exception("Search failed for query: %s", q)
        raise HTTPException(
            status_code=500,
            detail="検索レポートの生成中にエラーが発生しました。しばらく時間を置いてから再度お試しください。",
        ) from e
