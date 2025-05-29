from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreateSchema(BaseModel):
    rating: int = Field(gt=0, le=10)

    model_config = ConfigDict(extra="forbid")


class ReviewReadSchema(ReviewCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    movie_id: int
    title: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ReviewResponseSchema(BaseModel):
    reviews: list[ReviewReadSchema]
