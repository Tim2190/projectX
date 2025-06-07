import logging
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional
from scraper_search import ScraperSearch
from urllib.parse import quote_plus


class SearchEngine:
    def __init__(self, gnews_key: str):
        self.gnews_key = gnews_key

    @staticmethod
    def _clean_query(query: str) -> str:
        """Очищает спецсимволы, оставляя слова и тире"""
        words = re.findall(r"[\w\-]+", query, flags=re.UNICODE)
        return " ".join(words)

    def search_gnews(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        formatted_query = query.strip()
        if not formatted_query:
            return []

        params = {
            'q': quote_plus(formatted_query),
            'token': self.gnews_key,
            'max': 50  # без lang и country
        }

        try:
            response = requests.get('https://gnews.io/api/v4/search', params=params)
            response.raise_for_status()
            articles = response.json().get('articles', [])
        except requests.exceptions.RequestException:
            logging.exception("GNews request failed")
            return []

        words = query.lower().split()
        filtered = []
        for art in articles:
            text = f"{art.get('title', '')} {art.get('description', '')}".lower()
            if any(w in text for w in words):
                if from_date or to_date:
                    try:
                        published_str = art.get('publishedAt', '')[:19]
                        pub_dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%S").date()
                        if from_date and pub_dt < datetime.strptime(from_date, "%Y-%m-%d").date():
                            continue
                        if to_date and pub_dt > datetime.strptime(to_date, "%Y-%m-%d").date():
                            continue
                    except Exception:
                        continue  # если дата не читается — пропускаем
                filtered.append({
                    "title": art.get("title", ""),
                    "url": art.get("url", ""),
                    "published": art.get("publishedAt", "")
                })

        return filtered

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

    def search_all(self, query: str, from_date: Optional[str], to_date: Optional[str]) -> List[Dict]:
        gnews_results = self.search_gnews(query, from_date, to_date)
        scraper_results = self.search_scraper(query, from_date, to_date)

        seen = set()
        merged = []
        for item in gnews_results + scraper_results:
            key = (item.get("title", "") + item.get("url", "")).strip()
            if key not in seen:
                seen.add(key)
                merged.append(item)

        def parse_date(item):
            try:
                return datetime.strptime(item["published"][:19], "%Y-%m-%dT%H:%M:%S")
            except:
                return datetime.min

        return sorted(merged, key=parse_date, reverse=True)

    def search(self, engine: str, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        if engine == "gnews":
            return self.search_gnews(query, from_date, to_date)
        if engine == "scraper":
            return self.search_scraper(query, from_date, to_date)
        if engine == "all":
            return self.search_all(query, from_date, to_date)
        return []
