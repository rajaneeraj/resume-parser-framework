"""
Unit tests for all FieldExtractor implementations.
"""

from unittest.mock import MagicMock, patch

import pytest

from resume_parser.extractors.base import FieldExtractor
from resume_parser.extractors.email_extractor import RegexEmailExtractor
from resume_parser.extractors.name_extractor import (
    RuleBasedNameExtractor,
    LLMNameExtractor,
)
from resume_parser.extractors.skills_extractor import (
    KeywordSkillsExtractor,
    LLMSkillsExtractor,
)
from tests.sample_data import (
    SAMPLE_RESUME_TEXT,
    SAMPLE_RESUME_TEXT_MINIMAL,
    SAMPLE_RESUME_TEXT_NO_EMAIL,
)


# ──────────────────────────────────────────────────────────────
# FieldExtractor ABC tests
# ──────────────────────────────────────────────────────────────


class TestFieldExtractorAbstract:
    """Test that FieldExtractor cannot be instantiated directly."""

    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            FieldExtractor()


# ──────────────────────────────────────────────────────────────
# RegexEmailExtractor tests
# ──────────────────────────────────────────────────────────────


class TestRegexEmailExtractor:
    """Tests for RegexEmailExtractor."""

    def test_extract_valid_email(self):
        """Should extract a standard email address."""
        extractor = RegexEmailExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "jane.doe@gmail.com"

    def test_extract_email_from_minimal_text(self):
        """Should extract email from minimal resume text."""
        extractor = RegexEmailExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT_MINIMAL)
        assert result == "john.smith@outlook.com"

    def test_extract_no_email_found(self):
        """Should return empty string when no email is present."""
        extractor = RegexEmailExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT_NO_EMAIL)
        assert result == ""

    def test_extract_email_with_plus(self):
        """Should handle email addresses with + character."""
        extractor = RegexEmailExtractor()
        result = extractor.extract("Contact: user+tag@example.com")
        assert result == "user+tag@example.com"

    def test_extract_email_with_subdomain(self):
        """Should handle email addresses with subdomains."""
        extractor = RegexEmailExtractor()
        result = extractor.extract("Email: user@mail.company.co.uk")
        assert result == "user@mail.company.co.uk"

    def test_extract_first_email_when_multiple(self):
        """Should return the first email when multiple are present."""
        extractor = RegexEmailExtractor()
        text = "primary@test.com and secondary@test.com"
        result = extractor.extract(text)
        assert result == "primary@test.com"

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = RegexEmailExtractor()
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_none_text_raises(self):
        """Should raise ValueError for None input."""
        extractor = RegexEmailExtractor()
        with pytest.raises(ValueError, match="empty"):
            extractor.extract(None)

    def test_extract_whitespace_only_raises(self):
        """Should raise ValueError for whitespace-only input."""
        extractor = RegexEmailExtractor()
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("   \n\t  ")


# ──────────────────────────────────────────────────────────────
# RuleBasedNameExtractor tests
# ──────────────────────────────────────────────────────────────


class TestRuleBasedNameExtractor:
    """Tests for RuleBasedNameExtractor."""

    def test_extract_name_from_first_line(self):
        """Should extract name from the first line of resume text."""
        extractor = RuleBasedNameExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "Jane Doe"

    def test_extract_name_from_minimal_text(self):
        """Should extract name from minimal resume."""
        extractor = RuleBasedNameExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT_MINIMAL)
        assert result == "John Smith"

    def test_extract_name_skips_email_line(self):
        """Should skip lines that contain email addresses."""
        extractor = RuleBasedNameExtractor()
        text = "user@example.com\nJohn Doe\nSome content"
        result = extractor.extract(text)
        assert result == "John Doe"

    def test_extract_name_skips_phone_line(self):
        """Should skip lines that look like phone numbers."""
        extractor = RuleBasedNameExtractor()
        text = "+1 (555) 123-4567\nJane Smith\nContent"
        result = extractor.extract(text)
        assert result == "Jane Smith"

    def test_extract_name_removes_title_prefix(self):
        """Should strip common title prefixes like Dr., Mr., etc."""
        extractor = RuleBasedNameExtractor()
        text = "Dr. James Wilson\njames@test.com"
        result = extractor.extract(text)
        assert result == "James Wilson"

    def test_extract_name_handles_hyphenated(self):
        """Should handle hyphenated names."""
        extractor = RuleBasedNameExtractor()
        text = "Mary-Jane Watson\nmj@test.com"
        result = extractor.extract(text)
        assert result == "Mary-Jane Watson"

    def test_extract_name_handles_apostrophe(self):
        """Should handle names with apostrophes."""
        extractor = RuleBasedNameExtractor()
        text = "Patrick O'Brien\npatrick@test.com"
        result = extractor.extract(text)
        assert result == "Patrick O'Brien"

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = RuleBasedNameExtractor()
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_no_valid_name(self):
        """Should return empty string when no valid name line is found."""
        extractor = RuleBasedNameExtractor()
        text = "user@email.com\n+1 555-1234\n12345"
        result = extractor.extract(text)
        assert result == ""


# ──────────────────────────────────────────────────────────────
# LLMNameExtractor tests (mocked)
# ──────────────────────────────────────────────────────────────


