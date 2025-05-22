from typing import Iterable

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select

from api.exceptions import NotFoundException, BadRequestException
from api.services.users import UserRepository
from core.models import Review
from core.schemas.reviews import ReviewCreateSchema


class ReviewsRepository:

    @classmethod
    async def rate_movie(
        cls,
        session: AsyncSession,
        tg_id: int,
        movie_id: int,
        review_data: ReviewCreateSchema,
    ) -> Review:

        user = await session.scalar(
            select(Review)
            .where(Review.tg_id == tg_id)
        )

        if not user:
            raise NotFoundException("Пользователь не найден в базе данных")

        review = await session.scalar(
            select(Review)
            .where(Review.tg_id == tg_id, Review.movie_id == movie_id)
            .order_by(Review.id)
        )

        if review:
            raise BadRequestException("Отзыв на этот фильм уже имеется")

        data = {"tg_id": tg_id, "movie_id": movie_id, **review_data.model_dump()}

        stmt = insert(Review).values(**data).returning(Review)

        review = await session.scalar(stmt)
        await session.commit()
        await session.refresh(review)

        return review

    @classmethod
    async def get_user_movie_review(
        cls, session: AsyncSession, tg_id: int, movie_id: int
    ) -> Review:
        review = await session.scalar(
            select(Review).where(Review.tg_id == tg_id, Review.movie_id == movie_id)
        )
        if not review:
            raise NotFoundException("Отзыв не найден")
        return review

    @classmethod
    async def get_user_reviews(
        cls, session: AsyncSession, tg_id: int
    ) -> Iterable[Review]:
        res = await session.scalars(select(Review).where(Review.tg_id == tg_id))
        return res.all()
