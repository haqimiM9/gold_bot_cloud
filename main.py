from telegram.ext import ApplicationBuilder, CommandHandler
from gold_tracker import handle_gold
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gold", handle_gold))
    app.run_polling()
