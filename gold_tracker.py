from flask import Flask, request
import requests
import datetime
import asyncio
import os
from telegram import Bot

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GOLD_API_KEY = os.environ["GOLD_API_KEY"]
GOLD_API_URL = "https://www.goldapi.io/api/XAU/MYR"

headers = {"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
previous_price = None

async def send_telegram_alert(message):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def get_gold_price():
    try:
        response = requests.get(GOLD_API_URL, headers=headers)
        data = response.json()
        print("DEBUG API Response:", data)
        return {
            "price": data["price"],
            "gram_24k": data["price_gram_24k"],
            "gram_22k": data["price_gram_22k"],
            "gram_21k": data["price_gram_21k"],
            "timestamp": data["timestamp"]
        }
    except Exception as e:
        print("ERROR:", e)
        return None

async def run_check():
    global previous_price
    current = get_gold_price()
    if current:
        message = (
            f"🟡 Gold Price Update (MYR)\n"
            f"Spot Price: RM {current['price']:.2f}\n"
            f"999.9 (24K): RM {current['gram_24k']:.2f}/g\n"
            f"916 (22K): RM {current['gram_22k']:.2f}/g\n"
            f"21K: RM {current['gram_21k']:.2f}/g\n"
        )
        if previous_price and current['price'] != previous_price:
            change = current['price'] - previous_price
            message += f"\n📈 Change: RM {change:+.2f}"
        previous_price = current['price']
        await send_telegram_alert(message)
    else:
        await send_telegram_alert("❌ Failed to fetch gold price.")

@app.route("/", methods=["GET"])
def index():
    asyncio.run(run_check())
    return "Gold price alert sent.", 200
