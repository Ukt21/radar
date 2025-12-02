from typing import List, Dict


def ema(values: List[float], period: int) -> List[float]:
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    emas: List[float] = []
    ema_prev = sum(values[:period]) / period
    emas.append(ema_prev)
    for price in values[period:]:
        ema_prev = price * k + ema_prev * (1 - k)
        emas.append(ema_prev)
    return emas


def rsi(values: List[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = values[i] - values[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(-diff)
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val


def obv(closes: List[float], volumes: List[float]) -> float | None:
    if len(closes) != len(volumes) or not closes:
        return None
    obv_val = 0.0
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            obv_val += volumes[i]
        elif closes[i] < closes[i - 1]:
            obv_val -= volumes[i]
    return obv_val


def build_summary(symbol: str, close: float, btc_change_pct: float, alt_change_pct: float, rsi_val: float | None) -> str:
    parts: List[str] = []
    direction = "рост" if alt_change_pct >= 0 else "падение"
    parts.append(f"Монета {symbol}: {direction} {alt_change_pct:.2f}% за последние свечи.")
    if rsi_val is not None:
        if rsi_val > 70:
            parts.append(f"RSI {rsi_val:.1f} — зона перекупленности, повышенный риск отката.")
        elif rsi_val < 30:
            parts.append(f"RSI {rsi_val:.1f} — зона перепроданности, возможен отскок.")
        else:
            parts.append(f"RSI {rsi_val:.1f} — нейтральная зона.")
    if btc_change_pct <= -2:
        parts.append("BTC показывает потенциал снижения ≥2%. При сильном падении BTC альты обычно падают сильнее (8–10%). Управляй риском.")
    elif btc_change_pct >= 2:
        parts.append("BTC в положительной зоне. При устойчивом росте BTC альты часто дают 6–8% движения и больше.")
    return "\n".join(parts)
