"""Analyze sentiment and geography of results."""

from typing import Optional
from textblob import TextBlob
import tldextract


def analyze_sentiment(text: str) -> str:
    """Return sentiment label: positive, neutral, negative."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    if polarity < -0.1:
        return "negative"
    return "neutral"


def extract_country(url: str) -> Optional[str]:
    ext = tldextract.extract(url)
    return ext.suffix.split('.')[-1] if ext.suffix else None
