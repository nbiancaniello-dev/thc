import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

DEFAULT_DRAGON_BALL_API_URL = "https://dragonball-api.com/api"

DragonBallCharacter = dict[str, int | str]


class DragonBallClient:
    """Thin async client for https://web.dragonball-api.com/documentation."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("DRAGON_BALL_API_URL")
            or DEFAULT_DRAGON_BALL_API_URL
        ).rstrip("/")
        self.timeout = timeout
        self._transport = transport

    def _http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
            transport=self._transport,
        )

    async def _fetch_character(
        self, http: httpx.AsyncClient, character_id: int
    ) -> DragonBallCharacter | None:
        # GET {base_url}/characters/{id} -> only "id" and "name" are kept
        try:
            response = await http.get(f"/characters/{character_id}")
            response.raise_for_status()
            data = response.json()
            return {"id": data["id"], "name": data["name"]}
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            logger.warning(
                "Error fetching Dragon Ball character with ID %s: %s",
                character_id,
                error,
            )
            return None

    async def get_dragon_ball_character_by_id(
        self, character_id: int
    ) -> DragonBallCharacter | None:
        async with self._http_client() as http:
            return await self._fetch_character(http, character_id)

    async def get_dragon_ball_characters_by_ids(
        self, ids: list[int] | None
    ) -> list[DragonBallCharacter]:
        unique_ids = list(dict.fromkeys(ids or []))
        if not unique_ids:
            return []

        async with self._http_client() as http:
            results = await asyncio.gather(
                *(self._fetch_character(http, character_id) for character_id in unique_ids)
            )

        # Filter out ids that could not be resolved
        return [character for character in results if character is not None]
