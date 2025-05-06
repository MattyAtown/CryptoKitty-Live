from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT"]
PRICE_HISTORY = defaultdict(list)
TRENDS = {}
NEWS_HEADLINES = [
    "Bitcoin hits new high amid ETF optimism",
    "Ethereum upgrade causes network surge",
    "Market reacts to inflation data"
]

COIN_SYMBOLS = {
    "BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD",
    "SOL": "SOL-USD", "ADA": "ADA-USD", "DOGE": "DOGE-USD",
    "MATIC": "MATIC-USD", "DOT": "DOT-USD"
}

def fetch_price(coin):
    try:
        symbol = COIN_SYMBOLS.get(coin)
        url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
        response = requests.get(url)
        data = response.json()
        return round(float(data['data']['amount']), 2)
    except:
        return None

def get_trend(prices):
    if len(prices) < 3:
        return "Stable"
    if prices[-1] < prices[-2] < prices[-3]:
        return "WARNING"
    elif prices[-1] > prices[-2] > prices[-3]:
        return "RISER"
    else:
        return "Stable"

@app.route("/", methods=["GET", "POST"])
def index():
    selected = []
    time_range = "1h"
    if request.method == "POST":
        coins = request.form.get("coins", "")
        selected = coins.split(",") if coins else []
        time_range = request.form.get("time_range", "1h")

    prices = {}
    for coin in selected:
        price = fetch_price(coin)
        if price is not None:
            prices[coin] = price
            PRICE_HISTORY[coin].append(price)
            PRICE_HISTORY[coin] = PRICE_HISTORY[coin][-30:]
        else:
            prices[coin] = "N/A"

    for coin in selected:
        TRENDS[coin] = get_trend(PRICE_HISTORY[coin])

    top_risers = {}
    for coin in selected:
        history = PRICE_HISTORY[coin][-6:]
        if len(history) >= 2 and history[0] != 0:
            diff = ((history[-1] - history[0]) / history[0]) * 100
            top_risers[coin] = f"{diff:.2f}%"

    return render_template(
        "index.html",
        coins=COINS,
        selected=selected,
        prices=prices,
        price_history=PRICE_HISTORY,
        trends=TRENDS,
        top_risers=top_risers,
        news_headlines=NEWS_HEADLINES,
        time_range=time_range
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
