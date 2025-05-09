from flask import Flask, render_template, jsonify, request
import requests
from collections import defaultdict
import random

app = Flask(__name__)

COINS = ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "MATIC", "DOT", "POL", "LINK", "AERGO", "SUI"]

PRICE_HISTORY = defaultdict(list)

COIN_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "XRP": "XRP-USD",
    "SOL": "SOL-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "MATIC": "MATIC-USD",
    "DOT": "DOT-USD",
    "POL": "POL-USD",
    "LINK": "LINK-USD",
    "AERGO": "AERGO-USD",
    "SUI": "SUI-USD"
}

DOG_STATES = ["happy", "neutral", "angry", "excited"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices', methods=['POST'])
def get_prices():
    selected_coins = request.json.get('coins', [])
    prices = {}
    
    for coin in selected_coins:
        symbol = COIN_SYMBOLS.get(coin)
        if not symbol:
            continue
        
        try:
            response = requests.get(f"https://api.exchange.coinbase.com/products/{symbol}/ticker")
            data = response.json()
            price = float(data['price'])
            prices[coin] = price
            
            # Track price history for alert logic
            PRICE_HISTORY[coin].append(price)
            if len(PRICE_HISTORY[coin]) > 3:
                PRICE_HISTORY[coin].pop(0)

        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")
    
    # Random CryptoDog state for testing
    cryptodog_state = random.choice(DOG_STATES)
    
    return jsonify({
        "prices": prices,
        "cryptodog_state": cryptodog_state
    })

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
