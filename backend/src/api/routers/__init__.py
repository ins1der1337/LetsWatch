from fastapi import APIRouter
from api.routers.users import router as users_router
from api.routers.movies import router as movies_router
from api.routers.reviews import router as reviews_router

main_router = APIRouter(prefix="/api")

main_router.include_router(users_router)
main_router.include_router(reviews_router)
main_router.include_router(movies_router)
