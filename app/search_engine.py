import requests
from typing import List, Dict, Optional
from scraper_search import ScraperSearch
from urllib.parse import quote_plus

class SearchEngine:
    def __init__(self, gnews_key: str = ''):
        self.gnews_key = gnews_key

    def search_gnews(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        params = {
            'q': quote_plus(query),
            'token': self.gnews_key
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        response = requests.get('https://gnews.io/api/v4/search', params=params)
        response.raise_for_status()
        return response.json().get('articles', [])

    def search_scraper(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Use fallback scraper search"""
        scraper = ScraperSearch()
        return scraper.search(query, from_date, to_date)

    def search(self, engine: str, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """General search dispatcher"""
        if engine == "gnews":
            return self.search_gnews(query, from_date, to_date)
        if engine == "scraper":
            return self.search_scraper(query, from_date, to_date)
        return []
