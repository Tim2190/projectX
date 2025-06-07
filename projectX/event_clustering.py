from typing import List, Dict
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('cointegrated/rubert-tiny2')


def cluster_events(items: List[Dict], eps: float = 0.25, min_samples: int = 2) -> List[Dict]:
    """Group similar news items into events using DBSCAN clustering."""
    texts = [f"{i.get('title','')} {i.get('summary','')}" for i in items]
    if not texts:
        return []
    embeds = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeds)

    groups = defaultdict(list)
    for label, item in zip(labels, items):
        groups[label].append(item)

    events = []
    for label, group_items in groups.items():
        rep_item = group_items[0]
        sentiments = [g.get('sentiment', 'neutral') for g in group_items]
        ev_sent = Counter(sentiments).most_common(1)[0][0]
        events.append({
            'title': rep_item.get('title', ''),
            'published': rep_item.get('published', ''),
            'count': len(group_items),
            'sentiment': ev_sent,
            'items': group_items,
        })

    return sorted(events, key=lambda e: e['count'], reverse=True)
