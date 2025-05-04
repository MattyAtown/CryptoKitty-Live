from flask import Flask, render_template, request, jsonify, session
import requests
import threading
import time
import os
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

supported_coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "LTC", "DOT", "LINK", "AVAX"]
user_data = defaultdict(lambda: {
    "selected_coins": [],
    "prices": {},
    "price_history": {}
})

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

def update_price_history(data, symbol, price):
    if symbol not in data["price_history"]:
        data["price_history"][symbol] = []
    data["price_history"][symbol].append(price)
    if len(data["price_history"][symbol]) > 10:
        data["price_history"][symbol].pop(0)

def check_trend(history):
    if len(history) >= 3:
        if history[-3] > history[-2] > history[-1]:
            return "WARNING"
        elif history[-3] < history[-2] < history[-1]:
            return "RISER"
    return "Stable"

def get_top_risers(data):
    return dict(sorted({
        coin: round(history[-1] - history[0], 2)
        for coin, history in data["price_history"].items() if len(history) >= 2
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
        return headlines
    except Exception as e:
        print(f"[ERROR] Failed to fetch news: {e}")
        return []

def price_updater():
    while True:
        try:
            for sid, data in user_data.items():
                if data["selected_coins"]:
                    for coin in data["selected_coins"]:
                        price = get_coinbase_price(coin)
                        if price:
                            data["prices"][coin] = price
                            update_price_history(data, coin, price)
        except Exception as e:
            print(f"[ERROR] Price updater failed: {e}")
        time.sleep(300)

@app.route("/", methods=["GET", "POST"])
def index():
    sid = session.get("sid")
    if not sid:
        sid = os.urandom(16).hex()
        session["sid"] = sid
    data = user_data[sid]

    if request.method == "POST":
        form_data = request.form.get("coins", "")
        data["selected_coins"] = [c for c in form_data.split(",") if c]

    trends = {
        coin: check_trend(data["price_history"].get(coin, []))
        for coin in data["selected_coins"]
    }

    cryptodog_alerts = {
        coin: f"CryptoDog growls! {coin} is in free fall!" if trend == "WARNING" else
              f"CryptoDog barks excitedly! {coin} is surging!" if trend == "RISER" else ""
        for coin, trend in trends.items()
    }

    return render_template("index.html",
        coins=supported_coins,
        selected=data["selected_coins"],
        prices=data["prices"],
        trends=trends,
        top_risers=get_top_risers(data),
        price_history=data["price_history"],
        news_headlines=get_crypto_news(),
        cryptodog_alerts=cryptodog_alerts
    )

@app.route("/prices")
def get_prices():
    sid = session.get("sid")
    return jsonify(user_data[sid]["prices"])

@app.route("/history")
def get_history():
    sid = session.get("sid")
    return jsonify(user_data[sid]["price_history"])

@app.route("/trends")
def get_trends():
    sid = session.get("sid")
    data = user_data[sid]
    return jsonify({coin: check_trend(data["price_history"].get(coin, [])) for coin in data["selected_coins"]})

@app.route("/risers")
def get_risers():
    sid = session.get("sid")
    return jsonify(get_top_risers(user_data[sid]))

if __name__ == "__main__":
    print("🚀 Starting CryptoKitty + CryptoDog + NewsFlash App...")
    threading.Thread(target=price_updater, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
