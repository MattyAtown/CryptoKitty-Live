from flask import Flask, render_template, request
import requests
import threading
import time

app = Flask(__name__)

# Static list of supported coins
supported_coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "LTC", "DOT", "LINK", "AVAX"]

# Per-session data will be passed via context, not stored globally
# These are only for the background thread updater
live_prices = {}
price_history = {}

# API call to Coinbase

def get_coinbase_price(symbol):
    try:
        url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
        response = requests.get(url)
        response.raise_for_status()
        return float(response.json()["data"]["amount"])
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# Update price history (up to 10 points per coin)
def update_price_history(symbol, price):
    if symbol not in price_history:
        price_history[symbol] = []
    price_history[symbol].append(price)
    if len(price_history[symbol]) > 10:
        price_history[symbol].pop(0)

# Check trends based on last 3 points
def check_trend(symbol):
    hist = price_history.get(symbol, [])
    if len(hist) >= 3:
        if hist[-3] > hist[-2] > hist[-1]:
            return "WARNING"
        elif hist[-3] < hist[-2] < hist[-1]:
            return "RISER"
    return "Stable"

# Get top risers
def get_top_risers():
    return dict(sorted({
        c: round(h[-1] - h[0], 2)
        for c, h in price_history.items() if len(h) >= 2
    }.items(), key=lambda x: x[1], reverse=True)[:3])

# Background thread updates live data
def price_updater():
    while True:
        for coin in supported_coins:
            price = get_coinbase_price(coin)
            if price:
                live_prices[coin] = price
                update_price_history(coin, price)
        time.sleep(300)  # 5 minutes

@app.route("/", methods=["GET", "POST"])
def index():
    # Individual session coin selection
    selected = []
    if request.method == "POST":
        form_data = request.form.get("coins", "")
        selected = [c for c in form_data.split(",") if c.strip()] if form_data else []

    trends = {coin: check_trend(coin) for coin in selected}
    top_risers = get_top_risers()
    current_prices = {coin: live_prices.get(coin, None) for coin in selected}
    session_history = {coin: price_history.get(coin, []) for coin in selected}

    return render_template("index.html",
                           coins=supported_coins,
                           selected=selected,
                           prices=current_prices,
                           trends=trends,
                           top_risers=top_risers,
                           price_history=session_history)

# Start background thread
if __name__ == "__main__":
    threading.Thread(target=price_updater, daemon=True).start()
    app.run(debug=True, port=10000, host="0.0.0.0")
