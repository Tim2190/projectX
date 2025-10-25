"""Export results to CSV or PDF."""

import csv
from typing import List, Dict
from fpdf import FPDF


def export_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        return
    keys = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def export_pdf(rows: List[Dict], path: str, title: str = "Report") -> None:
    if not rows:
        return
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=1, align="C")
    headers = list(rows[0].keys())
    col_width = 190 / len(headers)
    for h in headers:
        pdf.cell(col_width, 10, h, border=1)
    pdf.ln()
    for row in rows:
        for h in headers:
            text = str(row.get(h, ""))[:30]
            pdf.cell(col_width, 10, text, border=1)
        pdf.ln()
    pdf.output(path)
