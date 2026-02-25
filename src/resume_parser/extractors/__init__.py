"""
Extractors sub-package — field-specific extraction strategies.
"""

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

# SpacyNameExtractor is optional — only available if spaCy is installed.
# Import it explicitly from resume_parser.extractors.spacy_name_extractor.
try:
    from resume_parser.extractors.spacy_name_extractor import SpacyNameExtractor
    _SPACY_AVAILABLE = True
except ImportError:
    _SPACY_AVAILABLE = False

__all__ = [
    "FieldExtractor",
    "RegexEmailExtractor",
    "RuleBasedNameExtractor",
    "LLMNameExtractor",
    "KeywordSkillsExtractor",
    "LLMSkillsExtractor",
]

if _SPACY_AVAILABLE:
    __all__.append("SpacyNameExtractor")

