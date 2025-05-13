from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy import func

from database.core import Base


class Review(Base):
    __tablename__ = "reviews"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[int]
    rating: Mapped[int]

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
