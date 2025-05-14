from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "POL", "LINK", "AERGO", "SUI"]

PRICE_HISTORY = defaultdict(lambda: {"prices": [], "timestamps": []})

COIN_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "XRP": "XRP-USD",
    "SOL": "SOL-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "MATIC": "MATIC-USD",
    "DOT": "DOT-USD",
    "POL": "POL-USD",
    "LINK": "LINK-USD",
    "AERGO": "AERGO-USD",
    "SUI": "SUI-USD"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    prices = {}

    for coin in selected_coins:
        symbol = COIN_SYMBOLS.get(coin)
        if not symbol:
            continue
        try:
            response = requests.get(f"https://api.exchange.coinbase.com/products/{symbol}/ticker")
            data = response.json()
            current_price = float(data['price'])

            # Update price history
            history = PRICE_HISTORY[coin]
            history["prices"].append(current_price)
            history["timestamps"].append(data['time'])

            # Limit history to last 20 data points
            if len(history["prices"]) > 20:
                history["prices"].pop(0)
                history["timestamps"].pop(0)

            # Calculate percentage change
            if len(history["prices"]) > 1:
                old_price = history["prices"][0]
                percentage_change = ((current_price - old_price) / old_price) * 100
            else:
                percentage_change = 0.0

            prices[coin] = {
                "price": current_price,
                "change": round(percentage_change, 2),
                "timestamps": history["timestamps"],
                "prices": history["prices"]
            }
        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")

    return jsonify({"prices": prices})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
