import os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from projectX.search_engine import SearchEngine

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env variable not set")

# Хранилище подписок и отправленных ссылок
user_keywords: dict[int, set[str]] = {}
sent_urls = set()
search_engine = SearchEngine()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот запущен. Используйте команды:\n/subscribe — добавить ключевые слова\n/unsubscribe — удалить\n/list — посмотреть подписки"
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Укажите ключевые слова через пробел")
        return

    kws = user_keywords.setdefault(chat_id, set())
    for kw in context.args:
        if len(kws) >= 5 and kw not in kws:
            await update.message.reply_text("Можно подписаться максимум на 5 ключевых слов")
            break
        kws.add(kw.lower())
    await update.message.reply_text("Текущие подписки: " + ", ".join(kws))


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    kws = user_keywords.setdefault(chat_id, set())

    if not context.args:
        kws.clear()
        await update.message.reply_text("Все подписки удалены")
        return

    for kw in context.args:
        kws.discard(kw.lower())
    await update.message.reply_text("Текущие подписки: " + ", ".join(kws))


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    kws = user_keywords.get(chat_id, set())
    if kws:
        await update.message.reply_text("Ваши подписки: " + ", ".join(kws))
    else:
        await update.message.reply_text("Нет активных подписок")


async def send_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    for chat_id, kws in user_keywords.items():
        for kw in kws:
            results = search_engine.search(kw)
            for item in results:
                url = item.get("url")
                if url and url not in sent_urls:
                    sent_urls.add(url)
                    title = item.get("title", url)
                    await context.bot.send_message(chat_id=chat_id, text=f"{title}\n{url}")


async def post_init(app: Application) -> None:
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("subscribe", "Подписаться на ключевые слова (до 5)"),
        BotCommand("unsubscribe", "Отписаться от одного или всех ключевых слов"),
        BotCommand("list", "Показать текущие подписки"),
    ]
    await app.bot.set_my_commands(commands)


def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list_cmd))

    # Каждые 5 минут запускаем проверку новых новостей
    application.job_queue.run_repeating(send_updates, interval=300, first=5)

    application.run_polling()


if __name__ == "__main__":
    main()
