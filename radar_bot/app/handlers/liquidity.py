from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.api_client import backend_get

router = Router()

class LiquidityStates(StatesGroup):
    waiting_symbol = State()

@router.callback_query(F.data == "menu_liquidity")
async def cb_liquidity(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(LiquidityStates.waiting_symbol)
    await callback.message.answer(
        "Введите тикер монеты для карты ликвидности (например: BTC, SUI):"
    )
    await callback.answer()

@router.message(LiquidityStates.waiting_symbol)
async def handle_liquidity_symbol(message: types.Message, state: FSMContext):
    symbol_raw = (message.text or "").strip().upper()
    if not symbol_raw:
        await message.answer("Пожалуйста, введите корректный тикер, например: BTC")
        return

    symbol = symbol_raw + "USDT"
    await message.answer(f"⏳ Строю карту ликвидности для {symbol} (1H)...")

    data = await backend_get(f"/liquidity/{symbol}", {"tf": "1h"})
    if not data or not data.get("levels"):
        await message.answer("❌ Не удалось получить уровни ликвидности.")
        await state.clear()
        return

    levels = data["levels"]
    text_lines = [f"🗺 <b>Radar Liquidity Map — {symbol} (1H)</b>", ""]

    # Разделим уровни на над/под ценой, если есть last_price
    last_price = data.get("last_price")
    above = []
    below = []
    if last_price:
        for lvl in levels:
            if lvl["price"] >= last_price:
                above.append(lvl)
            else:
                below.append(lvl)
    else:
        above = levels

    if above:
        text_lines.append("🔼 Ликвидность над ценой:")
        for lvl in above[:5]:
            text_lines.append(
                f"• {lvl['price']} — {lvl['type']} ({lvl['comment']})"
            )
        text_lines.append("")

    if below:
        text_lines.append("🔽 Ликвидность под ценой:")
        for lvl in below[:5]:
            text_lines.append(
                f"• {lvl['price']} — {lvl['type']} ({lvl['comment']})"
            )
        text_lines.append("")

    if not above and not below:
        text_lines.append("Нет выделенных уровней ликвидности.")

    await message.answer("\n".join(text_lines))
    await state.clear()
