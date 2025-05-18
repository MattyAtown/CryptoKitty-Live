from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import requests
from collections import defaultdict
import os
import random

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

COIN_SYMBOLS = {
    "ALGO": "algorand",
    "SOL": "wrapped-solana",
    "APE": "apetos",
    "AVAX": "binance-peg-avalanche",
    "BTC": "osmosis-allbtc",
    "BNB": "binance-coin-wormhole",
    "ETH": "the-ticker-is-eth",
    "MATIC": "matic-network",
    "BCH": "bitcoin-cash",
    "ADA": "cardano",
    "DOGE": "doge-on-pulsechain",
    "LTC": "litecoin",
    "NEAR": "near",
    "DOT": "xcdot",
    "SHIB": "strategic-hub-for-innovation-in-blockchain",
    "XRP": "warioxrpdumbledoreyugioh69inu",
    "LINK": "osmosis-alllink",
    "ATOM": "cosmos",
    "MANA": "meme-anarchic-numismatic-asset",
    "FTM": "fantom",
    "ICP": "internet-computer",
    "UNI": "uniswap-wormhole",
    "XMR": "monero",
    "SAND": "the-sandbox-wormhole",
    "VET": "vechain"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"
]

def fetch_price(coin_id):
    try:
        print(f"🌐 Fetching price for {coin_id}...")
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            headers=headers,
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if coin_id not in data:
            print(f"⚠️ No data found for {coin_id} in response: {data}")
            return None, None
        
        price = data[coin_id].get("usd")
        change = data[coin_id].get("usd_24h_change")
        
        if price is None or change is None:
            print(f"⚠️ Missing price or change data for {coin_id}: {data[coin_id]}")
            return None, None
        
        print(f"✅ Fetched price for {coin_id}: ${price} ({change}%)")
        return price, change
    except Exception as e:
        print(f"❌ Error fetching price for {coin_id}: {e}")
        return None, None

@app.route("/prices", methods=["POST"])
def get_prices():
    print("🚀 Received /prices request")
    selected_coins = request.json.get("coins", [])
    print(f"🪙 Requested Coins: {selected_coins}")
    prices = {}

    for symbol in selected_coins:
        coin_id = COIN_SYMBOLS.get(symbol)
        if not coin_id:
            print(f"⚠️ Invalid coin symbol: {symbol}")
            continue

        price, change = fetch_price(coin_id)
        if price is None or change is None:
            print(f"⚠️ No data returned for {symbol} ({coin_id})")
            continue

        prices[symbol] = {
            "price": round(price, 2),
            "change": round(change, 2)
        }
        print(f"📊 {symbol} - Price: {price}, Change: {change}")

    print(f"✅ Final Prices: {prices}")
    return jsonify({"prices": prices, "status": "success"})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/", methods=["GET", "POST"])
def index():
    selected = []
    time_range = "1h"
    if request.method == "POST":
        coins = request.form.get("coins", "")
        print("Coins received:", coins)  # Debug line
        selected = coins.split(",") if coins else []
        time_range = request.form.get("time_range", "1h")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
