"""
ResumeParserFramework — Top-level orchestrator combining parsing and extraction.

Provides a single entry point (`parse_resume`) that handles file format
detection, text extraction, and field extraction in one call.
"""

import logging
from pathlib import Path

from resume_parser.coordinator import ResumeExtractor
from resume_parser.models.resume_data import ResumeData
from resume_parser.parsers.base import FileParser
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.parsers.word_parser import WordParser

logger = logging.getLogger(__name__)

# Registry mapping file extensions to their default parser classes
_PARSER_REGISTRY: dict[str, type[FileParser]] = {
    ".pdf": PDFParser,
    ".docx": WordParser,
}


class ResumeParserFramework:
    """High-level framework combining file parsing and field extraction.

    Supports two modes of operation:
    1. **Explicit parser**: Pass a specific FileParser instance to always
       use that parser.
    2. **Auto-detection**: Omit the parser and the framework will automatically
       select the correct parser based on the file extension.

    Args:
        resume_extractor: A configured ResumeExtractor with field extractors.
        parser: Optional explicit FileParser. If None, auto-detection is used.

    Example:
        >>> framework = ResumeParserFramework(
        ...     resume_extractor=extractor,
        ...     parser=PDFParser(),  # or omit for auto-detection
        ... )
        >>> data = framework.parse_resume("resume.pdf")
    """

    def __init__(
        self,
        resume_extractor: ResumeExtractor,
        parser: FileParser | None = None,
    ):
        self._resume_extractor = resume_extractor
        self._parser = parser
        mode = type(parser).__name__ if parser else "auto-detect"
        logger.info("ResumeParserFramework initialized (parser mode: %s)", mode)

    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse a resume file and extract structured information.

        This is the main entry point of the framework. It:
        1. Selects the appropriate file parser (explicit or auto-detected).
        2. Extracts raw text from the file.
        3. Runs all configured field extractors on the text.
        4. Returns a structured ResumeData object.

        Args:
            file_path: Path to the resume file (PDF or DOCX).

        Returns:
            A ResumeData instance containing the extracted fields.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file type is unsupported or the extension
                        doesn't match the explicit parser.
        """
        logger.info("=" * 60)
        logger.info("Parsing resume: %s", file_path)

        # Step 1: Select parser
        parser = self._resolve_parser(file_path)
        logger.info("Using parser: %s", type(parser).__name__)

        # Step 2: Extract raw text
        raw_text = parser.parse(file_path)
        if not raw_text.strip():
            logger.warning("No text content extracted from file: %s", file_path)

        # Step 3: Run field extraction
        resume_data = self._resume_extractor.extract(raw_text)

        logger.info("Resume parsing complete for: %s", file_path)
        logger.info("=" * 60)
        return resume_data

    def _resolve_parser(self, file_path: str) -> FileParser:
        """Determine which parser to use for the given file.

        If an explicit parser was configured, it is returned directly.
        Otherwise, the file extension is used to auto-select a parser.

        Args:
            file_path: Path to the file.

        Returns:
            A FileParser instance appropriate for the file type.

        Raises:
            ValueError: If auto-detection fails (unsupported extension).
        """
        if self._parser is not None:
            return self._parser

        suffix = Path(file_path).suffix.lower()
        parser_class = _PARSER_REGISTRY.get(suffix)

        if parser_class is None:
            supported = ", ".join(_PARSER_REGISTRY.keys())
            raise ValueError(
                f"Unsupported file extension '{suffix}'. "
                f"Supported formats: {supported}"
            )

        logger.debug("Auto-detected parser for extension '%s'", suffix)
        return parser_class()
