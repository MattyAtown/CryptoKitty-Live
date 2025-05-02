from flask import Flask, render_template, request, jsonify
import requests
import threading
import time
import os

app = Flask(__name__)

supported_coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "LTC", "DOT", "LINK", "AVAX"]
selected_coins = []
prices = {}
price_history = {}

def get_coinbase_price(symbol):
    try:
        url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data["data"]["amount"])
    except Exception as e:
        print(f"[ERROR] Failed to get price for {symbol}: {e}")
        return None

def update_price_history(symbol, price):
    if symbol not in price_history:
        price_history[symbol] = []
    price_history[symbol].append(price)
    if len(price_history[symbol]) > 10:
        price_history[symbol].pop(0)

def check_trend(symbol):
    history = price_history.get(symbol, [])
    if len(history) >= 3:
        if history[-3] > history[-2] > history[-1]:
            return "WARNING"
        elif history[-3] < history[-2] < history[-1]:
            return "RISER"
    return "Stable"

def get_top_risers():
    return dict(sorted({
        coin: round(history[-1] - history[0], 2)
        for coin, history in price_history.items() if len(history) >= 2
    }.items(), key=lambda x: x[1], reverse=True)[:3])

def get_crypto_news():
    try:
        url = "https://openapi.coinstats.app/news/latest?limit=5"
        headers = {
            "accept": "application/json",
            "X-API-KEY": "B8btcyebVUFRSFaE5U7z+xwoiN96M2VBSU/UQP7s3oc="
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        headlines = [article["title"] for article in data.get("news", [])]
        print(f"[NEWS] Headlines fetched: {headlines}")
        return headlines
    except Exception as e:
        print(f"[ERROR] Failed to fetch news: {e}")
        return []

def price_updater():
    global prices
    while True:
        try:
            if selected_coins:
                print(f"[UPDATE] Fetching prices for: {selected_coins}")
                for coin in selected_coins:
                    price = get_coinbase_price(coin)
                    if price:
                        prices[coin] = price
                        update_price_history(coin, price)
            time.sleep(300)
        except Exception as e:
            print(f"[ERROR] Price updater failed: {e}")
            time.sleep(10)

@app.route("/", methods=["GET", "POST"])
def index():
    global selected_coins
    if request.method == "POST":
        form_data = request.form.get("coins", "")
        selected_coins = [c for c in form_data.split(",") if c]

    trends = {coin: check_trend(coin) for coin in selected_coins}
    top_risers = get_top_risers()

    news_headlines = []
    try:
        news_headlines = get_crypto_news()
    except Exception as e:
        print(f"[WARNING] Failed to fetch news safely in route: {e}")

    return render_template("index.html",
        coins=supported_coins,
        selected=selected_coins,
        prices=prices,
        trends=trends,
        top_risers=top_risers,
        price_history=price_history,
        news_headlines=news_headlines
    )

@app.route("/prices")
def get_prices():
    return jsonify(prices)

@app.route("/history")
def get_history():
    return jsonify(price_history)

@app.route("/trends")
def get_trends():
    return jsonify({coin: check_trend(coin) for coin in selected_coins})

@app.route("/risers")
def get_risers():
    return jsonify(get_top_risers())

if __name__ == "__main__":
    print("🚀 Starting CryptoKitty + CryptoDog + NewsFlash App...")
    threading.Thread(target=price_updater, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
