from __future__ import annotations

import os
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from openai import AsyncOpenAI

# Создаем роутер
ai_menu_router = Router(name="ai_menu")

# Подключаем OpenAI
openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
client: Optional[AsyncOpenAI] = None
if openai_api_key:
    client = AsyncOpenAI(api_key=openai_api_key)


async def ask_ai(prompt: str) -> str:
    """ИИ анализ трейдинга."""
    if client is None:
        return "Ошибка: не задан OPENAI_API_KEY."

    system_prompt = (
        "Ты профессиональный трейдер с опытом 15 лет. "
        "Дай объективный и спокойный анализ, включая точку входа, стоп, тейк и риски. "
        "Не обещай гарантированную прибыль."
    )

    try:
        resp = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return resp.choices[0].message.content

    except Exception as e:
        return f"Ошибка при запросе к ИИ: {e}"


# ======= HANDLERS =======

@ai_menu_router.message(Command("ai"))
async def ai_cmd(message: Message):
    """Обработка команды /ai <запрос>."""
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) == 1:
        await message.answer(
            "Использование:\n/ai BTC/USDT, дай точку входа\n\n"
            "Или просто отправьте текст – я всё пойму."
        )
        return

    query = parts[1]
    await message.answer("Секунду… получаю анализ от ИИ…")
    answer = await ask_ai(query)
    await message.answer(answer)


@ai_menu_router.message(F.text)
async def ai_free_chat(message: Message):
    """Свободное общение с ИИ."""
    query = message.text.strip()
    if not query:
        return

    await message.answer("Анализирую…")
    answer = await ask_ai(query)
    await message.answer(answer)

