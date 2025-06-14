import re
from datetime import datetime
from typing import List, Dict, Optional

        """Initialize search engine with lightweight sentiment detection."""
        self.sentiment_pipe = None
    @staticmethod
        text_low = self._preprocess_text(text).lower()
        pos = sum(text_low.count(k) for k in self.positive_keywords)
        neg = sum(text_low.count(k) for k in self.negative_keywords)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"
        return clean.strip()

    def _sentiment(self, text: str) -> str:
        if not self.sentiment_pipe:
            return 'neutral'
        try:
            text = self._preprocess_text(text)
            res = self.sentiment_pipe(text[:512])[0]
            label = res['label'].lower()
            score = res['score']
            text_low = text.lower()
            # mixed context handling
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

    def search_scraper(self, query: str, from_date: Optional[str], to_date: Optional[str]) -> List[Dict]:
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
        return filtered


    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        scraper_results = self.search_scraper(query, from_date, to_date)

        self._apply_sentiment(scraper_results)

        results_by_url = {}
        for item in scraper_results:
            url = item.get('url')
            if url and url not in results_by_url:
                results_by_url[url] = item

        merged = list(results_by_url.values())

        def parse_date(item):
            try:
                return datetime.fromisoformat(item['published'][:19])
            except Exception:
                return datetime.min

        return sorted(merged, key=parse_date, reverse=True)
