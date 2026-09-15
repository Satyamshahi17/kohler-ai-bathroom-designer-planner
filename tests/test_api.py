import pytest

flask = pytest.importorskip("flask")

from app.main import create_app


def test_health_and_index():
    client = create_app().test_client()
    assert client.get("/health").get_json() == {"status": "ok"}
    assert client.get("/").status_code == 200


def test_design_requires_requirements():
    client = create_app().test_client()
    response = client.post("/api/design", json={})
    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_result_empty():
    client = create_app().test_client()
    response = client.get("/api/result")
    assert response.status_code == 404
