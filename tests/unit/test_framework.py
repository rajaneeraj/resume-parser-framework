"""
Unit tests for the ResumeParserFramework.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from resume_parser.coordinator import ResumeExtractor
from resume_parser.framework import ResumeParserFramework
from resume_parser.models.resume_data import ResumeData
from resume_parser.parsers.base import FileParser
from resume_parser.parsers.word_parser import WordParser


def _mock_parser(return_text: str = "mock text") -> FileParser:
    """Create a mock FileParser."""
    mock = MagicMock(spec=FileParser)
    mock.parse.return_value = return_text
    return mock


def _mock_extractor(resume_data: ResumeData | None = None) -> ResumeExtractor:
    """Create a mock ResumeExtractor."""
    mock = MagicMock(spec=ResumeExtractor)
    mock.extract.return_value = resume_data or ResumeData(
        name="Test", email="test@test.com", skills=["Python"]
    )
    return mock


class TestResumeParserFramework:
    """Tests for the ResumeParserFramework."""

    def test_parse_resume_with_explicit_parser(self, tmp_docx: Path):
        """Should use the explicit parser when provided."""
        parser = WordParser()
        extractor = _mock_extractor()

        framework = ResumeParserFramework(resume_extractor=extractor, parser=parser)
        result = framework.parse_resume(str(tmp_docx))

        assert isinstance(result, ResumeData)
        extractor.extract.assert_called_once()

    def test_parse_resume_auto_detect_docx(self, tmp_docx: Path):
        """Should auto-detect WordParser for .docx files."""
        extractor = _mock_extractor()
        framework = ResumeParserFramework(resume_extractor=extractor)

        result = framework.parse_resume(str(tmp_docx))
        assert isinstance(result, ResumeData)

    def test_parse_resume_auto_detect_pdf(self, tmp_pdf: Path):
        """Should auto-detect PDFParser for .pdf files."""
        extractor = _mock_extractor()
        framework = ResumeParserFramework(resume_extractor=extractor)

        result = framework.parse_resume(str(tmp_pdf))
        assert isinstance(result, ResumeData)

    def test_parse_resume_unsupported_format(self, tmp_txt: Path):
        """Should raise ValueError for unsupported file formats."""
        extractor = _mock_extractor()
        framework = ResumeParserFramework(resume_extractor=extractor)

        with pytest.raises(ValueError, match="Unsupported file extension"):
            framework.parse_resume(str(tmp_txt))

    def test_parse_resume_file_not_found(self):
        """Should raise FileNotFoundError for non-existent files."""
        parser = _mock_parser()
        parser.parse.side_effect = FileNotFoundError("File not found")
        extractor = _mock_extractor()

        framework = ResumeParserFramework(resume_extractor=extractor, parser=parser)

        with pytest.raises(FileNotFoundError):
            framework.parse_resume("/nonexistent/file.pdf")

    def test_parse_resume_passes_text_to_extractor(self, tmp_docx: Path):
        """Should pass the parsed text to the ResumeExtractor."""
        extractor = _mock_extractor()
        framework = ResumeParserFramework(resume_extractor=extractor)

        framework.parse_resume(str(tmp_docx))

        # The extractor should have been called with some text
        extractor.extract.assert_called_once()
        call_args = extractor.extract.call_args[0][0]
        assert isinstance(call_args, str)

    def test_parse_resume_returns_extractor_result(self, tmp_docx: Path):
        """Should return the ResumeData from the extractor."""
        expected = ResumeData(name="Custom", email="custom@test.com", skills=["Go"])
        extractor = _mock_extractor(expected)
        framework = ResumeParserFramework(resume_extractor=extractor)

        result = framework.parse_resume(str(tmp_docx))
        assert result == expected
