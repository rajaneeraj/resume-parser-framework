"""
PDFParser — Extracts raw text content from PDF files.

Uses PyPDF2 to read each page of a PDF document and concatenate
the text content into a single string.
"""

import logging
from pathlib import Path

from PyPDF2 import PdfReader

from resume_parser.parsers.base import FileParser

logger = logging.getLogger(__name__)


class PDFParser(FileParser):
    """Concrete parser for PDF (.pdf) resume files.

    Reads all pages from a PDF and returns the combined text content.
    Handles multi-page documents and skips pages with no extractable text.
    """

    supported_extensions: set[str] = {".pdf"}

    def _extract_text(self, path: Path) -> str:
        """Extract text from all pages of a PDF file.

        Args:
            path: Path to the PDF file.

        Returns:
            Combined text from all pages, separated by newlines.

        Raises:
            RuntimeError: If the PDF cannot be read or is corrupted.
        """
        try:
            reader = PdfReader(str(path))
            pages_text: list[str] = []

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text.strip())
                    logger.debug(
                        "Page %d: extracted %d characters",
                        page_num,
                        len(page_text),
                    )
                else:
                    logger.debug("Page %d: no extractable text found", page_num)

            return "\n".join(pages_text)

        except Exception as exc:
            raise RuntimeError(
                f"Failed to extract text from PDF '{path.name}': {exc}"
            ) from exc
