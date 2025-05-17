from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import requests
from collections import defaultdict
import os

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

def fetch_price(coin_id):
    try:
        print(f"🌐 Fetching price for {coin_id}...")
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price",
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
