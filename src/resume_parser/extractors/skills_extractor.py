"""
Skills Extractors — Strategies for extracting skills from resume text.

Provides:
- KeywordSkillsExtractor: Matches text against a configurable keyword list.
- LLMSkillsExtractor: Uses Gemini API for intelligent skill identification.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

from resume_parser.extractors.base import FieldExtractor

if TYPE_CHECKING:
    from resume_parser.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

# Default list of common technical and professional skills for keyword matching.
# Users can provide their own list via the constructor.
DEFAULT_SKILLS_KEYWORDS: list[str] = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",
    # Web Technologies
    "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django",
    "Flask", "FastAPI", "Spring Boot", "Express.js", "Next.js",
    # Data & ML
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
    "Computer Vision", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
    "NumPy", "Data Analysis", "Data Science", "LLM", "Large Language Models",
    "Generative AI", "Neural Networks",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "CI/CD", "Terraform", "Jenkins", "Git", "GitHub", "GitLab",
    # Databases
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Elasticsearch", "DynamoDB", "Cassandra",
    # Other
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum",
    "Project Management", "Leadership", "Communication",
]


class KeywordSkillsExtractor(FieldExtractor):
    """Extracts skills by matching text against a keyword list.

    Performs case-insensitive matching of known skill keywords against
    the resume text. This approach is fast, deterministic, and does
    not require an API key.

    Args:
        keywords: Optional list of skill keywords to match against.
                  Defaults to DEFAULT_SKILLS_KEYWORDS.
    """

    def __init__(self, keywords: list[str] | None = None):
        self._keywords = keywords or DEFAULT_SKILLS_KEYWORDS

    def extract(self, text: str) -> list[str]:
        """Extract skills by keyword matching.

        Args:
            text: Raw text content from a resume.

        Returns:
            A list of matched skills (preserving the canonical keyword casing).

        Raises:
            ValueError: If the input text is empty.
        """
        self._validate_input(text)

        found_skills: list[str] = []
        text_lower = text.lower()

        for keyword in self._keywords:
            # Use word-boundary matching to avoid partial matches
            # (e.g., "R" shouldn't match "React")
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(keyword)

        logger.info("Skills extracted (keyword): %d found", len(found_skills))
        logger.debug("Matched skills: %s", found_skills)
        return found_skills


class LLMSkillsExtractor(FieldExtractor):
    """Extracts skills using the Gemini LLM.

    Sends resume text to the Gemini API with a targeted prompt to
    identify technical and professional skills. This approach can
    identify skills even when they're described implicitly.

    Args:
        client: An initialized GeminiClient instance.
    """

    def __init__(self, client: GeminiClient):
        self._client = client

    def extract(self, text: str) -> list[str]:
        """Extract skills using the Gemini LLM.

        Args:
            text: Raw text content from a resume.

        Returns:
            A list of identified skills.

        Raises:
            ValueError: If the input text is empty.
            RuntimeError: If the LLM API call fails.
        """
        self._validate_input(text)

        prompt = (
            "Extract a list of technical and professional skills from the "
            "following resume text. Return ONLY a valid JSON array of strings, "
            "with no extra text, explanation, or markdown formatting.\n\n"
            "Example output: [\"Python\", \"Machine Learning\", \"AWS\"]\n\n"
            f"Resume text:\n{text}"
        )

        raw_response = self._client.generate(prompt).strip()

        # Clean potential markdown code fences from LLM response
        raw_response = re.sub(r"^```(?:json)?\s*", "", raw_response)
        raw_response = re.sub(r"\s*```$", "", raw_response)

        try:
            skills = json.loads(raw_response)
            if isinstance(skills, list):
                # Ensure all items are strings and non-empty
                skills = [
                    str(s).strip()
                    for s in skills
                    if str(s).strip()
                ]
                logger.info("Skills extracted (LLM): %d found", len(skills))
                return skills
            else:
                logger.warning(
                    "LLM returned non-list type: %s. Returning empty list.",
                    type(skills).__name__,
                )
                return []
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse LLM response as JSON: %s", raw_response[:200]
            )
            return []
