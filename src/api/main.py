import uvicorn
from fastapi import FastAPI

from src.core.config import settings

app = FastAPI(title="LetsWatch")


@app.get("/")
def get_root():
    return {"message": "Api is working!"}


if __name__ == "__main__":
    uvicorn.run(
        app="src.api.main:app",
        reload=True,
        port=settings.api.port,
        host=settings.api.host,
    )
