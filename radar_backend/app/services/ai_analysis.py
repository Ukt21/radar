# radar_backend/app/services/ai_analysis.py
from typing import Dict
import os

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = (
    "Ты профессиональный трейдер и риск-менеджер. "
    "Делаешь краткий, чёткий анализ крипторынка на русском языке. "
    "Учитывай, что пользователь торгует внутри дня и смотрит на движение BTC "
    "и альтов. Не давай финансовых гарантий, только вероятностные сценарии."
)


def build_context_text(
    symbol_signals: Dict, btc_signals: Dict, whale_text: str
) -> str:
    return (
        f"Текущие сигналы по альту:\n"
        f"{symbol_signals}\n\n"
        f"Текущие сигналы по BTC:\n"
        f"{btc_signals}\n\n"
        f"Кошельки китов:\n{whale_text}\n\n"
        "Сделай три сценария для альта:\n"
        "- базовый (наиболее вероятный),\n"
        "- бычий (если BTC вырастет на 2–3%),\n"
        "- медвежий (если BTC упадёт на 2–3%).\n"
        "Для каждого сценария опиши:\n"
        "- направление (лонг/шорт/флэт),\n"
        "- примерный диапазон движения альта в %, "
        "ориентируясь на то, что при движении BTC 2–3% "
        "альт может ходить 6–10%,\n"
        "- на что обратить внимание по RSI, EMA50/200 и объёмам.\n"
        "Не пиши уровни входа/выхода и не давай финансовых советов."
    )


def make_ai_analysis(
    symbol_signals: Dict, btc_signals: Dict, whale_text: str
) -> str:
    if not OPENAI_API_KEY:
        return "⚠️ AI-аналитика отключена: не задан OPENAI_API_KEY."

    context = build_context_text(symbol_signals, btc_signals, whale_text)

    resp = _client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=context,
    )

    text = (resp.output_text or "").strip()
    if not text:
        return "Не удалось получить ответ от GPT."

    return text
