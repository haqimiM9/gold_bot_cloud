from telegram.ext import Application, CommandHandler
import os
from bot_handler import handle_gold

BOT_TOKEN = os.environ["BOT_TOKEN"]

def main():
    # Create the application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handler
    app.add_handler(CommandHandler("gold", handle_gold))

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
