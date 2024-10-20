# testing file

import pytest
from fastapi.testclient import TestClient
from app import app
from unittest.mock import patch

client = TestClient(app)

def test_version():
    """
    Test if the /version endpoint returns the correct version
    """
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == "v0.0.1"

@patch('requests.get')
def test_temperature(mock_get):
    """
    Test the /temperature endpoint by mocking the requests.get call
    """
    # Mock response data
    mock_response_data = [
        {
            'sensors': [
                {'unit': '°C', 'lastMeasurement': {'value': '22.5'}},
                {'unit': '°C', 'lastMeasurement': {'value': '24.0'}},
            ]
        },
        {
            'sensors': [
                {'unit': '°C', 'lastMeasurement': {'value': '21.5'}}
            ]
        }
    ]

    mock_get.return_value.json.return_value = mock_response_data

    response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json() == (22.5+24.0+21.5)/3  # Average of 22.5, 24.0, and 21.5
