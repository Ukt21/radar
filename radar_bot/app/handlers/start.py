from aiogram import Router, types
from ..keyboards.menu import main_menu

router = Router()

@router.message(commands={"start"})
async def start_cmd(message: types.Message):
    text = (
        "📡 <b>Radar</b> — твой AI-радар по крипторынку.\n\n"
        "Возможности:\n"
        "• Анализ любой монеты к USDT\n"
        "• Карта ликвидности (Equal Highs/Lows, FVG)\n"
        "• BTC обзор и контекст рынка\n"
        "• В будущем — авто-алерты по китам и BTC\n\n"
        "Выбери действие из меню ниже или введи команду вручную."
    )
    await message.answer(text, reply_markup=main_menu())
