import os
import asyncio
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from projectX.search_engine import SearchEngine

# Получение переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

# Инициализация
search_engine = SearchEngine()
user_keywords_map = {}       # user_id -> set of keywords
sent_urls_map = {}           # user_id -> set of urls
waiting_for_keywords = set()  # user_ids ожидающие ввода ключевых слов после /subscribe
waiting_for_unsubscribe = {}  # user_id -> set of keywords, если ожидается удаление

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот запущен. Используйте /subscribe, /unsubscribe и /list."
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    waiting_for_keywords.add(user_id)
    await update.message.reply_text("Введите ключевые слова через запятую.")

async def handle_keywords_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in waiting_for_keywords:
        keywords = [kw.strip() for kw in update.message.text.split(",") if kw.strip()]
        if user_id not in user_keywords_map:
            user_keywords_map[user_id] = set()
        added = []
        for kw in keywords:
            if kw and (len(user_keywords_map[user_id]) < 5 or kw in user_keywords_map[user_id]):
                user_keywords_map[user_id].add(kw)
                added.append(kw)
        waiting_for_keywords.discard(user_id)
        await update.message.reply_text("Добавлены: " + ", ".join(added))

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    kws = user_keywords_map.get(user_id)
    if not kws:
        return await update.message.reply_text("Нет активных подписок")

    waiting_for_unsubscribe[user_id] = kws.copy()
    message = "У вас следующие подписки:\n" + "\n".join(f"- {kw}" for kw in kws)
    message += "\n\nНапишите слово для удаления или 'все' для полной отписки."
    await update.message.reply_text(message)

async def handle_unsubscribe_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in waiting_for_unsubscribe:
        kws = user_keywords_map.get(user_id, set())
        msg = update.message.text.strip()
        if msg.lower() == "все":
            kws.clear()
            waiting_for_unsubscribe.pop(user_id, None)
            return await update.message.reply_text("Все подписки удалены")
        elif msg in kws:
            kws.remove(msg)
            waiting_for_unsubscribe.pop(user_id, None)
            return await update.message.reply_text(f"Удалено: {msg}\nОсталось: " + ", ".join(kws))
        else:
            return await update.message.reply_text("Такого слова нет в списке подписок. Попробуйте снова.")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    kws = user_keywords_map.get(user_id, set())
    if kws:
        await update.message.reply_text("Подписки: " + ", ".join(kws))
    else:
        await update.message.reply_text("Нет активных подписок")

# Обработка всех текстовых сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in waiting_for_keywords:
        await handle_keywords_input(update, context)
    elif user_id in waiting_for_unsubscribe:
        await handle_unsubscribe_input(update, context)

# Отправка новостей
async def send_updates():
    for user_id, keywords in user_keywords_map.items():
        print(f"[BOT] Пользователь: {user_id}")
        print(f"[BOT] Ключевые слова: {keywords}")

        if user_id not in sent_urls_map:
            sent_urls_map[user_id] = set()

        for kw in keywords:
            print(f"[SEARCH] Ищу по ключу: {kw}")
            results = search_engine.search(kw)

            print(f"[SEARCH] Найдено новостей: {len(results)}")

            for item in results:
                url = item.get("url")
                if url and url not in sent_urls_map[user_id]:
                    sent_urls_map[user_id].add(url)
                    title = item.get("title", url)
                    try:
                        print(f"[SEND] Отправка: {title}")
                        await application.bot.send_message(chat_id=user_id, text=f"{title}\n{url}")
                    except Exception as e:
                        print(f"[ERROR] Не удалось отправить сообщение: {e}")

# Ручной запуск обновлений через /trigger
async def handle_trigger(request):
    await send_updates()
    return web.Response(text="Manual trigger completed.")

# Обработка Webhook (Telegram POST)
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="ok")

# Регулярная проверка каждые 5 минут
async def periodic_checker():
    while True:
        await send_updates()
        await asyncio.sleep(300)

# Главная функция
async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("list", list_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await application.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("subscribe", "Подписаться на ключевые слова (до 5)"),
        BotCommand("unsubscribe", "Отписаться от одного или всех ключевых слов"),
        BotCommand("list", "Показать текущие подписки"),
    ])

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(WEBHOOK_URL)

    # Периодический запуск
    asyncio.create_task(periodic_checker())

    # HTTP сервер
    app = web.Application()
    app.add_routes([
        web.post('/webhook', handle_webhook),
        web.get('/trigger', handle_trigger)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
