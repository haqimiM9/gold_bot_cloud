import requests
import datetime
import os
from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GOLD_API_KEY = os.environ["GOLD_API_KEY"]
GOLD_API_URL = "https://www.goldapi.io/api/XAU/MYR"

headers = {"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
previous_prices = {
    "gram_24k": None,
    "gram_22k": None,
    "gram_21k": None
}

def get_gold_price():
    try:
        response = requests.get(GOLD_API_URL, headers=headers)
        data = response.json()
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

def analyze_price(current, previous):
    diff = current - previous
    percent = (diff / previous) * 100
    if percent >= 2.5:
        signal = f"💸 Gold price increased {percent:.2f}% – Buy now!"
    elif percent <= -2.5:
        signal = f"🚫 Gold price dropped {percent:.2f}% – Wait for a better price."
    else:
        signal = "📊 Gold price stable – Hold off on buying."
    return signal, percent

def build_gold_message():
    global previous_prices
    current = get_gold_price()
    if not current:
        return "❌ Failed to fetch gold price."

    timestamp_human = datetime.datetime.fromtimestamp(current["timestamp"], datetime.timezone(datetime.timedelta(hours=8)))
    message = (
        f"💰 Gold Price Alert (MYR) - {timestamp_human.strftime('%d %b %Y %I:%M %p')}\n"
        f"Spot Price: RM {current['price']:.2f}\n"
        f"999.9 (24K): RM {current['gram_24k']:.2f}/g\n"
        f"916 (22K): RM {current['gram_22k']:.2f}/g\n"
        f"21K: RM {current['gram_21k']:.2f}/g\n"
    )

    if all(previous_prices.values()):
        message += "\n\n📉 Price Change:"
        for karat in ["gram_24k", "gram_22k", "gram_21k"]:
            change = current[karat] - previous_prices[karat]
            label = karat.replace("gram_", "") + "K"
            message += f"\n{label}: {change:+.2f} MYR"

        signal, _ = analyze_price(current["gram_24k"], previous_prices["gram_24k"])
        message += f"\n\nSummary:\n{signal}"
    else:
        message += "\nℹ️ No previous price data for comparison yet."

    previous_prices.update({
        "gram_24k": current["gram_24k"],
        "gram_22k": current["gram_22k"],
        "gram_21k": current["gram_21k"]
    })

    return message

# === Telegram Command Handler ===
async def handle_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = build_gold_message()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# === For Flask-based manual run ===
async def main():
    bot = Bot(token=BOT_TOKEN)
    message = build_gold_message()
    await bot.send_message(chat_id=CHAT_ID, text=message)
