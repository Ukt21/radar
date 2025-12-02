import httpx
from ..config import BACKEND_URL

async def backend_get(path: str, params: dict | None = None):
    url = f"{BACKEND_URL}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return None
        return resp.json()
