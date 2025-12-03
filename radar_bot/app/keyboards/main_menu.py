
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu(is_premium: bool):
    kb = [
        [InlineKeyboardButton("📊 Крипто-аналитика", callback_data="crypto")],
        [InlineKeyboardButton("🤖 Чат с ИИ", callback_data="ai_chat")],
        [InlineKeyboardButton("📚 Уроки трейдинга", callback_data="lessons")],
    ]

    if not is_premium:
        kb.append([InlineKeyboardButton("💎 Premium", callback_data="premium_info")])

    return InlineKeyboardMarkup(inline_keyboard=kb)
