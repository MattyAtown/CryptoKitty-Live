# Fetch live prices from CoinGecko
def fetch_price(coin):
    try:
        symbol = COIN_SYMBOLS.get(coin)
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
