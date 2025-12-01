from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.api_client import backend_get

router = Router()

class AnalyzeStates(StatesGroup):
    waiting_symbol = State()

@router.callback_query(F.data == "menu_analyze")
async def cb_analyze(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AnalyzeStates.waiting_symbol)
    await callback.message.answer("Введите тикер монеты (например: SUI, SOL, APT):")
    await callback.answer()

@router.message(AnalyzeStates.waiting_symbol)
async def handle_analyze_symbol(message: types.Message, state: FSMContext):
    symbol_raw = (message.text or "").strip().upper()
    if not symbol_raw:
        await message.answer("Пожалуйста, введите корректный тикер, например: SUI")
        return

    symbol = symbol_raw + "USDT"
    await message.answer(f"⏳ Запрашиваю анализ для {symbol}...")

    data = await backend_get("/analyze", {"symbol": symbol, "tf": "1h"})
    if not data:
        await message.answer("❌ Не удалось получить данные с backend Radar.")
        await state.clear()
        return

    analysis = data.get("analysis") or "Нет данных анализа."
    await message.answer(analysis)
    await state.clear()
