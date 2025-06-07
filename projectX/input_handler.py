from datetime import date
import datetime
import streamlit as st


class InputHandler:
    def select_language(self) -> str:
        """Allow user to choose interface language"""
        return st.sidebar.selectbox('Language / Язык', ['Русский', 'English'])

    def date_filters(self):
        default_from = date.today() - datetime.timedelta(days=7)
        default_to = date.today()
        from_date = st.sidebar.date_input('Дата с', value=default_from)
        to_date = st.sidebar.date_input('Дата по', value=default_to)
        from_str = from_date.isoformat()
        to_str = to_date.isoformat()
        return from_str, to_str
