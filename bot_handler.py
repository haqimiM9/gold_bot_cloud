from telegram import Update
from telegram.ext import ContextTypes
from gold_tracker import get_gold_price, analyze_price

previous_prices = {
    "gram_24k": None,
    "gram_22k": None,
    "gram_21k": None
}

async def handle_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = get_gold_price()
    if not current:
        await update.message.reply_text("❌ Failed to fetch gold price.")
        return

    message = (
        f"💰 Gold Price Alert (MYR)\n"
        f"Spot Price: RM {current['price']:.2f}\n"
        f"999.9 (24K): RM {current['gram_24k']:.2f}/g\n"
        f"916 (22K): RM {current['gram_22k']:.2f}/g\n"
        f"21K: RM {current['gram_21k']:.2f}/g\n"
    )

    # Always show analysis
    if previous_prices["gram_24k"]:
        signal, _ = analyze_price(current["gram_24k"], previous_prices["gram_24k"])
    else:
        signal, _ = analyze_price(current["gram_24k"], current["gram_24k"])

    message += f"\n\nSummary:\n{signal}"

    # Update for next round
    for k in previous_prices:
        previous_prices[k] = current[k]

    await update.message.reply_text(message)
