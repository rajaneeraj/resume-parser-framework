.PHONY: install test lint format clean

## Install the project in development mode with all dev dependencies
install:
	python -m venv .venv
	.venv/Scripts/python -m pip install -e ".[dev]"
	@echo "✓ Installed. Activate with: .venv\\Scripts\\activate"

## Run the full test suite with coverage
test:
	.venv/Scripts/python -m pytest tests/ -v --cov=src/resume_parser --cov-report=term-missing

## Lint source and test files with ruff
lint:
	.venv/Scripts/python -m ruff check src/ tests/ parse_resumes.py

## Auto-format source and test files with ruff
format:
	.venv/Scripts/python -m ruff format src/ tests/ parse_resumes.py

## Remove build artifacts and caches
clean:
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q .ruff_cache 2>nul || true
	rmdir /s /q htmlcov 2>nul || true
	rmdir /s /q src\resume_parser_framework.egg-info 2>nul || true
	del /q .coverage 2>nul || true
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@echo "✓ Cleaned."
