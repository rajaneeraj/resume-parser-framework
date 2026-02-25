# Resume Parser Framework

A pluggable, extensible framework for extracting structured information from resumes in multiple file formats (PDF, DOCX). Built with a focus on **Object-Oriented Design** and the **Strategy Pattern**.

## Features

- **Multi-format support**: Parse PDF (`.pdf`) and Word Document (`.docx`) files
- **Pluggable extraction strategies**: Swap between regex, rule-based, and LLM-based extractors
- **LLM integration**: Optional Gemini API integration for intelligent extraction
- **Extensible design**: Easy to add new file formats or extraction strategies
- **Structured output**: Clean `ResumeData` object with JSON serialization

## Project Structure

```
├── src/resume_parser/          # Main package
│   ├── parsers/                # File format parsers (PDF, DOCX)
│   ├── extractors/             # Field extraction strategies
│   ├── models/                 # Data classes (ResumeData)
│   ├── llm/                    # LLM client (Gemini API)
│   ├── coordinator.py          # ResumeExtractor orchestrator
│   └── framework.py            # ResumeParserFramework entry point
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests for each component
│   └── integration/            # End-to-end pipeline tests
├── examples/                   # Usage examples
├── scripts/                    # Utility scripts (sample generation)
└── samples/                    # Sample resume files
```

## Quick Start

### 1. Set Up Environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### 2. Generate Sample Resumes

```bash
python scripts/create_sample_resumes.py
```

### 3. Run the Examples

```bash
python examples/usage_example.py
```

### 4. (Optional) Set Up Gemini API for LLM Extractors

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get a free key at: https://aistudio.google.com/apikey
```

## Usage

### Example 1: Parse a Word Resume

```python
from resume_parser import ResumeExtractor, ResumeParserFramework
from resume_parser.extractors import (
    RegexEmailExtractor,
    RuleBasedNameExtractor,
    KeywordSkillsExtractor,
)
from resume_parser.parsers import WordParser

# Configure field extractors
extractors = {
    "name": RuleBasedNameExtractor(),
    "email": RegexEmailExtractor(),
    "skills": KeywordSkillsExtractor(),
}

# Set up the framework
resume_extractor = ResumeExtractor(extractors)
framework = ResumeParserFramework(
    resume_extractor=resume_extractor,
    parser=WordParser(),
)

# Parse a resume
result = framework.parse_resume("samples/jane_doe_resume.docx")
print(result.to_json())
```

### Example 2: Parse a PDF Resume (Auto-Detect Format)

```python
from resume_parser import ResumeExtractor, ResumeParserFramework
from resume_parser.extractors import (
    RegexEmailExtractor,
    RuleBasedNameExtractor,
    KeywordSkillsExtractor,
)

# Configure extractors
extractors = {
    "name": RuleBasedNameExtractor(),
    "email": RegexEmailExtractor(),
    "skills": KeywordSkillsExtractor(),
}

# Create framework WITHOUT explicit parser (auto-detects from extension)
resume_extractor = ResumeExtractor(extractors)
framework = ResumeParserFramework(resume_extractor=resume_extractor)

# Parse — framework auto-selects PDFParser based on .pdf extension
result = framework.parse_resume("samples/john_smith_resume.pdf")
print(result.to_json())
```

### Example 3: Using LLM-Based Extractors

```python
from resume_parser import ResumeExtractor, ResumeParserFramework
from resume_parser.extractors import RegexEmailExtractor, LLMNameExtractor, LLMSkillsExtractor
from resume_parser.llm import GeminiClient

# Initialize Gemini client (reads GEMINI_API_KEY from environment)
client = GeminiClient()

# Mix strategies: LLM for name and skills, regex for email
extractors = {
    "name": LLMNameExtractor(client),
    "email": RegexEmailExtractor(),
    "skills": LLMSkillsExtractor(client),
}

resume_extractor = ResumeExtractor(extractors)
framework = ResumeParserFramework(resume_extractor=resume_extractor)
result = framework.parse_resume("samples/jane_doe_resume.docx")
print(result.to_json())
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
│                       │  │ ● RuleBasedName...  │  │ │
│                       │  │ ● LLMNameExtractor  │  │ │
│                       │  │ ● KeywordSkills...  │  │ │
│                       │  │ ● LLMSkillsExtractor│  │ │
│                       │  └──────────────────────┘  │ │
│                       └────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Key Design Patterns

| Pattern | Where Used | Purpose |
|---------|-----------|---------|
| **Strategy** | `FieldExtractor` hierarchy | Swap extraction algorithms at runtime |
| **Template Method** | `FileParser.parse()` | Shared validation + format-specific extraction |
| **Dependency Injection** | `ResumeExtractor`, `ResumeParserFramework` | Loose coupling between components |
| **Registry** | `_PARSER_REGISTRY` in `framework.py` | Auto-detect file format from extension |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run with coverage report
pytest tests/ -v --cov=src/resume_parser --cov-report=term-missing
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `PyPDF2` | PDF text extraction |
| `python-docx` | Word document text extraction |
| `google-generativeai` | Gemini LLM integration |
| `python-dotenv` | Environment variable management |
| `reportlab` | PDF generation (for samples) |
| `pytest` | Test framework |
| `pytest-cov` | Test coverage reporting |

## Extending the Framework

### Adding a New File Format

1. Create a new parser class extending `FileParser`
2. Set `supported_extensions` and implement `_extract_text()`
3. Register in `_PARSER_REGISTRY` in `framework.py`

### Adding a New Extraction Strategy

1. Create a new class extending `FieldExtractor`
2. Implement the `extract(text: str)` method
3. Pass it in the extractors dictionary when configuring `ResumeExtractor`
