from datetime import date
from typing import Optional
import streamlit as st
from profile_manager import ProfileManager

class InputHandler:
    def __init__(self):
        self.pm = ProfileManager()

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
        from_date = st.sidebar.date_input('Дата с', value=None)
        to_date = st.sidebar.date_input('Дата по', value=None)
        from_str = from_date.isoformat() if isinstance(from_date, date) else None
        to_str = to_date.isoformat() if isinstance(to_date, date) else None
        return from_str, to_str
