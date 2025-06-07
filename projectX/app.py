import pandas as pd
import datetime
import streamlit as st
from input_handler import InputHandler
from search_engine import SearchEngine
from event_clustering import cluster_events
from streamlit_ui import show_analytics
from report_utils import summarize_news

st.title('News Monitor')

handler = InputHandler()
language = handler.select_language()
query_label = 'Запрос' if language == 'Русский' else 'Query'
query = st.text_input(query_label)
from_date, to_date = handler.date_filters()

if st.button('Искать') and query:
    se = SearchEngine()
    try:
        results = se.search(query, from_date, to_date)
    except Exception:
        st.error('Ошибка при поиске. Измените запрос или источники.')
        results = []
    st.session_state['results'] = results
    events = cluster_events(results)
    st.session_state['events'] = events
    st.session_state.pop('report', None)

if 'events' in st.session_state:
    show_analytics(st.session_state['events'])

if 'results' in st.session_state and st.checkbox('Показать таблицу'):
    df = pd.DataFrame(st.session_state['results'])
    if language == 'Русский':
        translations = {'title': 'Заголовок', 'url': 'Ссылка', 'published': 'Дата', 'summary': 'Описание', 'source': 'Источник'}
        df = df.rename(columns={k: v for k, v in translations.items() if k in df.columns})
    st.dataframe(df, use_container_width=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    csv_name = f'results_{timestamp}.csv'
    st.download_button(
        label='Скачать CSV' if language == 'Русский' else 'Download CSV',
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=csv_name,
        mime='text/csv',
    )

if st.button('Развёрнутая аналитическая справка') and 'events' in st.session_state:
    st.session_state['report'] = summarize_news(st.session_state['events'])

if 'report' in st.session_state:
    st.text_area('Справка', st.session_state['report'], height=300)
