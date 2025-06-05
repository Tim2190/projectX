import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
import os
import sys
from datetime import datetime

# Добавить путь к app/ напрямую
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, "..", "app"))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Теперь можно импортировать напрямую
from input_handler import parse_input
from search_engine import search
from matcher import match_ratio, classify_match
from analyzer import analyze_sentiment, extract_country
from exporter import export_csv, export_pdf
from utils import filter_results, find_original


st.set_page_config(page_title="News Spread Monitor", layout="wide")
st.title("🛰 Распространение новости в интернете")

engine = st.selectbox("🔍 Выберите поисковик", ["serpapi", "gnews", "contextualweb"])
api_key = st.text_input("🔑 API-ключ")
host = ""
if engine == "contextualweb":
    host = st.text_input("🛠 ContextualWeb Host", value="contextualwebsearch-websearch-v1.p.rapidapi.com")

user_input = st.text_area("📝 Введите ссылку, заголовок или текст события")

if st.button("👁 Демо-анализ"):
    user_input = "OpenAI launches new AI model"

if st.button("🚀 Анализировать") and user_input and api_key:
    with st.spinner("Анализируем..."):
        text, url = parse_input(user_input)
        results = search(text, api_key, engine=engine, host=host)
        results = filter_results(results)

        rows = []
        for r in results:
            snippet = r.get("snippet", "")
            link = r.get("link") or r.get("url")
            ratio = match_ratio(text, snippet)
            match_type = classify_match(ratio)
            sentiment = analyze_sentiment(snippet)
            country = extract_country(link or "")
            rows.append({
                "URL": link,
                "Title": r.get("title", ""),
                "MatchType": match_type,
                "Similarity": ratio,
                "Sentiment": sentiment,
                "Country": country,
                "Date": r.get("published"),
            })

        if not rows:
            st.warning("Ничего не найдено. Проверьте текст или API ключ.")
            st.stop()

        df = pd.DataFrame(rows)

        # Сохранение с таймстемпом
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        export_csv(rows, f"results_{timestamp}.csv")
        export_pdf(rows, f"results_{timestamp}.pdf")

        st.success(f"🔍 Найдено {len(rows)} результатов. Сохранено в файлы results_{timestamp}.csv и .pdf")
        st.dataframe(df)

        fig_type = px.pie(df, names="MatchType", title="🧬 Типы совпадений")
        st.plotly_chart(fig_type)

        if df["Country"].notnull().any():
            fig_country = px.bar(df, x="Country", title="🌍 География распространения")
            st.plotly_chart(fig_country)

        if df["Date"].notnull().any():
            fig_time = px.histogram(df, x="Date", nbins=20, title="🕒 Хронология публикаций")
            st.plotly_chart(fig_time)

        if df["Country"].notnull().any():
            m = folium.Map(location=[20, 0], zoom_start=2)
            country_counts = df["Country"].value_counts()
            for country, count in country_counts.items():
                folium.CircleMarker(
                    location=[0, 0],  # Заменить на координаты страны в будущем
                    radius=5 + count,
                    popup=country,
                ).add_to(m)
            st_folium(m, width=700, height=450)
