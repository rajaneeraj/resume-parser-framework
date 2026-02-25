"""
Integration tests — End-to-end resume parsing pipeline.

These tests use REAL parsers and non-LLM extractors so they run
without an API key. They validate the full pipeline from file
input to structured ResumeData output.
"""

from pathlib import Path

import pytest

from resume_parser import ResumeExtractor, ResumeParserFramework, ResumeData
from resume_parser.extractors import (
    RegexEmailExtractor,
    RuleBasedNameExtractor,
    KeywordSkillsExtractor,
)
from resume_parser.parsers import PDFParser, WordParser


class TestEndToEndDocx:
    """Integration tests for the full DOCX parsing pipeline."""

    def test_full_pipeline_docx(self, tmp_docx: Path):
        """Full pipeline: DOCX → parse → extract → ResumeData."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(
            resume_extractor=resume_extractor, parser=WordParser()
        )

        result = framework.parse_resume(str(tmp_docx))

        assert isinstance(result, ResumeData)
        assert result.name == "Jane Doe"
        assert result.email == "jane.doe@gmail.com"
        assert "Python" in result.skills
        assert "Machine Learning" in result.skills

    def test_full_pipeline_docx_auto_detect(self, tmp_docx: Path):
        """Full pipeline with auto-detected parser for DOCX."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(resume_extractor=resume_extractor)

        result = framework.parse_resume(str(tmp_docx))

        assert isinstance(result, ResumeData)
        assert result.name != ""
        assert result.email != ""

    def test_result_serialization_docx(self, tmp_docx: Path):
        """Extracted data should serialize to valid JSON."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(
            resume_extractor=resume_extractor, parser=WordParser()
        )

        result = framework.parse_resume(str(tmp_docx))
        json_str = result.to_json()
        data_dict = result.to_dict()

        assert isinstance(json_str, str)
        assert isinstance(data_dict, dict)
        assert "name" in data_dict
        assert "email" in data_dict
        assert "skills" in data_dict


class TestEndToEndPdf:
    """Integration tests for the full PDF parsing pipeline."""

    def test_full_pipeline_pdf(self, tmp_pdf: Path):
        """Full pipeline: PDF → parse → extract → ResumeData."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(
            resume_extractor=resume_extractor, parser=PDFParser()
        )

        result = framework.parse_resume(str(tmp_pdf))

        assert isinstance(result, ResumeData)
        assert "john.smith@outlook.com" in result.email
        assert isinstance(result.skills, list)
        assert len(result.skills) > 0

    def test_full_pipeline_pdf_auto_detect(self, tmp_pdf: Path):
        """Full pipeline with auto-detected parser for PDF."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(resume_extractor=resume_extractor)

        result = framework.parse_resume(str(tmp_pdf))

        assert isinstance(result, ResumeData)
        assert result.email != ""


class TestEndToEndEdgeCases:
    """Integration tests for edge cases in the full pipeline."""

    def test_empty_docx_produces_defaults(self, tmp_empty_docx: Path):
        """Empty DOCX should produce ResumeData with default values."""
        extractors = {
            "name": RuleBasedNameExtractor(),
            "email": RegexEmailExtractor(),
            "skills": KeywordSkillsExtractor(),
        }
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(
            resume_extractor=resume_extractor, parser=WordParser()
        )

        result = framework.parse_resume(str(tmp_empty_docx))

        assert isinstance(result, ResumeData)
        # All fields should be defaults since the file is empty
        assert result.name == ""
        assert result.email == ""
        assert result.skills == []

    def test_wrong_parser_raises_error(self, tmp_docx: Path):
        """Using a PDF parser on a DOCX file should raise an error."""
        extractors = {"name": RuleBasedNameExtractor()}
        resume_extractor = ResumeExtractor(extractors)
        framework = ResumeParserFramework(
            resume_extractor=resume_extractor, parser=PDFParser()
        )

        with pytest.raises(ValueError, match="Unsupported file extension"):
            framework.parse_resume(str(tmp_docx))
