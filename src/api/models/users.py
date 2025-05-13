from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

from database.core import Base


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    username: Mapped[str]
