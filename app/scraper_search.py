import feedparser
from typing import List, Dict, Optional
import datetime

class ScraperSearch:
    """Fallback search engine using Google News RSS feeds."""

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Perform search via public RSS without API keys."""
        url = (
            "https://news.google.com/rss/search?q="
            f"{query}&hl=ru&gl=RU&ceid=RU:ru"
        )
        feed = feedparser.parse(url)
        results = []
        from_dt = datetime.date.fromisoformat(from_date) if from_date else None
        to_dt = datetime.date.fromisoformat(to_date) if to_date else None
        for entry in feed.entries:
            pub = getattr(entry, "published", "")
            pub_dt = None
            if getattr(entry, "published_parsed", None):
                pub_dt = datetime.date(*entry.published_parsed[:3])
            if from_dt and pub_dt and pub_dt < from_dt:
                continue
            if to_dt and pub_dt and pub_dt > to_dt:
                continue
            results.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "published": pub,
                }
            )
        return results
