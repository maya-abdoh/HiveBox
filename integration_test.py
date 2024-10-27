"""
Integration tests for the FastAPI application.
"""

import dataclasses
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@dataclasses.dataclass
class MockResponse:
    """
    Mock response to mimic the behavior of requests.get().json()
    when called to retrieve data.
    """
    def json(self):
        "convert to json"
        return [
            {
                "sensors": [
                    {"unit": "°C", "lastMeasurement": {"value": "22.5"}},
                    {"unit": "°C", "lastMeasurement": {"value": "23.0"}},
                ]
            },
            {
                "sensors": [
                    {"unit": "°C", "lastMeasurement": {"value": "24.5"}},
                ]
            },
        ]

def test_version():
    """
    Test the /version endpoint to ensure it returns the correct version.
    """
    response = client.get("/version")
    assert response.status_code == 200
    assert isinstance(response.json(), str)

def test_temperature_integration(monkeypatch):
    """
    Test the /temperature endpoint to ensure it returns a valid response
    with average temperature and status by mocking the OpenSenseMap API response.
    """
    def mock_get(*_args, **_kwargs):
        return MockResponse()
    monkeypatch.setattr("requests.get", mock_get)
    response = client.get("/temperature")
    assert response.status_code == 200
    data = response.json()
    expected_average = (22.5 + 23.0 + 24.5) / 3
    assert data["average_temperature"] == expected_average
    assert data["status"] == "Good"
def test_metrics_integration():
    """
    Test the /metrics endpoint to ensure Prometheus metrics are accessible.
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    