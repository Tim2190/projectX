import re
from datetime import date
from typing import List, Dict, Optional
from projectX.scraper_search import ScraperSearch


class SearchEngine:
    """Простой поисковик: ищет свежие новости по ключевым словам, без тональности."""

    def __init__(self):
        pass

    def _clean_query(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text).strip()

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        # Ищем за сегодня по умолчанию
        if not from_date:
            from_date = date.today().isoformat()
        if not to_date:
            to_date = date.today().isoformat()

        cleaned = self._clean_query(query)
        scraper = ScraperSearch()
        raw_results = scraper.search(cleaned, from_date, to_date)

        words = query.lower().split()
        filtered = []
        for item in raw_results:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            if all(w in text for w in words):
                item['source'] = item.get('source', 'Scraper')
                filtered.append(item)

        # Удаление дубликатов по URL
        results_by_url = {}
        for item in filtered:
            url = item.get('url')
            if url and url not in results_by_url:
                results_by_url[url] = item

        return list(results_by_url.values())
