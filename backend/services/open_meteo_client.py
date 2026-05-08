import asyncio
from datetime import date
from typing import Any

import httpx
from cachetools import TTLCache

from backend.core.config import settings
from backend.domain.cities import City
from backend.services.open_meteo_endpoints import OpenMeteoEndpoint


class OpenMeteoClient:
    _cache = TTLCache(maxsize=512, ttl=60 * 60)

    def __init__(
        self,
        base_url: str = settings.open_meteo_base_url,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch_hourly_weather(
        self,
        city: City,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        cache_key = (
            city.name,
            city.latitude,
            city.longitude,
            start_date.isoformat(),
            end_date.isoformat(),
        )

        if cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{self.base_url}{OpenMeteoEndpoint.ARCHIVE}"

        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "wind_speed_10m",
                    "relative_humidity_2m",
                    "cloud_cover",
                ]
            ),
            "timezone": "auto",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries + 1):
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")

                    delay = (
                        int(retry_after)
                        if retry_after and retry_after.isdigit()
                        else 2**attempt
                    )

                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()

                data = response.json()
                self._cache[cache_key] = data

                return data

        raise httpx.HTTPStatusError(
            "Open-Meteo rate limit exceeded after retries",
            request=response.request,
            response=response,
        )