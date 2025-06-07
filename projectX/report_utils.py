from collections import Counter
from typing import List, Dict


def summarize_news(items: List[Dict]) -> str:
    total = len(items)
    sentiments = Counter(i.get('sentiment', 'neutral') for i in items)
    sources = Counter(i.get('source', 'unknown') for i in items)
    titles = Counter(i.get('title', '') for i in items)

    lines = [f'Всего новостей: {total}']
    lines.append('Тональность: ' + ', '.join([
        f"{k}: {sentiments[k]}" for k in ['positive', 'neutral', 'negative'] if k in sentiments
    ]))

    top_sources = sources.most_common(3)
    if top_sources:
        src_line = ', '.join([f"{s[0]} ({s[1]})" for s in top_sources])
        lines.append('ТОП источники: ' + src_line)

    top_titles = titles.most_common(3)
    if top_titles:
        tit_line = '\n'.join([f"- {t[0]}" for t in top_titles])
        lines.append('ТОП заголовки:\n' + tit_line)

    return '\n'.join(lines)
