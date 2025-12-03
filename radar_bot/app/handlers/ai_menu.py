from aiogram import Router, types
from aiogram.filters import Command
from radar_bot.app.ai_menu.router import ai_menu_router
from ..keyboards.ai_menu import (
    ai_main_menu,
    ai_symbol_menu,
    ai_timeframe_menu,
    ai_mode_menu,
    ai_result_menu,
    ai_profile_menu,
)

from ..ai_client import get_ai_analysis, get_ai_analysis_image

router = Router()

# Простое хранилище состояний по пользователю
# В реале можно заменить на Redis/БД
user_ai_state = {}  # user_id: {"symbol": "SUIUSDT", "tf": "1h", "mode": "full", "premium": True}


def get_user_state(user_id: int):
    if user_id not in user_ai_state:
        user_ai_state[user_id] = {
            "symbol": "SUIUSDT",
            "tf": "1h",
            "mode": "full",   # "signal" / "full" / "image" / "multi_tf"
            "premium": True,  # пока всем даём Premium
        }
    return user_ai_state[user_id]


def extract_signal(text: str) -> str:
    """
    Ищем последнюю строку BUY / SELL / WAIT.
    Если нет — возвращаем "WAIT".
    """
    for line in reversed(text.splitlines()):
        w = line.strip().upper()
        if w in ("BUY", "SELL", "WAIT"):
            return w
    return "WAIT"


# ---------- /start ----------

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    state = get_user_state(message.from_user.id)
    await message.answer(
        f"👋 Добро пожаловать в Radar AI.\n\n"
        f"💎 Статус: {'Premium' if state['premium'] else 'Free'}\n"
        f"Монета по умолчанию: {state['symbol']}\n"
        f"Таймфрейм: {state['tf']}\n\n"
        f"Выбери, что сделать:",
        reply_markup=ai_main_menu()
    )


# ---------- Главное премиум меню ----------

