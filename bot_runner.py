# bot_runner.py

import os
from telegram.ext import Application
from bot_handler import gold_command
from telegram.ext import CommandHandler

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("gold", gold_command))

    print("Bot is running. Send /gold to your bot.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
