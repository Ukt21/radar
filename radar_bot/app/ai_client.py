import os
import httpx

AI_SERVICE_URL = os.getenv(
    "AI_SERVICE_URL",
    "https://radar-1-yxoy.onrender.com/ai-analysis"  # поменяй на свой домен
)

AI_IMAGE_URL = os.getenv(
    "AI_IMAGE_URL",
    "https://radar-1-yxoy.onrender.com/ai-analysis-image"  # и этот тоже
)


async def get_ai_analysis(symbol: str = "SUIUSDT", interval: str = "1h") -> str:
    payload = {
        "symbol": symbol.upper().replace("/", ""),
        "interval": interval,
        "limit": 150,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(AI_SERVICE_URL, json=payload)
        r.raise_for_status()
        data = r.json()

    analysis = data["analysis"]
    last_price = data["last_price"]
    change_pct = data["change_pct_1candle"]

    header = f"📊 AI-анализ *{data['symbol']}* ({data['interval']}):\n"
    price_line = f"Цена: `{last_price:.6f}`  |  Изм. последней свечи: `{change_pct:.2f}%`\n\n"

    return header + price_line + analysis


async def get_ai_analysis_image(symbol: str = "SUIUSDT", interval: str = "1h") -> bytes:
    params = {
        "symbol": symbol.upper().replace("/", ""),
        "interval": interval,
        "limit": 150,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await httpx.AsyncClient(timeout=60.0).get(AI_IMAGE_URL, params=params)
        r.raise_for_status()
        return r.content
