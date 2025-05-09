from flask import Flask, render_template, jsonify, request
import requests
from collections import defaultdict

app = Flask(__name__)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT"]
PRICE_HISTORY = defaultdict(list)

COIN_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "XRP": "XRP-USD",
    "SOL": "SOL-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "MATIC": "MATIC-USD",
    "DOT": "DOT-USD"
}

def fetch_price(coin):
    try:
        symbol = COIN_SYMBOLS.get(coin)
        url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
        response = requests.get(url)
        data = response.json()
        price = float(data['data']['amount'])
        PRICE_HISTORY[coin].append(price)
        PRICE_HISTORY[coin] = PRICE_HISTORY[coin][-10:]  # Keep only the last 10 prices
        return price
    except Exception as e:
        print(f"Error fetching price for {coin}: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    selected = request.form.get("coins", "").split(",") if request.method == "POST" else COINS
    prices = {coin: fetch_price(coin) for coin in selected}
    
    # Determine trends
    trends = {}
    for coin in selected:
        history = PRICE_HISTORY.get(coin, [])
        if len(history) >= 3:
            if history[-1] > history[-2] > history[-3]:
                trends[coin] = "Riser"
            elif history[-1] < history[-2] < history[-3]:
                trends[coin] = "Warning"
            else:
                trends[coin] = "Stable"
        else:
            trends[coin] = "Stable"
    
    # Calculate top risers
    top_risers = {}
    for coin, history in PRICE_HISTORY.items():
        if len(history) > 1:
            gain = ((history[-1] - history[0]) / history[0]) * 100
            top_risers[coin] = f"{gain:.2f}%"

    return render_template(
        "index.html",
        coins=COINS,
        selected=selected,
        prices=prices,
        trends=trends,
        price_history=PRICE_HISTORY,
        top_risers=top_risers
    )

@app.route("/api/prices", methods=["GET"])
def get_prices():
    prices = {coin: fetch_price(coin) for coin in COINS}
    return jsonify(prices)

@app.route("/api/price-history", methods=["GET"])
def get_price_history():
    return jsonify(PRICE_HISTORY)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
