import requests
from typing import List, Dict, Optional
from scraper_search import ScraperSearch
from urllib.parse import quote_plus
from datetime import datetime
import time

class SearchEngine:
    def __init__(self, gnews_key: str = ''):
        self.gnews_key = gnews_key

    def search_gnews(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        # Оборачиваем многословный запрос в кавычки
        formatted_query = f'"{query.strip()}"' if ' ' in query else query.strip()
        params = {
            'q': formatted_query,
            'token': self.gnews_key
        }

        response = requests.get('https://gnews.io/api/v4/search', params=params)
        response.raise_for_status()

        articles = response.json().get('articles', [])

        # Локальная фильтрация по дате
        if from_date or to_date:
            from_ts = time.mktime(datetime.strptime(from_date, "%Y-%m-%d").timetuple()) if from_date else 0
            to_ts = time.mktime(datetime.strptime(to_date, "%Y-%m-%d").timetuple()) if to_date else float('inf')

            filtered_articles = []
            for art in articles:
                try:
                    art_ts = time.mktime(datetime.strptime(art['publishedAt'][:19], "%Y-%m-%dT%H:%M:%S").timetuple())
                    if from_ts <= art_ts <= to_ts:
                        filtered_articles.append(art)
                except:
                    continue
            return filtered_articles
        return articles

    def search_scraper(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        # То же поведение — обёртка в кавычки
        formatted_query = f'"{query.strip()}"' if ' ' in query else query.strip()
        scraper = ScraperSearch()
        return scraper.search(formatted_query, from_date, to_date)

    def search(self, engine: str, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        if engine == "gnews":
            return self.search_gnews(query, from_date, to_date)
        if engine == "scraper":
            return self.search_scraper(query, from_date, to_date)
        return []
