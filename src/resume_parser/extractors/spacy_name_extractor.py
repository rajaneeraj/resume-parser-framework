"""
SpaCy Name Extractor — Uses spaCy NER to extract candidate names.

Provides:
- SpacyNameExtractor: Uses spaCy's PERSON entity recognition.
  Falls back gracefully if spaCy or the English model is not installed.
"""

import logging

from resume_parser.extractors.base import FieldExtractor

logger = logging.getLogger(__name__)


class SpacyNameExtractor(FieldExtractor):
    """Extracts candidate name using spaCy Named Entity Recognition.

    Uses the 'en_core_web_sm' model to identify PERSON entities in the
    resume text. Returns the first PERSON entity found, which is
    typically the candidate's name.

    Raises ImportError at construction time if spaCy or the English
    model is not available, allowing callers to fall back to
    RuleBasedNameExtractor.

    Args:
        model_name: spaCy model to load. Defaults to 'en_core_web_sm'.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            import spacy
        except ImportError as exc:
            raise ImportError(
                "spaCy is required for SpacyNameExtractor. "
                "Install it with: pip install spacy && "
                "python -m spacy download en_core_web_sm"
            ) from exc

        try:
            self._nlp = spacy.load(model_name)
        except OSError as exc:
            raise ImportError(
                f"spaCy model '{model_name}' not found. "
                f"Download it with: python -m spacy download {model_name}"
            ) from exc

        logger.info("SpacyNameExtractor initialized with model: %s", model_name)

    def extract(self, text: str) -> str:
        """Extract the candidate name using spaCy NER.

        Args:
            text: Raw text content from a resume.

        Returns:
            The first PERSON entity found, or an empty string if none found.

        Raises:
            ValueError: If the input text is empty.
        """
        self._validate_input(text)

        # Process only the first ~500 chars — name is almost always at the top
        doc = self._nlp(text[:500])

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                logger.info("Name extracted (spaCy NER): %s", name)
                return name

        logger.warning("No PERSON entity found by spaCy NER.")
        return ""
