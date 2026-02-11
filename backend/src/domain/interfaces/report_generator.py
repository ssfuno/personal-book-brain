"""Interface for Report Generator."""

from abc import ABC, abstractmethod

from src.domain.models.search_report import SearchReport


class ReportGenerator(ABC):
    """Abstract interface for Report Generator."""

    @abstractmethod
    def generate_report(self, query: str, search_results: list[dict]) -> SearchReport:
        """Generate a report from search results."""
