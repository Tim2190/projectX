import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

from app.input_handler import parse_input
from app.search_engine import search
from app.matcher import match_ratio, classify_match
from app.analyzer import analyze_sentiment, extract_country
from app.exporter import export_csv, export_pdf
from app.utils import filter_results, find_original

st.title("News Spread Monitor")

engine = st.selectbox("Search engine", ["serpapi", "gnews", "contextualweb"])
api_key = st.text_input("API Key")
host = ""
if engine == "contextualweb":
    host = st.text_input("ContextualWeb host", value="contextualwebsearch-websearch-v1.p.rapidapi.com")

user_input = st.text_area("Введите ссылку или текст новости")

if st.button("Демо-анализ"):
    user_input = "OpenAI launches new AI model"

if st.button("Анализировать") and user_input and api_key:
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

    export_csv(rows, "results.csv")
    export_pdf(rows, "results.pdf")
    st.success(
        f"Найдено {len(rows)} результатов. Сохранено в results.csv и results.pdf"
    )
    df = pd.DataFrame(rows)
    st.dataframe(df)

    fig_type = px.pie(df, names="MatchType", title="Типы совпадений")
    st.plotly_chart(fig_type)

    if df["Country"].notnull().any():
        fig_country = px.bar(df, x="Country", title="Страны")
        st.plotly_chart(fig_country)

    if df["Date"].notnull().any():
        fig_time = px.histogram(df, x="Date", nbins=20, title="Хронология")
        st.plotly_chart(fig_time)

    # Map visualization using folium if country codes available
    if df["Country"].notnull().any():
        m = folium.Map(location=[20, 0], zoom_start=2)
        country_counts = df["Country"].value_counts()
        for country, count in country_counts.items():
            folium.CircleMarker(
                location=[0, 0],
                radius=5 + count,
                popup=country,
            ).add_to(m)
        st_folium(m, width=700, height=450)
