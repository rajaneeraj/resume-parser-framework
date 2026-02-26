"""
Name Extractors — Strategies for extracting candidate names from resume text.

Provides:
- RuleBasedNameExtractor: Heuristic approach using the first non-empty line.
- LLMNameExtractor: Uses Gemini API for intelligent name extraction.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from resume_parser.extractors.base import FieldExtractor

if TYPE_CHECKING:
    from resume_parser.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class RuleBasedNameExtractor(FieldExtractor):
    """Extracts candidate name using heuristic rules.

    Strategy: The candidate's name is typically the first non-empty,
    non-email, non-phone line in a resume. This extractor takes the
    first line, strips common prefixes, and cleans it.

    This is a reliable fallback when LLM access is unavailable.
    """

    def extract(self, text: str) -> str:
        """Extract the candidate name from the first meaningful line.

        Args:
            text: Raw text content from a resume.

        Returns:
            The extracted name, or an empty string if extraction fails.

        Raises:
            ValueError: If the input text is empty.
        """
        self._validate_input(text)

        lines = text.strip().splitlines()
        for line in lines:
            cleaned = line.strip()
            # Skip empty lines, lines that look like emails or phone numbers
            if not cleaned:
                continue
            if "@" in cleaned:
                continue
            if re.match(r"^[\d\(\)+\-\s]+$", cleaned):
                continue

            # Remove common title prefixes
            name = re.sub(
                r"^(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
            name = name.strip()

            # A valid name should be mostly alphabetic with spaces
            if name and re.match(r"^[A-Za-z\s.\-']+$", name):
                logger.info("Name extracted (rule-based): %s", name)
                return name

        logger.warning("No name found using rule-based extraction.")
        return ""


class LLMNameExtractor(FieldExtractor):
    """Extracts candidate name using the Gemini LLM.

    Sends the resume text to the Gemini API with a targeted prompt
    to identify and extract the person's full name. This approach
    handles non-standard resume formats better than rule-based methods.

    Args:
        client: An initialized GeminiClient instance.
    """

    def __init__(self, client: GeminiClient):
        self._client = client

    def extract(self, text: str) -> str:
        """Extract the candidate name using the Gemini LLM.

        Args:
            text: Raw text content from a resume.

        Returns:
            The extracted name, or an empty string if extraction fails.

        Raises:
            ValueError: If the input text is empty.
            RuntimeError: If the LLM API call fails.
        """
        self._validate_input(text)

        prompt = (
            "Extract the full name of the person from the following resume text. "
            "Return ONLY the full name as a plain string with no extra text, "
            "quotes, or formatting. If no name is found, return 'UNKNOWN'.\n\n"
            f"Resume text:\n{text}"
        )

        result = self._client.generate(prompt).strip().strip('"').strip("'")

        if result.upper() == "UNKNOWN":
            logger.warning("LLM could not identify a name in the text.")
            return ""

        logger.info("Name extracted (LLM): %s", result)
        return result
