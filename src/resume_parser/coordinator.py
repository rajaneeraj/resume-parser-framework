"""
ResumeExtractor — Coordinator that orchestrates field extraction.

Takes a dictionary of field extractors and runs each one against the
raw resume text to produce a structured ResumeData instance.
"""

import logging

from resume_parser.extractors.base import FieldExtractor
from resume_parser.models.resume_data import ResumeData

logger = logging.getLogger(__name__)

# Canonical field names used as dictionary keys for extractors
FIELD_NAME = "name"
FIELD_EMAIL = "email"
FIELD_SKILLS = "skills"


class ResumeExtractor:
    """Coordinates field-specific extractors to build a ResumeData object.

    Uses dependency injection: receives a dictionary mapping field names
    to their respective FieldExtractor instances. This allows complete
    flexibility in choosing which extraction strategy to use for each field.

    Args:
        extractors: A dictionary mapping field names ('name', 'email', 'skills')
                    to FieldExtractor instances.

    Example:
        >>> extractors = {
        ...     "name": RuleBasedNameExtractor(),
        ...     "email": RegexEmailExtractor(),
        ...     "skills": KeywordSkillsExtractor(),
        ... }
        >>> coordinator = ResumeExtractor(extractors)
        >>> data = coordinator.extract("John Doe\\njohn@email.com\\nSkills: Python")
    """

    def __init__(self, extractors: dict[str, FieldExtractor]):
        if not extractors:
            raise ValueError("At least one field extractor must be provided.")
        self._extractors = extractors
        logger.info(
            "ResumeExtractor initialized with extractors: %s",
            list(extractors.keys()),
        )

    @property
    def extractors(self) -> dict[str, FieldExtractor]:
        """Return the configured field extractors (read-only)."""
        return dict(self._extractors)

    def extract(self, text: str) -> ResumeData:
        """Run all configured extractors against the text and build ResumeData.

        Each extractor is run independently. If an extractor fails, a warning
        is logged and the field is set to its default value (empty string or
        empty list), allowing the remaining fields to still be extracted.

        Args:
            text: Raw text content extracted from a resume file.

        Returns:
            A ResumeData instance with all extracted fields populated.
        """
        logger.info("Starting field extraction...")
        results: dict[str, object] = {}

        for field_name, extractor in self._extractors.items():
            try:
                logger.info(
                    "Extracting field '%s' using %s",
                    field_name,
                    type(extractor).__name__,
                )
                value = extractor.extract(text)
                results[field_name] = value
                logger.info("Field '%s' extracted successfully.", field_name)
            except Exception as exc:
                logger.warning(
                    "Failed to extract field '%s': %s. Using default value.",
                    field_name,
                    exc,
                )
                # Default: empty string for name/email, empty list for skills
                results[field_name] = [] if field_name == FIELD_SKILLS else ""

        resume_data = ResumeData(
            name=str(results.get(FIELD_NAME, "")),
            email=str(results.get(FIELD_EMAIL, "")),
            skills=list(results.get(FIELD_SKILLS, [])),
        )

        logger.info("Extraction complete: %s", resume_data)
        return resume_data
