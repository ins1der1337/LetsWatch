from typing import Annotated

from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends

from core.database import db_helper
from core.schemas.movies import PaginationParams, FiltersParams

# Зависимость сессии
DbSession = Annotated[AsyncSession, Depends(db_helper.get_session)]

# Зависимость пагинации
PaginationDep = Annotated[PaginationParams, Depends()]

# Зависимость фильтров поиска
FiltersDep = Annotated[FiltersParams, Depends()]
