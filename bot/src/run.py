from aiogram import Bot, Dispatcher

from handlers import router as main_router
from config import settings
import asyncio
import logging

from http_client import api_client

bot = Bot(token=settings.bot.token)
dp = Dispatcher()


# Функции для управления жизненным циклом сессии
async def on_startup_callback(dispatcher: Dispatcher):
    print("Бот запускается...")
    # Создаем сессию aiohttp при старте бота
    await api_client.create_session()
    print("Сессия ApiClient создана.")

async def on_shutdown_callback(dispatcher: Dispatcher):
    print("Бот останавливается...")
    # Закрываем сессию aiohttp при остановке бота
    await api_client.close_session()
    print("Сессия ApiClient закрыта.")


async def main():
    logging.basicConfig(level=logging.INFO)

    dp.startup.register(on_startup_callback)
    dp.shutdown.register(on_shutdown_callback)

    dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Bot deactivated")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
