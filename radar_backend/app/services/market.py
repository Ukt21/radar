# radar_backend/app/services/market.py
from typing import Dict
from datetime import datetime, timezone

import ccxt
import numpy as np
import pandas as pd

_binance = ccxt.binance({"enableRateLimit": True})


def _normalize_symbol(symbol: str) -> str:
    s = symbol.upper().replace("USDT", "").replace("/", "")
    return f"{s}/USDT"


def _fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
    market_symbol = _normalize_symbol(symbol)
    ohlcv = _binance.fetch_ohlcv(market_symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(
        ohlcv,
        columns=["ts", "open", "high", "low", "close", "volume"],
    )
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    roll_up = up.ewm(alpha=1 / period, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / period, adjust=False).mean().replace(0, np.nan)

    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = close.diff().fillna(0)
    sign = direction.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (sign * volume).cumsum()


def build_signals(symbol: str, timeframe: str = "1h") -> Dict:
    df = _fetch_ohlcv(symbol, timeframe, limit=200)

    close = df["close"]
    volume = df["volume"]

    rsi_series = _rsi(close)
    ema50 = _ema(close, 50)
    ema200 = _ema(close, 200)
    obv_series = _obv(close, volume)

    last = df.iloc[-1]

    price = float(last["close"])
    rsi = float(rsi_series.iloc[-1])
    ema50_val = float(ema50.iloc[-1])
    ema200_val = float(ema200.iloc[-1])
    obv_val = float(obv_series.iloc[-1])

    trend = "флэт"
    if ema50_val > ema200_val * 1.01:
        trend = "бычий"
    elif ema50_val < ema200_val * 0.99:
        trend = "медвежий"

    rsi_state = "нормальный"
    if rsi > 70:
        rsi_state = "перекуплен"
    elif rsi < 30:
        rsi_state = "перепродан"

    vol_mean = float(volume.tail(50).mean())
    vol_state = "средний объём"
    if last["volume"] > vol_mean * 1.5:
        vol_state = "повышенный объём"
    elif last["volume"] < vol_mean * 0.7:
        vol_state = "слабый объём"

    volatility = float((df["high"] - df["low"]).tail(50).mean() / price * 100)

    return {
        "symbol": _normalize_symbol(symbol),
        "timeframe": timeframe,
        "price": price,
        "rsi": round(rsi, 2),
        "rsi_state": rsi_state,
        "ema50": round(ema50_val, 4),
        "ema200": round(ema200_val, 4),
        "trend": trend,
        "obv": round(obv_val, 2),
        "volume_state": vol_state,
        "volatility": round(volatility, 2),
        "last_ts": df["ts"].iloc[-1].astimezone(timezone.utc).isoformat(),
    }
