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

COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")

if not COINBASE_API_KEY:
    print("\n🚨 WARNING: COINBASE_API_KEY is not set in the environment variables. Please add it to your Render dashboard.\n")

COINBASE_API_URL = "https://api.coinbase.com/v2/prices/{}/spot?currency=USD"

@app.route('/')
def index():
    print("Serving index.html")
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    print(f"Selected Coins Received: {selected_coins}")
    prices = {}

    headers = {
        "Authorization": f"Bearer {COINBASE_API_KEY}",
        "CB-VERSION": "2023-05-15"
    }

    for coin in selected_coins:
        symbol = COIN_SYMBOLS.get(coin)
        if not symbol:
            print(f"Coin not found in COIN_SYMBOLS: {coin}")
            continue
        try:
            print(f"Fetching price for {coin} ({symbol})")
            response = requests.get(COINBASE_API_URL.format(symbol), headers=headers)
            data = response.json()
            print(f"API Response for {coin}: {data}")
            current_price = float(data['data']['amount'])

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

            # Immediate data return for the first request
            if len(history["prices"]) == 1:
                print(f"Immediate data for {coin}: {prices[coin]}")

        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")

    # Force a flush to ensure data is sent immediately
    print("Sending immediate response")

    return jsonify({"prices": prices, "status": "success"})

@app.route('/top_risers', methods=['GET'])
def top_risers():
    try:
        headers = {
            "Authorization": f"Bearer {COINBASE_API_KEY}",
            "CB-VERSION": "2023-05-15"
        }
        response = requests.get("https://api.coinbase.com/v2/prices?currency=USD", headers=headers)
        data = response.json()
        top_risers = [f"{coin['base']}: ${coin['amount']}" for coin in data['data'][:3]]
        print(f"Top Risers: {top_risers}")
        return jsonify({"top_risers": top_risers})
    except Exception as e:
        print(f"Error fetching top risers: {e}")
        return jsonify({"top_risers": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
