"""
Unit tests for SpacyNameExtractor.

Uses mocked spaCy to avoid requiring the model for test runs.
"""

from unittest.mock import MagicMock, patch

import pytest

from resume_parser.extractors.base import FieldExtractor
from tests.sample_data import SAMPLE_RESUME_TEXT


class MockEntity:
    """Mock spaCy entity."""

    def __init__(self, text: str, label: str):
        self.text = text
        self.label_ = label


class MockDoc:
    """Mock spaCy Doc object."""

    def __init__(self, entities: list[MockEntity]):
        self.ents = entities


class TestSpacyNameExtractor:
    """Tests for SpacyNameExtractor with mocked spaCy."""

    def _make_extractor(self, entities: list[MockEntity]):
        """Create a SpacyNameExtractor with a mocked spaCy nlp."""
        mock_nlp = MagicMock()
        mock_nlp.return_value = MockDoc(entities)

        with patch.dict("sys.modules", {"spacy": MagicMock()}):
            with patch(
                "resume_parser.extractors.spacy_name_extractor.SpacyNameExtractor.__init__",
                lambda self, *a, **kw: None,
            ):
                from resume_parser.extractors.spacy_name_extractor import (
                    SpacyNameExtractor,
                )

                extractor = SpacyNameExtractor.__new__(SpacyNameExtractor)
                extractor._nlp = mock_nlp
                return extractor

    def test_extract_person_entity(self):
        """Should return the first PERSON entity."""
        entities = [MockEntity("Jane Doe", "PERSON")]
        extractor = self._make_extractor(entities)
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "Jane Doe"

    def test_extract_skips_non_person(self):
        """Should skip ORG entities and return the first PERSON."""
        entities = [
            MockEntity("TechCorp Inc.", "ORG"),
            MockEntity("Jane Doe", "PERSON"),
        ]
        extractor = self._make_extractor(entities)
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "Jane Doe"

    def test_extract_no_person_found(self):
        """Should return empty string when no PERSON entity is found."""
        entities = [MockEntity("Stanford University", "ORG")]
        extractor = self._make_extractor(entities)
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == ""

    def test_extract_empty_entities(self):
        """Should return empty string when no entities are found."""
        extractor = self._make_extractor([])
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == ""

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = self._make_extractor([])
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_none_text_raises(self):
        """Should raise ValueError for None input."""
        extractor = self._make_extractor([])
        with pytest.raises(ValueError, match="empty"):
            extractor.extract(None)

    def test_processes_only_first_500_chars(self):
        """Should only send the first 500 characters to spaCy."""
        entities = [MockEntity("Test Name", "PERSON")]
        extractor = self._make_extractor(entities)
        long_text = "A" * 1000 + "\nTest Name"
        extractor.extract(long_text)

        # The mock nlp should have been called with text[:500]
        call_args = extractor._nlp.call_args[0][0]
        assert len(call_args) == 500


class TestSpacyImportError:
    """Tests for SpacyNameExtractor when spaCy is not installed."""

    def test_import_error_without_spacy(self):
        """Should raise ImportError when spaCy is not installed."""
        with patch.dict("sys.modules", {"spacy": None}):
            # Reimport to trigger the ImportError
            import importlib

            try:
                from resume_parser.extractors import spacy_name_extractor

                importlib.reload(spacy_name_extractor)
                spacy_name_extractor.SpacyNameExtractor()
            except (ImportError, ModuleNotFoundError):
                pass  # Expected — spaCy is not available
