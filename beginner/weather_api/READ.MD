# Weather API

A simple FastAPI service for retrieving weather data from Visual Crossing Weather API with Redis caching and rate limiting.

## Setup

### Prerequisites

- Python 3.8+
- Redis server

### API Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install fastapi uvicorn httpx redis fastapi-limiter
   ```
3. Set environment variables:
   ```
   export VISUAL_CROSSING_API_KEY="your_api_key"
   ```

## Running the API

Start the API server:

```bash
python weather_api.py
```

Or with uvicorn directly:

```bash
uvicorn weather_api:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage

### Endpoints

- `GET /health` - Health check endpoint
- `GET /api/weather/{city_code}` - Get weather data for a specific city

### Request Examples

#### Browser / URL

```
http://localhost:8000/api/weather/Sydney
```

#### Command Line

```bash
curl -X GET "http://localhost:8000/api/weather/London"
```

#### Python

Use the provided `test_api.py` in the same directory:

Run with:
```bash
python test_api.py
```

## Features

- Weather data caching (12-hour expiration)
- Rate limiting (100 requests per hour)
- Error handling with appropriate HTTP status codes