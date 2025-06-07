import pandas as pd
import streamlit as st
import plotly.express as px


def show_analytics(events, sources):
    total_news = sum(e['count'] for e in events)
    st.subheader('Аналитика')
    cols = st.columns(3)
    cols[0].metric('Всего новостей', total_news)
    cols[1].metric('Количество источников', len(sources))
    cols[2].metric('Уникальных событий', len(events))

    if not events:
        st.info('Нет данных для отображения')
        return

    df = pd.DataFrame([
        {'date': e['published'][:10], 'count': e['count'], 'source': e['items'][0].get('source', '')}
        for e in events
    ])
    if not df.empty:
        by_day = df.groupby('date')['count'].sum().reset_index()
        fig = px.bar(by_day, x='date', y='count', title='Распределение по дням')
        st.plotly_chart(fig, use_container_width=True)

        by_source = df.groupby('source')['count'].sum().reset_index()
        fig2 = px.pie(by_source, names='source', values='count', title='По источникам')
        st.plotly_chart(fig2, use_container_width=True)
