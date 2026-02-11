"""Vertex AI Book Indexer implementation."""

import json
import logging

from google.cloud import discoveryengine_v1 as discoveryengine

from src.domain.interfaces.book_indexer import BookIndexer
from src.domain.models.book_master import BookMaster

logger = logging.getLogger(__name__)


class VertexAIBookIndexer(BookIndexer):
    """Indexer for books using Vertex AI Search."""

    def __init__(
        self,
        project_id: str,
        data_store_id: str,
        location: str = "global",
    ) -> None:
        """Initialize the Vertex AI Book Indexer."""
        self.client = discoveryengine.DocumentServiceClient()
        self.parent = self.client.branch_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            branch="default_branch",
        )

    def index_book(self, book: BookMaster, user_id: str) -> None:
        """Index a book into Vertex AI Search for a specific user."""
        try:
            # Flatten TOC for search
            # We want to make chapter titles searchable
            toc_text = "\n".join([f"{item.title}" for item in book.toc])

            # Generate deterministic document ID to allow multiple users for same book
            # while ensuring idempotency for the same user.
            document_id = f"{user_id}-{book.isbn}"

            document = discoveryengine.Document(
                struct_data={
                    "title": book.title,
                    "isbn": book.isbn,
                    "user_id": user_id,
                    "toc_text": toc_text,
                    # Add full JSON string of TOC if we want detailed retrieval
                    "toc_json": json.dumps(
                        [item.model_dump() for item in book.toc],
                        ensure_ascii=False,
                    ),
                },
            )

            request = discoveryengine.CreateDocumentRequest(
                parent=self.parent,
                document=document,
                document_id=document_id,
            )

            self.client.create_document(request=request)
            logger.info("Successfully indexed book %s to Vertex AI.", book.title)

        except Exception:
            logger.exception("Failed to index book to Vertex AI")
            # Don't break the main flow for MVP
