# ProjectX

Приложение на Streamlit для мониторинга новостей.

## Возможности
* Поиск новостей через SerpApi, GNews, ContextualWeb
* Экспорт результатов в CSV и PDF (поддержка Unicode благодаря шрифту DejaVuSans)
* Система профилей для хранения API‑ключей
* Фильтрация по диапазону дат
* Резервный поиск без ключей через Google News RSS
* Интерфейс на русском или английском

## Установка

```bash
pip install -r requirements.txt
```

Скачайте шрифт `DejaVuSans.ttf` и поместите его в `app/fonts/`.

## Запуск

```bash
streamlit run app/app.py
```
