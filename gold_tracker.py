import requests
import datetime
import asyncio
import os
from telegram import Bot

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

def analyze_price(current_price, previous_price):
    if previous_price is None:
        return "No previous data to analyze."
    change = current_price - previous_price
    if change > 0:
        return f"The gold price has increased by RM {change:.2f}. It is not a good time to buy."
    elif change < 0:
        return f"The gold price has decreased by RM {change:.2f}. It is a good time to buy."
    else:
        return "The gold price has not changed."

async def main():
    global previous_price
    current = get_gold_price()
    if current:
        today = datetime.date.today()
        signal = "✨" if current["price"] > previous_price else "❗️"
        msg = f"📅 {today.strftime('%d/%m/%Y')} {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%H:%M')} (Asia/Kuala_Lumpur)\n{signal}\n"
        message = (
            f"{msg}"
            f"🟡 Gold Price Alert (MYR)\n"
            f"Spot Price: RM {current['price']:.2f}\n"
            f"999.9 (24K): RM {current['gram_24k']:.2f}/g\n"
            f"916 (22K): RM {current['gram_22k']:.2f}/g\n"
            f"21K: RM {current['gram_21k']:.2f}/g\n"
        )
        if previous_price and current['price'] != previous_price:
            change = current['price'] - previous_price
            message += f"\n📈 Change: RM {change:+.2f}"
        
        analysis = analyze_price(current['price'], previous_price)
        message += f"\n\n🔍 Analysis: {analysis}"

        previous_price = current['price']
        await send_telegram_alert(message)
    else:
        await send_telegram_alert("❌ Failed to fetch gold price.")

