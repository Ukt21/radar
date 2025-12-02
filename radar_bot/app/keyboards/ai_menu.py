from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ai_main_menu():
    """
    Премиальное главное меню AI.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 ПРЕМИУМ АНАЛИТИКА",
                callback_data="ai_premium_analyze"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎 Монета",
                callback_data="ai_menu_symbols"
            ),
            InlineKeyboardButton(
                text="⏱ Таймфрейм",
                callback_data="ai_menu_timeframes"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🧠 Режим AI",
                callback_data="ai_menu_modes"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👤 Профиль & Подписка",
                callback_data="ai_menu_profile"
            ),
        ]
    ])
    return kb


def ai_symbol_menu():
    """
    Выбор монеты.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 SUI",  callback_data="ai_symbol_SUIUSDT"),
            InlineKeyboardButton(text="🟦 BTC",  callback_data="ai_symbol_BTCUSDT"),
            InlineKeyboardButton(text="🟣 ETH",  callback_data="ai_symbol_ETHUSDT"),
        ],
        [
            InlineKeyboardButton(text="🟢 SOL",  callback_data="ai_symbol_SOLUSDT"),
            InlineKeyboardButton(text="🔵 AVAX", callback_data="ai_symbol_AVAXUSDT"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="ai_menu_main"),
        ]
    ])
    return kb


def ai_timeframe_menu():
    """
    Выбор таймфрейма.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="15m", callback_data="ai_tf_15m"),
            InlineKeyboardButton(text="1h",  callback_data="ai_tf_1h"),
            InlineKeyboardButton(text="4h",  callback_data="ai_tf_4h"),
        ],
        [
            InlineKeyboardButton(text="1d",  callback_data="ai_tf_1d"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="ai_menu_main"),
        ]
    ])
    return kb


def ai_mode_menu():
    """
    Режимы AI-аналитики.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚡ Быстрый сигнал",
                callback_data="ai_mode_signal"
            )
        ],
        [
            InlineKeyboardButton(
                text="📜 Полный анализ",
                callback_data="ai_mode_full"
            )
        ],
        [
            InlineKeyboardButton(
                text="🖼 Картинка анализа",
                callback_data="ai_mode_image"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Multi TF (15m/1h/4h)",
                callback_data="ai_mode_multi_tf"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="ai_menu_main"
            )
        ]
    ])
    return kb


def ai_result_menu(symbol: str, interval: str):
    """
    Меню под результатом анализа.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🖼 Картинка анализа",
                callback_data=f"ai_result_image|{symbol}|{interval}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="♻️ Обновить",
                callback_data=f"ai_refresh|{symbol}|{interval}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню",
                callback_data="ai_menu_main"
            )
        ]
    ])
    return kb


def ai_profile_menu(is_premium: bool = True):
    """
    Профиль пользователя и статус подписки.
    Сейчас заглушка: все считаются Premium.
    """
    status = "💎 Premium активен" if is_premium else "🔓 Free аккаунт"
    btn_text = "Продлить Premium" if is_premium else "💎 Активировать Premium"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=btn_text,
                callback_data="ai_subscribe_premium"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="ai_menu_main"
            )
        ]
    ])

    return status, kb