@router.callback_query(lambda c: c.data == "ai_menu_main")
async def ai_menu_main(call: types.CallbackQuery):
    state = get_user_state(call.from_user.id)
    await call.message.edit_text(
        f"📊 <b>Премиальная AI-панель</b>\n\n"
        f"Монета: <code>{state['symbol']}</code>\n"
        f"Таймфрейм: <code>{state['tf']}</code>\n"
        f"Режим: <code>{state['mode']}</code>\n"
        f"Статус: {'💎 Premium' if state['premium'] else '🔓 Free'}\n\n"
        f"Выбери действие:",
        reply_markup=ai_main_menu(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "ai_premium_analyze")
async def ai_premium_analyze(call: types.CallbackQuery):
    state = get_user_state(call.from_user.id)
    symbol = state["symbol"]
    tf = state["tf"]
    mode = state["mode"]

    await call.message.edit_text(
        f"⏳ Запускаю <b>{mode}</b>-анализ для <code>{symbol}</code> • <code>{tf}</code>...\n"
        f"Подожди 3–7 секунд…",
        parse_mode="HTML"
    )

    # Режимы:
    if mode == "signal":
        await handle_quick_signal(call, symbol, tf)
    elif mode == "image":
        await handle_image_mode(call, symbol, tf)
    elif mode == "multi_tf":
        await handle_multi_tf(call, symbol)
    else:  # "full"
        await handle_full_analysis(call, symbol, tf)


# ---------- Выбор монеты ----------

@router.callback_query(lambda c: c.data == "ai_menu_symbols")
async def ai_menu_symbols(call: types.CallbackQuery):
    await call.message.edit_text(
        "💎 Выбери монету:",
        reply_markup=ai_symbol_menu()
    )


@router.callback_query(lambda c: c.data.startswith("ai_symbol_"))
async def ai_choose_symbol(call: types.CallbackQuery):
    symbol = call.data.split("ai_symbol_")[1]
    state = get_user_state(call.from_user.id)
    state["symbol"] = symbol

    await call.message.edit_text(
        f"Монета установлена: <b>{symbol}</b>\n"
        f"Таймфрейм: <code>{state['tf']}</code>\n\n"
        f"Теперь можешь запустить анализ:",
        reply_markup=ai_main_menu(),
        parse_mode="HTML"
    )


# ---------- Выбор таймфрейма ----------

@router.callback_query(lambda c: c.data == "ai_menu_timeframes")
async def ai_menu_timeframes(call: types.CallbackQuery):
    await call.message.edit_text(
        "⏱ Выбери таймфрейм:",
        reply_markup=ai_timeframe_menu()
    )


@router.callback_query(lambda c: c.data.startswith("ai_tf_"))
async def ai_choose_tf(call: types.CallbackQuery):
    tf = call.data.split("ai_tf_")[1]
    state = get_user_state(call.from_user.id)
    state["tf"] = tf

    await call.message.edit_text(
        f"Таймфрейм установлен: <b>{tf}</b>\n"
        f"Монета: <code>{state['symbol']}</code>\n\n"
        f"Теперь можешь запустить анализ:",
        reply_markup=ai_main_menu(),
        parse_mode="HTML"
    )


# ---------- Выбор режима ----------

@router.callback_query(lambda c: c.data == "ai_menu_modes")
async def ai_menu_modes_call(call: types.CallbackQuery):
    await call.message.edit_text(
        "🧠 Выбери режим работы AI:",
        reply_markup=ai_mode_menu()
    )


@router.callback_query(lambda c: c.data.startswith("ai_mode_"))
async def ai_choose_mode(call: types.CallbackQuery):
    mode = call.data.split("ai_mode_")[1]
    state = get_user_state(call.from_user.id)
    state["mode"] = {
        "signal": "signal",
        "full": "full",
        "image": "image",
        "multi_tf": "multi_tf",
    }.get(mode, "full")

    await call.message.edit_text(
        f"Режим установлен: <b>{state['mode']}</b>\n\n"
        f"Монета: <code>{state['symbol']}</code>\n"
        f"Таймфрейм: <code>{state['tf']}</code>\n\n"
        f"Теперь нажми «📊 ПРЕМИУМ АНАЛИТИКА».",
        reply_markup=ai_main_menu(),
        parse_mode="HTML"
    )


# ---------- Профиль и подписка ----------

@router.callback_query(lambda c: c.data == "ai_menu_profile")
async def ai_menu_profile_call(call: types.CallbackQuery):
    state = get_user_state(call.from_user.id)
    status_text, kb = ai_profile_menu(is_premium=state["premium"])

    await call.message.edit_text(
        f"👤 Профиль трейдера\n\n"
        f"ID: <code>{call.from_user.id}</code>\n"
        f"Имя: <b>{call.from_user.full_name}</b>\n\n"
        f"Статус: {status_text}\n\n"
        f"Скоро здесь можно будет оформить реальную подписку 🔐",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "ai_subscribe_premium")
async def ai_subscribe_premium(call: types.CallbackQuery):
    state = get_user_state(call.from_user.id)
    state["premium"] = True  # пока просто включаем

    status_text, kb = ai_profile_menu(is_premium=state["premium"])
    await call.message.edit_text(
        f"✅ Premium активирован.\n\n"
        f"Статус: {status_text}\n\n"
        f"Все функции AI открыты.",
        reply_markup=kb,
        parse_mode="HTML"
    )


# ---------- Обновление результата / картинка из результата ----------

@router.callback_query(lambda c: c.data.startswith("ai_refresh"))
async def ai_refresh(call: types.CallbackQuery):
    _, symbol, tf = call.data.split("|")
    await call.answer("♻️ Обновляю данные...")

    text = await get_ai_analysis(symbol, tf)
    await call.message.edit_text(
        text,
        reply_markup=ai_result_menu(symbol, tf),
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data.startswith("ai_result_image"))
async def ai_result_image(call: types.CallbackQuery):
    _, symbol, tf = call.data.split("|")
    await call.answer("🖼 Генерирую картинку...")

    img_bytes = await get_ai_analysis_image(symbol, tf)
    await call.message.answer_photo(
        img_bytes,
        caption=f"📊 AI-картинка анализа {symbol} • {tf}"
    )


# ---------- Реализация режимов ----------

async def handle_full_analysis(call: types.CallbackQuery, symbol: str, tf: str):
    text = await get_ai_analysis(symbol, tf)
    await call.message.edit_text(
        text,
        reply_markup=ai_result_menu(symbol, tf),
        parse_mode="Markdown"
    )


async def handle_quick_signal(call: types.CallbackQuery, symbol: str, tf: str):
    text = await get_ai_analysis(symbol, tf)
    signal = extract_signal(text)

    emoji = {
        "BUY": "🟢",
        "SELL": "🔴",
        "WAIT": "🟡",
    }.get(signal, "⚪️")

    msg = (
        f"{emoji} <b>Быстрый сигнал AI</b>\n\n"
        f"Монета: <code>{symbol}</code>\n"
        f"ТФ: <code>{tf}</code>\n"
        f"Сигнал: <b>{signal}</b>\n\n"
        f"Детальный анализ ниже 👇\n\n"
        f"{text}"
    )

    await call.message.edit_text(
        msg,
        reply_markup=ai_result_menu(symbol, tf),
        parse_mode="HTML"
    )


async def handle_image_mode(call: types.CallbackQuery, symbol: str, tf: str):
    await call.message.edit_text(
        f"🎨 Рисую картинку анализа для {symbol} • {tf}..."
    )
    img_bytes = await get_ai_analysis_image(symbol, tf)
    await call.message.answer_photo(
        img_bytes,
        caption=f"📊 AI-картинка анализа {symbol} • {tf}"
    )
    # после картинки вернём меню
    await call.message.answer(
        "Можешь запустить новый анализ:",
        reply_markup=ai_main_menu()
    )


async def handle_multi_tf(call: types.CallbackQuery, symbol: str):
    """
    Multi TF: 15m, 1h, 4h
    """
    await call.message.edit_text(
        f"📊 Multi TF анализ для <b>{symbol}</b> (15m / 1h / 4h)...",
        parse_mode="HTML"
    )

    tfs = ["15m", "1h", "4h"]
    blocks = []

    for tf in tfs:
        text = await get_ai_analysis(symbol, tf)
        signal = extract_signal(text)
        emoji = {
            "BUY": "🟢",
            "SELL": "🔴",
            "WAIT": "🟡",
        }.get(signal, "⚪️")

        blocks.append(
            f"{emoji} <b>{symbol}</b> • <code>{tf}</code> • Сигнал: <b>{signal}</b>\n"
            f"{text}\n"
            f"{'-' * 25}\n"
        )

    final_text = "📊 <b>Multi TF AI-анализ</b>\n\n" + "\n".join(blocks)

    await call.message.edit_text(
        final_text,
        reply_markup=ai_main_menu(),
        parse_mode="HTML"
    )
