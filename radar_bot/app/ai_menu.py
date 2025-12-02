from aiogram import Router, types
from aiogram.filters import Command

from .keyboards import market_menu, timeframe_menu

router = Router()


@router.message(Command("ai_menu"))
async def ai_menu(message: types.Message):
    await message.answer(
        "📊 <b>AI-меню</b>\n"
        "Выбери торговую пару:",
        reply_markup=market_menu()
    )


@router.callback_query(lambda c: c.data.startswith("pair_"))
async def select_pair(callback: types.CallbackQuery):
    pair = callback.data.replace("pair_", "").upper()
    await callback.message.edit_text(
        f"Пара выбрана: <b>{pair}</b>\nТеперь выбери таймфрейм:",
        reply_markup=timeframe_menu()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("tf_"))
async def select_timeframe(callback: types.CallbackQuery):
    tf = callback.data.replace("tf_", "")

    await callback.answer("⚡ Выполняю AI-анализ, подожди 2–3 секунды...")

    # Здесь позже подключим OPENAI + генерацию картинки
    await callback.message.edit_text(
        f"🔍 <b>AI-анализ</b>\n"
        f"Пара: BTC/USDT\n"
        f"Таймфрейм: {tf}\n\n"
        f"❗ [Тут будет твой реальный AI-анализ с картинкой 🔥]"
    )
