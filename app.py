from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

TOP_25_COINS = [
    "BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "LINK", 
    "BNB", "LTC", "BCH", "SHIB", "AVAX", "ATOM", "XMR", "FTM", "NEAR",
    "UNI", "ALGO", "VET", "MANA", "SAND", "ICP", "APE"
]

# Simulated data for testing
DUMMY_PRICES = {coin: {"price": round(random.uniform(0.01, 50000), 2), "change": round(random.uniform(-20, 20), 2)} for coin in TOP_25_COINS}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    print(f"📊 Coins Requested: {selected_coins}")

    # Return only the selected coins
    prices = {}
    for coin in selected_coins:
        current_price = DUMMY_PRICES.get(coin, {"price": 0, "change": 0})
        # Simulate 5-minute intervals for the past hour
        timestamps = [time.strftime('%H:%M', time.gmtime(time.time() - 300 * i)) for i in range(12)][::-1]
        price_changes = [round(random.uniform(-100, 100), 2) for _ in range(12)]
        prices[coin] = {
            "price": current_price["price"],
            "change": current_price["change"],
            "timestamps": timestamps,
            "percentage_changes": price_changes
        }

    return jsonify({"prices": prices, "status": "success"})

@app.route('/top_risers', methods=['GET'])
def top_risers():
    # Simulate top 3 risers
    risers = random.sample(TOP_25_COINS, 3)
    riser_messages = [f"{coin}: +{random.randint(5, 25)}%" for coin in risers]
    return jsonify({"top_risers": riser_messages})

@app.route('/news', methods=['GET'])
def get_news():
    # Simulate news headlines
    headlines = [f"Crypto market update {i}" for i in range(1, 6)]
    return jsonify({"news": headlines})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
