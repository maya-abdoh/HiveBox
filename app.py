""" hivebox server """
from datetime import datetime
import configparser
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
import requests
import aioredis
from minio import Minio
from minio.error import S3Error
from aioredis.exceptions import RedisError

app = FastAPI()

# Configuration
config = configparser.ConfigParser()
config.read('config.ini')
VERSION = config.get('app', 'version')

# Redis Configuration
REDIS_HOST = config.get('redis', 'host', fallback='localhost')
REDIS_PORT = config.get('redis', 'port', fallback=6379)
redis_cache = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")

# MinIO Configuration
MINIO_ENDPOINT = config.get('minio', 'endpoint', fallback='localhost:9000')
MINIO_ACCESS_KEY = config.get('minio', 'access_key')
MINIO_SECRET_KEY = config.get('minio', 'secret_key')
MINIO_BUCKET = config.get('minio', 'bucket')

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure MinIO bucket exists
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

@app.get("/version")
async def version():
    """
    Returns the current application version
    """
    return VERSION

@app.get("/temperature")
async def temperature():
    """
    Returns the average temperature in Celsius across all OpenSenseMap boxes
    along with a status based on the temperature value.
    """
    cached_temp = await redis_cache.get("average_temperature")
    if cached_temp:
        return {"average_temperature": float(cached_temp), "status": "Cached"}

    phenomenon = "temperature"
    date = datetime.now().isoformat() + 'Z'
    res = requests.get(
        f"https://api.opensensemap.org/boxes?date={date}&phenomenon={phenomenon}",
        timeout=1000
    )
    all_boxes = res.json()

    temperatures = [
        float(sensor['lastMeasurement']['value'])
        for box in all_boxes
        for sensor in box['sensors']
        if sensor.get('unit') == '°C' and 'lastMeasurement' in sensor
    ]

    if not temperatures:
        return {"average_temperature": None, "status": "No data available"}

    avg_temp = sum(temperatures) / len(temperatures)
    await redis_cache.set("average_temperature", avg_temp, ex=300)  # Cache for 5 minutes

    status = "Too Cold" if avg_temp < 10 else "Good" if 11 <= avg_temp <= 36 else "Too Hot"
    return {"average_temperature": avg_temp, "status": status}

@app.get("/metrics")
async def get_metrics():
    "Get default Prometheus metrics for the application"
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/readyz")
async def readyz():
    """
    Checks if more than 50% of senseBoxes are accessible and cache content is recent.
    """
    cached_readyz = await redis_cache.get("readyz_status")
    if cached_readyz:
        return {"status": cached_readyz.decode('utf-8')}

    # Fetch boxes
    date = datetime.now().isoformat() + 'Z'
    res = requests.get(f"https://api.opensensemap.org/boxes?date={date}", timeout=1000)
    all_boxes = res.json()
    accessible_boxes = len(all_boxes)

    # Cache the result
    total_boxes = int(config.get('app', 'total_boxes')) // 2
    status = "Healthy" if accessible_boxes >=  total_boxes + 1 else "Unhealthy"
    await redis_cache.set("readyz_status", status, ex=300)
    return {"status": status}

@app.get("/store")
async def store():
    """
    Stores data to MinIO immediately and resets cache.
    """
    try:
        data = {"timestamp": datetime.now().isoformat(), "data": "sample"}
        # Save to MinIO
        minio_client.put_object(
            MINIO_BUCKET,
            f"data_{data['timestamp']}.json",
            data,
            len(str(data).encode('utf-8')),
            content_type="application/json"
        )
        # Clear Redis cache
        await redis_cache.flushdb()
        return {"status": "Data stored successfully"}
    except S3Error as _s3_error:
        # Handles specific MinIO (S3) errors
        return {"status": "Failed to store data"}
    except RedisError as _redis_error:
        # Handles Redis-specific errors
        return {"status": "Failed to clear Redis cache"}
