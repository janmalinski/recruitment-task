# Weather Ranker Fullstack App

Recruitment task implementation using FastAPI and a minimal HTML/CSS/JavaScript frontend.

The application retrieves historical hourly weather data from the Open-Meteo API and generates a ranked list of cities using a weighted weather scoring algorithm.

---

## Features

- FastAPI backend
- Frontend weather dashboard with date range filtering
- Open-Meteo historical weather API integration
- Weather ranking for:
  - Warsaw, Poland
  - Gdansk, Poland
  - Berlin, Germany
  - Krakow, Poland
  - Nurnberg, Germany
  - Munich, Germany
- Default date range: yesterday
- Optional `start_date` and `end_date`
- Docker support
- Unit test for `/api/v1/cities-scores`
- User-friendly error handling
- Retry and rate-limit handling
- In-memory TTL cache
- Limited request concurrency

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- HTTPX AsyncClient

### Frontend

- HTML
- CSS
- Vanilla JavaScript

### Tooling

- Docker
- Pytest

---

## Scoring Algorithm

Open-Meteo provides hourly weather data.

This implementation aggregates hourly values using arithmetic mean before calculating the final city score.

### Final Score Weights

| Metric | Weight |
|---|---:|
| Temperature | 35% |
| Wind speed | 20% |
| Relative humidity | 20% |
| Cloud cover | 25% |

### Temperature

- 24°C = 10 points
- Every 1°C deviation subtracts 1 point
- Minimum: 0 points

### Wind Speed

- 0 m/s = 10 points
- Every 1 m/s subtracts 1 point
- Minimum: 0 points

### Relative Humidity

- 50% = 10 points
- 0% or 100% = 0 points

### Cloud Cover

- 25% = 10 points
- 0% or 100% = 0 points

---

## Environment Variables

Create local environment file:

```bash
cp .env.example .env
```

Available variable:

```env
OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com
```

The application provides a default value for `OPEN_METEO_BASE_URL`, so it can run without local `.env` configuration.

---

## Run with Docker

Build and start the application:

```bash
docker compose up --build
```

Open frontend:

```txt
http://localhost:8000
```

Open API documentation:

```txt
http://localhost:8000/docs
```

Open API endpoint:

```txt
http://localhost:8000/api/v1/cities-scores
```

Example with custom dates:

```txt
http://localhost:8000/api/v1/cities-scores?start_date=2025-01-01&end_date=2025-01-03
```

---

## Running Tests with Docker

```bash
docker compose run --rm weather-ranker pytest -v
```

---

## API

### `GET /api/v1/cities-scores`

Returns a sorted list of cities with weather statistics and calculated scores.

### Query Parameters

| Name | Required | Description |
|---|---:|---|
| `start_date` | No | Start date in `YYYY-MM-DD` format. Defaults to yesterday. |
| `end_date` | No | End date in `YYYY-MM-DD` format. Defaults to yesterday. |

### Example

```txt
/api/v1/cities-scores?start_date=2025-01-01&end_date=2025-01-03
```

---

## API Response Example

```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-01",
  "results": [
    {
      "city": "Munich",
      "country": "Germany",
      "weather": {
        "average_temperature": 4.2,
        "average_wind_speed": 2.1,
        "average_relative_humidity": 75.4,
        "average_cloud_cover": 80.5
      },
      "scores": {
        "temperature": 0,
        "wind_speed": 7.9,
        "relative_humidity": 4.92,
        "cloud_cover": 2.6,
        "total": 3.21
      }
    }
  ]
}
```

---

## Project Structure

```txt
weather-ranker-fullstack/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       └── cities_scores.py
│   ├── core/
│   │   └── config.py
│   ├── domain/
│   │   ├── cities.py
│   │   └── scoring.py
│   ├── schemas/
│   │   └── weather.py
│   ├── services/
│   │   ├── open_meteo_client.py
│   │   ├── open_meteo_endpoints.py
│   │   └── weather_ranking_service.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_cities_scores.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

---

## Architecture

```txt
Frontend HTML/CSS/JS
        │
        ▼
FastAPI route: GET /api/v1/cities-scores
        │
        ▼
WeatherRankingService
        │
        ├── city definitions
        ├── hourly weather aggregation
        ├── scoring algorithm
        └── OpenMeteoClient
                │
                ▼
          Open-Meteo API
```

---

## Technical Decisions

### Historical Weather API

The Open-Meteo archive API is used because the application works with historical weather data.

The default range is yesterday, but users can also provide custom historical date ranges.

### Hourly Data Aggregation

Open-Meteo returns hourly weather data.

The application aggregates hourly values using arithmetic mean before calculating the final score.

This approach keeps the ranking deterministic, simple and easy to test.

### Open-Meteo Rate Limiting

The Open-Meteo client includes:

- retry handling
- rate-limit handling
- in-memory TTL cache
- limited concurrency

This significantly reduces the likelihood of HTTP 429 (Too Many Requests) responses caused by excessive concurrent requests to the Open-Meteo API.

Concurrency is limited using `asyncio.Semaphore`.

### Separation of Concerns

The project separates:

- API routing
- configuration
- domain models
- scoring logic
- schemas
- external API integration
- frontend assets

This keeps the codebase maintainable and scalable.

### Coordinates

Latitude and longitude are stored internally because Open-Meteo requires coordinates for weather requests.

Coordinates are intentionally not exposed in the API response because the recruitment task only requires city weather data and ranking.

---

## Error Handling

The API returns user-friendly errors for common scenarios:

- invalid date range
- future end date
- temporary Open-Meteo unavailability
- Open-Meteo rate limiting
- missing weather data

Technical details are logged internally instead of being exposed directly to the user.

---