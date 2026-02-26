"""
Resume Parser Framework
=======================

A pluggable, extensible framework for extracting structured information
from resumes in multiple file formats (PDF, DOCX).

Supports configurable extraction strategies (regex, rule-based, LLM)
for each field via the Strategy pattern.
"""

from resume_parser.coordinator import ResumeExtractor
from resume_parser.framework import ResumeParserFramework
from resume_parser.models.resume_data import ResumeData

__all__ = [
    "ResumeData",
    "ResumeExtractor",
    "ResumeParserFramework",
]

__version__ = "1.1.0"
