"""
Unit tests for the ResumeData dataclass.
"""

import json

from resume_parser.models.resume_data import ResumeData


class TestResumeData:
    """Tests for the ResumeData dataclass."""

    def test_create_with_all_fields(self):
        """Should create ResumeData with all fields populated."""
        data = ResumeData(
            name="Jane Doe",
            email="jane@test.com",
            skills=["Python", "ML"],
        )
        assert data.name == "Jane Doe"
        assert data.email == "jane@test.com"
        assert data.skills == ["Python", "ML"]

    def test_create_with_defaults(self):
        """Should create ResumeData with default empty values."""
        data = ResumeData()
        assert data.name == ""
        assert data.email == ""
        assert data.skills == []

    def test_create_partial_fields(self):
        """Should allow partial field specification."""
        data = ResumeData(name="John")
        assert data.name == "John"
        assert data.email == ""
        assert data.skills == []

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        data = ResumeData(
            name="Jane Doe",
            email="jane@test.com",
            skills=["Python"],
        )
        result = data.to_dict()

        assert result == {
            "name": "Jane Doe",
            "email": "jane@test.com",
            "skills": ["Python"],
        }

    def test_to_dict_returns_copy_of_skills(self):
        """skills list in dict should be a copy (not same reference)."""
        data = ResumeData(skills=["Python"])
        result = data.to_dict()

        # Mutating the dict's skills should not affect the original
        result["skills"].append("Java")
        assert data.skills == ["Python"]

    def test_to_json(self):
        """Should serialize to valid JSON string."""
        data = ResumeData(
            name="Jane Doe",
            email="jane@test.com",
            skills=["Python", "ML"],
        )
        json_str = data.to_json()
        parsed = json.loads(json_str)

        assert parsed["name"] == "Jane Doe"
        assert parsed["email"] == "jane@test.com"
        assert parsed["skills"] == ["Python", "ML"]

    def test_to_json_custom_indent(self):
        """Should respect custom indent parameter."""
        data = ResumeData(name="Test")
        json_str = data.to_json(indent=4)

        # 4-space indent should produce lines starting with 4 spaces
        lines = json_str.split("\n")
        indented_lines = [line for line in lines if line.startswith("    ")]
        assert len(indented_lines) > 0

    def test_to_json_empty_data(self):
        """Should serialize empty ResumeData correctly."""
        data = ResumeData()
        json_str = data.to_json()
        parsed = json.loads(json_str)

        assert parsed == {"name": "", "email": "", "skills": []}

    def test_str_representation(self):
        """Should produce human-readable string representation."""
        data = ResumeData(
            name="Jane Doe",
            email="jane@test.com",
            skills=["Python"],
        )
        result = str(data)

        assert "Jane Doe" in result
        assert "jane@test.com" in result
        assert "Python" in result

    def test_str_empty_skills(self):
        """Should show 'None' for empty skills list in str representation."""
        data = ResumeData(name="Test")
        result = str(data)

        assert "None" in result

    def test_equality(self):
        """Two ResumeData with same values should be equal."""
        data1 = ResumeData(name="Jane", email="j@t.com", skills=["Python"])
        data2 = ResumeData(name="Jane", email="j@t.com", skills=["Python"])

        assert data1 == data2

    def test_inequality(self):
        """Two ResumeData with different values should not be equal."""
        data1 = ResumeData(name="Jane")
        data2 = ResumeData(name="John")

        assert data1 != data2

    def test_skills_default_not_shared(self):
        """Each instance should have its own skills list (no mutable default sharing)."""
        data1 = ResumeData()
        data2 = ResumeData()

        data1.skills.append("Python")
        assert data2.skills == []
