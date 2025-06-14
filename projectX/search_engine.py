import re
from datetime import datetime
from typing import List, Dict, Optional
from projectX.scraper_search import ScraperSearch  # ← подключаем парсер

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

    def _clean_query(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text).strip()

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Восстановленный поиск по RSS + тональность."""
        cleaned = self._clean_query(query.strip())
        scraper = ScraperSearch()
        raw_results = scraper.search(cleaned, from_date, to_date)
        words = query.lower().split()

        filtered = []
        for item in raw_results:
            text = f"{item.get('title','')} {item.get('summary','')}".lower()
            if all(w in text for w in words):
                if not item.get('source'):
                    item['source'] = 'Scraper'
                filtered.append(item)

        self._apply_sentiment(filtered)

        # убрать дубликаты по URL
        results_by_url = {}
        for item in filtered:
            url = item.get('url')
            if url and url not in results_by_url:
                results_by_url[url] = item

        return list(results_by_url.values())
