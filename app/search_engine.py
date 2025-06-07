import re
from typing import List, Dict, Optional
from scraper_search import ScraperSearch


class SearchEngine:
    def __init__(self):
        pass

    @staticmethod
    def _clean_query(query: str) -> str:
        """Очищает спецсимволы, оставляя слова и тире"""
        words = re.findall(r"[\w\-]+", query, flags=re.UNICODE)
        return " ".join(words)


    def search_scraper(self, query: str, from_date: Optional[str], to_date: Optional[str]) -> List[Dict]:
        cleaned = self._clean_query(query.strip())
        scraper = ScraperSearch()
        raw_results = scraper.search(cleaned, from_date, to_date)

        words = query.lower().split()
        filtered = []
        for item in raw_results:
            text = f"{item.get('title','')} {item.get('summary','')}".lower()
            if any(w in text for w in words):
                filtered.append(item)

        return filtered


    def search(self, engine: str, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        if engine == "scraper":
            return self.search_scraper(query, from_date, to_date)
        return []
