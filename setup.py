"""Setup script for the resume_parser package."""

from setuptools import setup, find_packages

setup(
    name="resume-parser-framework",
    version="1.0.0",
    description="A pluggable resume parsing framework with configurable extraction strategies.",
    author="Neeraj Raja",
    url="https://github.com/rajaneeraj/rajaneeraj",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "PyPDF2>=3.0.0",
        "python-docx>=1.1.0",
        "google-generativeai>=0.8.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "reportlab>=4.0.0",
        ],
    },
)
