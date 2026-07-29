#!/usr/bin/env python3
"""
Verification framework utilities.
"""

import os
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_evidence_dir() -> Path:
    """Get or create the evidence directory."""
    evidence_dir = get_project_root() / "evidence" / "runtime"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir


def ensure_env_file_exists() -> bool:
    """Check if .env file exists, return True if it does."""
    env_file = get_project_root() / ".env"
    return env_file.exists()


def load_env_file() -> dict:
    """Load environment variables from .env file."""
    env_file = get_project_root() / ".env"
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
    
    return env_vars


class VerificationResult:
    """Container for verification results."""
    
    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = True
        self.message = ""
        self.details = {}
    
    def fail(self, message: str, details: dict = None):
        """Mark as failed."""
        self.passed = False
        self.message = message
        if details:
            self.details.update(details)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "check": self.check_name,
            "status": "PASS" if self.passed else "FAIL",
            "message": self.message,
            "details": self.details
        }


def format_markdown_report(title: str, sections: dict) -> str:
    """Generate a markdown report."""
    lines = [
        f"# {title}\n",
        f"**Generated:** {datetime.now().isoformat()}\n",
        "\n",
    ]
    
    for section_name, section_content in sections.items():
        lines.append(f"## {section_name}\n\n")
        if isinstance(section_content, dict):
            for key, value in section_content.items():
                lines.append(f"- **{key}:** {value}\n")
        else:
            lines.append(section_content + "\n")
        lines.append("\n")
    
    return "".join(lines)


from datetime import datetime
