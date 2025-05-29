from aiogram import Router
from .start_search import router as main_router

router = Router()
router.include_router(main_router)
