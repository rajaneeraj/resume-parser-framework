"""
FileParser — Abstract base class for file format parsers.

Each concrete parser extracts raw text content from a specific file format
(e.g., PDF, DOCX). The extracted text is then passed to field extractors
for structured information extraction.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class FileParser(ABC):
    """Abstract base class defining the interface for file parsers.

    Subclasses must implement the `parse` method to extract raw text
    from a specific file format.

    Attributes:
        supported_extensions: Set of file extensions this parser can handle
                              (e.g., {".pdf"}, {".docx"}).
    """

    supported_extensions: set[str] = set()

    def parse(self, file_path: str) -> str:
        """Extract raw text content from a file.

        Validates the file path and delegates to the format-specific
        `_extract_text` method implemented by subclasses.

        Args:
            file_path: Absolute or relative path to the resume file.

        Returns:
            The extracted text content as a single string.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not supported by this parser.
        """
        path = Path(file_path)
        self._validate_file(path)
        logger.info("Parsing file: %s", path.name)
        text = self._extract_text(path)
        logger.info(
            "Successfully extracted %d characters from %s",
            len(text),
            path.name,
        )
        return text

    @abstractmethod
    def _extract_text(self, path: Path) -> str:
        """Format-specific text extraction logic.

        Subclasses implement this method to handle the actual file reading
        and text extraction for their supported format.

        Args:
            path: Validated Path object pointing to the file.

        Returns:
            The extracted text content.
        """

    def _validate_file(self, path: Path) -> None:
        """Validate that the file exists and has a supported extension.

        Args:
            path: Path object to validate.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not in `supported_extensions`.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        suffix = path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file extension '{suffix}'. "
                f"Expected one of: {self.supported_extensions}"
            )
