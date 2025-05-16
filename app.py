from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import os
import time
from collections import defaultdict, deque

app = Flask(__name__)
CORS(app)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "LINK", "POL", "AERGO", "SUI"]

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

COIN_LORE_IDS = {
    "bitcoin": 90,
    "ethereum": 80,
    "ripple": 58,
    "solana": 48543,
    "cardano": 257,
    "dogecoin": 2,
    "polygon": 3635,
    "polkadot": 4637,
    "polymath": 265,
    "chainlink": 1975,
    "aergo": 1656,
    "sui": 24074
}

API_URLS = [
    # CoinGecko
    "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd",
    # CoinCap
    "https://api.coincap.io/v2/assets/{}",
    # CoinLore
    "https://api.coinlore.net/api/ticker/?id={}"
]

PRICE_HISTORY = defaultdict(lambda: {"prices": deque(maxlen=20), "timestamps": deque(maxlen=20), "percentage_changes": deque(maxlen=20)})

def fetch_price(coin):
    symbol = COIN_SYMBOLS.get(coin.lower())
    if not symbol:
        print(f"⚠️ Coin not found in COIN_SYMBOLS: {coin}")
        return None

    for url in API_URLS:
        try:
            if "coingecko" in url:
                response = requests.get(url.format(symbol), timeout=5)
                data = response.json()
                print(f"🟢 CoinGecko Response ({symbol}):", data)
                return float(data[symbol]['usd'])

            elif "coincap" in url:
                response = requests.get(url.format(symbol), timeout=5)
                data = response.json()
                print(f"🟢 CoinCap Response ({symbol}):", data)
                return float(data['data']['priceUsd'])

            elif "coinlore" in url:
                coin_id = COIN_LORE_IDS.get(symbol)
                if not coin_id:
                    print(f"⚠️ No CoinLore ID for {symbol}")
                    continue
                response = requests.get(url.format(coin_id), timeout=5)
                data = response.json()[0]
                print(f"🟢 CoinLore Response ({symbol}):", data)
                return float(data['price_usd'])

        except Exception as e:
            print(f"🔴 Error fetching price from {url} for {coin}: {e}")

    print(f"🔴 Failed to fetch price for {coin} from all sources.")
    return None

@app.route('/')
def index():
    print("🚀 Serving index.html")
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    print(f"📊 Coins Requested: {selected_coins}")

    prices = {}

    for coin in selected_coins:
        current_price = fetch_price(coin)
        if current_price is None:
            print(f"⚠️ Skipping {coin} due to missing price data.")
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

        print(f"✅ Data for {coin}: {prices[coin]}\n")

    print("✅ Sending response\n")
    return jsonify({"prices": prices, "status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
