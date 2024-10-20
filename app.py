""" hivebox server """
from datetime import datetime
import configparser
from fastapi import FastAPI
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
