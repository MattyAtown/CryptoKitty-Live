from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import requests
from collections import defaultdict
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

COIN_SYMBOLS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "polygon",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "BNB": "binancecoin",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "SHIB": "shiba-inu",
    "AVAX": "avalanche-2",
    "ATOM": "cosmos",
    "XMR": "monero",
    "FTM": "fantom",
    "NEAR": "near",
    "UNI": "uniswap",
    "ALGO": "algorand",
    "VET": "vechain",
    "MANA": "decentraland",
    "SAND": "the-sandbox",
    "ICP": "internet-computer",
    "APE": "apecoin"
}

# Cache to reduce API calls
PRICE_HISTORY = defaultdict(list)
MAX_HISTORY = 12

def fetch_price(coin_id):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10
        )
        data = response.json()
        return data[coin_id]["usd"], data[coin_id]["usd_24h_change"]
    except Exception as e:
        print(f"Error fetching price for {coin_id}: {e}")
        return None, None

@app.route("/prices", methods=["POST"])
def get_prices():
    print("🚀 Received /prices request")
    selected_coins = request.json.get("coins", [])
    prices = {}

    for symbol in selected_coins:
        coin_id = COIN_SYMBOLS.get(symbol)
        if not coin_id:
            continue

        price, change = fetch_price(coin_id)
        if price is None or change is None:
            continue

        # Add the current price and change to the history
        PRICE_HISTORY[symbol].append({"price": price, "change": round(change, 2)})
        if len(PRICE_HISTORY[symbol]) > MAX_HISTORY:
            PRICE_HISTORY[symbol].pop(0)

        prices[symbol] = {
            "price": round(price, 2),
            "change": round(change, 2),
            "history": PRICE_HISTORY[symbol]
        }

    return jsonify({"prices": prices, "status": "success"})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
