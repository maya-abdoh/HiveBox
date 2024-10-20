""" hivebox server """
from datetime import datetime
import requests
from fastapi import FastAPI
import configparser

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

