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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    print(f"📊 Coins Requested: {selected_coins}")

    # Simulate real data
    prices = {}
    for coin in selected_coins:
        current_price = round(random.uniform(1, 50000), 2)
        percentage_change = round(random.uniform(-100, 100), 2)
        timestamps = [time.strftime('%H:%M', time.gmtime(time.time() - 300 * i)) for i in range(12)][::-1]
        price_changes = [round(random.uniform(-100, 100), 2) for _ in range(12)]
        prices[coin] = {
            "price": current_price,
            "change": percentage_change,
            "timestamps": timestamps,
            "percentage_changes": price_changes
        }

    return jsonify({"prices": prices, "status": "success"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
