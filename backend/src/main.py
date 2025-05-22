import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from api.dependencies import DbSession
from api.exceptions import AppException
from api.routers import main_router
from core.config import settings
from core.database import db_helper, admin


@asynccontextmanager
async def lifespan(_: FastAPI):
    # startup
    yield

    # shutdown
    await db_helper.dispose()


app = FastAPI(
    title="LetsWatch",
    lifespan=lifespan,
    version="0.1.7",
    default_response_class=ORJSONResponse,
)

app.include_router(main_router)

admin.mount_to(app)


@app.exception_handler(AppException)
def handle_app_exceptions(request: Request, exc: AppException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health-check")
async def get_database_version(session: DbSession):
    res = await session.execute(text("SELECT VERSION()"))
    return {"version": res.scalar()}


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        reload=True,
        port=settings.api.port,
        host=settings.api.host,
    )
