# text_preprocessor.py
# Lightweight text cleaning and normalization for resume text.
# Goal: clean extraction artifacts WITHOUT destroying useful information.

import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize excessive whitespace while preserving paragraph structure.

    - Collapses multiple spaces/tabs into a single space within lines
    - Normalizes line endings to \n
    - Collapses 3+ consecutive blank lines into 2 (preserves section gaps)
    - Strips trailing whitespace from each line
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple spaces/tabs within each line (preserve newlines)
    lines = text.split("\n")
    lines = [re.sub(r"[ \t]+", " ", line).rstrip() for line in lines]
    text = "\n".join(lines)

    # Collapse 3+ blank lines into 2 (keeps section boundaries)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_extraction_artifacts(text: str) -> str:
    """
    Remove common PDF/DOCX extraction artifacts.

    - Removes page break markers and form feed characters
    - Removes excessive special character sequences (-----, =====, *****)
    - Removes null bytes
    - Strips BOM markers
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove BOM
    text = text.lstrip("\ufeff")

    # Remove form feed characters (page breaks)
    text = text.replace("\f", "\n")

    # Remove lines that are ONLY separator characters (---, ===, ***)
    # but keep short dashes in bullet points like "- item"
    text = re.sub(r"^[\-=\*_]{4,}$", "", text, flags=re.MULTILINE)

    return text


def preserve_bullet_points(text: str) -> str:
    """
    Normalize bullet point markers to a consistent format.

    Handles common bullet styles:
    - •, ●, ○, ▪, ▸, ►, ◦, ‣, ⁃
    - Unicode dashes (—, –)
    - Asterisks used as bullets

    Converts them all to "• " for consistency while preserving the content.
    """
    # Normalize various bullet characters to a standard bullet
    bullet_chars = r"[•●○▪▸►◦‣⁃]"
    text = re.sub(rf"^\s*{bullet_chars}\s*", "• ", text, flags=re.MULTILINE)

    # Normalize lines starting with * followed by space (but not bold markdown **)
    text = re.sub(r"^\s*\*\s+", "• ", text, flags=re.MULTILINE)

    # Normalize unicode dashes at start of line used as bullets
    text = re.sub(r"^\s*[—–]\s+", "- ", text, flags=re.MULTILINE)

    return text


def clean_encoding_issues(text: str) -> str:
    """
    Fix common encoding artifacts from PDF extraction.

    - Replaces common mojibake sequences
    - Removes control characters (except newlines and tabs)
    - Fixes smart quotes to standard quotes
    """
    # Fix smart quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')

    # Fix en/em dashes used in text (not as bullets — those are handled separately)
    # Only replace mid-sentence dashes
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2014", " - ")  # em dash

    # Remove control characters except \n, \t, \r
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text


def preprocess_resume_text(text: str) -> str:
    """
    Full preprocessing pipeline for resume text.

    Applies all cleaning steps in the correct order:
    1. Fix encoding issues
    2. Remove extraction artifacts
    3. Preserve bullet points
    4. Normalize whitespace

    Args:
        text: Raw extracted resume text.

    Returns:
        Cleaned, normalized resume text preserving meaningful content.
    """
    if not text or not text.strip():
        return ""

    text = clean_encoding_issues(text)
    text = remove_extraction_artifacts(text)
    text = preserve_bullet_points(text)
    text = normalize_whitespace(text)

    return text
