from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from starlette_admin.contrib.sqla import ModelView
from core.database import Base, admin


class Review(Base):
    __tablename__ = "reviews"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    movie_id: Mapped[int]
    rating: Mapped[int]

    __table_args__ = (UniqueConstraint("tg_id", "movie_id", name="uq_tg_id_movie_id"),)


admin.add_view(ModelView(Review))
