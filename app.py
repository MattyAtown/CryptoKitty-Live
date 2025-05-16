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

COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")

if not COINBASE_API_KEY:
    print("\n🚨 WARNING: COINBASE_API_KEY is not set in the environment variables. Please add it to your Render dashboard.\n")

COINBASE_API_URL = "https://api.coinbase.com/v2/prices/{}/spot?currency=USD"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd"

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
            # Attempt Coinbase first
            response = requests.get(COINBASE_API_URL.format(coin), headers=headers)
            data = response.json()
            current_price = float(data['data']['amount'])

        except Exception as e:
            print(f"Coinbase failed for {coin}, falling back to CoinGecko: {e}")
            try:
                # Fallback to CoinGecko if Coinbase fails
                response = requests.get(COINGECKO_API_URL.format(symbol))
                data = response.json()
                current_price = float(data[symbol]['usd'])
            except Exception as gecko_error:
                print(f"CoinGecko failed for {coin}: {gecko_error}")
                continue

        # Update price history
        history = PRICE_HISTORY[coin]
        history["prices"].append(current_price)
        current_time = time.strftime('%H:%M:%S', time.gmtime())
        history["timestamps"].append(current_time)

        # Calculate percentage change based on the last known price
        if len(history["prices"]) > 1:
            previous_price = history["prices"][-2]
            percentage_change = ((current_price - previous_price) / previous_price) * 100
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

        print(f"Data for {coin}: {prices[coin]}\n")

    print("Sending immediate response\n")

    return jsonify({"prices": prices, "status": "success"})

@app.route('/top_risers', methods=['GET'])
def top_risers():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=3&page=1&sparkline=false")
        data = response.json()
        top_risers = [f"{coin['name']}: ${coin['current_price']}" for coin in data]
        print(f"Top Risers: {top_risers}\n")
        return jsonify({"top_risers": top_risers})
    except Exception as e:
        print(f"Error fetching top risers: {e}\n")
        return jsonify({"top_risers": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
