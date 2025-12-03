def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = closes[-i] - closes[-i - 1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(-diff)
    avg_gain = sum(gains) / period if gains else 0.0001
    avg_loss = sum(losses) / period if losses else 0.0001
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 2)


def calc_ema(closes, period=50):
    k = 2 / (period + 1)
    ema = closes[0]
    for price in closes:
        ema = price * k + ema * (1 - k)
    return round(ema, 2)
