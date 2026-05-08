from dataclasses import dataclass


@dataclass(frozen=True)
class MetricScores:
    temperature: float
    wind_speed: float
    relative_humidity: float
    cloud_cover: float
    total: float


def clamp(value: float, min_value: float = 0.0, max_value: float = 10.0) -> float:
    return max(min_value, min(value, max_value))


def score_temperature(value: float) -> float:
    return clamp(10.0 - abs(value - 24.0))


def score_wind_speed(value: float) -> float:
    return clamp(10.0 - value)


def score_relative_humidity(value: float) -> float:
    # 50% is best.
    # Distance 50 percentage points from the optimum gives 0 points.
    return clamp(10.0 - (abs(value - 50.0) / 5.0))


def score_cloud_cover(value: float) -> float:
    # 25% is best.
    # Requirement says 0% and 100% should receive 0 points.
    # The function below is triangular around 25% and additionally clamps exact extremes.
    if value <= 0.0 or value >= 100.0:
        return 0.0

    if value <= 25.0:
        return clamp(value / 25.0 * 10.0)

    return clamp((100.0 - value) / 75.0 * 10.0)


def calculate_metric_scores(
    temperature: float,
    wind_speed: float,
    relative_humidity: float,
    cloud_cover: float,
) -> MetricScores:
    temperature_points = score_temperature(temperature)
    wind_speed_points = score_wind_speed(wind_speed)
    humidity_points = score_relative_humidity(relative_humidity)
    cloud_cover_points = score_cloud_cover(cloud_cover)

    total = (
        temperature_points * 0.35
        + wind_speed_points * 0.20
        + humidity_points * 0.20
        + cloud_cover_points * 0.25
    )

    return MetricScores(
        temperature=round(temperature_points, 2),
        wind_speed=round(wind_speed_points, 2),
        relative_humidity=round(humidity_points, 2),
        cloud_cover=round(cloud_cover_points, 2),
        total=round(total, 2),
    )
