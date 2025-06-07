from typing import List, Dict
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer
from email.utils import parsedate_to_datetime
from datetime import datetime

model = SentenceTransformer('cointegrated/rubert-tiny2')


def _parse_date(text: str) -> datetime:
    try:
        return parsedate_to_datetime(text)
    except Exception:
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return datetime.min


def _split_by_date(items: List[Dict], max_days: int = 3) -> List[List[Dict]]:
    if not items:
        return []
    items.sort(key=lambda i: _parse_date(i.get('published', '')))
    groups = []
    current = []
    start = _parse_date(items[0].get('published', ''))
    for it in items:
        dt = _parse_date(it.get('published', ''))
        if (dt - start).days > max_days:
            if current:
                groups.append(current)
            current = []
            start = dt
        current.append(it)
    if current:
        groups.append(current)
    return groups


def cluster_events(items: List[Dict], eps: float = 0.25, min_samples: int = 2) -> List[Dict]:
    """Group similar news items into events using semantic embeddings and DBSCAN."""
    texts = [f"{i.get('title','')} {i.get('summary','')}" for i in items]
    if not texts:
        return []
    embeds = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeds)

    raw_groups = defaultdict(list)
    for label, item in zip(labels, items):
        raw_groups[label].append(item)

    events = []
    for group_items in raw_groups.values():
        for date_group in _split_by_date(group_items):
            rep_item = date_group[0]
            sentiments = [g.get('sentiment', 'neutral') for g in date_group]
            ev_sent = Counter(sentiments).most_common(1)[0][0]
            sources = {g.get('source', 'unknown') for g in date_group}
            events.append({
                'title': rep_item.get('title', ''),
                'published': rep_item.get('published', ''),
                'count': len(date_group),
                'sentiment': ev_sent,
                'sources': sorted(sources),
                'items': date_group,
            })

    return sorted(events, key=lambda e: e['count'], reverse=True)
