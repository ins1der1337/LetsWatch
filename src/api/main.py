from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from api.exceptions import AppException
from api.routers import main_router
from database.core import DbSession, db_helper
from config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    # startup
    yield

    # shutdown
    print("Подключение к БД разорвано...")
    await db_helper.dispose()


app = FastAPI(
    title="LetsWatch",
    lifespan=lifespan,
    version="0.1.5",
    default_response_class=ORJSONResponse,
)

app.include_router(main_router)


@app.exception_handler(AppException)
def handle_not_found_error(request: Request, exc: AppException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/")
def get_root():
    return {"message": "Api is working!"}


@app.get("/version")
async def get_database_version(session: DbSession):
    res = await session.execute(text("SELECT VERSION()"))
    return {"version": res.scalar()}


if __name__ == "__main__":
    uvicorn.run(
        app="src.api.main:app",
        reload=True,
        port=settings.api.port,
        host=settings.api.host,
    )
