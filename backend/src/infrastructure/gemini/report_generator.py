"""Gemini-based Report Generator."""

import logging

from google import genai
from google.genai import types

from src.domain.interfaces.report_generator import ReportGenerator
from src.domain.models.search_report import SearchReport

logger = logging.getLogger(__name__)


class GeminiReportGenerator(ReportGenerator):
    """Implementation of ReportGenerator using Gemini."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model: str = "gemini-2.5-flash",
    ) -> None:
        """Initialize Gemini Report Generator."""
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )
        self.model_name = model

    def generate_report(self, query: str, search_results: list[dict]) -> SearchReport:
        """Generate a structured report from search results."""
        # Format search results for the prompt
        context = self._format_search_results(search_results)

        prompt = f"""
        あなたは蔵書検索アシスタントです。
        提供された目次情報に基づき、ユーザーの興味「{query}」に関連がありそうな本と章を特定して案内してください。

        【蔵書リスト（目次情報）】
        {context}

        【要件】
        1. **recommendations**: 提供された目次情報を含む書籍を全てリストアップしてください。
           - **summary**: 単なるタイトルの一致ではなく、「目次（構成）の全体像から見て、なぜこの本がユーザーの検索意図に沿うか」について、1文で簡潔に述べてください。
           - **relevant_chapters**: 関連性が高いと思われる章のタイトルのみを列挙してください（各本最大5項目）。
        2. **謙虚かつ構造的なトーン**: 内容を推測して解説するのではなく、「目次に〜や〜といったキーワードや構成が含まれているため、関連する知見が得られることが示唆される」というスタンスを維持してください。
        3. **簡潔さ**: 前置きや結びの言葉は一切省き、JSONデータのみを出力してください。
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SearchReport,
                ),
            )

            return SearchReport.model_validate_json(response.text)

        except Exception:
            logger.exception("Report generation error")
            return SearchReport(recommendations=[])

    def _format_search_results(self, results: list[dict]) -> str:
        if not results:
            return "（検索結果なし）"

        formatted = []
        for i, result in enumerate(results[:10], 1):  # Top 10
            title = result.get("title", "不明")
            isbn = result.get("isbn", result.get("id", "不明"))
            toc_text = result.get("toc_text", "")
            formatted.append(f"{i}. Title: {title} (ISBN: {isbn})\n   TOC: {toc_text}")

        return "\n\n".join(formatted)
