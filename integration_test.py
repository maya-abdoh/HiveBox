"""
Integration tests for the HiveBox application.
"""

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_version():
    """
    Test the /version endpoint to ensure it returns the correct version.
    """
    response = client.get("/version")
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_temperature(monkeypatch):
    """
    Test the /temperature endpoint to ensure it returns a valid float
    by mocking the OpenSenseMap API response.
    """

    # Mock response for the OpenSenseMap API
    mock_response = [
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

    # Mock requests.get to return a mocked response
    def mock_get():
        """
        Mocks the requests.get function to return a predefined JSON response.
        """
        return type("MockResponse", (object,), {"json": lambda: mock_response})

    # Use monkeypatch to substitute the real requests.get with our mock
    monkeypatch.setattr("requests.get", mock_get)

    # Send a request to /temperature and check the response
    response = client.get("/temperature")
    assert response.status_code == 200
    assert isinstance(response.json(), float)

    # Calculate expected average for assertion
    expected_average = (22.5 + 23.0 + 24.5) / 3
    assert response.json() == expected_average
