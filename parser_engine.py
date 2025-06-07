import asyncio
from typing import List, Dict
from urllib.parse import urlparse, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient


class RSSParser:
    """Parse RSS feeds using feedparser."""

    def parse(self, feed_url: str) -> List[Dict[str, str]]:
        feed = feedparser.parse(feed_url)
        source = urlparse(feed_url).netloc
        entries = []
        for entry in feed.entries:
            entries.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": source,
            })
        return entries


class HTMLParser:
    """Parse HTML pages and extract article links."""

    def parse(self, url: str) -> List[Dict[str, str]]:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        source = urlparse(url).netloc
        entries = []
        for article in soup.find_all("article"):
            anchor = article.find("a")
            if not anchor or not anchor.get("href"):
                continue
            link = urljoin(url, anchor["href"])
            title = anchor.get_text(strip=True)
            summary = article.get_text(" ", strip=True)
            entries.append({
                "title": title,
                "url": link,
                "published": "",
                "summary": summary,
                "source": source,
            })
        if not entries:
            title = soup.title.string.strip() if soup.title else ""
            summary = soup.get_text(" ", strip=True)[:200]
            entries.append({
                "title": title,
                "url": url,
                "published": "",
                "summary": summary,
                "source": source,
            })
        return entries


class TelegramParser:
    """Parse Telegram channel messages using Telethon."""

    def __init__(self, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash

    def parse(self, channel: str, limit: int = 20) -> List[Dict[str, str]]:
        async def _run():
            entries = []
            async with TelegramClient("parser_session", self.api_id, self.api_hash) as client:
                async for msg in client.iter_messages(channel, limit=limit):
                    if not msg.message:
                        continue
                    entries.append({
                        "title": msg.message.split("\n", 1)[0][:80],
                        "url": f"https://t.me/{channel}/{msg.id}",
                        "published": msg.date.isoformat() if msg.date else "",
                        "summary": msg.message,
                        "source": channel,
                    })
            return entries

        return asyncio.run(_run())
