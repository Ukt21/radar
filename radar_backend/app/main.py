from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any

from fastapi import FastAPI, Query
from .services.market import build_signals
from .services.whales import summarize_whales
from .services.ai_analysis import make_ai_analysis

app = FastAPI(title="Radar Backend", version="1.0.0")

@app.get("/")
async def index():
    return {"status": "ok", "message": "Radar backend is running 🚀"}

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/analyze")
async def analyze(symbol: str = Query(..., min_length=2), tf: str = "1h"):
    """
    Возвращает подробный текстовый анализ:
    техника + AI-сценарий + киты.
    Ответ по-прежнему в поле 'analysis', чтобы бот ничего не ломался.
    """
    symbol = symbol.upper()

    # Техника по альту и по BTC
    symbol_signals = build_signals(symbol, tf)
    btc_signals = build_signals("BTC", tf)

    # Кошельки китов
    whales_text = await summarize_whales()

    # GPT-анализ
    ai_text = make_ai_analysis(symbol_signals, btc_signals, whales_text)

    # Финальный текст, который увидит пользователь в боте
    analysis_parts = []

    analysis_parts.append(
        f"📊 Технический снимок по {symbol_signals['symbol']} "
        f"({symbol_signals['timeframe']}):\n"
        f"- Цена: {symbol_signals['price']:.4f} USDT\n"
        f"- Тренд по EMA50/200: {symbol_signals['trend']}\n"
        f"- RSI(14): {symbol_signals['rsi']} ({symbol_signals['rsi_state']})\n"
        f"- EMA50: {symbol_signals['ema50']}, EMA200: {symbol_signals['ema200']}\n"
        f"- OBV: {symbol_signals['obv']}\n"
        f"- Объём: {symbol_signals['volume_state']}\n"
        f"- Средняя внутридневная волатильность ~{symbol_signals['volatility']}%\n"
    )

    analysis_parts.append(
        f"₿ BTC ({btc_signals['timeframe']}):\n"
        f"- Цена: {btc_signals['price']:.2f} USDT\n"
        f"- Тренд: {btc_signals['trend']}, RSI: {btc_signals['rsi']} "
        f"({btc_signals['rsi_state']})\n"
        f"- Волатильность BTC ~{btc_signals['volatility']}%\n"
    )

    analysis_parts.append("🐋 Кошельки китов (BTC):\n" + whales_text)

    analysis_parts.append("🤖 AI-сценарий (GPT):\n" + ai_text)

    full_text = "\n\n".join(analysis_parts)

    return {"analysis": full_text}


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
