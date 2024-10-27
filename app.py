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
def temperature():
    """
    Returns the average temperature in Celsius across all OpenSenseMap boxes
    along with a status based on the temperature value.
    """
    phenomenon = "temperature"
    date = datetime.now().isoformat() + 'Z'
    res = requests.get(
        f"https://api.opensensemap.org/boxes?date={date}&phenomenon={phenomenon}",
        timeout=1000
    )
    all_boxes = res.json()

    # Extract temperature values
    temperatures = [
        float(sensor['lastMeasurement']['value'])
        for box in all_boxes
        for sensor in box['sensors']
        if sensor.get('unit') == '°C' and 'lastMeasurement' in sensor
    ]

    if not temperatures:
        return {"average_temperature": None, "status": "No data available"}

    # Calculate the average temperature
    avg_temp = sum(temperatures) / len(temperatures)

    # Determine the status based on the temperature average
    if avg_temp < 10:
        status = "Too Cold"
    elif 11 <= avg_temp <= 36:
        status = "Good"
    else:
        status = "Too Hot"

    return {"average_temperature": avg_temp, "status": status}

@app.get("/metrics")
async def get_metrics():
    "Get default Prometheus metrics for the application"
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
