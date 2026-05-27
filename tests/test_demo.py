from fastapi.testclient import TestClient

from pseudo_apis.main import app


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_booking_api() -> None:
    client = TestClient(app)

    response = client.post(
        "/bookings",
        json={"user_id": "usr_101", "trip_id": "trip_goa_4d", "seats": 2},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
