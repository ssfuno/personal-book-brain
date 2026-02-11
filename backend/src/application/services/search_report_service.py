"""Service for searching and reporting."""

from src.domain.interfaces.report_generator import ReportGenerator
from src.domain.interfaces.search_engine import SearchEngine
from src.domain.models.search_report import SearchReport


class SearchReportUseCase:
    """Use case for searching books and generating reports."""

    def __init__(
        self,
        search_engine: SearchEngine,
        report_generator: ReportGenerator,
    ) -> None:
        """Initialize the use case."""
        self.search_engine = search_engine
        self.report_generator = report_generator

    def execute(self, query: str, limit: int = 10, user_id: str | None = None) -> dict:
        """Execute the search and report generation process."""
        # 1. Search for relevant books (filtered by user if user_id provided)
        search_results = self.search_engine.search(query, limit, user_id=user_id)

        # 2. Generate report only if there are search results
        if search_results:
            report = self.report_generator.generate_report(query, search_results)
        else:
            report = SearchReport(recommendations=[])

        return {
            "query": query,
            "results_count": len(search_results),
            "search_results": search_results,
            "report": report,
        }
