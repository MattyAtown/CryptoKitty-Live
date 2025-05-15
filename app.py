from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import os
import time
from collections import defaultdict, deque

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "LINK", "POL", "AERGO", "SUI"]

PRICE_HISTORY = defaultdict(lambda: {"prices": deque(maxlen=20), "timestamps": deque(maxlen=20), "percentage_changes": deque(maxlen=20)})

COIN_SYMBOLS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "polygon",
    "DOT": "polkadot",
    "POL": "polymath",
    "LINK": "chainlink",
    "AERGO": "aergo",
    "SUI": "sui"
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
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd")
            data = response.json()
            current_price = float(data[symbol]['usd'])

            # Update price history
            history = PRICE_HISTORY[coin]
            history["prices"].append(current_price)
            current_time = time.strftime('%H:%M:%S', time.gmtime())
            history["timestamps"].append(current_time)

            # Calculate percentage change based on the latest two points
            if len(history["prices"]) > 1:
                old_price = history["prices"][-2]
                percentage_change = ((current_price - old_price) / old_price) * 100
                history["percentage_changes"].append(round(percentage_change, 2))
            else:
                history["percentage_changes"].append(0.0)

            # Build the response data
            prices[coin] = {
                "price": current_price,
                "change": round(history["percentage_changes"][-1], 2),
                "timestamps": list(history["timestamps"]),
                "prices": list(history["prices"]),
                "percentage_changes": list(history["percentage_changes"])
            }
        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")

    return jsonify({"prices": prices, "status": "success"})

@app.route('/top_risers', methods=['GET'])
def top_risers():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={"vs_currency": "usd", "order": "percent_change_24h_desc", "per_page": 3, "page": 1})
        data = response.json()
        top_risers = [f"{coin['symbol'].upper()}: +{coin['price_change_percentage_24h']}%" for coin in data[:3]]
        return jsonify({"top_risers": top_risers})
    except Exception as e:
        print(f"Error fetching top risers: {e}")
        return jsonify({"top_risers": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
