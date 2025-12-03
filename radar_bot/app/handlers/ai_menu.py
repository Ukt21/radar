from __future__ import annotations

import os
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from openai import AsyncOpenAI

# Роутер для меню "Чат с ИИ / уроки трейдинга"
ai_menu_router = Router(name="ai_menu")

# Клиент OpenAI (использует переменную окружения OPENAI_API_KEY)
openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
client: Optional[AsyncOpenAI] = None
if openai_api_key:
    client = AsyncOpenAI(api_key=openai_api_key)


async def ask_trading_ai(prompt: str) -> str:
    """
    Запрос к ИИ как к опытному трейдеру:
    даёт аккуратный разбор + точку входа/стоп/тейк.
    Если ключа нет – возвращаем заглушку.
    """
    if client is None:
        return (
            "ИИ-анализ временно недоступен: не задан OPENAI_API_KEY. "
            "Обратитесь к администратору бота."
        )

    # Здесь можно усложнить промт под твой стиль.
    system_prompt = (
        "Ты профессиональный трейдер с опытом 15+ лет. "
        "Дай аккуратный, консервативный анализ. "
        "Всегда указывай: точку входа, стоп-лосс, тейк-профит, риск на сделку "
        "(в процентах от депозита) и краткий комментарий по риск-менеджменту. "
        "Не обещай гарантированную прибыль."
    )

    user_prompt = (
        "Сделай анализ по следующему запросу пользователя и предложи сделку:\n\n"
        f"{prompt}"
    )

    resp = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=800,
    )

    answer = resp.choices[0].message.content
    return answer or "Не удалось получить ответ от модели."


# ====== Хэндлеры ======


@ai_menu_router.message(Command("ai"))
async def ai_command_entry(message: Message) -> None:
    """
    Стартовая команда, например: /ai BTC/USDT H1
    Пользователь может кратко описать монету/таймфрейм/идею.
    """
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) == 1:
        await message.answer(
            "Отправьте монету и идею, например:\n"
            "`/ai SUI/USDT H1, ищу консервативный вход`",
            parse_mode="Markdown",
        )
        return

    user_query = parts[1].strip()
    await message.answer("Секунду, считаю варианты входа…")

    try:
        answer = await ask_trading_ai(user_query)
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при запросе к ИИ: {e}\n"
            "Попробуйте ещё раз чуть позже."
        )
        return

    await message.answer(answer)


@ai_menu_router.message(F.text & ~F.text.startswith("/"))
async def ai_free_chat(message: Message) -> None:
    """
    Свободный чат с ИИ (если ты хочешь, чтобы все обычные сообщения,
    попавшие в этот роутер, шли в ИИ).
    При необходимости можно привязать этот роутер только к отдельным кнопкам.
    """
    user_query = message.text.strip()
    if not user_query:
        return

    await message.answer("Анализирую как опытный трейдер…")

    try:
        answer = await ask_trading_ai(user_query)
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при запросе к ИИ: {e}\n"
            "Попробуйте ещё раз."
        )
        return

    await message.answer(answer)

