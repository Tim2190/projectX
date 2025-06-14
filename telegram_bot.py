import os
import asyncio
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from projectX.search_engine import SearchEngine

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://projectx-uxr4.onrender.com/webhook"
PORT = int(os.getenv("PORT", "10000"))

search_engine = SearchEngine()
user_keywords = {}
sent_urls = set()

# --- Команды Telegram ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_keywords.setdefault(user_id, set())
    await update.message.reply_text("Бот запущен. Используйте /subscribe, /unsubscribe и /list.")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    keywords = user_keywords.setdefault(user_id, set())
    if not context.args:
        await update.message.reply_text("Укажите ключевые слова через пробел")
        return
    for kw in context.args:
        if len(keywords) >= 5 and kw not in keywords:
            await update.message.reply_text("Можно подписаться максимум на 5 ключевых слов")
            return
        keywords.add(kw)
    await update.message.reply_text("Текущие: " + ", ".join(keywords))

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    keywords = user_keywords.setdefault(user_id, set())
    if not context.args:
        keywords.clear()
        await update.message.reply_text("Все подписки удалены")
        return
    for kw in context.args:
        keywords.discard(kw)
    await update.message.reply_text("Текущие: " + ", ".join(keywords))

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    keywords = user_keywords.get(user_id, set())
    if keywords:
        await update.message.reply_text("Подписки: " + ", ".join(keywords))
    else:
        await update.message.reply_text("Нет активных подписок")

# --- Отправка новостей ---

async def send_updates():
    for user_id, keywords in user_keywords.items():
        for kw in keywords:
            results = search_engine.search(kw)
            for item in results:
                url = item.get("url")
                if url and url not in sent_urls:
                    sent_urls.add(url)
                    title = item.get("title", url)
                    await app.bot.send_message(chat_id=user_id, text=f"{title}\n{url}")

# --- Обработка webhook Telegram ---

async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="ok")

# --- Периодическая проверка ---

async def periodic_checker():
    while True:
        await send_updates()
        await asyncio.sleep(300)

# --- Основная точка запуска ---

async def run():
    global app
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("list", list_cmd))

    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("subscribe", "Подписаться на ключевые слова (до 5)"),
        BotCommand("unsubscribe", "Отписаться от одного или всех ключевых слов"),
        BotCommand("list", "Показать текущие подписки"),
    ])

    await app.bot.set_webhook(WEBHOOK_URL)

    web_app = web.Application()
    web_app.add_routes([web.post("/webhook", handle_webhook)])

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    asyncio.create_task(periodic_checker())
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
