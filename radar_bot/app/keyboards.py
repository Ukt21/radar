from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def market_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="BTC/USDT", callback_data="pair_btc"),
                InlineKeyboardButton(text="ETH/USDT", callback_data="pair_eth"),
            ],
            [
                InlineKeyboardButton(text="SUI/USDT", callback_data="pair_sui"),
                InlineKeyboardButton(text="SOL/USDT", callback_data="pair_sui"),
            ],
            [
                InlineKeyboardButton(text="Выбрать таймфрейм ⏱️", callback_data="tf_menu"),
            ]
        ]
    )


def timeframe_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="15m", callback_data="tf_15m"),
                InlineKeyboardButton(text="1h", callback_data="tf_1h"),
                InlineKeyboardButton(text="4h", callback_data="tf_4h"),
            ],
            [
                InlineKeyboardButton(text="Назад ↩️", callback_data="back_market"),
            ]
        ]
    )
