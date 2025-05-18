from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from http_client import api_client

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    # Записываем в бд
    reg_info = await api_client.register_user(message.from_user.id, message.from_user.username)

    await message.answer(f"Здравствуйте, {message.from_user.username}!. {reg_info}")
