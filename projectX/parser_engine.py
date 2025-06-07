import os
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

try:
    import telethon
    from telethon.sync import TelegramClient
except Exception:
    TelegramClient = None

class ParserEngine:
    """Parse different types of sources."""

    def _parse_rss(self, url: str) -> List[Dict]:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            items.append({
                'title': getattr(entry, 'title', ''),
                'url': getattr(entry, 'link', ''),
                'published': getattr(entry, 'published', ''),
                'description': getattr(entry, 'summary', ''),
                'source': url
            })
        return items

    def _parse_html(self, url: str) -> List[Dict]:
        try:
            resp = requests.get(url, timeout=10)
        except Exception:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = []
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            link = a.get('href', '')
            if title and link:
                full_link = link if link.startswith('http') else os.path.join(url, link)
                items.append({
                    'title': title,
                    'url': full_link,
                    'published': '',
                    'description': '',
                    'source': url
                })
        return items

    def _parse_telegram(self, handle: str) -> List[Dict]:
        if TelegramClient is None:
            return []
        api_id = os.getenv('TG_API_ID')
        api_hash = os.getenv('TG_API_HASH')
        if not api_id or not api_hash:
            return []
        client = TelegramClient('session', api_id, api_hash)
        items = []
        with client:
            for msg in client.iter_messages(handle, limit=20):
                if msg.text:
                    items.append({
                        'title': msg.text.split('\n')[0][:60],
                        'url': f"https://t.me/{handle.strip('@')}/{msg.id}",
                        'published': msg.date.isoformat(),
                        'description': msg.text[:200],
                        'source': handle
                    })
        return items

    def parse(self, source: Dict) -> List[Dict]:
        t = source.get('type')
        url = source.get('url')
        if t == 'rss':
            return self._parse_rss(url)
        if t == 'html':
            return self._parse_html(url)
        if t == 'telegram':
            return self._parse_telegram(url)
        return []
