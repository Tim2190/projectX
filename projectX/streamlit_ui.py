import pandas as pd
import streamlit as st
import plotly.express as px


def show_analytics(events):
    total_news = sum(e['count'] for e in events)
    st.subheader('Аналитика')
    cols = st.columns(2)
    cols[0].metric('Всего новостей', total_news)
    cols[1].metric('Уникальных событий', len(events))

    if not events:
        st.info('Нет данных для отображения')
        return

    # Expand events into individual items for detailed analytics
    item_rows = []
    for e in events:
        for it in e['items']:
            item_rows.append({
                'date': it.get('published', '')[:10],
                'source': it.get('source', 'unknown'),
            })
    df = pd.DataFrame(item_rows)

    if not df.empty:
        by_day = df.groupby('date').size().reset_index(name='count')
        fig = px.bar(by_day, x='date', y='count', title='Распределение по дням')
        st.plotly_chart(fig, use_container_width=True)

        by_source = df.groupby('source').size().reset_index(name='count')
        fig2 = px.pie(by_source, names='source', values='count', title='По источникам')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader('События')
    for ev in events:
        with st.expander(f"{ev['title']} ({ev['count']})"):
            for it in ev['items']:
                line = f"{it.get('published','')[:10]} [{it.get('source','')}] {it.get('title','')}"
                st.write(line)
