import sys
import os
import pandas as pd
import datetime
import streamlit as st
from input_handler import InputHandler
from search_engine import SearchEngine
from exporter import Exporter

sys.path.append(os.path.dirname(__file__))

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
    results = se.search(engine_name, query, from_date, to_date)
    df = pd.DataFrame(results)

    if language == 'Русский':
        translations = {
            'title': 'Заголовок',
            'url': 'Ссылка',
            'published': 'Дата',
            'snippet': 'Описание',
        }
        df = df.rename(columns={k: v for k, v in translations.items() if k in df.columns})

    st.dataframe(df)

    exporter = Exporter()
    csv_label = 'Путь для CSV' if language == 'Русский' else 'CSV path'
    pdf_label = 'Путь для PDF' if language == 'Русский' else 'PDF path'
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    csv_path = st.text_input(csv_label, f'results_{timestamp}.csv')
    pdf_path = st.text_input(pdf_label, f'results_{timestamp}.pdf')

    if st.button('Экспорт CSV'):
        if df.empty:
            st.warning('Нет данных для экспорта')
        else:
            try:
                exporter.export_csv(df, csv_path)
                st.success('CSV сохранен' if language == 'Русский' else 'CSV saved')
            except Exception as e:
                st.error(str(e))

    if st.button('Экспорт PDF'):
        if df.empty:
            st.warning('Нет данных для экспорта')
        else:
            try:
                exporter.export_pdf(df, pdf_path)
                st.success('PDF сохранен' if language == 'Русский' else 'PDF saved')
            except Exception as e:
                st.error(str(e))
