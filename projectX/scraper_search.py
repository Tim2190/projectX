import feedparser
import logging
import datetime
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import dateparser


def extract_pub_date(url: str) -> Optional[str]:
    """Try to extract publication date from the article HTML page."""
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
    except Exception:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    meta_props = [
        ('meta', {'property': 'article:published_time'}),
        ('meta', {'name': 'pubdate'}),
        ('meta', {'name': 'publishdate'}),
        ('meta', {'itemprop': 'datePublished'}),
    ]
    for tag_name, attrs in meta_props:
        tag = soup.find(tag_name, attrs=attrs)
        if tag and tag.get('content'):
            dt = dateparser.parse(tag['content'])
            if dt:
                return dt.isoformat()
    # look for generic date-like elements
    date_tags = soup.find_all(class_=re.compile(r'(date|time|published)', re.I))
    for tag in date_tags:
        text = tag.get('datetime') or tag.get_text(' ', strip=True)
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

class ScraperSearch:
    """Fallback search engine using Google News RSS feeds."""

    def search(self, query: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Perform search via public RSS without API keys."""
        safe_query = quote_plus(query)
        url = (
            "https://news.google.com/rss/search?q="
            f"{safe_query}&hl=ru&gl=RU&ceid=RU:ru"
        )

        feed = feedparser.parse(url)

        if getattr(feed, "bozo", False):
            logging.error("Feedparser error: %s", feed.get("bozo_exception"))
            return []

        results = []

        try:
            from_dt = datetime.date.fromisoformat(from_date) if from_date else None
            to_dt = datetime.date.fromisoformat(to_date) if to_date else None
        except ValueError:
            from_dt, to_dt = None, None

        for entry in feed.entries:
            pub = getattr(entry, "published", "")
            pub_dt = None
            if getattr(entry, "published_parsed", None):
                try:
                    pub_dt = datetime.date(*entry.published_parsed[:3])
                except Exception:
                    pass
            if not pub or (pub_dt and pub_dt.year < 2000) or (not pub_dt and pub and not dateparser.parse(pub)):
                html_date = extract_pub_date(entry.link)
                if html_date:
                    pub = html_date
                    try:
                        pub_dt = dateparser.parse(html_date).date()
                    except Exception:
                        pub_dt = None

            if from_dt and pub_dt and pub_dt < from_dt:
                continue
            if to_dt and pub_dt and pub_dt > to_dt:
                continue

            # Расширенный поиск: все слова должны быть в тексте
            text = f"{getattr(entry, 'title', '')} {getattr(entry, 'summary', '')}".lower()
            query_words = query.lower().split()
            if not all(word in text for word in query_words):
                continue

            title = getattr(entry, "title", "")
            src_name = None
            if getattr(entry, "source", None) and entry.source.get("title"):
                src_name = entry.source["title"].strip()
            if not src_name and " - " in title:
                title, src_name = title.rsplit(" - ", 1)
                title = title.strip()
                src_name = src_name.strip()

            results.append(
                {
                    "title": title,
                    "url": entry.link,
                    "published": pub,
                    "summary": getattr(entry, "summary", ""),
                    "source": src_name or "Scraper",
                }
            )

        return results
