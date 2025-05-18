from aiohttp import ClientSession

from config import settings


class ApiClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session: ClientSession | None = None

    async def create_session(self):
        if self._session is None:
            print(self._base_url)
            self._session = ClientSession(base_url=f'{self._base_url}/')

    async def close_session(self):
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def register_user(self, tg_id: int, username: str) -> None:
        async with self._session.post(
            f"users/{tg_id}", json={"username": username}, params={"title": t}
        ) as response:
            res = await response.json()
            return res


api_client = ApiClient(base_url=settings.api.url)
