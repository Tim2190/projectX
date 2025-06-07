import pandas as pd
import datetime
import streamlit as st
from input_handler import InputHandler
from search_engine import SearchEngine
from source_manager import SourceManager
from event_clustering import cluster_events
from streamlit_ui import show_analytics

st.title('News Monitor')

handler = InputHandler()
language = handler.select_language()
query_label = 'Запрос' if language == 'Русский' else 'Query'
query = st.text_input(query_label)
from_date, to_date = handler.date_filters()

sm = SourceManager()
st.sidebar.subheader('Источники')
uploaded = st.sidebar.file_uploader('CSV/XLSX', type=['csv', 'xlsx'])
sm.load_from_file(uploaded)

new_url = st.sidebar.text_input('URL источника')
type_choice = st.sidebar.selectbox('Тип источника', ['rss', 'html', 'telegram'])
if st.sidebar.button('Добавить') and new_url:
    sm.add_source(new_url, type_choice)

sources = sm.get_sources()
if sources:
    for idx, src in enumerate(sources):
        cols = st.sidebar.columns(2)
        cols[0].write(f"{src['url']} ({src['type']})")
        if cols[1].button('Удалить', key=f'del_{idx}'):
            sm.remove_source(idx)

if st.button('Искать') and query:
    se = SearchEngine(sources)
    try:
        results = se.search(query, from_date, to_date)
    except Exception:
        st.error('Ошибка при поиске. Измените запрос или источники.')
        results = []
    st.session_state['results'] = results
    events = cluster_events(results)
    st.session_state['events'] = events
    show_analytics(events)

if 'results' in st.session_state and st.checkbox('Показать таблицу'):
    df = pd.DataFrame(st.session_state['results'])
    if language == 'Русский':
        translations = {'title': 'Заголовок', 'url': 'Ссылка', 'published': 'Дата', 'description': 'Описание'}
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
