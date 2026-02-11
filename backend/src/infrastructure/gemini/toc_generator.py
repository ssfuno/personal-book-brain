"""Gemini-based TOC Generator implementation."""

import json
import logging
import re
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817
import httpx
from google import genai
from google.genai import types

from src.domain.interfaces.book_repository import TOCGenerator

logger = logging.getLogger(__name__)


class GeminiTOCGenerator(TOCGenerator):
    """Implementation of TOCGenerator using Gemini."""

    TOC_THRESHOLD = 0.8
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model: str = "gemini-2.5-pro",
    ) -> None:
        """Initialize Gemini client."""
        # Initialize Gen AI Client with Vertex AI backend
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )
        self.model_name = model

    async def _fetch_book_metadata(self, isbn: str) -> dict[str, Any]:
        """Fetch canonical metadata, trying NDL Search first, then Google Books."""
        # 1. Try NDL Search API first (accurate Japanese titles)
        metadata = await self._fetch_ndl_metadata(isbn)
        if metadata:
            logger.info("Got metadata from NDL Search: %s", metadata.get("title"))
            return metadata

        # 2. Fall back to Google Books API
        logger.info("NDL Search returned no results, falling back to Google Books")
        return await self._fetch_google_books_metadata(isbn)

    async def _fetch_ndl_metadata(self, isbn: str) -> dict[str, Any]:
        """Fetch metadata from National Diet Library Search API."""
        url = f"https://ndlsearch.ndl.go.jp/api/opensearch?isbn={isbn}"
        namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcndl": "http://ndl.go.jp/dcndl/terms/",
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == httpx.codes.OK:
                    root = ET.fromstring(response.text)
                    # Find the first <item> element
                    item = root.find(".//item")
                    if item is not None:
                        title = item.findtext(
                            "dc:title", default="", namespaces=namespaces
                        )
                        # dc:creator may contain birth year like "水野, 貴明, 1973-"
                        creator_raw = item.findtext(
                            "dc:creator", default="", namespaces=namespaces
                        )
                        # Clean up creator: remove birth year pattern
                        authors = []
                        if creator_raw:
                            # Split by comma, take name parts, remove year patterns
                            parts = [p.strip() for p in creator_raw.split(",")]
                            name_parts = [
                                p for p in parts if not re.match(r"^\d{4}-?", p)
                            ]
                            if name_parts:
                                authors = ["".join(name_parts)]

                        if title:
                            return {
                                "title": title,
                                "description": "",
                                "authors": authors,
                            }
        except Exception:
            logger.exception("Error fetching metadata from NDL Search")
        return {}

    async def _fetch_google_books_metadata(self, isbn: str) -> dict[str, Any]:
        """Fetch metadata from Google Books API (fallback)."""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == httpx.codes.OK:
                    data = response.json()
                    if data.get("totalItems", 0) > 0:
                        volume_info = data["items"][0]["volumeInfo"]
                        return {
                            "title": volume_info.get("title", ""),
                            "description": volume_info.get("description", ""),
                            "authors": volume_info.get("authors", []),
                        }
        except Exception:
            logger.exception("Error fetching metadata from Google Books")
        return {}

    async def generate_from_query(self, query: str) -> dict[str, Any]:
        """Generate TOC from query."""
        # 1. First, try to get precise metadata from Google Books
        # if the query looks like an ISBN
        isbn_match = re.search(r"ISBN:\s*(\d{10,13})", query)
        book_metadata = {}
        if isbn_match:
            isbn = isbn_match.group(1)
            book_metadata = await self._fetch_book_metadata(isbn)

        # 2. Refine prompt based on metadata
        target_info = f"ISBN: {query}"
        if book_metadata.get("title"):
            target_info = (
                f"Book Title: {book_metadata['title']}, "
                f"Authors: {', '.join(book_metadata['authors'])}"
            )

        prompt = f"""
        あなたは、書籍の目次（Table of Contents）を作成する専門家です。
        Google検索ツールを積極的に使用して、以下の書籍の正確かつ詳細な目次を見つけてください。

        書籍情報:
        "{target_info}"

        検索のヒント:
        - "書籍タイトル 目次" や "Book Title Table of Contents" で検索すると詳細が見つかることが多いです。
        - 版元（出版社）の公式サイトや、Amazonなどの商品ページ情報を参照してください。

        要件:
        1. **正確性最優先**: 検索結果に**明示的に**書かれている章・節・項のみを含めてください。
        2. **ハルシネーション（嘘）の禁止**:
           - 検索結果に見つからない章題や節題を**絶対に創作しないでください**。
           - これは**すべての階層**に適用されます。
           - 詳細（Level 2, 3）が見つからない場合は、
             見つかった範囲（Level 1のみなど）で出力してください。
             無理に埋める必要はありません。
        3. **省略禁止**:
           見つかった項目については、"..."などで省略せず正式名称を出力してください。
        4. **階層構造**:
           - level 1: 章 (Chapter, Partなど)
           - level 2: 節 (Section)
           - level 3: 項 (Subsection)
        5. **フォーマット**: 以下のJSON形式のみを出力してください。

        出力フォーマット (JSON):
        あなたの回答は、以下のJSON形式のデータのみを含める必要があります。説明や前置き、Markdownのコードブロック（```json ... ```）は含めず、純粋なJSON文字列として出力してください。

        {{
            "title": "正式な書籍タイトル",
            "toc": [
                {{ "title": "Chapter 1: ...", "level": 1 }},
                {{ "title": "1.1 ...", "level": 2 }}
            ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )

            text = response.text
            # Robust extraction of the first balanced JSON object
            try:
                start_index = text.find("{")
                if start_index == -1:
                    logger.warning("No JSON starting brace found in response: %s", text)
                    return {
                        "title": book_metadata.get("title") or "Unknown Title",
                        "toc": [],
                    }

                # Use raw_decode to find the first valid balanced JSON block
                decoder = json.JSONDecoder()
                data, _ = decoder.raw_decode(text[start_index:])
            except (json.JSONDecodeError, ValueError):
                # Fallback: If raw_decode fails, try the greedy regex as a last resort
                logger.warning("JSONDecoder failed, trying greedy regex fallback...")
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        logger.warning("Failed to decode JSON from: %r", text)
                        return {
                            "title": book_metadata.get("title") or "Unknown Title",
                            "toc": [],
                        }
                else:
                    logger.warning("Failed to decode JSON from: %r", text)
                    return {
                        "title": book_metadata.get("title") or "Unknown Title",
                        "toc": [],
                    }

            # Use Google Books title as a priority if Gemini returned something generic
            final_title = (
                book_metadata.get("title") or data.get("title") or "Unknown Title"
            )

            toc = data.get("toc", [])
            toc = self._normalize_toc(toc)
        except Exception:
            logger.exception("Error generating TOC/Title")
            return {
                "title": book_metadata.get("title") or "Unknown Title",
                "toc": [],
            }
        else:
            return {
                "title": final_title,
                "toc": toc,
            }

    def _normalize_toc(self, toc: list[dict]) -> list[dict]:
        """Normalize TOC with multi-stage fallback.

        Strategy:
        1. Level 2 Check: If L2 coverage is inconsistent across chapters, drop L2.
        2. Level 3 Check: If L3 coverage is inconsistent across sections, drop L3.

        Ignores "Appendix", "Index", etc. from strict counting.
        """
        if not toc:
            return []

        logger.info("[TOC Normalize] Input TOC has %d items", len(toc))

        def is_ignored_section(title: str) -> bool:
            t = title.lower()
            return any(
                x in t
                for x in [
                    "appendix",
                    "index",
                    "bibliography",
                    "reference",
                    "索引",
                    "付録",
                    "参考文献",
                ]
            )

        # --- Step 1: Check Level 2 Consistency ---
        toc = self._check_level_2_consistency(toc, is_ignored_section)

        # --- Step 2: Check Level 3 Consistency ---
        toc = self._check_level_3_consistency(toc)

        logger.info("[TOC Normalize] Final TOC has %d items", len(toc))
        return toc

    def _check_level_2_consistency(
        self, toc: list[dict], is_ignored_section: callable
    ) -> list[dict]:
        """Check L2 consistency and flatten to L1 if needed."""
        # For each L1, check if there are ANY L2 items between it and the next L1
        level1_indices = [
            i for i, item in enumerate(toc) if item.get("level") == self.LEVEL_1
        ]

        if len(level1_indices) == 0:
            return toc

        valid_chapters = 0
        detailed_chapters = 0

        for idx, l1_idx in enumerate(level1_indices):
            title = toc[l1_idx].get("title", "")
            if is_ignored_section(title):
                logger.info("[TOC Normalize] Ignoring '%s'", title)
                continue

            valid_chapters += 1

            # Determine the range to check: from current L1 to next L1 (or end of list)
            next_l1_idx = (
                level1_indices[idx + 1] if idx + 1 < len(level1_indices) else len(toc)
            )

            # Check if any item in range (l1_idx+1, next_l1_idx) has level > 1
            has_l2_between = any(
                toc[i].get("level", self.LEVEL_1) > self.LEVEL_1
                for i in range(l1_idx + 1, next_l1_idx)
            )

            if has_l2_between:
                detailed_chapters += 1
                logger.debug(
                    "[TOC Normalize] '%s' has children (items %d to %d)",
                    title,
                    l1_idx + 1,
                    next_l1_idx - 1,
                )
            else:
                logger.debug("[TOC Normalize] '%s' is flat", title)

        logger.info(
            "[TOC Normalize] L2 Check: %d/%d chapters have L2 children",
            detailed_chapters,
            valid_chapters,
        )

        if valid_chapters > 0:
            l2_ratio = detailed_chapters / valid_chapters
            logger.info(
                "[TOC Normalize] L2 Ratio: %.2f (threshold: %.1f)",
                l2_ratio,
                self.TOC_THRESHOLD,
            )

            if 0 < l2_ratio < self.TOC_THRESHOLD:
                # Inconsistent - some have details, some don't. Flatten to L1.
                logger.warning(
                    "[TOC Normalize] L2 Inconsistency -> Flattening to Level 1. Original TOC: %s",
                    json.dumps(toc, ensure_ascii=False),
                )
                return [item for item in toc if item.get("level") == self.LEVEL_1]
            if l2_ratio == 0:
                # No chapters have L2 at all - already flat, keep as is
                logger.info("[TOC Normalize] Already flat (no L2), keeping as is")
                return toc

        return toc

    def _check_level_3_consistency(self, toc: list[dict]) -> list[dict]:
        """Check L3 consistency and flatten to L2 if needed."""
        # Only if we kept L2, check if L3 is consistent
        level2_indices = [
            i for i, item in enumerate(toc) if item.get("level") == self.LEVEL_2
        ]

        if len(level2_indices) == 0:
            return toc

        detailed_sections = 0
        for _idx, l2_idx in enumerate(level2_indices):
            # Range: from current L2 to next L2 (or next L1, or end)
            next_boundary = len(toc)
            for i in range(l2_idx + 1, len(toc)):
                if toc[i].get("level", self.LEVEL_1) <= self.LEVEL_2:
                    next_boundary = i
                    break

            has_l3_between = any(
                toc[i].get("level", self.LEVEL_1) == self.LEVEL_3
                for i in range(l2_idx + 1, next_boundary)
            )
            if has_l3_between:
                detailed_sections += 1

        total_sections = len(level2_indices)
        logger.info(
            "[TOC Normalize] L3 Check: %d/%d sections have L3 children",
            detailed_sections,
            total_sections,
        )

        if total_sections > 0:
            l3_ratio = detailed_sections / total_sections
            if 0 < l3_ratio < self.TOC_THRESHOLD:
                logger.warning(
                    "[TOC Normalize] L3 Inconsistency -> Dropping Level 3. Original TOC: %s",
                    json.dumps(toc, ensure_ascii=False),
                )
                return [item for item in toc if item.get("level") < self.LEVEL_3]
        return toc

    def generate_from_image(self, _image_data: bytes) -> list[dict]:
        """Generate TOC from image (Not implemented)."""
        # Implementation for Vision
        return []
