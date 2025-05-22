from aiogram import Router
from .start_search import router as start_router

router = Router()
router.include_router(start_router)
