import os
import datetime
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from projectX.search_engine import SearchEngine
from projectX.event_clustering import cluster_events
from projectX.report_utils import summarize_news


def run_monitoring(keyword: str, date_from: Optional[str], date_to: Optional[str]) -> str:
    from projectX.search_engine import SearchEngine  # импорт только при вызове
    se = SearchEngine()
    results = se.search(keyword, date_from, date_to)
    events = cluster_events(results)
    summary = summarize_news(events)
    return summary or 'Нет результатов'


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text(
            'Использование: /анализ ключевое_слово [дата_с] [дата_по]')
        return

    keyword = args[0]
    date_from = args[1] if len(args) >= 2 else None
    date_to = args[2] if len(args) >= 3 else None

    if not date_from and not date_to:
        today = datetime.date.today()
        date_to = today.isoformat()
        date_from = (today - datetime.timedelta(days=7)).isoformat()

    loop = asyncio.get_running_loop()
    summary = await loop.run_in_executor(
        None, run_monitoring, keyword, date_from, date_to)
    await update.message.reply_text(summary)


def main() -> None:
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise RuntimeError('TELEGRAM_TOKEN env variable not set')

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('analyze', analyze))
    app.run_polling()


if __name__ == '__main__':
    main()
