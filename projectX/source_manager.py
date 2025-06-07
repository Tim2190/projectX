import pandas as pd
import streamlit as st

class SourceManager:
    """Manage user-provided monitoring sources."""

    def __init__(self):
        if 'sources' not in st.session_state:
            st.session_state['sources'] = []

    def get_sources(self):
        """Return list of sources."""
        return st.session_state['sources']

    def add_source(self, url: str, source_type: str):
        """Add single source."""
        if {'url': url, 'type': source_type} not in st.session_state['sources']:
            st.session_state['sources'].append({'url': url, 'type': source_type})

    def remove_source(self, index: int):
        """Remove source by index."""
        if 0 <= index < len(st.session_state['sources']):
            st.session_state['sources'].pop(index)

    def load_from_file(self, uploaded_file):
        if uploaded_file is None:
            return
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error('Unsupported file format')
            return
        for _, row in df.iterrows():
            url = row.get('url')
            t = str(row.get('type', '')).lower()
            if pd.notna(url) and t:
                self.add_source(str(url), t)
