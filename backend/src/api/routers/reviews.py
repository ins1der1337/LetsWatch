from fastapi import APIRouter

from api.dependencies import DbSession
from api.services.reviews import ReviewsRepository
from core.schemas.reviews import (
    ReviewCreateSchema,
    ReviewReadSchema,
    ReviewResponseSchema,
)

router = APIRouter(prefix="/users", tags=["Оценки"])


@router.get("/{tg_id}/reviews", response_model=ReviewResponseSchema)
async def get_movie_review(session: DbSession, tg_id: int):
    reviews = await ReviewsRepository.get_user_reviews(session, tg_id)
    return ReviewResponseSchema(
        reviews=[ReviewReadSchema.model_validate(review) for review in reviews]
    )


@router.get("/{tg_id}/reviews/{movie_id}", response_model=ReviewReadSchema)
async def get_movie_review(session: DbSession, tg_id: int, movie_id: int):
    review = await ReviewsRepository.get_user_movie_review(session, tg_id, movie_id)
    return review


@router.post("/{tg_id}/reviews/{movie_id}", response_model=ReviewReadSchema)
async def create_movie_review(
    session: DbSession, tg_id: int, movie_id: int, review: ReviewCreateSchema
):
    review = await ReviewsRepository.rate_movie(session, tg_id, movie_id, review)
    return review
