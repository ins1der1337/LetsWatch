from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreateSchema(BaseModel):
    rating: int = Field(gt=0, le=10)

    model_config = ConfigDict(extra="forbid")


class ReviewReadSchema(ReviewCreateSchema):
    id: int
    tg_id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewResponseSchema(BaseModel):
    reviews: list[ReviewReadSchema]
