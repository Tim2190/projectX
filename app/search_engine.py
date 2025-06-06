import requests
from typing import List, Dict, Optional
from scraper_search import ScraperSearch

class SearchEngine:
    def __init__(self, serpapi_key: str = '', gnews_key: str = '', contextual_key: str = ''):
        self.serpapi_key = serpapi_key
        self.gnews_key = gnews_key
        self.contextual_key = contextual_key

    def search_serpapi(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        params = {
            'q': query,
            'api_key': self.serpapi_key,
            'engine': 'google',
            'tbm': 'nws'
        }
        if from_date:
            params['after'] = from_date
        if to_date:
            params['before'] = to_date
        response = requests.get('https://serpapi.com/search', params=params)
        response.raise_for_status()
        return response.json().get('news_results', [])

    def search_gnews(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        params = {
            'q': query,
            'token': self.gnews_key
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        response = requests.get('https://gnews.io/api/v4/search', params=params)
        response.raise_for_status()
        return response.json().get('articles', [])

    def search_contextual(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        headers = {
            'X-RapidAPI-Key': self.contextual_key,
            'X-RapidAPI-Host': 'contextualwebsearch-websearch-v1.p.rapidapi.com'
        }
        params = {'q': query}
        if from_date:
            params['fromPublishedDate'] = from_date
        if to_date:
            params['toPublishedDate'] = to_date
        response = requests.get('https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/NewsSearchAPI',
                                headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('value', [])

    def search_scraper(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Use fallback scraper search"""
        scraper = ScraperSearch()
        return scraper.search(query, from_date, to_date)

    def search(self, engine: str, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """General search dispatcher"""
        if engine == "serpapi":
            return self.search_serpapi(query, from_date, to_date)
        if engine == "gnews":
            return self.search_gnews(query, from_date, to_date)
        if engine == "contextual":
            return self.search_contextual(query, from_date, to_date)
        if engine == "scraper":
            return self.search_scraper(query, from_date, to_date)
        return []
