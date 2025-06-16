from flask import Flask
import asyncio
from gold_tracker import main as run_bot  # your existing function from another file

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Gold Bot is running!"

@app.route("/run", methods=["GET"])
def trigger_bot():
    asyncio.run(run_bot())  # calls your original code
    return "📬 Bot executed."