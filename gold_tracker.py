import requests
import datetime
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
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
        if "price" not in data:
            return None, data

        return {
            "price": data["price"],
            "gram_24k": data["price_gram_24k"],
            "gram_22k": data["price_gram_22k"],
            "gram_21k": data["price_gram_21k"],
            "timestamp": data["timestamp"]
        }, None
    except Exception as e:
        return None, str(e)

def analyze_price(current, previous):
    diff = current - previous
    percent = (diff / previous) * 100
    if percent >= 2.5:
        signal = "💸 Gold price increased {:.2f}% – Buy now!".format(percent)
    elif percent <= -2.5:
        signal = "🚫 Gold price dropped {:.2f}% – Wait for a better price.".format(percent)
    else:
        signal = "📊 Gold price stable – Hold off on buying."
    return signal, percent

async def gold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global previous_prices

    current, error = get_gold_price()
    if error or not current:
        await update.message.reply_text("❌ Failed to fetch gold price.\n" + str(error or current))
        return

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
            current_value = current[karat]
            prev_value = previous_prices[karat]
            change = current_value - prev_value
            label = karat.replace("gram_", "").upper()
            message += f"\n{label}: {change:+.2f} MYR"

        signal, percent = analyze_price(current["gram_24k"], previous_prices["gram_24k"])
        message += f"\n\nSummary:\n{signal}"
    else:
        message += "\nℹ️ No previous price data for comparison yet."

    for karat in previous_prices:
        previous_prices[karat] = current[karat]

    await update.message.reply_text(message)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gold", gold_command))
    print("🚀 Bot is running. Use /gold in Telegram to get prices.")
    app.run_polling()
