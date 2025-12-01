from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="📊 Анализ монеты", callback_data="menu_analyze"),
    )
    kb.row(
        InlineKeyboardButton(text="🗺 Карта ликвидности", callback_data="menu_liquidity"),
    )
    kb.row(
        InlineKeyboardButton(text="💹 BTC обзор", callback_data="menu_btc"),
    )
    return kb.as_markup()
