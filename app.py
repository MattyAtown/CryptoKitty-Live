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

# Update price history with a full timestamp log (1 entry every 5 min)
def update_price_history(symbol, price):
    if symbol not in price_history:
        price_history[symbol] = []
    timestamp = int(time.time())
    price_history[symbol].append((timestamp, price))
    if len(price_history[symbol]) > 288:  # store up to ~1 day of 5min intervals
        price_history[symbol].pop(0)

# Check trends based on last 3 points
def check_trend(symbol):
    hist = price_history.get(symbol, [])
    values = [p[1] for p in hist[-3:]]
    if len(values) == 3:
        if values[0] > values[1] > values[2]:
            return "WARNING"
        elif values[0] < values[1] < values[2]:
            return "RISER"
    return "Stable"

# Get top risers

def get_top_risers():
    risers = {}
    for coin, history in price_history.items():
        values = [p[1] for p in history if len(history) >= 2]
        if values:
            risers[coin] = round(values[-1] - values[0], 2)
    return dict(sorted(risers.items(), key=lambda x: x[1], reverse=True)[:3])

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
    selected = []
    time_range = "5m"
    if request.method == "POST":
        form_data = request.form.get("coins", "")
        selected = [c for c in form_data.split(",") if c.strip()] if form_data else []
        time_range = request.form.get("time_range", "5m")

    trends = {coin: check_trend(coin) for coin in selected}
    top_risers = get_top_risers()
    current_prices = {coin: live_prices.get(coin, None) for coin in selected}

    # Filter history based on selected time range
    session_history = {}
    time_now = int(time.time())
    range_minutes = {
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "1d": 1440,
        "1w": 10080,
        "1mo": 43200
    }.get(time_range, 5)
    seconds_back = range_minutes * 60

    for coin in selected:
        full_history = price_history.get(coin, [])
        filtered = [price for ts, price in full_history if time_now - ts <= seconds_back]
        session_history[coin] = filtered

    return render_template("index.html",
                           coins=supported_coins,
                           selected=selected,
                           prices=current_prices,
                           trends=trends,
                           top_risers=top_risers,
                           price_history=session_history,
                           time_range=time_range)

if __name__ == "__main__":
    threading.Thread(target=price_updater, daemon=True).start()
    app.run(debug=True, port=10000, host="0.0.0.0")
