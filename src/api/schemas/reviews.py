from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    user_id: int
    movie_id: int
    rating: int = Field(gt=0, lt=10)


class ReviewReadSchema(ReviewCreateSchema):
    id: int
    created_at: datetime
    updated_at: datetime
