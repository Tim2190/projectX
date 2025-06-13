from typing import List, Dict
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from email.utils import parsedate_to_datetime
from datetime import datetime
import dateparser

model = SentenceTransformer('cointegrated/rubert-tiny2')


def _parse_date(text: str) -> datetime:
    try:
        return parsedate_to_datetime(text)
    except Exception:
        try:
            return datetime.fromisoformat(text)
        except Exception:
            dt = dateparser.parse(text)
            if dt:
                return dt
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


def cluster_events(items: List[Dict], eps: float = 0.25, min_samples: int = 2, parent_threshold: float = 0.85) -> List[Dict]:
    """Group similar news items into events using semantic embeddings and DBSCAN.
    Also aggregate semantically close events into parent clusters."""
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
    event_vectors = []
    for label, group_items in raw_groups.items():
        indices = [i for i, l in enumerate(labels) if l == label]
        embed_subset = [embeds[i] for i in indices]
        for date_group in _split_by_date(group_items):
            rep_item = date_group[0]
            sentiments = [g.get('sentiment', 'neutral') for g in date_group]
            ev_sent = Counter(sentiments).most_common(1)[0][0]
            sources = {g.get('source', 'unknown') for g in date_group}
            vector = np.mean(embed_subset, axis=0)
            events.append({
                'title': rep_item.get('title', ''),
                'published': rep_item.get('published', ''),
                'count': len(date_group),
                'sentiment': ev_sent,
                'sources': sorted(sources),
                'items': date_group,
            })
            event_vectors.append(vector)

    # build parent clusters based on similarity of event vectors
    parent_labels = [-1] * len(events)
    if events:
        sims = cosine_similarity(event_vectors)
        parent_id = 0
        for i in range(len(events)):
            if parent_labels[i] != -1:
                continue
            parent_labels[i] = parent_id
            for j in range(i + 1, len(events)):
                if parent_labels[j] == -1 and sims[i][j] > parent_threshold:
                    parent_labels[j] = parent_id
            parent_id += 1
        for ev, pid in zip(events, parent_labels):
            ev['parent_event_id'] = pid

    for idx, ev in enumerate(events):
        ev['event_id'] = idx

    return sorted(events, key=lambda e: e['count'], reverse=True)
