from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAIRS = {
    "btc": "BTC/USDT",
    "eth": "ETH/USDT",
    "sui": "SUI/USDT",
    "sol": "SOL/USDT",
}


def market_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="BTC/USDT", callback_data="pair:btc"),
                InlineKeyboardButton(text="ETH/USDT", callback_data="pair:eth"),
            ],
            [
                InlineKeyboardButton(text="SUI/USDT", callback_data="pair:sui"),
                InlineKeyboardButton(text="SOL/USDT", callback_data="pair:sol"),
            ],
        ]
    )


def timeframe_menu(pair_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="15m",
                    callback_data=f"analyze:{pair_code}:15m",
                ),
                InlineKeyboardButton(
                    text="1h",
                    callback_data=f"analyze:{pair_code}:1h",
                ),
                InlineKeyboardButton(
                    text="4h",
                    callback_data=f"analyze:{pair_code}:4h",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data="back:markets",
                )
            ],
        ]
    )

