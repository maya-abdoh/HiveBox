"""
This module contains tests for the FastAPI application.
"""

from unittest.mock import patch  # Standard library import
from fastapi.testclient import TestClient  # Third-party imports
from app import app  # First-party imports

client = TestClient(app)

def test_version():
    """
    Test if the /version endpoint returns the correct version.
    """
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == "v0.0.1"

@patch('app.requests.get')
def test_temperature_status_good(mock_get):
    """
    Test the /temperature endpoint with a 'Good' status by mocking the requests.get call.
    """
    # Mock response data for "Good" temperature range
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
    data = response.json()
    expected_average = (22.5 + 24.0 + 21.5) / 3
    assert data["average_temperature"] == expected_average
    assert data["status"] == "Good"
