import os
import datetime
import asyncio
from typing import Optional
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from projectX.search_engine import SearchEngine
from projectX.event_clustering import cluster_events
from projectX.report_utils import summarize_news


def run_monitoring(keyword: str, date_from: Optional[str], date_to: Optional[str]) -> str:
token = os.getenv('TELEGRAM_TOKEN')
webhook_url = os.getenv('WEBHOOK_URL')

if not token:
    raise RuntimeError('TELEGRAM_TOKEN env variable not set')
if not webhook_url:
    raise RuntimeError('WEBHOOK_URL env variable not set')

app = Flask(__name__)
application = Application.builder().token(token).build()
application.add_handler(CommandHandler('анализ', analyze))

@app.route('/webhook', methods=['POST'])
def webhook() -> tuple[str, int]:
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return 'ok', 200


def main() -> None:
    application.bot.set_webhook(webhook_url)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

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
