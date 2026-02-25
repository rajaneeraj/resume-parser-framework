"""
Usage Examples — Demonstrates how to use the Resume Parser Framework.

Shows two use cases as required by the assignment:
1. Parse a Word resume using field-specific extractors.
2. Parse a PDF resume using field-specific extractors.

Usage:
    # First, generate sample resumes:
    python scripts/create_sample_resumes.py

    # Then run this example:
    python examples/usage_example.py
"""

import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser import ResumeExtractor, ResumeParserFramework
from resume_parser.extractors import (
    RegexEmailExtractor,
    RuleBasedNameExtractor,
    KeywordSkillsExtractor,
)
from resume_parser.parsers import PDFParser, WordParser

# Configure logging to see framework activity
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

SAMPLES_DIR = PROJECT_ROOT / "samples"


def example_1_parse_word_resume() -> None:
    """Example 1: Parse a Word resume using field-specific extractors.

    Uses:
    - RuleBasedNameExtractor (heuristic: first line of resume)
    - RegexEmailExtractor (regex pattern matching)
    - KeywordSkillsExtractor (keyword list matching)
    """
    print("=" * 60)
    print("EXAMPLE 1: Parse Word Resume (.docx)")
    print("=" * 60)

    # Step 1: Configure field extractors
    extractors = {
        "name": RuleBasedNameExtractor(),
        "email": RegexEmailExtractor(),
        "skills": KeywordSkillsExtractor(),
    }

    # Step 2: Create the resume extractor coordinator
    resume_extractor = ResumeExtractor(extractors)

    # Step 3: Create the framework with a specific Word parser
    framework = ResumeParserFramework(
        resume_extractor=resume_extractor,
        parser=WordParser(),
    )

    # Step 4: Parse the resume
    docx_path = SAMPLES_DIR / "jane_doe_resume.docx"
    if not docx_path.exists():
        print(f"  ⚠ Sample file not found: {docx_path}")
        print("  Run 'python scripts/create_sample_resumes.py' first.")
        return

    result = framework.parse_resume(str(docx_path))

    # Step 5: Display results
    print("\n📄 Extracted Resume Data:")
    print(result.to_json())
    print()


def example_2_parse_pdf_resume() -> None:
    """Example 2: Parse a PDF resume using field-specific extractors.

    Uses auto-detection (no explicit parser) — the framework selects
    PDFParser based on the .pdf extension.
    """
    print("=" * 60)
    print("EXAMPLE 2: Parse PDF Resume (.pdf)")
    print("=" * 60)

    # Step 1: Configure field extractors
    extractors = {
        "name": RuleBasedNameExtractor(),
        "email": RegexEmailExtractor(),
        "skills": KeywordSkillsExtractor(),
    }

    # Step 2: Create the resume extractor coordinator
    resume_extractor = ResumeExtractor(extractors)

    # Step 3: Create the framework WITHOUT an explicit parser (auto-detect)
    framework = ResumeParserFramework(resume_extractor=resume_extractor)

    # Step 4: Parse the resume (auto-detects PDF format)
    pdf_path = SAMPLES_DIR / "john_smith_resume.pdf"
    if not pdf_path.exists():
        print(f"  ⚠ Sample file not found: {pdf_path}")
        print("  Run 'python scripts/create_sample_resumes.py' first.")
        return

    result = framework.parse_resume(str(pdf_path))

    # Step 5: Display results
    print("\n📄 Extracted Resume Data:")
    print(result.to_json())
    print()


def example_3_llm_extractors() -> None:
    """Example 3 (Optional): Parse using LLM-based extractors.

    Requires GEMINI_API_KEY to be set in your environment or .env file.
    Uncomment the code below to try LLM-based extraction.
    """
    print("=" * 60)
    print("EXAMPLE 3: LLM-Based Extraction (requires Gemini API key)")
    print("=" * 60)

    # To use LLM extractors, uncomment the following:
    #
    # from resume_parser.llm import GeminiClient
    # from resume_parser.extractors import LLMNameExtractor, LLMSkillsExtractor
    #
    # client = GeminiClient()  # Reads GEMINI_API_KEY from environment
    #
    # extractors = {
    #     "name": LLMNameExtractor(client),
    #     "email": RegexEmailExtractor(),       # Regex is ideal for emails
    #     "skills": LLMSkillsExtractor(client),
    # }
    #
    # resume_extractor = ResumeExtractor(extractors)
    # framework = ResumeParserFramework(resume_extractor=resume_extractor)
    # result = framework.parse_resume(str(SAMPLES_DIR / "jane_doe_resume.docx"))
    # print(result.to_json())

    print("  ℹ This example is commented out by default.")
    print("  Set GEMINI_API_KEY and uncomment code to try it.\n")


if __name__ == "__main__":
    example_1_parse_word_resume()
    example_2_parse_pdf_resume()
    example_3_llm_extractors()
