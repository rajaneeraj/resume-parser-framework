#!/usr/bin/env python3
"""
parse_resumes.py — Production CLI entry point for the Resume Parser Framework.

Scans an input folder for .pdf and .docx resume files, extracts structured
data (name, email, skills) using configurable strategies, and writes:
  - output/results.json   — array of successfully parsed resumes
  - output/errors.json    — array of {file, error} for any failures

Successfully parsed files are moved to archive/<timestamp>/.

Usage:
    python parse_resumes.py
    python parse_resumes.py --input-dir resumes/ --output-dir output/
    python parse_resumes.py --no-llm --no-archive
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from resume_parser import ResumeExtractor, ResumeParserFramework, ResumeData
from resume_parser.extractors import (
    RegexEmailExtractor,
    RuleBasedNameExtractor,
    KeywordSkillsExtractor,
)

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def configure_logging() -> None:
    """Set up structured logging to console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Optional argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed namespace with all CLI options.
    """
    parser = argparse.ArgumentParser(
        prog="parse_resumes",
        description="Scan a folder for resumes and extract structured data.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("resumes"),
        help="Directory to scan for resume files (default: resumes/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for output JSON files (default: output/)",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("archive"),
        help="Directory for archived resumes (default: archive/)",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip archiving processed files",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Force keyword-only skills extraction (skip LLM even if API key exists)",
    )
    return parser.parse_args(argv)


def discover_resumes(input_dir: Path) -> list[Path]:
    """Recursively find all .pdf and .docx files in the input directory.

    Args:
        input_dir: Root directory to scan.

    Returns:
        Sorted list of resume file paths.
    """
    if not input_dir.is_dir():
        logger.error("Input directory does not exist: %s", input_dir)
        return []

    resumes = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    logger.info("Found %d resume(s) in %s", len(resumes), input_dir)
    return resumes


def build_name_extractor():
    """Build the best available name extractor.

    Tries spaCy NER first; falls back to rule-based if unavailable.

    Returns:
        A FieldExtractor instance for name extraction.
    """
    try:
        from resume_parser.extractors.spacy_name_extractor import SpacyNameExtractor
        extractor = SpacyNameExtractor()
        logger.info("Using SpacyNameExtractor (NER) for name extraction")
        return extractor
    except ImportError:
        logger.info(
            "spaCy not available — falling back to RuleBasedNameExtractor"
        )
        return RuleBasedNameExtractor()


def build_skills_extractor(no_llm: bool):
    """Build the best available skills extractor.

    Uses LLM (Gemini) if API key is set and --no-llm is not passed;
    otherwise falls back to keyword matching.

    Args:
        no_llm: If True, skip LLM even if API key is available.

    Returns:
        A FieldExtractor instance for skills extraction.
    """
    if not no_llm:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_api_key_here":
            try:
                from resume_parser.llm import GeminiClient
                from resume_parser.extractors import LLMSkillsExtractor
                client = GeminiClient(api_key=api_key)
                logger.info("Using LLMSkillsExtractor (Gemini) for skills extraction")
                return LLMSkillsExtractor(client)
            except Exception as exc:
                logger.warning("Failed to init LLM client: %s — using keyword fallback", exc)

    logger.info("Using KeywordSkillsExtractor for skills extraction")
    return KeywordSkillsExtractor()


def archive_file(
    file_path: Path,
    archive_dir: Path,
    timestamp: str,
    input_dir: Path,
) -> Path:
    """Move a successfully parsed file to the archive directory.

    Preserves the original subdirectory structure relative to input_dir.

    Args:
        file_path: Path to the processed resume file.
        archive_dir: Root archive directory.
        timestamp: Timestamp string for the run subfolder.
        input_dir: Original input directory (for relative path calculation).

    Returns:
        The new path of the archived file.
    """
    relative = file_path.relative_to(input_dir)
    dest = archive_dir / timestamp / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(dest))
    logger.info("Archived: %s -> %s", file_path.name, dest)
    return dest


def run(args: argparse.Namespace) -> int:
    """Main execution logic for the CLI.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0 = success, 1 = partial failures, 2 = no files found).
    """
    # Step 1: Discover resume files
    resumes = discover_resumes(args.input_dir)
    if not resumes:
        logger.warning("No resume files found in %s", args.input_dir)
        return 2

    # Step 2: Build extractors with fallback logic
    extractors = {
        "name": build_name_extractor(),
        "email": RegexEmailExtractor(),
        "skills": build_skills_extractor(args.no_llm),
    }

    resume_extractor = ResumeExtractor(extractors)
    framework = ResumeParserFramework(resume_extractor=resume_extractor)

    # Step 3: Process each file
    results: list[dict] = []
    errors: list[dict] = []
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    for file_path in resumes:
        logger.info("Processing: %s", file_path)
        try:
            data: ResumeData = framework.parse_resume(str(file_path))
            entry = data.to_dict()
            entry["source_file"] = file_path.name
            results.append(entry)
            logger.info("OK: %s", file_path.name)

            # Archive on success
            if not args.no_archive:
                archive_file(file_path, args.archive_dir, timestamp, args.input_dir)

        except Exception as exc:
            error_entry = {
                "file": str(file_path),
                "error": str(exc),
            }
            errors.append(error_entry)
            logger.error("FAILED: %s — %s", file_path.name, exc)

    # Step 4: Write output JSON files
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results_path = args.output_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info("Results written to %s (%d resumes)", results_path, len(results))

    if errors:
        errors_path = args.output_dir / "errors.json"
        errors_path.write_text(json.dumps(errors, indent=2), encoding="utf-8")
        logger.warning("Errors written to %s (%d failures)", errors_path, len(errors))

    # Summary
    total = len(resumes)
    ok = len(results)
    fail = len(errors)
    logger.info("=" * 50)
    logger.info("BATCH COMPLETE: %d/%d succeeded, %d failed", ok, total, fail)
    logger.info("=" * 50)

    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: Optional argument list for testing.

    Returns:
        Exit code.
    """
    configure_logging()
    args = parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
