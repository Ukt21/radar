from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN
from .handlers import start, analyze, liquidity, btc


async def main():
    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(analyze.router)
    dp.include_router(liquidity.router)
    dp.include_router(btc.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
