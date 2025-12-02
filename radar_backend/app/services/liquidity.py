from typing import List, Dict


def detect_liquidity_levels(highs: List[float], lows: List[float], closes: List[float]) -> List[Dict]:
    levels: List[Dict] = []
    n = len(highs)
    if n < 5:
        return levels

    # Простые уровни: локальные экстремумы
    for i in range(2, n - 2):
        local_high = highs[i - 2:i + 3]
        local_low = lows[i - 2:i + 3]
        if highs[i] == max(local_high):
            levels.append({"type": "liquidity_high", "price": highs[i]})
        if lows[i] == min(local_low):
            levels.append({"type": "liquidity_low", "price": lows[i]})

    # Уровень текущей цены
    if closes:
        levels.append({"type": "current_price", "price": closes[-1]})

    return levels
