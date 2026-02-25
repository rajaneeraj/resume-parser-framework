"""
ResumeData — Dataclass encapsulating structured resume information.

Provides a clean data container with serialization helpers for
converting resume data to dict and JSON formats.
"""

import json
from dataclasses import dataclass, field


@dataclass
class ResumeData:
    """Structured representation of extracted resume information.

    Attributes:
        name: The candidate's full name.
        email: The candidate's email address.
        skills: A list of the candidate's skills.
    """

    name: str = ""
    email: str = ""
    skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert the resume data to a dictionary.

        Returns:
            A dictionary with keys 'name', 'email', and 'skills'.
        """
        return {
            "name": self.name,
            "email": self.email,
            "skills": list(self.skills),  # Return a copy to prevent mutation
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize the resume data to a JSON string.

        Args:
            indent: Number of spaces for JSON indentation. Defaults to 2.

        Returns:
            A formatted JSON string representation of the resume data.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def __str__(self) -> str:
        """Human-readable string representation."""
        skills_str = ", ".join(self.skills) if self.skills else "None"
        return (
            f"ResumeData(\n"
            f"  name={self.name!r},\n"
            f"  email={self.email!r},\n"
            f"  skills=[{skills_str}]\n"
            f")"
        )
