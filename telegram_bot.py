import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from projectX.search_engine import SearchEngine
from aiohttp import web

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))

search_engine = SearchEngine()
user_keywords = set()
sent_urls = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот запущен. Используйте /subscribe, /unsubscribe и /list."
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Укажите ключевые слова через пробел")
        return
    for kw in context.args:
        if len(user_keywords) >= 5 and kw not in user_keywords:
            await update.message.reply_text(
                "Можно подписаться максимум на 5 ключевых слов"
            )
            break
        user_keywords.add(kw)
    await update.message.reply_text("Текущие: " + ", ".join(user_keywords))


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        user_keywords.clear()
        await update.message.reply_text("Все подписки удалены")
        return
    for kw in context.args:
        user_keywords.discard(kw)
    await update.message.reply_text("Текущие: " + ", ".join(user_keywords))


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if user_keywords:
        await update.message.reply_text("Подписки: " + ", ".join(user_keywords))
    else:
        await update.message.reply_text("Нет активных подписок")


async def send_updates():
    for kw in user_keywords:
        results = search_engine.search(kw)
        for item in results:
            url = item.get("url")
            if url and url not in sent_urls:
                sent_urls.add(url)
                title = item.get("title", url)
                for user_id in search_engine.subscribers:
                    await search_engine.bot.send_message(chat_id=user_id, text=f"{title}\n{url}")


async def periodic_checker():
    while True:
        await send_updates()
        await asyncio.sleep(300)  # каждые 5 минут


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

    asyncio.create_task(application.initialize())
    asyncio.create_task(application.start())
    asyncio.create_task(periodic_checker())

    app = web.Application()
    app.add_routes([web.get('/trigger', handle_trigger)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
