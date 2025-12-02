from typing import List, Tuple
import httpx


async def fetch_klines(symbol: str, interval: str = "1h", limit: int = 200) -> List[Tuple[float, float, float, float, float]]:
    """Получаем OHLCV с Binance для пары, например SUIUSDT."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return []
        data = resp.json()
    result: List[Tuple[float, float, float, float, float]] = []
    for item in data:
        open_, high, low, close, volume = map(float, item[1:6])
        result.append((open_, high, low, close, volume))
    return result
