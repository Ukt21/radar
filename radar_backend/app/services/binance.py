import httpx
from .utils import calc_rsi, calc_ema

BASE = "https://api.binance.com"


async def fetch_klines(symbol: str, tf: str):
    tf_map = {
        "1H": "1h",
        "15m": "15m",
        "4H": "4h",
        "1D": "1d",
    }
    interval = tf_map.get(tf, "1h")

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            BASE + "/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": 200}
        )
    return r.json()


async def build_indicators(symbol: str, tf: str):
    k = await fetch_klines(symbol, tf)

    closes = [float(c[4]) for c in k]
    volumes = [float(c[5]) for c in k]

    price = closes[-1]
    rsi = calc_rsi(closes)
    ema50 = calc_ema(closes, 50)
    ema200 = calc_ema(closes, 200)
    vol24 = sum(volumes[-24:])

    return price, rsi, ema50, ema200, vol24
