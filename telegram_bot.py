import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from projectX.search_engine import SearchEngine
from aiohttp import web

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))

search_engine = SearchEngine()
user_keywords_map = {}  # user_id -> set of keywords
sent_urls_map = {}      # user_id -> set of urls


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот запущен. Используйте /subscribe, /unsubscribe и /list."
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_keywords_map:
        user_keywords_map[user_id] = set()

    if not context.args:
        await update.message.reply_text("Укажите ключевые слова через пробел")
        return

    added = []
    for kw in context.args:
        if len(user_keywords_map[user_id]) < 5 or kw in user_keywords_map[user_id]:
            user_keywords_map[user_id].add(kw)
            added.append(kw)

    await update.message.reply_text("Добавлены: " + ", ".join(added))


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_keywords_map:
        return await update.message.reply_text("Нет активных подписок")

    if not context.args:
        user_keywords_map[user_id].clear()
        return await update.message.reply_text("Все подписки удалены")

    for kw in context.args:
        user_keywords_map[user_id].discard(kw)
    await update.message.reply_text("Текущие: " + ", ".join(user_keywords_map[user_id]))


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    kws = user_keywords_map.get(user_id, set())
    if kws:
        await update.message.reply_text("Подписки: " + ", ".join(kws))
    else:
        await update.message.reply_text("Нет активных подписок")


async def send_updates():
    for user_id, keywords in user_keywords_map.items():
        if user_id not in sent_urls_map:
            sent_urls_map[user_id] = set()
        for kw in keywords:
            results = search_engine.search(kw)
            for item in results:
                url = item.get("url")
                if url and url not in sent_urls_map[user_id]:
                    sent_urls_map[user_id].add(url)
                    title = item.get("title", url)
                    try:
                        await search_engine.bot.send_message(chat_id=user_id, text=f"{title}\n{url}")
                    except Exception:
                        pass


async def periodic_checker():
    while True:
        await send_updates()
        await asyncio.sleep(300)


async def handle_trigger(request):
    await send_updates()
    return web.Response(text="Manual trigger completed.")


async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list_cmd))

    await application.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("subscribe", "Подписаться на ключевые слова (до 5)"),
        BotCommand("unsubscribe", "Отписаться от одного или всех ключевых слов"),
        BotCommand("list", "Показать текущие подписки"),
    ])

    await application.initialize()
    await application.start()

    asyncio.create_task(periodic_checker())

    app = web.Application()
    app.add_routes([web.get('/trigger', handle_trigger)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await application.updater.start_polling()  # fallback polling (если нужен)
    await application.running.wait()


if __name__ == "__main__":
    asyncio.run(main())
