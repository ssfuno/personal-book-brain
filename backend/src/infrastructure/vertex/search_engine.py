"""Vertex AI Search Engine implementation."""

import logging

from google.cloud import discoveryengine_v1 as discoveryengine

from src.domain.interfaces.search_engine import SearchEngine, SearchResult

logger = logging.getLogger(__name__)


class VertexAISearchEngine(SearchEngine):
    """Implementation of SearchEngine using Vertex AI Search."""

    def __init__(
        self,
        project_id: str,
        data_store_id: str,
        location: str = "global",
    ) -> None:
        """Initialize the Vertex AI Search engine."""
        self.project_id = project_id
        self.data_store_id = data_store_id
        self.location = location
        self.client = discoveryengine.SearchServiceClient()
        self.serving_config = self.client.serving_config_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            serving_config="default_config",
        )

    def search(
        self, query: str, limit: int = 5, user_id: str | None = None
    ) -> list[SearchResult]:
        """Search documents in Vertex AI, optionally filtered by user."""
        try:
            filter_str = f'user_id: ANY("{user_id}")' if user_id else ""

            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=limit,
                filter=filter_str,
            )
            response = self.client.search(request)

            results: list[SearchResult] = []
            for result in response.results:
                data = {}
                # Extract struct data
                if hasattr(result.document, "derived_struct_data"):
                    data.update(result.document.derived_struct_data)

                # If struct data is in 'struct_data' (for imported JSONL)
                if hasattr(result.document, "struct_data"):
                    data.update(result.document.struct_data)

                # Add ID
                data["id"] = result.document.id
                results.append(SearchResult(data))

        except Exception:
            logger.exception("Vertex AI Search Error")
            return []
        else:
            return results
