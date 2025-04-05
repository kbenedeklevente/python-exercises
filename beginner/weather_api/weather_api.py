from math import ceil
import redis.asyncio as redis
import uvicorn
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.logger import logger
import logging
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import os
import httpx
import json
from datetime import datetime

VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
REDIS_URL = 'redis://localhost:6379'
CACHE_EXPIRATION = 43200

logger = logging.getLogger("weather_api")
logging.basicConfig(level=logging.INFO)

redis_client = redis.from_url(REDIS_URL)

async def service_name_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service


async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    await FastAPILimiter.init(
        redis=redis_client,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "OK"}


@app.get("/api/weather/{city_code}", dependencies=[Depends(RateLimiter(times=100, seconds=3600))])
async def get_weather(city_code: str, request: Request):
    if not city_code:
        raise HTTPException(status_code=400, detail="City code is required")
    
    try:
        # Check if data exists in cache
        cache_key = f"weather:{city_code}"
        cached_data = await redis_client.get(cache_key)
        
        if cached_data:
            logger.info(f"Serving cached data for {city_code}")
            return json.loads(cached_data)
        
        # Fetch data from Visual Crossing Weather API
        async with httpx.AsyncClient() as client:
            weather_api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_code}"
            params = {
                "unitGroup": "metric",
                "key": VISUAL_CROSSING_API_KEY,
                "contentType": "json"
            }
            
            response = await client.get(weather_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise HTTPException(status_code=404, detail="Weather data not found")
            
            # Process and format the data
            weather_data = {
                "location": data.get("address"),
                "currentConditions": data.get("currentConditions"),
                "forecast": data.get("days", [])[:7],
                "lastUpdated": datetime.now().isoformat()
            }
            
            # Store data in Redis cache with expiration
            await redis_client.setex(
                cache_key,
                CACHE_EXPIRATION,
                json.dumps(weather_data)
            )
            
            return weather_data
    
    except httpx.HTTPStatusError as err:
        status_code = err.response.status_code
        
        if status_code in (401, 403):
            raise HTTPException(status_code=status_code, detail="API key error or quota exceeded")
        elif status_code == 404:
            raise HTTPException(status_code=404, detail="City not found")
        else:
            raise HTTPException(status_code=status_code, detail=f"Weather service error: {str(err)}")
    
    except httpx.RequestError as err:
        raise HTTPException(status_code=500, detail=f"Error connecting to weather service: {str(err)}")
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal server error{str(err)}")

if __name__ == "__main__":
    uvicorn.run(
        "weather_api:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )