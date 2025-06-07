import os
import pandas as pd
import datetime
import streamlit as st
from input_handler import InputHandler
from search_engine import SearchEngine

st.title('News Monitor')

handler = InputHandler()
language = handler.select_language()
engine_name = handler.select_engine()
profile = handler.select_profile(engine_name)

query_label = 'Запрос' if language == 'Русский' else 'Query'
query = st.text_input(query_label)
from_date, to_date = handler.date_filters()

if st.button('Искать') and query:
    se = SearchEngine(
        profile.get('gnews', '')
    )
    try:
        results = se.search(engine_name, query, from_date, to_date)
    except Exception:
        st.error('Ошибка запроса к поисковику. Попробуйте изменить ключевые слова.')
        results = []
    df = pd.DataFrame(results)

    if language == 'Русский':
        translations = {
            'title': 'Заголовок',
            'url': 'Ссылка',
            'published': 'Дата',
            'snippet': 'Описание',
        }
        df = df.rename(columns={k: v for k, v in translations.items() if k in df.columns})

    if df.empty:
        st.info('Нет результатов. Попробуйте изменить ключевые слова.')
    st.dataframe(df, use_container_width=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    csv_name = f'results_{timestamp}.csv'
    st.download_button(
        label='Скачать CSV' if language == 'Русский' else 'Download CSV',
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=csv_name,
        mime='text/csv'
    )
