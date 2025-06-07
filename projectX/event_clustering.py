from typing import List, Dict
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')


def cluster_events(items: List[Dict], threshold: float = 0.65) -> List[Dict]:
    """Group similar news items into events using embeddings."""
    texts = [f"{i.get('title','')} {i.get('description','')}" for i in items]
    if not texts:
        return []
    embeds = model.encode(texts, show_progress_bar=False)
    sim = cosine_similarity(embeds)
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
        sentiments = [g.get('sentiment', 'neutral') for g in group]
        ev_sent = Counter(sentiments).most_common(1)[0][0]
        events.append({
            'title': item.get('title', ''),
            'published': item.get('published', ''),
            'count': len(group),
            'sentiment': ev_sent,
            'items': group
        })
    return sorted(events, key=lambda e: e['count'], reverse=True)
