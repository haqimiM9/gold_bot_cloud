from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import datetime
from gold_tracker import get_gold_price, analyze_price

previous_prices = {
    "gram_24k": None,
    "gram_22k": None,
    "gram_21k": None
}

async def gold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = get_gold_price()

    if not current:
        await update.message.reply_text("❌ Failed to fetch gold price.")
        return

    timestamp = datetime.datetime.fromtimestamp(
        current["timestamp"],
        datetime.timezone(datetime.timedelta(hours=8))
    )

    message = (
        f"💰 Gold Price Alert (MYR) - {timestamp.strftime('%d %b %Y %I:%M %p')}\n"
        f"Spot Price: RM {current['price']:.2f}\n"
        f"999.9 (24K): RM {current['gram_24k']:.2f}/g\n"
        f"916 (22K): RM {current['gram_22k']:.2f}/g\n"
        f"21K: RM {current['gram_21k']:.2f}/g\n"
        f"\n📉 Price Change:"
    )

    for karat in ["gram_24k", "gram_22k", "gram_21k"]:
        current_value = current[karat]
        prev_value = previous_prices[karat]
        label = karat.replace("gram_", "").upper()
        if prev_value:
            diff = current_value - prev_value
            message += f"\n{label}: {diff:+.2f} MYR"
        else:
            message += f"\n{label}: No previous data"

    if previous_prices["gram_24k"]:
        signal, _ = analyze_price(current["gram_24k"], previous_prices["gram_24k"])
        message += f"\n\nSummary:\n{signal}"
    else:
        message += "\n\nSummary:\n📊 No previous data – Monitoring begins."

    for karat in previous_prices:
        previous_prices[karat] = current[karat]

    await update.message.reply_text(message)
