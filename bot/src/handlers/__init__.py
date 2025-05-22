from aiogram import Router
from bot.src.handlers.start_search import router as start_router


router = Router()
router.include_router(start_router)
