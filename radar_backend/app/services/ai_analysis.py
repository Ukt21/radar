import os
import io
from typing import Optional

import httpx
from fastapi import FastAPI, Response
from pydantic import BaseModel
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# ---------- Настройки ----------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY не задан в переменных окружения")

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
BINANCE_BASE_URL = "https://api.binance.com"

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="Radar AI Analysis")


# ---------- Модели ----------
class AnalysisRequest(BaseModel):
    symbol: str = "SUIUSDT"   # без слеша
    interval: str = "1h"      # 15m, 1h, 4h, 1d
    limit: int = 150          # свечи (до 1000)


class AnalysisResponse(BaseModel):
    symbol: str
    interval: str
    analysis: str
    last_price: float
    change_pct_1candle: float
    trend: Optional[str] = None
    signal: Optional[str] = None   # BUY / SELL / WAIT


# ---------- Работа с Binance ----------
async def fetch_klines(symbol: str, interval: str, limit: int = 150):
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}

    async with httpx.AsyncClient(timeout=10.0) as http:
        r = await http.get(url, params=params)
        r.raise_for_status()
        return r.json()


def build_features(klines):
    closes = [float(k[4]) for k in klines]  # цена закрытия
    last = closes[-1]
    prev = closes[-2]

    change_pct = (last - prev) / prev * 100 if prev != 0 else 0.0

    sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
    sma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None

    trend = None
    if sma50 is not None and sma200 is not None:
        if sma50 > sma200:
            trend = "uptrend"
        elif sma50 < sma200:
            trend = "downtrend"
        else:
            trend = "sideways"

    return {
        "closes": closes,
        "last_price": last,
        "prev_close": prev,
        "change_pct_1candle": change_pct,
        "sma50": sma50,
        "sma200": sma200,
        "trend": trend,
    }


