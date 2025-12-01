from aiogram import Router, types, F
from app.services.api_client import backend_get

router = Router()

@router.callback_query(F.data == "menu_btc")
async def cb_btc(callback: types.CallbackQuery):
    await callback.message.answer("⏳ Получаю обзор BTC (1H)...")
    data = await backend_get("/analyze", {"symbol": "BTCUSDT", "tf": "1h"})
    if not data:
        await callback.message.answer("❌ Не удалось получить данные по BTC.")
        await callback.answer()
        return

    analysis = data.get("analysis") or "Нет данных анализа."
    await callback.message.answer(analysis)
    await callback.answer()
