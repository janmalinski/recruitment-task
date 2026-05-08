import asyncio
from datetime import date
from statistics import mean
from typing import Any

from backend.domain.cities import CITIES, City
from backend.domain.scoring import calculate_metric_scores
from backend.schemas.weather import (
    CitiesScoresResponse,
    CityWeatherScore,
    ScoreBreakdown,
    WeatherAverages,
)
from backend.services.open_meteo_client import OpenMeteoClient


class WeatherRankingService:
    def __init__(self, client: OpenMeteoClient | None = None) -> None:
        self.client = client or OpenMeteoClient()
        self.semaphore = asyncio.Semaphore(2)

    async def get_ranked_cities(
        self,
        start_date: date,
        end_date: date,
    ) -> CitiesScoresResponse:
        city_score_tasks = [
            self._build_city_score_with_limit(
                city=city,
                start_date=start_date,
                end_date=end_date,
            )
            for city in CITIES
        ]

        results = await asyncio.gather(*city_score_tasks)
        results.sort(key=lambda item: item.scores.total, reverse=True)

        return CitiesScoresResponse(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            results=results,
        )

    async def _build_city_score_with_limit(
        self,
        city: City,
        start_date: date,
        end_date: date,
    ) -> CityWeatherScore:
        async with self.semaphore:
            return await self._build_city_score(
                city=city,
                start_date=start_date,
                end_date=end_date,
            )

    async def _build_city_score(
        self,
        city: City,
        start_date: date,
        end_date: date,
    ) -> CityWeatherScore:
        weather_payload = await self.client.fetch_hourly_weather(
            city=city,
            start_date=start_date,
            end_date=end_date,
        )

        hourly_data = weather_payload.get("hourly")

        if not hourly_data:
            raise ValueError(f"No hourly weather data returned for {city.name}")

        weather_averages = self._calculate_averages(hourly_data)

        metric_scores = calculate_metric_scores(
            temperature=weather_averages.average_temperature,
            wind_speed=weather_averages.average_wind_speed,
            relative_humidity=weather_averages.average_relative_humidity,
            cloud_cover=weather_averages.average_cloud_cover,
        )

        return CityWeatherScore(
            city=city.name,
            country=city.country,
            weather=weather_averages,
            scores=ScoreBreakdown(
                temperature=metric_scores.temperature,
                wind_speed=metric_scores.wind_speed,
                relative_humidity=metric_scores.relative_humidity,
                cloud_cover=metric_scores.cloud_cover,
                total=metric_scores.total,
            ),
        )

    @staticmethod
    def _calculate_averages(hourly_data: dict[str, list[Any]]) -> WeatherAverages:
        return WeatherAverages(
            average_temperature=round(mean(hourly_data["temperature_2m"]), 2),
            average_wind_speed=round(mean(hourly_data["wind_speed_10m"]), 2),
            average_relative_humidity=round(
                mean(hourly_data["relative_humidity_2m"]),
                2,
            ),
            average_cloud_cover=round(mean(hourly_data["cloud_cover"]), 2),
        )