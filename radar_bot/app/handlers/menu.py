from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from utils.premium_db import ensure_trial_started, is_premium_active, get_user_status_text
from keyboards.main_menu import main_menu

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    uid = message.from_user.id
    await ensure_trial_started(uid)

    status = await get_user_status_text(uid)
    premium = await is_premium_active(uid)

    await message.answer(
        status + "\n\nВыбери раздел:",
        reply_markup=main_menu(premium)
    )
