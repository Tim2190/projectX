import re
from datetime import datetime
from typing import List, Dict, Optional
from scraper_search import ScraperSearch
from parser_engine import ParserEngine
from transformers import pipeline


class SearchEngine:
    """Search news using built-in scraper and custom sources."""

    @staticmethod
    def _clean_query(query: str) -> str:
        words = re.findall(r"[\w\-]+", query, flags=re.UNICODE)
        return " ".join(words)

    def __init__(self, sources: List[Dict]):
        self.sources = sources
        self.parser = ParserEngine()
        try:
            self.sentiment_pipe = pipeline('text-classification',
                                           model='cointegrated/rubert-tiny2-cedr-emotion-detection')
        except Exception:
            self.sentiment_pipe = None

    def _sentiment(self, text: str) -> str:
        if not self.sentiment_pipe:
            return 'neutral'
        try:
            res = self.sentiment_pipe(text[:512])[0]['label']
            return res.lower()
        except Exception:
            return 'neutral'

    def search_scraper(self, query: str, from_date: Optional[str], to_date: Optional[str]) -> List[Dict]:
        cleaned = self._clean_query(query.strip())
        scraper = ScraperSearch()
        raw_results = scraper.search(cleaned, from_date, to_date)
        words = query.lower().split()
        filtered = []
        for item in raw_results:
            text = f"{item.get('title','')} {item.get('summary','')}".lower()
            if all(w in text for w in words):
                item['source'] = 'Scraper'
                filtered.append(item)
        return filtered

    def search_sources(self, query: str) -> List[Dict]:
        results = []
        words = query.lower().split()
        for src in self.sources:
            for item in self.parser.parse(src):
                text = f"{item.get('title','')} {item.get('description','')}".lower()
                if all(w in text for w in words):
                    results.append(item)
        return results

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        scraper_results = self.search_scraper(query, from_date, to_date)
        source_results = self.search_sources(query)

        results_by_url = {}

        # Add custom sources first
        for item in source_results:
            url = item.get('url')
            if url:
                results_by_url[url] = item

        # Add scraper results only if url not already seen
        for item in scraper_results:
            url = item.get('url')
            if url and url not in results_by_url:
                results_by_url[url] = item

        merged = list(results_by_url.values())

        for item in merged:
            text = f"{item.get('title','')} {item.get('description','')}"
            item['sentiment'] = self._sentiment(text)

        def parse_date(item):
            try:
                return datetime.fromisoformat(item['published'][:19])
            except Exception:
                return datetime.min

        return sorted(merged, key=parse_date, reverse=True)
