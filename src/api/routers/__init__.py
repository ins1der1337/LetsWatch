from fastapi import APIRouter
from api.routers.users import router as users_router

main_router = APIRouter(prefix="/api")

main_router.include_router(users_router)
