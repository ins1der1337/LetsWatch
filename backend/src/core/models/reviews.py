from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey

from core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    movie_id: Mapped[int]
    rating: Mapped[int]