class TestLLMNameExtractor:
    """Tests for LLMNameExtractor with mocked Gemini client."""

    def _make_extractor(self, response: str) -> LLMNameExtractor:
        """Create an LLMNameExtractor with a mocked client."""
        mock_client = MagicMock()
        mock_client.generate.return_value = response
        return LLMNameExtractor(mock_client)

    def test_extract_name_success(self):
        """Should extract name from LLM response."""
        extractor = self._make_extractor("Jane Doe")
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "Jane Doe"

    def test_extract_name_strips_quotes(self):
        """Should strip surrounding quotes from LLM response."""
        extractor = self._make_extractor('"Jane Doe"')
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == "Jane Doe"

    def test_extract_name_unknown_returns_empty(self):
        """Should return empty string when LLM returns UNKNOWN."""
        extractor = self._make_extractor("UNKNOWN")
        result = extractor.extract(SAMPLE_RESUME_TEXT)
        assert result == ""

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = self._make_extractor("irrelevant")
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_calls_client_with_prompt(self):
        """Should call the Gemini client with a prompt containing the text."""
        mock_client = MagicMock()
        mock_client.generate.return_value = "Test Name"
        extractor = LLMNameExtractor(mock_client)
        extractor.extract("some resume text")

        mock_client.generate.assert_called_once()
        prompt = mock_client.generate.call_args[0][0]
        assert "some resume text" in prompt

    def test_extract_api_failure_propagates(self):
        """Should propagate RuntimeError from failed API calls."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API error")
        extractor = LLMNameExtractor(mock_client)

        with pytest.raises(RuntimeError, match="API error"):
            extractor.extract(SAMPLE_RESUME_TEXT)


# ──────────────────────────────────────────────────────────────
# KeywordSkillsExtractor tests
# ──────────────────────────────────────────────────────────────


class TestKeywordSkillsExtractor:
    """Tests for KeywordSkillsExtractor."""

    def test_extract_multiple_skills(self):
        """Should find multiple matching skills."""
        extractor = KeywordSkillsExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert isinstance(result, list)
        assert "Python" in result
        assert "Machine Learning" in result
        assert "TensorFlow" in result
        assert "AWS" in result

    def test_extract_with_custom_keywords(self):
        """Should match against custom keyword list."""
        extractor = KeywordSkillsExtractor(keywords=["Python", "Rust", "Go"])
        result = extractor.extract("I know Python and Go, but not Rust.")

        assert "Python" in result
        assert "Go" in result
        assert "Rust" in result  # "Rust" appears in text even with "not"

    def test_extract_no_skills_found(self):
        """Should return empty list when no skills match."""
        extractor = KeywordSkillsExtractor(keywords=["Haskell", "Erlang"])
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == []

    def test_extract_case_insensitive(self):
        """Should match skills case-insensitively."""
        extractor = KeywordSkillsExtractor(keywords=["python"])
        result = extractor.extract("I know Python programming.")

        assert len(result) == 1

    def test_extract_word_boundary_matching(self):
        """Should not partially match (e.g., 'R' in 'React')."""
        extractor = KeywordSkillsExtractor(keywords=["R"])
        result = extractor.extract("I use React and REST APIs.")

        # "R" should NOT match "React" or "REST" due to word boundaries
        assert "R" not in result

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = KeywordSkillsExtractor()
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_from_minimal_text(self):
        """Should extract skills from minimal resume."""
        extractor = KeywordSkillsExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT_MINIMAL)

        assert "Python" in result
        assert "Java" in result


# ──────────────────────────────────────────────────────────────
# LLMSkillsExtractor tests (mocked)
# ──────────────────────────────────────────────────────────────


class TestLLMSkillsExtractor:
    """Tests for LLMSkillsExtractor with mocked Gemini client."""

    def _make_extractor(self, response: str) -> LLMSkillsExtractor:
        """Create an LLMSkillsExtractor with a mocked client."""
        mock_client = MagicMock()
        mock_client.generate.return_value = response
        return LLMSkillsExtractor(mock_client)

    def test_extract_valid_json_list(self):
        """Should parse a valid JSON array response."""
        extractor = self._make_extractor('["Python", "Machine Learning", "AWS"]')
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == ["Python", "Machine Learning", "AWS"]

    def test_extract_handles_markdown_fences(self):
        """Should strip markdown code fences from LLM response."""
        extractor = self._make_extractor(
            '```json\n["Python", "Docker"]\n```'
        )
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == ["Python", "Docker"]

    def test_extract_handles_invalid_json(self):
        """Should return empty list for invalid JSON response."""
        extractor = self._make_extractor("not valid json at all")
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == []

    def test_extract_handles_non_list_json(self):
        """Should return empty list when JSON is valid but not a list."""
        extractor = self._make_extractor('{"skill": "Python"}')
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == []

    def test_extract_filters_empty_strings(self):
        """Should filter out empty strings from the result."""
        extractor = self._make_extractor('["Python", "", "  ", "AWS"]')
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == ["Python", "AWS"]

    def test_extract_empty_text_raises(self):
        """Should raise ValueError for empty input."""
        extractor = self._make_extractor("irrelevant")
        with pytest.raises(ValueError, match="empty"):
            extractor.extract("")

    def test_extract_api_failure_propagates(self):
        """Should propagate RuntimeError from failed API calls."""
        mock_client = MagicMock()
        mock_client.generate.side_effect = RuntimeError("API error")
        extractor = LLMSkillsExtractor(mock_client)

        with pytest.raises(RuntimeError, match="API error"):
            extractor.extract(SAMPLE_RESUME_TEXT)

    def test_extract_empty_json_array(self):
        """Should handle empty JSON array response."""
        extractor = self._make_extractor("[]")
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert result == []
