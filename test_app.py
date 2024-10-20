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

