from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def cluster_events(items: List[Dict], threshold: float = 0.6) -> List[Dict]:
    """Group similar news items into events."""
    texts = [f"{i.get('title','')} {i.get('description','')}" for i in items]
    if not texts:
        return []
    vect = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(vect)
    used = set()
    events = []
    for idx, item in enumerate(items):
        if idx in used:
            continue
        group = [item]
        used.add(idx)
        for j in range(idx + 1, len(items)):
            if j not in used and sim[idx, j] >= threshold:
                group.append(items[j])
                used.add(j)
        events.append({
            'title': item.get('title',''),
            'published': item.get('published',''),
            'count': len(group),
            'items': group
        })
    return sorted(events, key=lambda e: e['count'], reverse=True)
