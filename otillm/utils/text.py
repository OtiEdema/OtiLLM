"""Small text utility helpers."""

import re
from typing import Iterable, List


def normalize_text(text: str) -> str:
    """Normalize text by lowercasing and collapsing whitespace."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize_simple(text: str) -> List[str]:
    """Tokenize text using a simple regex word tokenizer."""
    return re.findall(r"[a-zA-Z0-9_\-]+", normalize_text(text))


def safe_contains(text: str, terms: Iterable[str]) -> bool:
    """Return True if any risky term appears in the normalized text."""
    norm = normalize_text(text)
    return any(term.lower() in norm for term in terms)
