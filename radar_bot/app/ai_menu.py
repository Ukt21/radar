import asyncio
import os

from aiogram import Router, types, F
from aiogram.filters import Command
from openai import OpenAI

from .keyboards import market_menu, timeframe_menu, PAIRS

router = Router()

# клиент OpenAI (использует OPENAI_API_KEY из ENV)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def _generate_ai_analysis(pair: str, timeframe: str) -> str:
    """
    Запрос к GPT: текстовый анализ рынка.
    """
    prompt = f"""
Ты профессиональный крипто-трейдер и аналитик.
Сделай краткий, структурированный анализ по инструменту {pair} на таймфрейме {timeframe}.

Структура ответа:
1) Общий контекст рынка.
2) Ключевые уровни (поддержки/сопротивления) — в виде списка.
3) Сценарий LONG.
4) Сценарий SHORT.
5) Риски и на что смотреть (объёмы, новости, уровни).

Пиши ёмко, без воды, как для трейдера. Не давай финансовых советов, только аналитическое мнение.
    """.strip()

    loop = asyncio.get_running_loop()

    def _call():
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return resp.output[0].content[0].text

    text = await loop.run_in_executor(None, _call)
    return text


async def _generate_ai_image(pair: str, timeframe: str, analysis_short: str) -> str:
    """
    Запрос к OpenAI на генерацию картинки. Возвращает URL.
    """
    img_prompt = f"""
Minimalistic dark trading dashboard, crypto chart for {pair} on timeframe {timeframe},
with clear trend, support/resistance zones and arrows showing possible scenarios.
No text on image. Premium design, neon accents, professional trading interface.
    """.strip()

    loop = asyncio.get_running_loop()

    def _call():
        img = client.images.generate(
            model="gpt-image-1",
            prompt=img_prompt,
            size="1024x1024",
            n=1,
        )
        return img.data[0].url

    url = await loop.run_in_executor(None, _call)
    return url


@router.message(Command("ai_menu"))
async def cmd_ai_menu(message: types.Message):
    await message.answer(
        "📊 <b>Radar AI</b>\n\n"
        "Выбери торговую пару для анализа:",
        reply_markup=market_menu(),
    )


@router.callback_query(F.data == "back:markets")
async def back_to_markets(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📊 <b>Radar AI</b>\n\n"
        "Выбери торговую пару для анализа:",
        reply_markup=market_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pair:"))
async def select_pair(callback: types.CallbackQuery):
    pair_code = callback.data.split(":", 1)[1]
    pair_name = PAIRS.get(pair_code, pair_code.upper())

    await callback.message.edit_text(
        f"Пара выбрана: <b>{pair_name}</b>\n\n"
        "Теперь выбери таймфрейм:",
        reply_markup=timeframe_menu(pair_code),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("analyze:"))
async def analyze_pair(callback: types.CallbackQuery):
    """
    Запуск AI-аналитики + картинки.
    callback_data формат: analyze:btc:1h
    """
    _, pair_code, timeframe = callback.data.split(":", 2)
    pair_name = PAIRS.get(pair_code, pair_code.upper())

    await callback.answer("⚡ Делаю AI-анализ...")

    # Черновой «заглушка»-сообщение, чтобы пользователь что-то видел
    await callback.message.edit_text(
        f"⏳ Запускаю AI-анализ по <b>{pair_name}</b> ({timeframe})...\n\n"
        f"Обычно это занимает 3–5 секунд.",
    )

    # 1) Текстовый анализ
    try:
        analysis_text = await _generate_ai_analysis(pair_name, timeframe)
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка AI-аналитики:\n<code>{e}</code>"
        )
        return

    # 2) Картинка с анализом
    try:
        image_url = await _generate_ai_image(
            pair_name,
            timeframe,
            analysis_short=analysis_text[:300],
        )
    except Exception:
        image_url = None

    # 3) Красивый финальный ответ
    caption = (
        f"📊 <b>Radar AI — премиальный обзор</b>\n\n"
        f"Пара: <b>{pair_name}</b>\n"
        f"Таймфрейм: <b>{timeframe}</b>\n\n"
        f"{analysis_text}\n\n"
        f"⚠️ Это не финансовый совет. Используй как дополнительную аналитику."
    )

    if image_url:
        await callback.message.answer_photo(photo=image_url, caption=caption)
    else:
        await callback.message.answer(caption)

    # Можно добавить повторный вызов меню
    await callback.message.answer(
        "Хочешь ещё анализ? Выбери новую пару 👇",
        reply_markup=market_menu(),
    )
