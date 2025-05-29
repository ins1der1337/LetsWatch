from typing import Iterable, Sequence

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select

from api.exceptions import NotFoundException, BadRequestException
from api.services.movies import search_model
from api.services.users import UserRepository
from core.models import Review, User
from core.schemas.movies import MovieReadSchema, MoviesResponseSchema
from core.schemas.reviews import ReviewCreateSchema, ReviewResponseSchema, ReviewReadSchema


class ReviewsRepository:

    @classmethod
    async def rate_movie(
        cls,
        session: AsyncSession,
        tg_id: int,
        movie_id: int,
        review_data: ReviewCreateSchema,
    ) -> Review:

        user = await UserRepository.get_user_by_tg_id(session, tg_id)

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
    ) -> ReviewReadSchema:
        review = await session.scalar(
            select(Review).where(Review.tg_id == tg_id, Review.movie_id == movie_id)
        )

        if not review:
            raise NotFoundException("Отзыв не найден")

        review_schema = ReviewReadSchema.model_validate(review)
        movie = search_model.search_movie_by_movie_id(movie_id=review_schema.movie_id)
        movie_schema = MoviesResponseSchema.model_validate(movie)
        movie_data = {
            "title": movie_schema.movies[0].title,
            "year": movie_schema.movies[0].year,
        }

        return ReviewReadSchema(**review_schema.model_dump(), **movie_data)

    @classmethod
    async def get_user_reviews(
        cls, session: AsyncSession, tg_id: int
    ) -> ReviewResponseSchema:
        reviews = await session.scalars(select(Review).where(Review.tg_id == tg_id))

        res: list[ReviewReadSchema] = []

        for review in reviews.all():
            review_schema = ReviewReadSchema.model_validate(review)
            movie = search_model.search_movie_by_movie_id(movie_id=review_schema.movie_id)

            movie_schema = MoviesResponseSchema.model_validate(movie)
            movie_data = {
                "title": movie_schema.movies[0].title,
                "year": movie_schema.movies[0].year,
            }
            data = {**review_schema.model_dump(), **movie_data}

            result = ReviewReadSchema(**data)
            res.append(result)

        return ReviewResponseSchema(reviews=res)
