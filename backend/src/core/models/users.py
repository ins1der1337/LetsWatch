from starlette_admin.contrib.sqla import ModelView
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

from core.database import Base, admin


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    username: Mapped[str]


admin.add_view(ModelView(User))
