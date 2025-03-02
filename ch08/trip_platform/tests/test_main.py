from datetime import date

from app.dependencies import time_range
from app.main import app
from fastapi.testclient import TestClient


def test_get_v1_trips_endpoint():
    client = TestClient(app)
    app.dependency_overrides[time_range] = lambda: (date.fromisoformat("2025-02-01"), None)

    response = client.get("/v1/trips")
    assert response.status_code == 200
    assert response.json() == "Request trips from 2025-02-01"
