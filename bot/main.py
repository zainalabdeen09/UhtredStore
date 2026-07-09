from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN
from bot.handlers import get_handlers


def run_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    for handler in get_handlers():
        app.add_handler(handler)

    print("Bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    run_bot()
