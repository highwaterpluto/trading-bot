import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

COIN_ID_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "xrp": "ripple",
    "sol": "solana",
    "doge": "dogecoin",
    "pepe": "pepe",
    "floki": "floki",
    "apt": "aptos",
    "arb": "arbitrum",
    "op": "optimism",
    "dot": "polkadot",
    "ltc": "litecoin",
    "link": "chainlink",
    "avax": "avalanche-2"
}

def build_mvrv_chart(coin_id="bitcoin"):
    coin_id = COIN_ID_MAP.get(coin_id.lower(), coin_id)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"❌ Не вдалося завантажити дані для монети '{coin_id}'.")
    data = r.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("date", inplace=True)
    mean = df["price"].mean()
    std = df["price"].std()
    df["z_score"] = (df["price"] - mean) / std
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["z_score"], label="MVRV Z-Score", linewidth=2)
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.axhline(1, color="green", linestyle="--", linewidth=1)
    plt.axhline(-1, color="red", linestyle="--", linewidth=1)
    plt.title(f"MVRV Z-Score — {coin_id.upper()} (ост. 30 днів)", fontsize=14)
    plt.xlabel("Дата")
    plt.ylabel("Z-Score")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("mvrv_chart.png")
    plt.close()
