from pydantic import BaseModel


class WeatherAverages(BaseModel):
    average_temperature: float
    average_wind_speed: float
    average_relative_humidity: float
    average_cloud_cover: float


class ScoreBreakdown(BaseModel):
    temperature: float
    wind_speed: float
    relative_humidity: float
    cloud_cover: float
    total: float


class CityWeatherScore(BaseModel):
    city: str
    country: str
    weather: WeatherAverages
    scores: ScoreBreakdown


class CitiesScoresResponse(BaseModel):
    start_date: str
    end_date: str
    results: list[CityWeatherScore]