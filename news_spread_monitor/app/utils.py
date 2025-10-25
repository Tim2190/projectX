"""Utility helpers for filtering and deduplication."""

from typing import Iterable, List, Dict, Set, Optional
from datetime import datetime
import tldextract

EXCLUDED_DOMAINS = {
    "copy-site.xyz",
    "aggregator.com",
}


def filter_results(results: Iterable[Dict]) -> List[Dict]:
    """Remove results from excluded domains and drop duplicates by URL."""
    seen: Set[str] = set()
    filtered: List[Dict] = []
    for r in results:
        url = r.get("link") or r.get("url")
        if not url:
            continue
        domain = tldextract.extract(url).registered_domain
        if domain in EXCLUDED_DOMAINS:
            continue
        if url in seen:
            continue
        seen.add(url)
        filtered.append(r)
    return filtered


def find_original(results: Iterable[Dict]) -> Optional[Dict]:
    """Return result with earliest publication date if available."""
    earliest_dt: Optional[datetime] = None
    earliest: Optional[Dict] = None
    for r in results:
        date_str = r.get("published") or r.get("date") or r.get("publishedAt")
        if not date_str:
            continue
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str[:19], fmt)
                break
            except ValueError:
                dt = None
        if dt is None:
            continue
        if earliest_dt is None or dt < earliest_dt:
            earliest_dt = dt
            earliest = r
    return earliest
