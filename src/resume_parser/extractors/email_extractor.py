"""
Email Extractors — Strategies for extracting email addresses from resume text.

Currently provides:
- RegexEmailExtractor: Uses a regular expression pattern to find email addresses.
"""

import logging
import re

from resume_parser.extractors.base import FieldExtractor

logger = logging.getLogger(__name__)

# RFC 5322 simplified email regex pattern
_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)


class RegexEmailExtractor(FieldExtractor):
    """Extracts email addresses from text using regex pattern matching.

    This is the most reliable strategy for email extraction since email
    addresses follow a well-defined format that regex handles effectively.

    Returns the first email found in the text.
    """

    def extract(self, text: str) -> str:
        """Extract the first email address from the resume text.

        Args:
            text: Raw text content from a resume.

        Returns:
            The first email address found, or an empty string if none found.

        Raises:
            ValueError: If the input text is empty.
        """
        self._validate_input(text)

        match = _EMAIL_PATTERN.search(text)
        if match:
            email = match.group(0)
            logger.info("Email extracted: %s", email)
            return email

        logger.warning("No email address found in text.")
        return ""
