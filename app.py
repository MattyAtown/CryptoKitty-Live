from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

COINS = [
    "BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "LINK", "BNB", "BCH", "SHIB", "AVAX", "ATOM", "XMR", "FTM", "NEAR", "UNI", "ALGO", "VET", "MANA", "SAND", "ICP", "APE"
]

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

PRICE_HISTORY = defaultdict(list)
TRENDS = {}
NEWS_HEADLINES = [
    "Bitcoin hits new high amid ETF optimism",
    "Ethereum upgrade causes network surge",
    "Market reacts to inflation data"
]

# Fetch live prices from CoinGecko
def fetch_price(coin):
    try:
        symbol = COIN_SYMBOLS.get(coin.upper())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()

        # Correctly handle the response format
        if symbol in data and 'usd' in data[symbol]:
            price = data[symbol]['usd']
            print(f"✅ Price for {coin} ({symbol}): {price} USD")
            return round(float(price), 2)
        else:
            print(f"⚠️ No USD price found for {coin} ({symbol}) in API response: {data}")
            return None

    except Exception as e:
        print(f"🚨 Error fetching price for {coin}: {e}")
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
    time_range = "1h"
    if request.method == "POST":
        coins = request.form.get("coins", "")
        selected = coins.split(",") if coins else []
        time_range = request.form.get("time_range", "1h")

    prices = {}
    price_history = {}
    for coin in selected:
        price = fetch_price(coin)
        if price is not None:
            prices[coin] = price
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            PRICE_HISTORY[coin].append((timestamp, price))
            PRICE_HISTORY[coin] = PRICE_HISTORY[coin][-100:]
            # Prepare price history for the frontend
            price_history[coin] = [p[1] for p in PRICE_HISTORY[coin]]
        else:
            prices[coin] = "N/A"

    # Determine trends
    for coin in selected:
        TRENDS[coin] = get_trend([p[1] for p in PRICE_HISTORY[coin]])

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
        trends=TRENDS,
        top_risers=top_risers,
        news_headlines=NEWS_HEADLINES,
        time_range=time_range
    )

@app.route("/api/price-history")
def price_history_api():
    # Return a simplified JSON structure for easier frontend integration
    simplified_history = {
        coin: [entry[1] for entry in history]
        for coin, history in PRICE_HISTORY.items()
    }
    return jsonify(simplified_history)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
