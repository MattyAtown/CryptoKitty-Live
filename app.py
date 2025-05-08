from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT"]
PRICE_HISTORY = defaultdict(list)
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

# Fetch live prices from Coinbase
def fetch_price(coin):
    try:
        symbol = COIN_SYMBOLS.get(coin)
        url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
        response = requests.get(url)
        data = response.json()
        return round(float(data['data']['amount']), 2)
    except Exception as e:
        print(f"Error fetching price for {coin}: {e}")
        return None

# Determine trend based on recent prices
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
    if request.method == "POST":
        coins = request.form.get("coins", "")
        selected = coins.split(",") if coins else []

    prices = {}
    price_history = {}
    for coin in selected:
        price = fetch_price(coin)
        if price is not None:
            prices[coin] = price
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            PRICE_HISTORY[coin].append((timestamp, price))
            PRICE_HISTORY[coin] = PRICE_HISTORY[coin][-100:]
            price_history[coin] = [p[1] for p in PRICE_HISTORY[coin]]
        else:
            prices[coin] = "N/A"

    # Determine trends
    trends = {coin: get_trend(price_history.get(coin, [])) for coin in selected}

    # Calculate top risers
    top_risers = {}
    for coin in selected:
        history = price_history.get(coin, [])
        if len(history) >= 2 and history[0] != 0:
            diff = ((history[-1] - history[0]) / history[0]) * 100
            top_risers[coin] = f"{diff:.2f}%"

    return render_template(
        "index.html",
        coins=COINS,
        selected=selected,
        prices=prices,
        price_history=price_history,
        trends=trends,
        top_risers=top_risers,
        news_headlines=NEWS_HEADLINES
    )

@app.route("/api/prices")
def prices_api():
    current_prices = {}
    for coin in COINS:
        price = fetch_price(coin)
        current_prices[coin] = price if price is not None else "N/A"
    return jsonify(current_prices)

@app.route("/api/price-history")
def price_history_api():
    simplified_history = {
        coin: [entry[1] for entry in history]
        for coin, history in PRICE_HISTORY.items()
    }
    return jsonify(simplified_history)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
