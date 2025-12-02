from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any

from app.services.market import fetch_klines
from app.services.indicators import ema, rsi, obv, build_summary
from app.services.liquidity import detect_liquidity_levels

app = FastAPI(title="Radar Backend", version="1.0.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/analyze")
async def analyze(
    symbol: str = Query(..., description="Тикер монеты, например SUIUSDT"),
    tf: str = Query("1h", description="Таймфрейм Binance, например 1h, 4h"),
) -> Dict[str, Any]:
    # Данные по альткоину
    alt_klines = await fetch_klines(symbol, interval=tf)
    if not alt_klines:
        raise HTTPException(status_code=400, detail="Не удалось получить данные по монете.")

    # Данные по BTC
    btc_klines = await fetch_klines("BTCUSDT", interval=tf)
    if not btc_klines:
        raise HTTPException(status_code=400, detail="Не удалось получить данные по BTC.")

    alt_closes = [c[3] for c in alt_klines]
    alt_volumes = [c[4] for c in alt_klines]
    btc_closes = [c[3] for c in btc_klines]

    if len(alt_closes) < 5 or len(btc_closes) < 5:
        raise HTTPException(status_code=400, detail="Недостаточно данных для анализа.")

    # Процентные изменения
    alt_change = (alt_closes[-1] / alt_closes[-5] - 1) * 100
    btc_change = (btc_closes[-1] / btc_closes[-5] - 1) * 100

    # Индикаторы
    rsi_val = rsi(alt_closes, period=14)
    obv_val = obv(alt_closes, alt_volumes)
    ema_fast = ema(alt_closes, period=21)
    ema_slow = ema(alt_closes, period=55)
    ema_trend = None
    if ema_fast and ema_slow:
        ema_trend = "bullish" if ema_fast[-1] > ema_slow[-1] else "bearish"

    summary = build_summary(symbol, alt_closes[-1], btc_change, alt_change, rsi_val)

    return {
        "symbol": symbol.upper(),
        "tf": tf,
        "price": alt_closes[-1],
        "btc_change_pct": btc_change,
        "alt_change_pct": alt_change,
        "rsi": rsi_val,
        "obv": obv_val,
        "ema_trend": ema_trend,
        "analysis": summary,
    }


@app.get("/liquidity")
async def liquidity(
    symbol: str = Query(..., description="Тикер монеты, например SUIUSDT"),
    tf: str = Query("1h", description="Таймфрейм Binance, например 1h, 4h"),
):
    klines = await fetch_klines(symbol, interval=tf)
    if not klines:
        raise HTTPException(status_code=400, detail="Не удалось получить данные по монете.")

    highs = [k[1] for k in klines]
    lows = [k[2] for k in klines]
    closes = [k[3] for k in klines]

    levels = detect_liquidity_levels(highs, lows, closes)

    return {
        "symbol": symbol.upper(),
        "tf": tf,
        "levels": levels,
    }


@app.get("/btc")
async def btc_overview(
    tf: str = Query("1h", description="Таймфрейм для BTC, например 1h, 4h"),
):
    btc_klines = await fetch_klines("BTCUSDT", interval=tf)
    if not btc_klines:
        raise HTTPException(status_code=400, detail="Не удалось получить данные по BTC.")

    btc_closes = [c[3] for c in btc_klines]
    btc_volumes = [c[4] for c in btc_klines]

    change_pct = (btc_closes[-1] / btc_closes[-5] - 1) * 100
    rsi_val = rsi(btc_closes, period=14)
    obv_val = obv(btc_closes, btc_volumes)

    if change_pct <= -2:
        scenario = "BTC показывает слабость, есть риск продолжения снижения. Следи за уровнями поддержки и не завышай плечо."
    elif change_pct >= 2:
        scenario = "BTC в фазе роста, тренд выглядит уверенно. Альты в такой фазе часто двигаются сильнее."
    else:
        scenario = "BTC в боковике, сильного тренда нет. Альты могут двигаться хаотично."

    return {
        "symbol": "BTCUSDT",
        "tf": tf,
        "price": btc_closes[-1],
        "change_pct": change_pct,
        "rsi": rsi_val,
        "obv": obv_val,
        "scenario": scenario,
    }
