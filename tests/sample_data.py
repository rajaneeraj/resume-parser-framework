"""
Shared test data constants used across test modules.

Centralizes sample resume text so it can be imported by both
unit and integration tests without conftest import issues.
"""

SAMPLE_RESUME_TEXT = """\
Jane Doe
jane.doe@gmail.com | (555) 123-4567 | San Francisco, CA

Professional Summary
Experienced Machine Learning Engineer with 5+ years of expertise in
designing and deploying production ML systems. Passionate about
Natural Language Processing and Large Language Models.

Experience
Senior ML Engineer — TechCorp Inc.
January 2021 - Present
- Led development of an NLP pipeline using Python, TensorFlow, and AWS.
- Built and deployed LLM-based summarization service using Docker and Kubernetes.

Education
M.S. Computer Science — Stanford University, 2018

Skills
Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, NLP, LLM,
AWS, GCP, Docker, Kubernetes, SQL, Git, REST API, Scikit-learn, Pandas
"""

SAMPLE_RESUME_TEXT_MINIMAL = """\
John Smith
john.smith@outlook.com

Skills: Python, Java
"""

SAMPLE_RESUME_TEXT_NO_EMAIL = """\
Alice Johnson

Professional Summary
Software engineer with experience in web development.

Skills
JavaScript, React, Node.js
"""

SAMPLE_RESUME_TEXT_EMPTY = ""
