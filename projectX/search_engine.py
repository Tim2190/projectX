import re
from datetime import datetime
from typing import List, Dict, Optional

# Если нужны ключевые слова для тональности
POSITIVE = ["good", "success", "growth", "positive", "improved"]
NEGATIVE = ["bad", "failure", "decline", "negative", "worse"]


class SearchEngine:
    """Lightweight search engine with keyword-based sentiment detection."""

    def __init__(self):
        self.sentiment_pipe = None
        self.positive_keywords = POSITIVE
        self.negative_keywords = NEGATIVE

    @staticmethod
    def _preprocess_text(text: str) -> str:
        clean = re.sub(r"\s+", " ", text)
        return clean.strip()

    def detect_sentiment(self, text: str) -> str:
        text_low = self._preprocess_text(text).lower()
        pos = sum(text_low.count(k) for k in self.positive_keywords)
        neg = sum(text_low.count(k) for k in self.negative_keywords)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"

    def _sentiment(self, text: str) -> str:
        if not self.sentiment_pipe:
            return self.detect_sentiment(text)
        try:
            text = self._preprocess_text(text)
            res = self.sentiment_pipe(text[:512])[0]
            label = res['label'].lower()
            score = res['score']
            text_low = text.lower()
            if any(n in text_low for n in self.negative_keywords) and any(p in text_low for p in self.positive_keywords):
                return 'neutral'
            if label == 'neutral' and score < 0.6:
                if any(k in text_low for k in self.negative_keywords):
                    return 'negative'
                if any(k in text_low for k in self.positive_keywords):
                    return 'positive'
            if label == 'negative' and score < 0.6 and not any(k in text_low for k in self.negative_keywords):
                return 'neutral'
            if label == 'positive' and score < 0.6 and not any(k in text_low for k in self.positive_keywords):
                return 'neutral'
            return label
        except Exception:
            return 'neutral'

    def _apply_sentiment(self, items: List[Dict]):
        for it in items:
            text = f"{it.get('title','')} {it.get('summary','')}"
            it['sentiment'] = self._sentiment(text)

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Метод-заглушка. Источники отключены, возвращает пустой список."""
        return []

    @staticmethod
    def _clean_query(text: str) -> str:
        return re.sub(r"[^\w\s]", "", text).strip()
