from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("ai_menu"))
async def cmd_ai_menu(message: Message):
    """
    Простая команда для проверки, что router работает.
    """
    await message.answer(
        "👋 Привет! Это AI-меню радар-бота.\n\n"
        "Пока я просто тестовая команда.\n"
        "Скоро здесь будет:\n"
        "• AI-анализ рынка\n"
        "• Картинка с анализом\n"
        "• Меню с кнопками для выбора пары и таймфрейма."
    )


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Базовая /start через backend-worker.
    """
    await message.answer(
        "🚀 Radar backend запущен.\n"
        "Напиши /ai_menu, чтобы проверить AI-меню."
    )
