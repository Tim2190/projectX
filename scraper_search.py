import feedparser
from typing import List, Dict

class ScraperSearch:
    """Fallback search engine using Google News RSS feeds."""

    def search(self, query: str) -> List[Dict]:
        """Perform search via public RSS without API keys."""
        url = (
            "https://news.google.com/rss/search?q="
            f"{query}&hl=ru&gl=RU&ceid=RU:ru"
        )
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            results.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "published": getattr(entry, "published", ""),
                }
            )
        return results