# ---------- OpenAI-анализ ----------
async def ask_openai(symbol: str, interval: str, features: dict) -> str:
    system_prompt = (
        "Ты профессиональный крипто-трейдер с опытом >15 лет. "
        "Делаешь аккуратный анализ без финансовых советов. "
        "Пиши по-русски, структурировано, коротко, как аналитик из Telegram-канала. "
        "В конце добавь ОТДЕЛЬНОЙ строкой одно слово CAPS: BUY или SELL или WAIT."
    )

    user_prompt = f"""
Проанализируй криптопару {symbol} на таймфрейме {interval}.

Данные по рынку:
- Текущая цена: {features['last_price']:.6f}
- Предыдущее закрытие: {features['prev_close']:.6f}
- Изменение за последнюю свечу: {features['change_pct_1candle']:.2f}%
- SMA50: {features['sma50']:.6f} 
- SMA200: {features['sma200']:.6f}
- Тренд по пересечению SMA50/200: {features['trend']}

Сделай:
1) Краткий обзор тренда (бычий/медвежий/флэт).
2) Возможные зоны интереса (области набора/фиксации) в процентах от текущей цены.
3) Бычий сценарий.
4) Медвежий сценарий.
5) Риск-менеджмент (без конкретных сумм).
6) В конце ОТДЕЛЬНОЙ строкой напиши одно слово CAPS: BUY или SELL или WAIT.
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
        max_tokens=700,
    )

    return response.choices[0].message.content


def extract_signal(analysis_text: str) -> Optional[str]:
    """Ищем в конце анализа строку BUY/SELL/WAIT."""
    for line in reversed(analysis_text.splitlines()):
        word = line.strip().upper()
        if word in ("BUY", "SELL", "WAIT"):
            return word
    return None


# ---------- Рисование картинки анализа ----------
def generate_chart_image(
    symbol: str,
    interval: str,
    features: dict,
    signal: Optional[str],
) -> bytes:
    """
    Рисуем простую псевдо-картинку: линия цены + уровни + стрелка тренда + сигнал.
    Возвращаем PNG в виде bytes.
    """
    # базовые настройки
    width, height = 1200, 630
    bg_color = (15, 18, 30)
    grid_color = (40, 45, 70)
    line_color = (80, 180, 255)
    text_color = (230, 230, 240)

    # цвет сигнала
    signal_color_map = {
        "BUY": (46, 204, 113),
        "SELL": (231, 76, 60),
        "WAIT": (241, 196, 15),
        None: (127, 140, 141),
    }
    signal_color = signal_color_map.get(signal, signal_color_map[None])

    # создаём картинку
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # шрифты
    font_title = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # заголовок
    title = f"RADAR AI • {symbol.upper()} • {interval}"
    draw.text((40, 30), title, fill=text_color, font=font_title)

    # зона под график
    margin_left, margin_right = 80, 80
    margin_top, margin_bottom = 90, 140
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom

    # сетка
    for i in range(6):
        y = margin_top + i * chart_h / 5
        draw.line((margin_left, y, margin_left + chart_w, y), fill=grid_color)
    for i in range(6):
        x = margin_left + i * chart_w / 5
        draw.line((x, margin_top, x, margin_top + chart_h), fill=grid_color)

    closes = features["closes"]
    min_price = min(closes)
    max_price = max(closes)
    price_range = max_price - min_price or 1.0

    # нормализация точек
    points = []
    for i, price in enumerate(closes):
        x = margin_left + chart_w * (i / max(1, len(closes) - 1))
        # цена сверху вниз (чем выше цена, тем ближе к верхней границе)
        y = margin_top + chart_h * (1 - (price - min_price) / price_range)
        points.append((x, y))

    # линия цены
    if len(points) > 1:
        draw.line(points, fill=line_color, width=3)

    # текущая цена
    last_price = features["last_price"]
    last_y = margin_top + chart_h * (1 - (last_price - min_price) / price_range)
    draw.line(
        (margin_left, last_y, margin_left + chart_w, last_y),
        fill=(100, 100, 220),
        width=1,
    )
    draw.text(
        (margin_left + chart_w + 10, last_y - 8),
        f"{last_price:.6f}",
        fill=text_color,
        font=font_small,
    )

    # стрелка тренда
    trend = features["trend"]
    arrow_center = (width - 200, margin_top + 40)

    if trend == "uptrend":
        arrow_color = (46, 204, 113)
        arrow = [
            (arrow_center[0] - 15, arrow_center[1] + 15),
            (arrow_center[0] + 15, arrow_center[1] + 15),
            (arrow_center[0], arrow_center[1] - 15),
        ]
    elif trend == "downtrend":
        arrow_color = (231, 76, 60)
        arrow = [
            (arrow_center[0] - 15, arrow_center[1] - 15),
            (arrow_center[0] + 15, arrow_center[1] - 15),
            (arrow_center[0], arrow_center[1] + 15),
        ]
    else:  # sideways / None
        arrow_color = (241, 196, 15)
        arrow = [
            (arrow_center[0] - 15, arrow_center[1] - 10),
            (arrow_center[0] + 15, arrow_center[1] - 10),
            (arrow_center[0] + 15, arrow_center[1] + 10),
            (arrow_center[0] - 15, arrow_center[1] + 10),
        ]

    draw.polygon(arrow, fill=arrow_color)
    draw.text(
        (arrow_center[0] - 40, arrow_center[1] + 25),
        trend or "no trend",
        fill=text_color,
        font=font_small,
    )

    # блок сигнала
    signal_text = f"SIGNAL: {signal or 'UNKNOWN'}"
    box_w, box_h = 260, 60
    box_x, box_y = 40, height - margin_bottom + 40
    box_color = (signal_color[0], signal_color[1], signal_color[2],)

    draw.rounded_rectangle(
        (box_x, box_y, box_x + box_w, box_y + box_h),
        radius=12,
        fill=box_color,
    )
    draw.text(
        (box_x + 20, box_y + 20),
        signal_text,
        fill=(0, 0, 0),
        font=font_title,
    )

    # подпись изменения цены
    change_pct = features["change_pct_1candle"]
    change_text = f"Δ последняя свеча: {change_pct:.2f}%"
    draw.text(
        (40, margin_top - 40),
        change_text,
        fill=text_color,
        font=font_small,
    )

    # сохраняем в память
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


# ---------- Эндпоинты ----------
@app.get("/")
async def root():
    return {"status": "ok", "service": "radar-ai-analysis"}


@app.post("/ai-analysis", response_model=AnalysisResponse)
async def ai_analysis(req: AnalysisRequest):
    klines = await fetch_klines(req.symbol, req.interval, req.limit)
    features = build_features(klines)
    analysis_text = await ask_openai(req.symbol, req.interval, features)
    signal = extract_signal(analysis_text)

    return AnalysisResponse(
        symbol=req.symbol.upper(),
        interval=req.interval,
        analysis=analysis_text,
        last_price=features["last_price"],
        change_pct_1candle=features["change_pct_1candle"],
        trend=features["trend"],
        signal=signal,
    )


@app.get("/ai-analysis-image")
async def ai_analysis_image(
    symbol: str = "SUIUSDT",
    interval: str = "1h",
    limit: int = 150,
):
    """
    Возвращает PNG-картинку анализа.
    """
    klines = await fetch_klines(symbol, interval, limit)
    features = build_features(klines)

    # берём текстовый анализ, чтобы достать сигнал, но он же пригодится боту
    analysis_text = await ask_openai(symbol, interval, features)
    signal = extract_signal(analysis_text)

    img_bytes = generate_chart_image(symbol, interval, features, signal)
    return Response(content=img_bytes, media_type="image/png")

