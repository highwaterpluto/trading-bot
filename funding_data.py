import requests

def symbol_exists_on_binance(symbol: str) -> bool:
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    symbols = [s["symbol"] for s in response.json()["symbols"]]
    return symbol.upper() in symbols

def get_funding_info(coin_id="bitcoin"):
    symbol = coin_id.upper() + "USDT"
    if not symbol_exists_on_binance(symbol):
        raise Exception(f"Монета '{coin_id}' не знайдена на Binance Futures")
    funding_url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1"
    r1 = requests.get(funding_url)
    if r1.status_code != 200:
        raise Exception("❌ Binance не відповідає (funding)")
    funding_data = r1.json()
    if not funding_data:
        raise Exception("❌ Binance не дав funding rate для цієї монети")
    funding_rate = float(funding_data[0]["fundingRate"]) * 100
    oi_url = f"https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period=5m&limit=1"
    r2 = requests.get(oi_url)
    if r2.status_code != 200:
        raise Exception("❌ Binance не відповідає (open interest)")
    oi_data = r2.json()
    oi_val = float(oi_data[0]["sumOpenInterest"]) if oi_data else None
    oi_mil = oi_val / 1e6 if oi_val else None
    return funding_rate, oi_mil
