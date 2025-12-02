from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    text = (
        "📡 <b>Radar</b> — твой AI-радар по крипторынку.\n\n"
        "Доступно:\n"
        "• Анализ монеты\n"
        "• Карта ликвидности\n"
        "• Обзор BTC\n\n"
        "Выбери действие из меню:"
    )
    from ..keyboards.menu import main_menu
    await message.answer(text, reply_markup=main_menu())
