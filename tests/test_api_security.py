from fastapi.testclient import TestClient

from api.main import app
from tests.test_api_measure import good_request

client = TestClient(app)


def test_health_is_public(monkeypatch):
    monkeypatch.setenv("CLOTHMATE_API_KEY", "secret123")
    assert client.get("/health").status_code == 200


def test_api_key_is_required_when_configured(monkeypatch):
    monkeypatch.setenv("CLOTHMATE_API_KEY", "secret123")
    assert client.get("/v1/garments").status_code == 401
    assert client.get("/v1/garments", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/v1/garments", headers={"X-API-Key": "secret123"}).status_code == 200


def test_refuses_to_run_unconfigured_outside_dev(monkeypatch):
    monkeypatch.delenv("CLOTHMATE_API_KEY", raising=False)
    monkeypatch.setenv("CLOTHMATE_ENV", "prod")
    assert client.get("/v1/garments").status_code == 503


def test_oversized_request_is_rejected():
    response = client.post("/v1/measure", content="x" * 200_000,
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 413


def test_unexpected_error_does_not_leak_details(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr("api.main.measure_garment", boom)
    safe_client = TestClient(app, raise_server_exceptions=False)
    response = safe_client.post("/v1/measure", json=good_request())
    assert response.status_code == 500
    assert "secret" not in response.text