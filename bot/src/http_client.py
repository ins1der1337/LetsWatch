from aiohttp import ClientSession
from typing import Optional
from config import settings


class ApiClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session: ClientSession | None = None

    async def create_session(self):
        if self._session is None:
            self._session = ClientSession(base_url=f"{self._base_url}/")

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def register_user(self, tg_id: int, username: str) -> None:
        async with self._session.post(
            f"users/{tg_id}", json={"username": username}
        ) as response:
            res = await response.json()
            return res

    async def ssearch_movie(
        self,
        actor: Optional[str] = None,
        genre: Optional[str] = None,
        title: Optional[str] = None,
    ):

        params = {"limit": 5, "page": 1}

        if actor:
            params["actor"] = actor
        if genre:
            params["genre"] = genre
        if title:
            params["title"] = title

        async with self._session.get("movies", params=params) as response:
            return await response.json()

    @property
    def session(self):
        return self._session

    async def send_rating(self, tg_id: int, movie_id: int, rating: int) -> dict:
        url = f"users/{tg_id}/reviews/{movie_id}"
        payload = {"rating": rating}
        async with self._session.post(url, json=payload) as response:
            return await response.json()
        
    async def get_user_reviews(self, tg_id: int):
        url = f"users/{tg_id}/reviews"
        async with self._session.get(url) as response:
            return await response.json()

api_client = ApiClient(base_url=settings.api.url)
