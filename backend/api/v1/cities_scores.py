import logging
from datetime import date, timedelta

import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.services.weather_ranking_service import WeatherRankingService
from backend.schemas.weather import CitiesScoresResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["weather"])


@router.get("/cities-scores", response_model=CitiesScoresResponse)
async def get_cities_scores(
    start_date: date | None = Query(
        default=None,
        description="Start date in YYYY-MM-DD format. Defaults to yesterday.",
    ),
    end_date: date | None = Query(
        default=None,
        description="End date in YYYY-MM-DD format. Defaults to yesterday.",
    ),
) -> CitiesScoresResponse:
    yesterday = date.today() - timedelta(days=1)

    resolved_start_date = start_date or yesterday
    resolved_end_date = end_date or yesterday

    if resolved_start_date > resolved_end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be later than end date.",
        )

    if resolved_end_date > yesterday:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be in the future. Please select yesterday or an earlier date.",
        )

    service = WeatherRankingService()

    try:
        return await service.get_ranked_cities(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

    except httpx.HTTPStatusError as error:
        logger.exception("Open-Meteo returned an HTTP error")

        if error.response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="Weather service is temporarily busy. Please try again in a moment.",
            ) from error

        raise HTTPException(
            status_code=502,
            detail="Weather service is temporarily unavailable. Please try again later.",
        ) from error

    except httpx.RequestError as error:
        logger.exception("Open-Meteo request failed")

        raise HTTPException(
            status_code=502,
            detail="Could not connect to the weather service. Please try again later.",
        ) from error

    except ValueError as error:
        logger.exception("Weather data validation failed")

        raise HTTPException(
            status_code=502,
            detail="Weather data is currently unavailable for the selected date range.",
        ) from error

    except Exception as error:
        logger.exception("Unexpected weather ranking error")

        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while calculating weather scores.",
        ) from error