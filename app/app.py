import sys
import os
import pandas as pd
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
        profile.get('serpapi', ''),
        profile.get('gnews', ''),
        profile.get('contextualweb', ''),
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
    csv_path = st.text_input(csv_label, 'results.csv')
    pdf_path = st.text_input(pdf_label, 'results.pdf')
    if st.button('Экспорт CSV'):
        exporter.export_csv(df, csv_path)
        st.success('CSV сохранен' if language == 'Русский' else 'CSV saved')
    if st.button('Экспорт PDF'):
        exporter.export_pdf(df, pdf_path)
        st.success('PDF сохранен' if language == 'Русский' else 'PDF saved')
