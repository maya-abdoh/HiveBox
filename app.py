""" hivebox server """
from datetime import datetime
import configparser
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI,Response
import requests

app = FastAPI()

config = configparser.ConfigParser()
config.read('config.ini')

VERSION = config.get('app', 'version')

@app.get("/version")
def version() -> str:
    """
    Returns the current application version
    """
    return VERSION

@app.get("/temperature")
def temperature() -> float:
    """
    Returns the average temperature in celcius
    across all opensensemap boxes
    """
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
        return 0

    return sum(temperatures) / len(temperatures)

@app.get("/metrics")
async def get_metrics():
    "Get default Prometheus metrics for the application"
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
