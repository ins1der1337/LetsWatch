from datetime import datetime
from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.types import Integer, DateTime

from api.exceptions import UnavailableServiceException
from config import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class DataBaseHelper:
    def __init__(self, url: str, echo: int):
        self._engine: AsyncEngine = create_async_engine(url=url, echo=echo)
        self._session_factory = async_sessionmaker(bind=self._engine)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except OperationalError as e:
                await session.rollback()
                raise UnavailableServiceException(message=str(e))
            finally:
                await session.close()

    async def dispose(self) -> None:
        await self._engine.dispose()


db_helper = DataBaseHelper(url=str(settings.db.url), echo=int(settings.db.echo))
DbSession = Annotated[AsyncSession, Depends(db_helper.get_session)]
