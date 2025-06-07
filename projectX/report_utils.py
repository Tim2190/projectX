from collections import Counter, defaultdict
from typing import List, Dict


def summarize_news(events: List[Dict]) -> str:
    """Generate brief text summary for a list of clustered events."""
    total_news = sum(e.get('count', 0) for e in events)
    sentiments = Counter(e.get('sentiment', 'neutral') for e in events)
    source_counter = Counter()
    for e in events:
        for s in e.get('sources', []):
            source_counter[s] += 1

    lines = [f'Всего новостей: {total_news}']
    tone_line = ', '.join(
        f"{k}: {sentiments[k]}" for k in ['positive', 'neutral', 'negative'] if k in sentiments
    )
    if tone_line:
        lines.append('Тональность событий: ' + tone_line)

    top_sources = source_counter.most_common(3)
    if top_sources:
        src_line = ', '.join(f"{s[0]} ({s[1]})" for s in top_sources)
        lines.append('ТОП источники: ' + src_line)

    # hierarchical listing
    groups = defaultdict(list)
    for e in events:
        groups[e.get('parent_event_id', -1)].append(e)
    for pid, evs in groups.items():
        if pid == -1 or len(evs) == 1:
            ev = evs[0]
            lines.append(f"Событие: {ev['title']} ({ev['sentiment']})")
        else:
            lines.append(f"Событие: {evs[0]['title']}")
            for sub in evs:
                lines.append(f"  - {sub['title']} ({sub['sentiment']})")

    top_titles = sorted(events, key=lambda e: e['count'], reverse=True)[:3]
    if top_titles:
        tit_line = '\n'.join(f"- {e['title']}" for e in top_titles)
        lines.append('ТОП события:\n' + tit_line)

    return '\n'.join(lines)
