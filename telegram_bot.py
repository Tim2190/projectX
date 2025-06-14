import os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from projectX.search_engine import SearchEngine

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("SUBSCRIBER_CHAT_ID")
KEYWORDS = {k.strip() for k in os.getenv("KEYWORDS", "news,technology").split(',') if k.strip()}

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env variable not set")
if not CHAT_ID:
    raise RuntimeError("SUBSCRIBER_CHAT_ID env variable not set")

search_engine = SearchEngine()
sent_urls = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "Бот запущен. Используйте /subscribe, /unsubscribe и /list."
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Subscribe to new keywords."""
    if not context.args:
        await update.message.reply_text("Укажите ключевые слова через пробел")
        return
    for kw in context.args:
        if len(KEYWORDS) >= 5 and kw not in KEYWORDS:
            await update.message.reply_text(
                "Можно подписаться максимум на 5 ключевых слов"
            )
            break
        KEYWORDS.add(kw)
    await update.message.reply_text("Текущие: " + ", ".join(KEYWORDS))


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unsubscribe from keywords."""
    if not context.args:
        KEYWORDS.clear()
        await update.message.reply_text("Все подписки удалены")
        return
    for kw in context.args:
        KEYWORDS.discard(kw)
    await update.message.reply_text("Текущие: " + ", ".join(KEYWORDS))


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List current keywords."""
    if KEYWORDS:
        await update.message.reply_text("Подписки: " + ", ".join(KEYWORDS))
    else:
        await update.message.reply_text("Нет активных подписок")


async def send_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    for kw in KEYWORDS:
        results = search_engine.search(kw)
        for item in results:
            url = item.get("url")
            if url and url not in sent_urls:
                sent_urls.add(url)
                title = item.get("title", url)
                await context.bot.send_message(chat_id=CHAT_ID, text=f"{title}\n{url}")


async def post_init(app: Application) -> None:
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("subscribe", "Подписаться на ключевые слова (до 5)"),
        BotCommand("unsubscribe", "Отписаться от одного или всех ключевых слов"),
        BotCommand("list", "Показать текущие подписки"),
    ]
    await app.bot.set_my_commands(commands)


def main() -> None:
    application = (
        Application.builder().token(TOKEN).post_init(post_init).build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list_cmd))
    application.job_queue.run_repeating(send_updates, interval=300, first=0)
    application.run_polling()


if __name__ == "__main__":
    main()
