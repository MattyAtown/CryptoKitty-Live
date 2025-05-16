from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    print(f"📊 Coins Requested: {selected_coins}")

    # Dummy data for testing
    prices = {coin: {"price": 1000, "change": 2.5} for coin in selected_coins}
    return jsonify({"prices": prices, "status": "success"})

@app.route('/top_risers', methods=['GET'])
def top_risers():
    # Dummy top risers
    return jsonify({"top_risers": ["BTC +5%", "ETH +4%", "XRP +3%"]})

@app.route('/news', methods=['GET'])
def get_news():
    # Dummy news
    return jsonify({"news": ["Crypto markets remain volatile", "ETH 2.0 staking update", "DOGE hits new high"]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
