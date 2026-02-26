# Resume Parser Framework

A pluggable, extensible framework for extracting structured information from resumes in multiple file formats (PDF, DOCX). Built with a focus on **Object-Oriented Design** and the **Strategy Pattern**.

## Features

- **Multi-format support**: Parse PDF (`.pdf`) and Word Document (`.docx`) files
- **Pluggable extraction strategies**: Swap between regex, rule-based, NER, and LLM-based extractors
- **spaCy NER integration**: Named Entity Recognition for intelligent name extraction (with heuristic fallback)
- **LLM integration**: Optional Gemini API integration for intelligent skills extraction (with keyword fallback)
- **CLI entry point**: Production-ready batch processor with JSON output and archiving
- **Structured output**: Clean `ResumeData` object with JSON serialization

## Project Structure

```
├── parse_resumes.py            # CLI entry point (run this!)
├── resumes/                    # Drop resume files here (.pdf, .docx)
├── output/                     # Generated: per-resume JSON + manifest.json
├── archive/                    # Generated: processed files with timestamps
├── src/resume_parser/          # Main package
│   ├── parsers/                # File format parsers (PDF, DOCX)
│   ├── extractors/             # Field extraction strategies
│   ├── models/                 # Data classes (ResumeData)
│   ├── llm/                    # LLM client (Gemini API)
│   ├── coordinator.py          # ResumeExtractor orchestrator
│   └── framework.py            # ResumeParserFramework engine
├── tests/                      # Test suite (unit + integration)
│   ├── unit/                   # Unit tests for each component
│   └── integration/            # End-to-end pipeline tests
├── scripts/                    # Utility scripts (sample generation)
├── pyproject.toml              # Project config, dependencies, tool settings
├── Makefile                    # Dev commands (make test, make lint, etc.)
└── LICENSE                     # MIT License
```

## Quick Start

### 1. Set Up Environment

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # macOS/Linux

# Install in development mode (all dependencies are in pyproject.toml)
pip install -e ".[dev]"
```

### 2. Install spaCy Model (Optional — for NER-based name extraction)

```bash
python -m spacy download en_core_web_sm
```

> If spaCy is not installed, the framework automatically falls back to heuristic-based name extraction.

### 3. Run the Parser

```bash
# Parse all resumes in the resumes/ folder
python parse_resumes.py

# Parse with custom directories
python parse_resumes.py --input-dir my_resumes/ --output-dir my_output/

# Skip LLM (use keyword matching for skills)
python parse_resumes.py --no-llm

# Skip archiving (leave files in place)
python parse_resumes.py --no-archive
```

### 4. (Optional) Set Up Gemini API for LLM Extractors

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get a free key at: https://aistudio.google.com/apikey
```

## CLI Usage

```
usage: parse_resumes [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]
                     [--archive-dir ARCHIVE_DIR] [--no-archive] [--no-llm]

Scan a folder for resumes and extract structured data.

options:
  --input-dir     Directory to scan for resume files (default: resumes/)
  --output-dir    Directory for output JSON files (default: output/)
  --archive-dir   Directory for archived resumes (default: archive/)
  --no-archive    Skip archiving processed files
  --no-llm        Force keyword-only skills extraction
```

### Workflow

1. Drop `.pdf` / `.docx` files into the `resumes/` folder
2. Run `python parse_resumes.py`
3. Check `output/parsed/` for individual JSON files (one per resume)
4. Check `output/manifest.json` for a summary of the run
5. Check `output/errors.json` for any failures
6. Processed files are automatically moved to `archive/<timestamp>/`

### Output Format

Each successfully parsed resume is written as an individual JSON file in `output/parsed/`:

**`output/parsed/jane_doe_resume.json`**:
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@gmail.com",
  "skills": ["Python", "Machine Learning", "AWS", "Docker"],
  "source_file": "jane_doe_resume.docx",
  "parsed_at": "2026-02-25T20:52:00+00:00"
}
```

**`output/manifest.json`** — run summary and index of all parsed files:
```json
{
  "run_timestamp": "2026-02-25_205200",
  "total_files": 2,
  "succeeded": 2,
  "failed": 0,
  "parsed_files": [
    {
      "source_file": "jane_doe_resume.docx",
      "output_file": "parsed/jane_doe_resume.json",
      "parsed_at": "2026-02-25T20:52:00+00:00"
    }
  ]
}
```

**`output/errors.json`** (only written if failures occur):
```json
[
  {
    "file": "resumes/corrupt_file.pdf",
    "error": "Failed to extract text from PDF 'corrupt_file.pdf': ..."
  }
]
```

## Design

### Architecture

```
┌─────────────────────────────────────────────────────┐
│              ResumeParserFramework                   │
│                                                     │
│  ┌──────────────┐    ┌────────────────────────────┐ │
│  │  FileParser   │    │    ResumeExtractor          │ │
│  │  (Strategy)   │    │    (Coordinator)            │ │
│  │               │    │                            │ │
│  │  ● PDFParser  │    │  ┌──────────────────────┐  │ │
│  │  ● WordParser │    │  │ FieldExtractor(s)    │  │ │
│  │               │    │  │ (Strategy Pattern)   │  │ │
│  └──────────────┘    │  │                      │  │ │
│                       │  │ ● RegexEmailExtractor│  │ │
│                       │  │ ● SpacyNameExtractor │  │ │
│                       │  │ ● RuleBasedName...  │  │ │
│                       │  │ ● LLMNameExtractor  │  │ │
│                       │  │ ● KeywordSkills...  │  │ │
│                       │  │ ● LLMSkillsExtractor│  │ │
│                       │  └──────────────────────┘  │ │
│                       └────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Extraction Strategies & Fallback Logic

| Field | Primary Strategy | Fallback |
|-------|-----------------|----------|
| **Email** | `RegexEmailExtractor` | — (always used) |
| **Name** | `SpacyNameExtractor` (NER) | `RuleBasedNameExtractor` (if spaCy not installed) |
| **Skills** | `LLMSkillsExtractor` (Gemini) | `KeywordSkillsExtractor` (if no API key / `--no-llm`) |

### Key Design Patterns

| Pattern | Where Used | Purpose |
|---------|-----------|---------||
| **Strategy** | `FieldExtractor` hierarchy | Swap extraction algorithms at runtime |
| **Template Method** | `FileParser.parse()` | Shared validation + format-specific extraction |
| **Dependency Injection** | `ResumeExtractor`, `ResumeParserFramework` | Loose coupling between components |
| **Registry** | `_PARSER_REGISTRY` in `framework.py` | Auto-detect file format from extension |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src/resume_parser --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

## Dependencies

| Package | Purpose |
|---------|---------||
| `pypdf` | PDF text extraction |
| `python-docx` | Word document text extraction |
| `spacy` | Named Entity Recognition for name extraction (optional) |
| `google-generativeai` | Gemini LLM integration (optional) |
| `python-dotenv` | Environment variable management |
| `reportlab` | PDF generation (for sample resumes) |
| `pytest` / `pytest-cov` | Testing and coverage |

## Extending the Framework

### Adding a New File Format

1. Create a new parser class extending `FileParser`
2. Set `supported_extensions` and implement `_extract_text()`
3. Register in `_PARSER_REGISTRY` in `framework.py`

### Adding a New Extraction Strategy

1. Create a new class extending `FieldExtractor`
2. Implement the `extract(text: str)` method
3. Pass it in the extractors dictionary when configuring `ResumeExtractor`
