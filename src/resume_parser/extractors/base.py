"""
FieldExtractor — Abstract base class for field-specific extraction strategies.

Each concrete extractor implements a specific strategy (regex, rule-based, LLM)
for extracting a single field from raw resume text. This follows the Strategy
pattern: different extractors can be swapped in at runtime.
"""

from abc import ABC, abstractmethod
from typing import Any


class FieldExtractor(ABC):
    """Abstract base class defining the interface for field extractors.

    Each concrete extractor is responsible for extracting a single piece
    of information (e.g., name, email, skills) from raw resume text.

    The Strategy pattern allows different extraction algorithms to be
    used interchangeably for the same field.
    """

    @abstractmethod
    def extract(self, text: str) -> Any:
        """Extract a specific field value from raw text.

        Args:
            text: Raw text content extracted from a resume file.

        Returns:
            The extracted field value. The type depends on the field:
            - name: str
            - email: str
            - skills: list[str]

        Raises:
            ValueError: If the text is empty or None.
            ExtractionError: If extraction fails due to an external error (e.g., API).
        """

    def _validate_input(self, text: str) -> None:
        """Validate that the input text is non-empty.

        Args:
            text: The text to validate.

        Raises:
            ValueError: If text is None or empty after stripping whitespace.
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty or None.")
