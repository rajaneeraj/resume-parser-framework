"""
Unit tests for the ResumeExtractor coordinator.
"""

from unittest.mock import MagicMock

import pytest

from resume_parser.coordinator import ResumeExtractor
from resume_parser.extractors.base import FieldExtractor
from resume_parser.models.resume_data import ResumeData
from tests.sample_data import SAMPLE_RESUME_TEXT


def _mock_extractor(return_value) -> FieldExtractor:
    """Create a mock FieldExtractor that returns the given value."""
    mock = MagicMock(spec=FieldExtractor)
    mock.extract.return_value = return_value
    return mock


def _failing_extractor(error: Exception) -> FieldExtractor:
    """Create a mock FieldExtractor that raises the given error."""
    mock = MagicMock(spec=FieldExtractor)
    mock.extract.side_effect = error
    return mock


class TestResumeExtractor:
    """Tests for the ResumeExtractor coordinator."""

    def test_extract_all_fields(self):
        """Should extract all three fields successfully."""
        extractors = {
            "name": _mock_extractor("Jane Doe"),
            "email": _mock_extractor("jane@test.com"),
            "skills": _mock_extractor(["Python", "ML"]),
        }
        coordinator = ResumeExtractor(extractors)
        result = coordinator.extract(SAMPLE_RESUME_TEXT)

        assert isinstance(result, ResumeData)
        assert result.name == "Jane Doe"
        assert result.email == "jane@test.com"
        assert result.skills == ["Python", "ML"]

    def test_extract_single_field(self):
        """Should work with only one extractor configured."""
        extractors = {"email": _mock_extractor("jane@test.com")}
        coordinator = ResumeExtractor(extractors)
        result = coordinator.extract(SAMPLE_RESUME_TEXT)

        assert result.email == "jane@test.com"
        assert result.name == ""  # Default
        assert result.skills == []  # Default

    def test_extract_calls_each_extractor_once(self):
        """Should call each extractor exactly once with the input text."""
        mock_name = _mock_extractor("Jane")
        mock_email = _mock_extractor("j@t.com")

        extractors = {"name": mock_name, "email": mock_email}
        coordinator = ResumeExtractor(extractors)
        coordinator.extract("some text")

        mock_name.extract.assert_called_once_with("some text")
        mock_email.extract.assert_called_once_with("some text")

    def test_extract_graceful_failure(self):
        """Should handle extractor failure gracefully and use defaults."""
        extractors = {
            "name": _failing_extractor(RuntimeError("API down")),
            "email": _mock_extractor("jane@test.com"),
            "skills": _failing_extractor(ValueError("parse error")),
        }
        coordinator = ResumeExtractor(extractors)
        result = coordinator.extract(SAMPLE_RESUME_TEXT)

        # Failed fields get defaults; email still works
        assert result.name == ""
        assert result.email == "jane@test.com"
        assert result.skills == []

    def test_extract_empty_extractors_raises(self):
        """Should raise ValueError when no extractors are provided."""
        with pytest.raises(ValueError, match="At least one"):
            ResumeExtractor({})

    def test_extractors_property_returns_copy(self):
        """The extractors property should return a copy, not the internal dict."""
        extractors = {"name": _mock_extractor("Test")}
        coordinator = ResumeExtractor(extractors)

        returned = coordinator.extractors
        returned["extra"] = _mock_extractor("hacked")

        # Original should not be affected
        assert "extra" not in coordinator.extractors
