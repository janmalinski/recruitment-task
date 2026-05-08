import os
from datetime import date

os.environ.setdefault(
    "OPEN_METEO_BASE_URL",
    "https://archive-api.open-meteo.com",
)

from fastapi.testclient import TestClient

from backend.main import create_app
from backend.schemas.weather import (
    CitiesScoresResponse,
    CityWeatherScore,
    ScoreBreakdown,
    WeatherAverages,
)
from backend.services.weather_ranking_service import WeatherRankingService


async def fake_get_ranked_cities(
    self,
    start_date: date,
    end_date: date,
) -> CitiesScoresResponse:
    return CitiesScoresResponse(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        results=[
            CityWeatherScore(
                city="Warsaw",
                country="Poland",
                weather=WeatherAverages(
                    average_temperature=24.0,
                    average_wind_speed=0.0,
                    average_relative_humidity=50.0,
                    average_cloud_cover=25.0,
                ),
                scores=ScoreBreakdown(
                    temperature=10.0,
                    wind_speed=10.0,
                    relative_humidity=10.0,
                    cloud_cover=10.0,
                    total=10.0,
                ),
            ),
            CityWeatherScore(
                city="Berlin",
                country="Germany",
                weather=WeatherAverages(
                    average_temperature=18.0,
                    average_wind_speed=4.0,
                    average_relative_humidity=70.0,
                    average_cloud_cover=60.0,
                ),
                scores=ScoreBreakdown(
                    temperature=4.0,
                    wind_speed=6.0,
                    relative_humidity=6.0,
                    cloud_cover=5.33,
                    total=5.13,
                ),
            ),
        ],
    )


def test_cities_scores_returns_ranked_weather_scores(monkeypatch):
    monkeypatch.setattr(
        WeatherRankingService,
        "get_ranked_cities",
        fake_get_ranked_cities,
    )

    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/api/v1/cities-scores",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-01-01",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["start_date"] == "2025-01-01"
    assert data["end_date"] == "2025-01-01"
    assert len(data["results"]) == 2

    assert data["results"][0]["city"] == "Warsaw"
    assert data["results"][0]["country"] == "Poland"
    assert data["results"][0]["scores"]["total"] == 10.0

    assert data["results"][1]["city"] == "Berlin"
    assert data["results"][1]["country"] == "Germany"
    assert data["results"][1]["scores"]["total"] == 5.13


def test_cities_scores_rejects_invalid_date_range():
    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/api/v1/cities-scores",
        params={
            "start_date": "2025-01-02",
            "end_date": "2025-01-01",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Start date cannot be later than end date."