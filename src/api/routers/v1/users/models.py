from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import String

from database.core import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True)
