import os
import streamlit as st
from fpdf import FPDF
import pandas as pd

class Exporter:
    def __init__(self):
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        self.font_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
        self.font_available = os.path.exists(self.font_path)
        if not self.font_available:
            st.warning('Font DejaVuSans.ttf not found in app/fonts/')

    def export_csv(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

    def export_pdf(self, df: pd.DataFrame, path: str):
        if not self.font_available:
            st.error('Невозможно создать PDF: отсутствует шрифт DejaVuSans.ttf')
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', self.font_path, uni=True)
        pdf.set_font('DejaVu', size=12)
        col_width = pdf.epw / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), border=1)
        pdf.ln()
        for _, row in df.iterrows():
            for cell in row:
                pdf.cell(col_width, 10, str(cell), border=1)
            pdf.ln()
        pdf.output(path)
