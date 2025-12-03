import json
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def build_scenarios(symbol, tf, data):
    """
    data = {
        price, rsi, ema50, ema200,
        volume24, money_flow, whales,
        best_side, vs_btc
    }
    """

    system_prompt = """
Ты опытный трейдер с 10+ лет стажа. 
Пиши профессиональные трейдинговые сценарии.
Делай разумные точки входа, стоп-лосс, тейк-профит.
Учитывай RSI, EMA, объёмы, money flow, активность китов.
НЕ используй категоричные фразы.
"""

    user_prompt = f"""
Проанализируй данные:
{json.dumps(data, ensure_ascii=False, indent=2)}

Сформируй JSON:

{{
  "long": {{
    "entry": "число-число",
    "sl": "число",
    "tp1": "число",
    "tp2": "число",
    "text": "логика входа",
    "score": 0-10
  }},
  "short": {{
    "entry": "...",
    "sl": "...",
    "tp1": "...",
    "tp2": "...",
    "text": "...",
    "score": 0-10
  }},
  "comment": "общий вывод"
}}
"""

    res = client.chat.completions.create(
        model="gpt-5.1-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw = res.choices[0].message.content
    return json.loads(raw)
