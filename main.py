from flask import Flask
import asyncio
from gold_tracker import main as run_bot

app = Flask(__name__)

@app.route('/')
def index():
    asyncio.run(run_bot())
    return "Gold price checked and sent!"
