"""Utility functions for matching and similarity."""

from typing import Tuple
from fuzzywuzzy import fuzz


def match_ratio(text1: str, text2: str) -> int:
    """Return similarity ratio between two pieces of text."""
    return fuzz.token_set_ratio(text1, text2)


def classify_match(ratio: int) -> str:
    if ratio > 90:
        return "репост"
    if ratio > 70:
        return "перефраз"
    return "упоминание"
