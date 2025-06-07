from datetime import date
import datetime
from typing import Optional, List, Dict
import pandas as pd
import streamlit as st
from profile_manager import ProfileManager
from source_manager import SourceManager

class InputHandler:
    def __init__(self):
        self.pm = ProfileManager()
        self.sm = SourceManager()

    def select_language(self) -> str:
        """Allow user to choose interface language"""
        return st.sidebar.selectbox('Language / Язык', ['Русский', 'English'])

    def select_engine(self) -> str:
        """Choose search engine"""
        engines = ['gnews', 'scraper']
        labels = {
            'gnews': 'GNews',
            'scraper': 'Scraper'
        }
        choice = st.sidebar.selectbox('Движок поиска', [labels[e] for e in engines])
        return engines[[labels[e] for e in engines].index(choice)]
    def select_profile(self, engine: str):
        profiles = self.pm.load_profiles()
        names = list(profiles.keys()) + ['Создать новый']
        choice = st.sidebar.selectbox('Выберите профиль', names)
        if choice == 'Создать новый':
            name = st.text_input('Имя профиля')
            keys = {}
            if engine != 'scraper':
                gnews = st.text_input('GNews ключ')
                keys = {
                    'gnews': gnews,
                }
            if st.button('Сохранить профиль'):
                self.pm.add_profile(name, keys)
                st.success('Профиль сохранен')
                st.rerun()
            return {}
        else:
            return profiles.get(choice, {})

    def date_filters(self):
        default_from = date.today() - datetime.timedelta(days=7)
        default_to = date.today()
        from_date = st.sidebar.date_input('Дата с', value=default_from)
        to_date = st.sidebar.date_input('Дата по', value=default_to)
        from_str = from_date.isoformat()
        to_str = to_date.isoformat()
        return from_str, to_str

    def sources_widget(self, language: str) -> List[Dict[str, str]]:
        """Load, edit and persist news sources."""
        title = 'Источники' if language == 'Русский' else 'Sources'
        upload_label = 'Загрузить CSV/XLSX' if language == 'Русский' else 'Upload CSV/XLSX'
        save_label = 'Сохранить источники' if language == 'Русский' else 'Save sources'

        st.sidebar.markdown(f"### {title}")
        uploaded = st.sidebar.file_uploader(upload_label, type=['csv', 'xlsx'])
        if uploaded is not None:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
        else:
            df = pd.DataFrame(self.sm.load_sources())

        edited = st.sidebar.data_editor(df, num_rows='dynamic', key='sources_editor')
        if st.sidebar.button(save_label):
            if {'url', 'type'}.issubset(edited.columns):
                records = edited[['url', 'type']].fillna('').to_dict(orient='records')
                self.sm.save_sources(records)
                st.sidebar.success('Сохранено' if language == 'Русский' else 'Saved')
        return self.sm.load_sources()
