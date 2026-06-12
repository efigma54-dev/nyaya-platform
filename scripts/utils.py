# scripts/utils.py

import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize legal text — remove control chars, fix whitespace."""
    if not text:
        return ""
    # Normalize unicode (handles Hindi + English mixed text)
    text = unicodedata.normalize("NFKC", text)
    # Remove null bytes and control chars except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_section_number(heading: str) -> str | None:
    """Extract '302', '498A', '4' from headings like 'Section 302' or '4.'"""
    if not heading:
        return None
    match = re.search(
        r"(?:section|sec\.?|s\.)\s*(\d+[A-Za-z]*(?:\.\d+[A-Za-z]*)*)",
        heading,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    match = re.match(r"^(\d+[A-Za-z]*(?:\.\d+[A-Za-z]*)*)[.\s]", heading.strip())
    if match:
        return match.group(1).strip()
    return None


def is_bailable_from_text(text: str) -> bool | None:
    """Detect bailable/non-bailable from section text."""
    text_lower = text.lower()
    if "non-bailable" in text_lower:
        return False
    if "bailable" in text_lower:
        return True
    return None


def is_cognizable_from_text(text: str) -> bool | None:
    """Detect cognizable/non-cognizable from section text."""
    text_lower = text.lower()
    if "non-cognizable" in text_lower:
        return False
    if "cognizable" in text_lower:
        return True
    return None


def extract_punishment(text: str) -> dict:
    """Extract punishment details from section text."""
    result = {
        "punishment_summary": None,
        "max_punishment": None,
        "min_punishment": None,
        "fine_amount": None,
    }
    text_lower = text.lower()

    # Death penalty
    if "death" in text_lower or "capital punishment" in text_lower:
        result["max_punishment"] = "Death"
        result["punishment_summary"] = "Death penalty or imprisonment for life"

    # Life imprisonment
    elif "imprisonment for life" in text_lower or "life imprisonment" in text_lower:
        result["max_punishment"] = "Imprisonment for Life"
        result["punishment_summary"] = "Imprisonment for life"

    # Specific year terms
    years = re.findall(
        r"(?:imprisonment[^.]*?(?:which may extend to|not less than|for a term of))\s*(\d+)\s*year",
        text_lower,
    )
    if years:
        result["max_punishment"] = f"{max(int(y) for y in years)} years imprisonment"

    # Fine
    fine = re.findall(
        r"fine[^.]*?(?:which may extend to|not exceeding|of)\s*(?:rupees\s*)?([0-9,]+)",
        text_lower,
    )
    if fine:
        result["fine_amount"] = f"₹{fine[0].replace(',', '')}"

    return result
